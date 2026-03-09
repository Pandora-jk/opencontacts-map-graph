#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
import pwd
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MIN_BYTES = 100 * 1024 * 1024
DEFAULT_LIST_LIMIT = 6
ALLOWED_CACHE_TARGETS = {
    Path('/home/ubuntu/.gradle/caches'): 'Gradle dependency cache',
    Path('/home/ubuntu/.gradle/wrapper/dists'): 'Gradle wrapper distributions',
    Path('/home/ubuntu/.npm'): 'npm download cache',
    Path('/home/ubuntu/.cache/pip'): 'pip download cache',
    Path('/home/ubuntu/.cache/go-build'): 'Go build cache',
    Path('/home/ubuntu/.cache/node-gyp'): 'node-gyp build cache',
}


@dataclass(frozen=True)
class CleanupCandidate:
    path: Path
    size_bytes: int
    mtime: dt.datetime
    owner: str
    note: str
    apply_blocked_reason: str | None = None


def human_size(num_bytes: int) -> str:
    units = ('B', 'K', 'M', 'G', 'T')
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == 'B':
                return f'{int(value)}{unit}'
            if value >= 10:
                return f'{value:.0f}{unit}'
            return f'{value:.1f}{unit}'
        value /= 1024
    return f'{int(num_bytes)}B'


def normalize_path(path: Path) -> Path:
    expanded = path.expanduser()
    try:
        return expanded.resolve(strict=False)
    except OSError:
        return expanded


def du_bytes(path: Path) -> int:
    proc = subprocess.run(
        ['bash', '-lc', f"du -sxk '{path}' 2>/dev/null | awk 'NR==1 {{print $1}}'"],
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    value = (proc.stdout or proc.stderr).strip()
    if value.isdigit():
        return int(value) * 1024
    raise ValueError(f'unable to measure {path}')


def path_owner(path: Path) -> str:
    try:
        return pwd.getpwuid(path.lstat().st_uid).pw_name
    except KeyError:
        return str(path.lstat().st_uid)


def has_open_files(path: Path) -> bool:
    if shutil.which('lsof') is None:
        return False
    cmd = ['lsof', '+D', str(path)] if path.is_dir() else ['lsof', str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
    return bool((proc.stdout or '').strip())


def probe_write_access(path: Path) -> str | None:
    probe_dir = path if path.is_dir() else path.parent
    try:
        fd, probe_path = tempfile.mkstemp(prefix='.openclaw-write-probe-', dir=probe_dir)
    except OSError as exc:
        detail = exc.strerror or str(exc)
        return f'current session cannot write inside {probe_dir} ({detail})'

    os.close(fd)
    try:
        Path(probe_path).unlink()
    except OSError as exc:
        detail = exc.strerror or str(exc)
        return f'current session created a probe in {probe_dir} but could not remove it ({detail})'
    return None


def validate_candidate(path: Path, *, min_bytes: int) -> tuple[CleanupCandidate | None, str | None]:
    normalized = normalize_path(path)
    note = ALLOWED_CACHE_TARGETS.get(normalized)
    if note is None:
        return None, 'not an allowlisted home cache path'
    if not normalized.exists():
        return None, 'missing'
    if normalized.is_symlink():
        return None, 'symlink skipped'

    stat = normalized.lstat()
    owner = path_owner(normalized)
    current_user = pwd.getpwuid(os.getuid()).pw_name
    if stat.st_uid != os.getuid():
        return None, f'owner {owner} != {current_user}'
    if has_open_files(normalized):
        return None, 'open files detected'

    try:
        size_bytes = du_bytes(normalized)
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return None, 'size check failed'
    if size_bytes < min_bytes:
        return None, f'smaller than {human_size(min_bytes)}'

    mtime = dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc)
    return (
        CleanupCandidate(
            path=normalized,
            size_bytes=size_bytes,
            mtime=mtime,
            owner=owner,
            note=note,
            apply_blocked_reason=probe_write_access(normalized),
        ),
        None,
    )


def scan_cleanup_candidates(*, min_bytes: int, limit: int | None = None) -> list[CleanupCandidate]:
    candidates: list[CleanupCandidate] = []
    for path in ALLOWED_CACHE_TARGETS:
        candidate, _ = validate_candidate(path, min_bytes=min_bytes)
        if candidate is None:
            continue
        candidates.append(candidate)
    candidates.sort(key=lambda item: item.size_bytes, reverse=True)
    if limit is not None:
        return candidates[:limit]
    return candidates


def total_reclaim_bytes(candidates: list[CleanupCandidate]) -> int:
    return sum(candidate.size_bytes for candidate in candidates)


def select_reclaim_bundle(candidates: list[CleanupCandidate], *, required_bytes: int) -> list[CleanupCandidate]:
    if required_bytes <= 0:
        return []

    selected: list[CleanupCandidate] = []
    reclaimed = 0
    for candidate in sorted(candidates, key=lambda item: item.size_bytes, reverse=True):
        selected.append(candidate)
        reclaimed += candidate.size_bytes
        if reclaimed >= required_bytes:
            break
    return selected


def format_candidate(candidate: CleanupCandidate) -> str:
    mtime = candidate.mtime.astimezone(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    return f'- {human_size(candidate.size_bytes)} {mtime}Z {candidate.path} ({candidate.note}, owner={candidate.owner})'


def suggested_apply_args(candidates: list[CleanupCandidate]) -> str:
    return ' '.join(f"--path {shlex.quote(str(candidate.path))}" for candidate in candidates)


def applyable_candidates(candidates: list[CleanupCandidate]) -> list[CleanupCandidate]:
    return [candidate for candidate in candidates if candidate.apply_blocked_reason is None]


def blocked_candidates(candidates: list[CleanupCandidate]) -> list[CleanupCandidate]:
    return [candidate for candidate in candidates if candidate.apply_blocked_reason is not None]


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink()


def list_mode(min_bytes: int, limit: int) -> int:
    candidates = scan_cleanup_candidates(min_bytes=min_bytes, limit=limit)
    if not candidates:
        print('HOME_CACHE_CLEANUP_NO_ELIGIBLE_CANDIDATES')
        return 0

    print('HOME_CACHE_CLEANUP_REVIEW')
    for candidate in candidates:
        print(format_candidate(candidate))
    applyable = applyable_candidates(candidates)
    blocked = blocked_candidates(candidates)
    if blocked:
        print('apply_blocked:')
        for candidate in blocked:
            print(f'- {candidate.path}: {candidate.apply_blocked_reason}')
        print('Run cleanup from a shell with write access to these cache paths before using --apply')
    if applyable:
        print(f"Suggested apply: python3 tools/infra_home_cache_cleanup.py --apply {suggested_apply_args(applyable)}")
    else:
        print('Suggested apply unavailable from current session')
    return 0


def apply_mode(paths: list[str], min_bytes: int) -> int:
    if not paths:
        print('HOME_CACHE_CLEANUP_APPLY_REQUIRES_PATHS', file=sys.stderr)
        return 2

    reclaimed = 0
    removed: list[CleanupCandidate] = []
    skipped: list[str] = []

    for raw in paths:
        candidate, reason = validate_candidate(Path(raw), min_bytes=min_bytes)
        if candidate is None:
            skipped.append(f'- {raw}: {reason}')
            continue
        if candidate.apply_blocked_reason is not None:
            skipped.append(f'- {candidate.path}: {candidate.apply_blocked_reason}')
            continue
        try:
            remove_path(candidate.path)
        except OSError as exc:
            skipped.append(f'- {candidate.path}: remove failed ({exc})')
            continue
        reclaimed += candidate.size_bytes
        removed.append(candidate)

    print('HOME_CACHE_CLEANUP_RESULT')
    for candidate in removed:
        print(f"removed {human_size(candidate.size_bytes)} {candidate.path}")
    if skipped:
        print('skipped:')
        for line in skipped:
            print(line)
    print(f'total_reclaimed={human_size(reclaimed)}')
    return 0 if removed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description='Safe allowlisted home cache cleanup helper')
    parser.add_argument('--apply', action='store_true', help='remove the provided cache paths after validation')
    parser.add_argument('--path', action='append', default=[], help='allowlisted home cache path to review or remove')
    parser.add_argument('--min-bytes', type=int, default=DEFAULT_MIN_BYTES)
    parser.add_argument('--limit', type=int, default=DEFAULT_LIST_LIMIT)
    args = parser.parse_args()

    if args.apply:
        return apply_mode(args.path, args.min_bytes)

    if args.path:
        candidates: list[CleanupCandidate] = []
        skipped: list[str] = []
        for raw in args.path:
            candidate, reason = validate_candidate(Path(raw), min_bytes=args.min_bytes)
            if candidate is None:
                skipped.append(f'- {raw}: {reason}')
                continue
            candidates.append(candidate)
        if not candidates and skipped:
            print('HOME_CACHE_CLEANUP_NO_ELIGIBLE_CANDIDATES')
            for line in skipped:
                print(line)
            return 1
        print('HOME_CACHE_CLEANUP_REVIEW')
        for candidate in candidates:
            print(format_candidate(candidate))
        if skipped:
            print('skipped:')
            for line in skipped:
                print(line)
        blocked = blocked_candidates(candidates)
        if blocked:
            print('apply_blocked:')
            for candidate in blocked:
                print(f'- {candidate.path}: {candidate.apply_blocked_reason}')
            print('Run cleanup from a shell with write access to these cache paths before using --apply')
        applyable = applyable_candidates(candidates)
        if applyable:
            print(f"Suggested apply: python3 tools/infra_home_cache_cleanup.py --apply {suggested_apply_args(applyable)}")
        else:
            print('Suggested apply unavailable from current session')
        return 0

    return list_mode(args.min_bytes, args.limit)


if __name__ == '__main__':
    raise SystemExit(main())
