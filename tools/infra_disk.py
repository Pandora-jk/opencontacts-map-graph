#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import shlex
import subprocess
from pathlib import Path

from infra_tmp_cleanup import DEFAULT_MIN_AGE_HOURS, scan_cleanup_candidates

DISK_ALERT_THRESHOLD = 80
DISK_CRITICAL_THRESHOLD = 90
INODE_ALERT_THRESHOLD = 85

_TMP_STALE_MINUTES = 24 * 60
_TMP_STALE_LIMIT = 5
_RECLAIM_TARGETS = (
    (Path('/tmp'), 200 * 1024 * 1024, 'temporary files under /tmp'),
    (Path('/var/cache/apt'), 150 * 1024 * 1024, 'APT package cache'),
    (Path('/var/log/journal'), 100 * 1024 * 1024, 'systemd journals'),
    (Path('/home/ubuntu/.cache'), 200 * 1024 * 1024, 'user cache'),
)
_HOTSPOT_LIMIT = 6
_HOTSPOT_DEPTH = {
    Path('/tmp'): 1,
    Path('/var/cache/apt'): 2,
    Path('/var/log/journal'): 1,
    Path('/home/ubuntu/.cache'): 2,
}
_HOME_REVIEW_ROOT = Path('/home/ubuntu')
_HOME_REVIEW_THRESHOLD_BYTES = 1024 * 1024 * 1024
_HOME_REVIEW_LIMIT = 12
_HOME_REVIEW_DEPTH = 2


def run_cmd(cmd: list[str], max_chars: int = 800) -> str:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return f'Error: {str(exc)[:200]}'
    text = (proc.stdout or proc.stderr).strip()
    return text[:max_chars] if text else 'n/a'


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


def path_usage_bytes(path: Path) -> int | None:
    if not path.exists():
        return None
    output = run_cmd(
        ['bash', '-lc', f"du -sxk '{path}' 2>/dev/null | awk 'NR==1 {{print $1}}'"],
        max_chars=64,
    )
    if output.startswith('Error:') or not output.isdigit():
        return None
    return int(output) * 1024


def summarize_reclaim_candidates() -> list[str]:
    candidates: list[tuple[int, Path, str]] = []
    for path, min_bytes, note in _RECLAIM_TARGETS:
        size_bytes = path_usage_bytes(path)
        if size_bytes is None or size_bytes < min_bytes:
            continue
        candidates.append((size_bytes, path, note))

    if not candidates:
        return []

    lines = ['Reclaim candidates (review before cleanup):']
    for size_bytes, path, note in sorted(candidates, key=lambda item: item[0], reverse=True):
        lines.append(f'- {human_size(size_bytes)} {path} ({note})')
    return lines


def collect_reclaim_candidates() -> list[tuple[int, Path, str]]:
    candidates: list[tuple[int, Path, str]] = []
    for path, min_bytes, note in _RECLAIM_TARGETS:
        size_bytes = path_usage_bytes(path)
        if size_bytes is None or size_bytes < min_bytes:
            continue
        candidates.append((size_bytes, path, note))
    return sorted(candidates, key=lambda item: item[0], reverse=True)


def summarize_hotspots(path: Path) -> list[str]:
    depth = _HOTSPOT_DEPTH.get(path, 1)
    output = run_cmd(
        [
            'bash',
            '-lc',
            f"du -x -h --max-depth={depth} '{path}' 2>/dev/null | sort -hr | sed -n '1,{_HOTSPOT_LIMIT}p'",
        ],
        max_chars=2400,
    )
    if output in {'n/a', ''} or output.startswith('Error:'):
        return []
    return [f'Largest paths under {path}:', output]


def summarize_reclaim_guidance(candidates: list[tuple[int, Path, str]]) -> list[str]:
    lines: list[str] = []
    for _, path, _ in candidates:
        if path == Path('/tmp'):
            stale_tmp_lines = summarize_stale_tmp_entries()
            if stale_tmp_lines:
                lines.extend(stale_tmp_lines)
                lines.extend(summarize_tmp_cleanup_helper())
            continue

        hotspot_lines = summarize_hotspots(path)
        if hotspot_lines:
            lines.extend(hotspot_lines)

        if path == Path('/var/cache/apt'):
            lines.append('APT cleanup hint: sudo apt-get clean')
        elif path == Path('/var/log/journal'):
            lines.append('Journal review hint: journalctl --disk-usage')
            lines.append('Journal vacuum hint: sudo journalctl --vacuum-time=7d')
        elif path == Path('/home/ubuntu/.cache'):
            lines.append('Cache review hint: focus on package/build caches before deleting app state')
    return lines


def summarize_home_hotspots() -> list[str]:
    size_bytes = path_usage_bytes(_HOME_REVIEW_ROOT)
    if size_bytes is None or size_bytes < _HOME_REVIEW_THRESHOLD_BYTES:
        return []

    output = run_cmd(
        [
            'bash',
            '-lc',
            (
                f"du -x -h --max-depth={_HOME_REVIEW_DEPTH} '{_HOME_REVIEW_ROOT}' 2>/dev/null | "
                f"sort -hr | sed -n '1,{_HOME_REVIEW_LIMIT}p'"
            ),
        ],
        max_chars=3200,
    )
    if output in {'n/a', ''} or output.startswith('Error:'):
        return []

    return [
        f'Largest paths under {_HOME_REVIEW_ROOT} (review-only):',
        output,
        'Home review hint: prioritize build/package caches before SDKs or active workspaces',
    ]


def summarize_stale_tmp_entries() -> list[str]:
    if not Path('/tmp').exists():
        return []

    output = run_cmd(
        [
            'bash',
            '-lc',
            (
                "find /tmp -mindepth 1 -maxdepth 1 -mmin +1440 -print0 2>/dev/null | "
                "while IFS= read -r -d '' path; do "
                "size_kb=$(du -sxk \"$path\" 2>/dev/null | awk 'NR==1 {print $1}'); "
                "[ -n \"$size_kb\" ] || continue; "
                "mtime=$(stat -c '%y' \"$path\" 2>/dev/null | cut -d'.' -f1); "
                "printf '%s\\t%s\\t%s\\n' \"$size_kb\" \"$mtime\" \"$path\"; "
                "done | sort -nr | sed -n '1,5p'"
            ),
        ],
        max_chars=4000,
    )
    if output in {'n/a', ''} or output.startswith('Error:'):
        return []

    lines = ['Stale /tmp entries older than 24h:']
    added = 0
    for raw in output.splitlines():
        parts = raw.split('\t', 2)
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        size_bytes = int(parts[0]) * 1024
        mtime, path = parts[1], parts[2]
        lines.append(f'- {human_size(size_bytes)} {mtime} {path}')
        added += 1
        if added >= _TMP_STALE_LIMIT:
            break

    if added == 0:
        return []
    return lines


def summarize_tmp_cleanup_helper() -> list[str]:
    try:
        candidates = scan_cleanup_candidates(min_age_hours=DEFAULT_MIN_AGE_HOURS, limit=_TMP_STALE_LIMIT)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        return ['Cleanup helper unavailable (candidate scan failed)']

    if not candidates:
        return []

    quoted = ' '.join(f"--path {shlex.quote(str(candidate.path))}" for candidate in candidates)
    lines = [
        f'Cleanup helper available for ubuntu-owned stale /tmp entries older than {DEFAULT_MIN_AGE_HOURS}h:',
        f'- Review: python3 tools/infra_tmp_cleanup.py {quoted}',
        f'- Apply: python3 tools/infra_tmp_cleanup.py --apply {quoted}',
    ]
    return lines


def summarize_deleted_open_files() -> list[str]:
    if not shutil.which('lsof'):
        return ['Deleted-but-open-file check unavailable (lsof missing)']

    output = run_cmd(['lsof', '+L1', '-nP'], max_chars=20000)
    if output in {'n/a', ''}:
        return ['No deleted-but-open files detected']
    if output.startswith('Error:'):
        return [f'Deleted-but-open-file check error: {output}']

    entries: list[tuple[int, str, str, str]] = []
    for line in output.splitlines()[1:]:
        parts = line.split(None, 8)
        if len(parts) < 9 or '(deleted)' not in parts[8]:
            continue
        size_match = re.match(r'(\d+)', parts[6])
        if not size_match:
            continue
        entries.append((int(size_match.group(1)), parts[0], parts[1], parts[8]))

    if not entries:
        return ['No deleted-but-open files detected']

    total = sum(item[0] for item in entries)
    lines = [f'ALERT: {len(entries)} deleted-but-open files retain {human_size(total)}']
    for size_bytes, command, pid, name in sorted(entries, key=lambda item: item[0], reverse=True)[:5]:
        lines.append(f'- {human_size(size_bytes)} {command} pid={pid} {name}')
    return lines


def build_disk_usage_report() -> list[str]:
    lines: list[str] = []
    high_pressure = False

    disk_line = run_cmd(['bash', '-lc', "df -hP / | awk 'NR==2 {print $2, $3, $4, $5, $6}'"])
    disk_match = re.search(r'(\S+)\s+(\S+)\s+(\S+)\s+(\d+)%\s+(\S+)', disk_line)
    if disk_match:
        size, used, avail, pct_txt, mount = disk_match.groups()
        pct = int(pct_txt)
        lines.append(f'Root usage: {mount}: {pct}% used ({used}/{size}, avail {avail})')
        if pct > DISK_CRITICAL_THRESHOLD:
            lines.append(f'CRITICAL: Root filesystem usage is {pct}% (>{DISK_CRITICAL_THRESHOLD}%)')
            high_pressure = True
        elif pct > DISK_ALERT_THRESHOLD:
            lines.append(f'ALERT: Root filesystem usage is {pct}% (>{DISK_ALERT_THRESHOLD}%)')
            high_pressure = True
    else:
        lines.append(disk_line)

    inode_line = run_cmd(['bash', '-lc', "df -Pi / | awk 'NR==2 {print $5, $6}'"])
    inode_match = re.search(r'(\d+)%\s+(\S+)', inode_line)
    if inode_match:
        inode_pct = int(inode_match.group(1))
        inode_mount = inode_match.group(2)
        lines.append(f'Inodes: {inode_mount}: {inode_pct}% used')
        if inode_pct > INODE_ALERT_THRESHOLD:
            lines.append(f'ALERT: Inode usage on {inode_mount} is {inode_pct}% (>{INODE_ALERT_THRESHOLD}%)')
    else:
        lines.append(f'Inodes: {inode_line}')

    if high_pressure:
        lines.append('Top disk usage under / (depth 1):')
        lines.append(run_cmd(['bash', '-lc', "du -x -h --max-depth=1 / 2>/dev/null | sort -hr | sed -n '1,8p'"], max_chars=1600))

        candidates = collect_reclaim_candidates()
        reclaim_lines: list[str] = []
        if candidates:
            reclaim_lines.append('Reclaim candidates (review before cleanup):')
            for size_bytes, path, note in candidates:
                reclaim_lines.append(f'- {human_size(size_bytes)} {path} ({note})')
        if reclaim_lines:
            lines.extend(reclaim_lines)
            lines.extend(summarize_reclaim_guidance(candidates))

        lines.extend(summarize_home_hotspots())
        lines.extend(summarize_deleted_open_files())

    return lines
