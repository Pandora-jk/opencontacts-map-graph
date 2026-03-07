#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
import pwd
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MIN_AGE_HOURS = 24
DEFAULT_LIST_LIMIT = 5
TMP_ROOT = Path('/tmp')
PROTECTED_NAMES = {
    '.ICE-unix',
    '.X11-unix',
    '.XIM-unix',
    '.font-unix',
    'hsperfdata_root',
    'snap-private-tmp',
}
PROTECTED_PREFIXES = (
    'systemd-private-',
    'systemd-resolved-',
)


@dataclass(frozen=True)
class CleanupCandidate:
    path: Path
    size_bytes: int
    mtime: dt.datetime
    owner: str
    kind: str


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


def direct_tmp_child(path: Path) -> bool:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return False
    return resolved.parent == TMP_ROOT


def protected_name(path: Path) -> bool:
    if path.name in PROTECTED_NAMES:
        return True
    return any(path.name.startswith(prefix) for prefix in PROTECTED_PREFIXES)


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


def kind_label(path: Path) -> str:
    if path.is_symlink():
        return 'symlink'
    if path.is_dir():
        return 'dir'
    if path.is_file():
        return 'file'
    return 'other'


def validate_candidate(path: Path, *, min_age_hours: int) -> tuple[CleanupCandidate | None, str | None]:
    if not path.exists() and not path.is_symlink():
        return None, 'missing'
    if not direct_tmp_child(path):
        return None, 'not a direct /tmp child'
    if protected_name(path):
        return None, 'protected path'
    if path.is_symlink():
        return None, 'symlink skipped'

    stat = path.lstat()
    owner = path_owner(path)
    current_user = pwd.getpwuid(os.getuid()).pw_name
    if stat.st_uid != os.getuid():
        return None, f'owner {owner} != {current_user}'

    age_cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=min_age_hours)
    mtime = dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc)
    if mtime > age_cutoff:
        return None, f'newer than {min_age_hours}h'
    if has_open_files(path):
        return None, 'open files detected'

    try:
        size_bytes = du_bytes(path)
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return None, 'size check failed'
    return CleanupCandidate(path=path, size_bytes=size_bytes, mtime=mtime, owner=owner, kind=kind_label(path)), None


def scan_cleanup_candidates(*, min_age_hours: int, limit: int | None = None) -> list[CleanupCandidate]:
    candidates: list[CleanupCandidate] = []
    for path in TMP_ROOT.iterdir():
        candidate, _ = validate_candidate(path, min_age_hours=min_age_hours)
        if candidate is None:
            continue
        candidates.append(candidate)
    candidates.sort(key=lambda item: item.size_bytes, reverse=True)
    if limit is not None:
        return candidates[:limit]
    return candidates


def format_candidate(candidate: CleanupCandidate) -> str:
    mtime = candidate.mtime.astimezone(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    return f'- {human_size(candidate.size_bytes)} {mtime}Z {candidate.path} ({candidate.kind}, owner={candidate.owner})'


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink()


def list_mode(min_age_hours: int, limit: int) -> int:
    candidates = scan_cleanup_candidates(min_age_hours=min_age_hours, limit=limit)
    if not candidates:
        print('TMP_CLEANUP_NO_ELIGIBLE_CANDIDATES')
        return 0

    print('TMP_CLEANUP_REVIEW')
    for candidate in candidates:
        print(format_candidate(candidate))
    suggested = ' '.join(f"--path '{candidate.path}'" for candidate in candidates)
    print(f"Suggested apply: python3 tools/infra_tmp_cleanup.py --apply {suggested}")
    return 0


def apply_mode(paths: list[str], min_age_hours: int) -> int:
    if not paths:
        print('TMP_CLEANUP_APPLY_REQUIRES_PATHS', file=sys.stderr)
        return 2

    reclaimed = 0
    removed: list[CleanupCandidate] = []
    skipped: list[str] = []

    for raw in paths:
        candidate, reason = validate_candidate(Path(raw), min_age_hours=min_age_hours)
        if candidate is None:
            skipped.append(f'- {raw}: {reason}')
            continue
        try:
            remove_path(candidate.path)
        except OSError as exc:
            skipped.append(f'- {candidate.path}: remove failed ({exc})')
            continue
        reclaimed += candidate.size_bytes
        removed.append(candidate)

    print('TMP_CLEANUP_RESULT')
    for candidate in removed:
        print(f"removed {human_size(candidate.size_bytes)} {candidate.path}")
    if skipped:
        print('skipped:')
        for line in skipped:
            print(line)
    print(f'total_reclaimed={human_size(reclaimed)}')
    return 0 if removed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description='Safe stale /tmp cleanup helper')
    parser.add_argument('--apply', action='store_true', help='remove the provided paths after validation')
    parser.add_argument('--path', action='append', default=[], help='direct child of /tmp to review or remove')
    parser.add_argument('--min-age-hours', type=int, default=DEFAULT_MIN_AGE_HOURS)
    parser.add_argument('--limit', type=int, default=DEFAULT_LIST_LIMIT)
    args = parser.parse_args()

    if args.apply:
        return apply_mode(args.path, args.min_age_hours)

    if args.path:
        candidates: list[CleanupCandidate] = []
        skipped: list[str] = []
        for raw in args.path:
            candidate, reason = validate_candidate(Path(raw), min_age_hours=args.min_age_hours)
            if candidate is None:
                skipped.append(f'- {raw}: {reason}')
                continue
            candidates.append(candidate)
        if not candidates and skipped:
            print('TMP_CLEANUP_NO_ELIGIBLE_CANDIDATES')
            for line in skipped:
                print(line)
            return 1
        print('TMP_CLEANUP_REVIEW')
        for candidate in candidates:
            print(format_candidate(candidate))
        if skipped:
            print('skipped:')
            for line in skipped:
                print(line)
        suggested = ' '.join(f"--path '{candidate.path}'" for candidate in candidates)
        print(f"Suggested apply: python3 tools/infra_tmp_cleanup.py --apply {suggested}")
        return 0

    return list_mode(args.min_age_hours, args.limit)


if __name__ == '__main__':
    raise SystemExit(main())
