#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import shlex
import subprocess
from pathlib import Path

from infra_home_cache_cleanup import (
    ALLOWED_CACHE_TARGETS,
    CleanupCandidate,
    DEFAULT_MIN_BYTES as HOME_CACHE_MIN_BYTES,
    applyable_candidates as filter_applyable_home_cache_candidates,
    blocked_candidates as filter_blocked_home_cache_candidates,
    scan_cleanup_candidates as scan_home_cache_cleanup_candidates,
    select_reclaim_bundle as select_home_cache_reclaim_bundle,
    suggested_apply_args as suggested_home_cache_apply_args,
    total_reclaim_bytes as total_home_cache_reclaim_bytes,
)
from infra_tmp_cleanup import DEFAULT_MIN_AGE_HOURS, scan_cleanup_candidates
from infra_workspace_cache_cleanup import (
    DEFAULT_MIN_BYTES as WORKSPACE_CACHE_MIN_BYTES,
    CleanupCandidate as WorkspaceCleanupCandidate,
    applyable_candidates as filter_applyable_workspace_cache_candidates,
    blocked_candidates as filter_blocked_workspace_cache_candidates,
    scan_cleanup_candidates as scan_workspace_cache_cleanup_candidates,
    select_reclaim_bundle as select_workspace_cache_reclaim_bundle,
    suggested_apply_args as suggested_workspace_cache_apply_args,
    total_reclaim_bytes as total_workspace_cache_reclaim_bytes,
)

DISK_ALERT_THRESHOLD = 80
DISK_CRITICAL_THRESHOLD = 90
INODE_ALERT_THRESHOLD = 85

_TMP_STALE_MINUTES = 24 * 60
_TMP_STALE_LIMIT = 5
_RECLAIM_TARGETS = (
    (Path('/tmp'), 200 * 1024 * 1024, 'temporary files under /tmp'),
    (Path('/var/cache/apt'), 150 * 1024 * 1024, 'APT package cache'),
    (Path('/var/log/journal'), 100 * 1024 * 1024, 'systemd journals'),
)
_REVIEW_ONLY_CACHE_ROOTS = (
    (
        Path('/home/ubuntu/.cache'),
        200 * 1024 * 1024,
        'shared cache root; review allowlisted build/package caches before deleting app state',
    ),
)
_HOTSPOT_LIMIT = 6
_HOTSPOT_DEPTH = {
    Path('/tmp'): 1,
    Path('/var/cache/apt'): 2,
    Path('/var/log/journal'): 1,
    Path('/home/ubuntu/.openclaw/workspace/.gradle'): 2,
    Path('/home/ubuntu/.cache'): 2,
    Path('/home/ubuntu/.npm'): 2,
    Path('/home/ubuntu/.gradle/caches'): 2,
    Path('/home/ubuntu/.gradle/wrapper/dists'): 2,
    Path('/home/ubuntu/.cache/pip'): 2,
    Path('/home/ubuntu/.cache/go-build'): 1,
    Path('/home/ubuntu/.cache/node-gyp'): 2,
}
_HOME_REVIEW_ROOT = Path('/home/ubuntu')
_HOME_REVIEW_THRESHOLD_BYTES = 1024 * 1024 * 1024
_HOME_REVIEW_LIMIT = 12
_HOME_REVIEW_DEPTH = 2
_PROTECTED_HOME_TARGETS = {
    Path('/home/ubuntu/.npm-global'): 'global npm packages; removing may break installed CLIs',
    Path('/home/ubuntu/.local/share/pipx/venvs'): 'pipx virtualenvs; removing breaks installed pipx apps',
    Path('/home/ubuntu/.local/share/claude/versions'): 'Claude local app versions; treat as installed software',
    Path('/home/ubuntu/.android-sdk'): 'Android SDK toolchains; removing breaks Android builds',
}
_PROTECTED_HOME_THRESHOLD_BYTES = 200 * 1024 * 1024
_HOST_LEVEL_RECOVERY_TARGETS = {
    Path('/var/cache/apt'): 'sudo apt-get clean',
    Path('/var/log/journal'): 'sudo journalctl --vacuum-time=7d',
}


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


def current_root_usage_bytes() -> tuple[int, int, int, int, str] | None:
    output = run_cmd(['bash', '-lc', "df -B1 -P / | awk 'NR==2 {print $2, $3, $4, $5, $6}'"], max_chars=200)
    match = re.search(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%\s+(\S+)', output)
    if not match:
        return None
    total_bytes, used_bytes, avail_bytes, used_pct, mount = match.groups()
    return int(total_bytes), int(used_bytes), int(avail_bytes), int(used_pct), mount


def bytes_to_target_usage(total_bytes: int, used_bytes: int, target_pct: int) -> int:
    allowed_used = (total_bytes * target_pct) // 100
    return max(0, used_bytes - allowed_used)


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
    try:
        home_candidates = scan_home_cache_cleanup_candidates(min_bytes=HOME_CACHE_MIN_BYTES)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        home_candidates = []
    for candidate in home_candidates:
        candidates.append((candidate.size_bytes, candidate.path, candidate.note))
    try:
        workspace_candidates = scan_workspace_cache_cleanup_candidates(min_bytes=WORKSPACE_CACHE_MIN_BYTES)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        workspace_candidates = []
    for candidate in workspace_candidates:
        candidates.append((candidate.size_bytes, candidate.path, candidate.note))
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
    home_cache_paths: list[Path] = []
    workspace_cache_paths: list[Path] = []
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

        if path in ALLOWED_CACHE_TARGETS:
            home_cache_paths.append(path)
            continue
        if str(path).startswith('/home/ubuntu/.openclaw/workspace/'):
            workspace_cache_paths.append(path)
            continue
        if path == Path('/var/cache/apt'):
            lines.append('APT cleanup hint: sudo apt-get clean')
        elif path == Path('/var/log/journal'):
            lines.append('Journal review hint: journalctl --disk-usage')
            lines.append('Journal vacuum hint: sudo journalctl --vacuum-time=7d')
    helper_lines = summarize_home_cache_cleanup_helper(home_cache_paths)
    if helper_lines:
        lines.extend(helper_lines)
    workspace_helper_lines = summarize_workspace_cache_cleanup_helper(workspace_cache_paths)
    if workspace_helper_lines:
        lines.extend(workspace_helper_lines)
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


def summarize_review_only_cache_roots() -> list[str]:
    lines: list[str] = []
    for path, min_bytes, note in _REVIEW_ONLY_CACHE_ROOTS:
        size_bytes = path_usage_bytes(path)
        if size_bytes is None or size_bytes < min_bytes:
            continue
        if not lines:
            lines.append('Review-only cache roots (not safe broad cleanup targets):')
        lines.append(f'- {human_size(size_bytes)} {path} ({note})')
        hotspot_lines = summarize_hotspots(path)
        if hotspot_lines:
            lines.extend(hotspot_lines)
        lines.append('Cache review hint: focus on package/build caches before deleting app state')
    return lines


def collect_protected_home_paths() -> list[tuple[int, Path, str]]:
    candidates: list[tuple[int, Path, str]] = []
    for path, note in _PROTECTED_HOME_TARGETS.items():
        size_bytes = path_usage_bytes(path)
        if size_bytes is None or size_bytes < _PROTECTED_HOME_THRESHOLD_BYTES:
            continue
        candidates.append((size_bytes, path, note))
    return sorted(candidates, key=lambda item: item[0], reverse=True)


def summarize_protected_home_paths() -> list[str]:
    candidates = collect_protected_home_paths()
    if not candidates:
        return []

    lines = ['Protected install roots under /home/ubuntu (manual review, not safe cache cleanup):']
    for size_bytes, path, note in candidates:
        lines.append(f'- {human_size(size_bytes)} {path} ({note})')
    lines.append(
        'Protected-root hint: reclaim caches first; remove these only when intentionally uninstalling the owning toolchain'
    )
    return lines


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


def summarize_home_cache_cleanup_helper(paths: list[Path]) -> list[str]:
    unique_paths: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path not in ALLOWED_CACHE_TARGETS or path in seen:
            continue
        seen.add(path)
        unique_paths.append(path)

    if not unique_paths:
        return []

    quoted = ' '.join(f"--path {shlex.quote(str(path))}" for path in unique_paths)
    lines = [
        'Home cache cleanup helper available for allowlisted user-owned caches:',
        f'- Review: python3 tools/infra_home_cache_cleanup.py {quoted}',
    ]

    try:
        scanned_candidates = scan_home_cache_cleanup_candidates(min_bytes=HOME_CACHE_MIN_BYTES)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        scanned_candidates = []

    candidate_by_path = {candidate.path: candidate for candidate in scanned_candidates}
    selected_candidates: list[CleanupCandidate] = []
    blocked_missing: list[tuple[Path, str]] = []
    for path in unique_paths:
        candidate = candidate_by_path.get(path)
        if candidate is None:
            blocked_missing.append((path, 'candidate scan unavailable for current session'))
            continue
        selected_candidates.append(candidate)

    applyable = filter_applyable_home_cache_candidates(selected_candidates)
    blocked = filter_blocked_home_cache_candidates(selected_candidates)

    if applyable:
        lines.append(f'- Apply: python3 tools/infra_home_cache_cleanup.py --apply {suggested_home_cache_apply_args(applyable)}')
    if blocked or blocked_missing:
        lines.append('Home cache apply blocked from current session:')
        for candidate in blocked:
            lines.append(f'- {candidate.path}: {candidate.apply_blocked_reason}')
        for path, reason in blocked_missing:
            lines.append(f'- {path}: {reason}')
        lines.append('Run cleanup from a shell with write access to these cache paths')
    return lines


def summarize_workspace_cache_cleanup_helper(paths: list[Path]) -> list[str]:
    unique_paths: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique_paths.append(path)

    if not unique_paths:
        return []

    quoted = ' '.join(f"--path {shlex.quote(str(path))}" for path in unique_paths)
    lines = [
        'Workspace cache cleanup helper available for repo-local caches:',
        f'- Review: python3 tools/infra_workspace_cache_cleanup.py {quoted}',
    ]

    try:
        scanned_candidates = scan_workspace_cache_cleanup_candidates(min_bytes=WORKSPACE_CACHE_MIN_BYTES)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        scanned_candidates = []

    candidate_by_path = {candidate.path: candidate for candidate in scanned_candidates}
    selected_candidates: list[WorkspaceCleanupCandidate] = []
    blocked_missing: list[tuple[Path, str]] = []
    for path in unique_paths:
        candidate = candidate_by_path.get(path)
        if candidate is None:
            blocked_missing.append((path, 'candidate scan unavailable for current session'))
            continue
        selected_candidates.append(candidate)

    applyable = filter_applyable_workspace_cache_candidates(selected_candidates)
    blocked = filter_blocked_workspace_cache_candidates(selected_candidates)

    if applyable:
        lines.append(
            f'- Apply: python3 tools/infra_workspace_cache_cleanup.py --apply {suggested_workspace_cache_apply_args(applyable)}'
        )
    if blocked or blocked_missing:
        lines.append('Workspace cache apply blocked from current session:')
        for candidate in blocked:
            lines.append(f'- {candidate.path}: {candidate.apply_blocked_reason}')
        for path, reason in blocked_missing:
            lines.append(f'- {path}: {reason}')
        lines.append('Run cleanup from a shell with write access to these workspace cache paths')
    return lines


def summarize_home_cache_recovery_plan(total_bytes: int, used_bytes: int, used_pct: int) -> list[str]:
    if used_pct <= DISK_ALERT_THRESHOLD:
        return []

    try:
        candidates = scan_home_cache_cleanup_candidates(min_bytes=HOME_CACHE_MIN_BYTES)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        return []

    if not candidates:
        return []

    total_reclaim = total_home_cache_reclaim_bytes(candidates)
    total_applyable = total_home_cache_reclaim_bytes(filter_applyable_home_cache_candidates(candidates))
    targets: list[int] = []
    if used_pct > DISK_CRITICAL_THRESHOLD:
        targets.append(DISK_CRITICAL_THRESHOLD)
    targets.append(DISK_ALERT_THRESHOLD)

    lines = ['Allowlisted home-cache recovery plan:']
    for target_pct in targets:
        required_bytes = bytes_to_target_usage(total_bytes, used_bytes, target_pct)
        if required_bytes <= 0:
            continue

        bundle = select_home_cache_reclaim_bundle(candidates, required_bytes=required_bytes)
        bundle_reclaim = total_home_cache_reclaim_bytes(bundle)
        applyable_bundle = filter_applyable_home_cache_candidates(bundle)
        applyable_bundle_reclaim = total_home_cache_reclaim_bytes(applyable_bundle)
        blocked_bundle = filter_blocked_home_cache_candidates(bundle)
        lines.append(f'- Need about {human_size(required_bytes)} reclaimed to reach <={target_pct}% on /')
        if bundle and bundle_reclaim >= required_bytes:
            review_args = suggested_home_cache_apply_args(bundle)
            lines.append(
                f'  Allowlisted home caches can cover this with {human_size(bundle_reclaim)} across {len(bundle)} path(s)'
            )
            lines.append(f'  Review bundle: python3 tools/infra_home_cache_cleanup.py {review_args}')
            if applyable_bundle_reclaim >= required_bytes:
                apply_args = suggested_home_cache_apply_args(applyable_bundle)
                lines.append(f'  Apply bundle: python3 tools/infra_home_cache_cleanup.py --apply {apply_args}')
            elif blocked_bundle:
                lines.append(
                    f'  Apply blocked from current session; directly writable bundle capacity is only '
                    f'{human_size(applyable_bundle_reclaim)}'
                )
                for candidate in blocked_bundle:
                    lines.append(f'  - {candidate.path}: {candidate.apply_blocked_reason}')
                lines.append('  Run this cleanup from a writable shell on the host before relying on it for recovery')
            continue

        shortfall = max(0, required_bytes - total_reclaim)
        apply_args = suggested_home_cache_apply_args(candidates)
        lines.append(
            f'  All allowlisted home caches total {human_size(total_reclaim)} across {len(candidates)} path(s); '
            f'short by {human_size(shortfall)}'
        )
        lines.append(f'  Review remaining home caches: python3 tools/infra_home_cache_cleanup.py {apply_args}')
        if total_applyable < total_reclaim:
            lines.append(
                f'  Directly writable home-cache capacity from current session is only {human_size(total_applyable)}'
            )
        lines.append('  Additional host-level reclaim is still required after allowlisted home-cache cleanup')

    return lines


def summarize_workspace_cache_recovery_plan(total_bytes: int, used_bytes: int, used_pct: int) -> list[str]:
    if used_pct <= DISK_ALERT_THRESHOLD:
        return []

    try:
        candidates = scan_workspace_cache_cleanup_candidates(min_bytes=WORKSPACE_CACHE_MIN_BYTES)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        return []

    if not candidates:
        return []

    total_reclaim = total_workspace_cache_reclaim_bytes(candidates)
    total_applyable = total_workspace_cache_reclaim_bytes(filter_applyable_workspace_cache_candidates(candidates))
    targets: list[int] = []
    if used_pct > DISK_CRITICAL_THRESHOLD:
        targets.append(DISK_CRITICAL_THRESHOLD)
    targets.append(DISK_ALERT_THRESHOLD)

    lines = ['Current-session writable workspace-cache plan:']
    for target_pct in targets:
        required_bytes = bytes_to_target_usage(total_bytes, used_bytes, target_pct)
        if required_bytes <= 0:
            continue

        bundle = select_workspace_cache_reclaim_bundle(candidates, required_bytes=required_bytes)
        bundle_reclaim = total_workspace_cache_reclaim_bytes(bundle)
        applyable_bundle = filter_applyable_workspace_cache_candidates(bundle)
        applyable_bundle_reclaim = total_workspace_cache_reclaim_bytes(applyable_bundle)
        blocked_bundle = filter_blocked_workspace_cache_candidates(bundle)
        lines.append(f'- Need about {human_size(required_bytes)} reclaimed to reach <={target_pct}% on /')
        if bundle and bundle_reclaim >= required_bytes:
            review_args = suggested_workspace_cache_apply_args(bundle)
            lines.append(f'  Workspace caches can cover this with {human_size(bundle_reclaim)} across {len(bundle)} path(s)')
            lines.append(f'  Review bundle: python3 tools/infra_workspace_cache_cleanup.py {review_args}')
            if applyable_bundle_reclaim >= required_bytes:
                apply_args = suggested_workspace_cache_apply_args(applyable_bundle)
                lines.append(f'  Apply bundle: python3 tools/infra_workspace_cache_cleanup.py --apply {apply_args}')
            elif blocked_bundle:
                lines.append(
                    f'  Apply blocked from current session; directly writable bundle capacity is only '
                    f'{human_size(applyable_bundle_reclaim)}'
                )
                for candidate in blocked_bundle:
                    lines.append(f'  - {candidate.path}: {candidate.apply_blocked_reason}')
            continue

        shortfall = max(0, required_bytes - total_reclaim)
        apply_args = suggested_workspace_cache_apply_args(candidates)
        lines.append(
            f'  All workspace caches total {human_size(total_reclaim)} across {len(candidates)} path(s); '
            f'short by {human_size(shortfall)}'
        )
        lines.append(f'  Review remaining workspace caches: python3 tools/infra_workspace_cache_cleanup.py {apply_args}')
        if total_applyable < total_reclaim:
            lines.append(
                f'  Directly writable workspace-cache capacity from current session is only {human_size(total_applyable)}'
            )
        lines.append('  Host-level reclaim is still required after workspace-cache cleanup')

    return lines


def total_candidate_bytes(candidates: list[object]) -> int:
    return sum(getattr(candidate, 'size_bytes', 0) for candidate in candidates)


def select_candidate_bundle(candidates: list[object], *, required_bytes: int) -> list[object]:
    if required_bytes <= 0:
        return []

    selected: list[object] = []
    reclaimed = 0
    for candidate in sorted(candidates, key=lambda item: getattr(item, 'size_bytes', 0), reverse=True):
        selected.append(candidate)
        reclaimed += getattr(candidate, 'size_bytes', 0)
        if reclaimed >= required_bytes:
            break
    return selected


def tmp_cleanup_args(candidates: list[object]) -> str:
    return ' '.join(f"--path {shlex.quote(str(getattr(candidate, 'path')))}" for candidate in candidates)


def tmp_review_command(limit: int) -> str:
    return f'python3 tools/infra_tmp_cleanup.py --limit {limit}'


def select_host_level_candidates(candidates: list[tuple[int, Path, str]]) -> list[tuple[int, Path, str]]:
    return [candidate for candidate in candidates if candidate[1] in _HOST_LEVEL_RECOVERY_TARGETS]


def host_level_cleanup_hint(path: Path) -> str | None:
    return _HOST_LEVEL_RECOVERY_TARGETS.get(path)


def summarize_host_level_recovery_plan(
    total_bytes: int,
    used_bytes: int,
    used_pct: int,
    candidates: list[tuple[int, Path, str]],
) -> list[str]:
    if used_pct <= DISK_ALERT_THRESHOLD:
        return []

    host_candidates = select_host_level_candidates(candidates)
    if not host_candidates:
        return []

    total_reclaim = sum(size_bytes for size_bytes, _path, _note in host_candidates)
    targets: list[int] = []
    if used_pct > DISK_CRITICAL_THRESHOLD:
        targets.append(DISK_CRITICAL_THRESHOLD)
    targets.append(DISK_ALERT_THRESHOLD)

    lines = ['Host-level recovery plan (sudo required for host-owned caches/logs):']
    for target_pct in targets:
        required_bytes = bytes_to_target_usage(total_bytes, used_bytes, target_pct)
        if required_bytes <= 0:
            continue

        bundle = select_candidate_bundle(host_candidates, required_bytes=required_bytes)
        bundle_reclaim = sum(size_bytes for size_bytes, _path, _note in bundle)
        lines.append(f'- Need about {human_size(required_bytes)} reclaimed to reach <={target_pct}% on /')
        if bundle and bundle_reclaim >= required_bytes:
            lines.append(
                f'  Host-level caches/logs can cover this with {human_size(bundle_reclaim)} across {len(bundle)} path(s)'
            )
            for _size_bytes, path, _note in bundle:
                hint = host_level_cleanup_hint(path)
                if hint:
                    lines.append(f'  - {path}: {hint}')
            lines.append('  Review these paths from a writable host shell before cleanup')
            continue

        shortfall = max(0, required_bytes - total_reclaim)
        lines.append(
            f'  All host-level caches/logs total {human_size(total_reclaim)} across {len(host_candidates)} path(s); '
            f'short by {human_size(shortfall)}'
        )
        for _size_bytes, path, _note in host_candidates:
            hint = host_level_cleanup_hint(path)
            if hint:
                lines.append(f'  - {path}: {hint}')
        lines.append('  Additional reclaim is still required after host-level cleanup')

    return lines


def summarize_current_session_recovery_plan(total_bytes: int, used_bytes: int, used_pct: int) -> list[str]:
    if used_pct <= DISK_ALERT_THRESHOLD:
        return []

    try:
        candidates = scan_cleanup_candidates(min_age_hours=DEFAULT_MIN_AGE_HOURS, limit=None)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        return []

    if not candidates:
        return []

    total_reclaim = total_candidate_bytes(candidates)
    targets: list[int] = []
    if used_pct > DISK_CRITICAL_THRESHOLD:
        targets.append(DISK_CRITICAL_THRESHOLD)
    targets.append(DISK_ALERT_THRESHOLD)

    lines = ['Current-session writable recovery plan (stale /tmp only):']
    for target_pct in targets:
        required_bytes = bytes_to_target_usage(total_bytes, used_bytes, target_pct)
        if required_bytes <= 0:
            continue

        bundle = select_candidate_bundle(candidates, required_bytes=required_bytes)
        bundle_reclaim = total_candidate_bytes(bundle)
        lines.append(f'- Need about {human_size(required_bytes)} reclaimed to reach <={target_pct}% on /')
        if bundle and bundle_reclaim >= required_bytes:
            args = tmp_cleanup_args(bundle)
            lines.append(f'  Writable stale /tmp paths can cover this with {human_size(bundle_reclaim)} across {len(bundle)} path(s)')
            lines.append(f'  Review bundle: python3 tools/infra_tmp_cleanup.py {args}')
            lines.append(f'  Apply bundle: python3 tools/infra_tmp_cleanup.py --apply {args}')
            continue

        shortfall = max(0, required_bytes - total_reclaim)
        review_limit = min(_TMP_STALE_LIMIT, len(candidates))
        lines.append(
            f'  All writable stale /tmp paths total {human_size(total_reclaim)} across {len(candidates)} path(s); '
            f'short by {human_size(shortfall)}'
        )
        lines.append(f'  Review top stale /tmp paths: {tmp_review_command(review_limit)}')
        if len(candidates) > review_limit:
            lines.append(
                f'  Current scan found {len(candidates)} writable stale /tmp path(s); '
                'rerun the helper with a higher --limit or targeted --path values before cleanup'
            )
        lines.append('  Host-level reclaim is still required after current-session cleanup')

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
    root_snapshot = current_root_usage_bytes()
    if root_snapshot is not None:
        total_bytes, used_bytes, avail_bytes, used_pct, mount = root_snapshot
        lines.append(
            f'Root usage: {mount}: {used_pct}% used '
            f'({human_size(used_bytes)}/{human_size(total_bytes)}, avail {human_size(avail_bytes)})'
        )
        if used_pct > DISK_CRITICAL_THRESHOLD:
            lines.append(f'CRITICAL: Root filesystem usage is {used_pct}% (>{DISK_CRITICAL_THRESHOLD}%)')
            high_pressure = True
        elif used_pct > DISK_ALERT_THRESHOLD:
            lines.append(f'ALERT: Root filesystem usage is {used_pct}% (>{DISK_ALERT_THRESHOLD}%)')
            high_pressure = True
    else:
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
        if root_snapshot is not None:
            total_bytes, used_bytes, _avail_bytes, used_pct, _mount = root_snapshot
            lines.extend(summarize_current_session_recovery_plan(total_bytes, used_bytes, used_pct))
            lines.extend(summarize_workspace_cache_recovery_plan(total_bytes, used_bytes, used_pct))
            lines.extend(summarize_home_cache_recovery_plan(total_bytes, used_bytes, used_pct))
            lines.extend(summarize_host_level_recovery_plan(total_bytes, used_bytes, used_pct, candidates))

        lines.extend(summarize_review_only_cache_roots())
        lines.extend(summarize_home_hotspots())
        lines.extend(summarize_protected_home_paths())
        lines.extend(summarize_deleted_open_files())

    return lines
