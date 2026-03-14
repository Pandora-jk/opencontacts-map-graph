#!/usr/bin/env python3
"""
Helpers for assessing unattended-upgrades configuration and recent activity.
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
from pathlib import Path

AUTO_UPGRADES_CONFIG = Path('/etc/apt/apt.conf.d/20auto-upgrades')
UNATTENDED_UPGRADES_CONFIG = Path('/etc/apt/apt.conf.d/50unattended-upgrades')
UNATTENDED_UPGRADES_LOG = Path('/var/log/unattended-upgrades/unattended-upgrades.log')
APT_HISTORY_LOG = Path('/var/log/apt/history.log')
APT_PERIODIC_DIR = Path('/var/lib/apt/periodic')
REBOOT_REQUIRED = Path('/var/run/reboot-required')
AUTO_UPDATE_STALE_AFTER = dt.timedelta(hours=18)
AUTO_UPDATE_STALLED_AFTER = dt.timedelta(minutes=30)
AUTO_UPDATE_PERIODIC_STAMP_SKEW = dt.timedelta(minutes=5)
AUTO_UPGRADES_REQUIRED_KEYS = {
    'APT::Periodic::Update-Package-Lists': '1',
    'APT::Periodic::Unattended-Upgrade': '1',
}
UNATTENDED_REQUIRED_ORIGINS = (
    '${distro_id}:${distro_codename}-security',
    '${distro_id}:${distro_codename}-updates',
)
_SETTING_RE = re.compile(r'^\s*([^"\s][^"]*?)\s+"([^"]*)";\s*$')
_RUN_TS_RE = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+INFO\s+(.*)$')
_APT_HISTORY_RE = re.compile(r'^(Start-Date|End-Date|Commandline):\s*(.*)$')
_RUN_COMPLETE_PATTERNS = (
    'All upgrades installed',
    'No packages found that can be upgraded unattended and no pending auto-removals',
)
APT_PERIODIC_STAMP_FILES = {
    'update': 'update-stamp',
    'update_success': 'update-success-stamp',
    'download_upgradeable': 'download-upgradeable-stamp',
    'unattended_upgrades': 'unattended-upgrades-stamp',
    'upgrade': 'upgrade-stamp',
}
PACKAGE_MANAGER_COMMAND = ['ps', '-eo', 'pid=,etimes=,comm=,args=']
SYSTEMD_ETC_DIR = Path('/etc/systemd/system')
SYSTEMD_UNIT_DIRS = (
    SYSTEMD_ETC_DIR,
    Path('/lib/systemd/system'),
    Path('/usr/lib/systemd/system'),
)
APT_TIMER_UNITS = (
    'apt-daily.timer',
    'apt-daily-upgrade.timer',
)
SECURITY_SENSITIVE_PACKAGE_GROUPS = (
    ('kernel', re.compile(r'^linux-(?:aws|base|headers|image|libc|modules|tools)\b')),
    ('ssh', re.compile(r'^(?:openssh|ssh)\b')),
    ('openssl', re.compile(r'^(?:libssl|openssl)\b')),
    ('sudo', re.compile(r'^sudo\b')),
    ('systemd', re.compile(r'^(?:libsystemd|systemd)\b')),
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return ''


def _read_mtime(path: Path) -> dt.datetime | None:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.UTC)
    except OSError:
        return None


def parse_auto_upgrade_settings(text: str) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw in text.splitlines():
        match = _SETTING_RE.match(raw.strip())
        if not match:
            continue
        settings[match.group(1).strip()] = match.group(2).strip()
    return settings


def unattended_origins_present(text: str) -> set[str]:
    found: set[str] = set()
    for origin in UNATTENDED_REQUIRED_ORIGINS:
        if origin in text:
            found.add(origin)
    return found


def load_auto_update_config(
    auto_upgrades_path: Path = AUTO_UPGRADES_CONFIG,
    unattended_path: Path = UNATTENDED_UPGRADES_CONFIG,
) -> dict[str, object]:
    auto_text = _read_text(auto_upgrades_path)
    unattended_text = _read_text(unattended_path)
    settings = parse_auto_upgrade_settings(auto_text)
    missing_required = {
        key: expected
        for key, expected in AUTO_UPGRADES_REQUIRED_KEYS.items()
        if settings.get(key) != expected
    }
    origins_present = unattended_origins_present(unattended_text)
    missing_origins = [origin for origin in UNATTENDED_REQUIRED_ORIGINS if origin not in origins_present]
    enabled = not missing_required and not missing_origins
    return {
        'settings': settings,
        'missing_required': missing_required,
        'origins_present': origins_present,
        'missing_origins': missing_origins,
        'enabled': enabled,
        'auto_upgrades_path': auto_upgrades_path,
        'unattended_path': unattended_path,
    }


def parse_latest_unattended_run(
    text: str,
) -> dict[str, object]:
    latest: dict[str, object] = {
        'started_at': None,
        'completed_at': None,
        'completion_line': '',
        'status': 'missing',
    }
    current: dict[str, object] | None = None
    for raw in text.splitlines():
        match = _RUN_TS_RE.match(raw)
        if not match:
            continue
        timestamp = dt.datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.UTC)
        message = match.group(2).strip()
        if message == 'Starting unattended upgrades script':
            current = {
                'started_at': timestamp,
                'completed_at': None,
                'completion_line': '',
                'status': 'started',
            }
            latest = current
            continue
        if current is None:
            continue
        if message in _RUN_COMPLETE_PATTERNS:
            current['completed_at'] = timestamp
            current['completion_line'] = message
            current['status'] = 'completed'

    if latest['started_at'] and latest['status'] != 'completed':
        latest['status'] = 'incomplete'
    return latest


def load_latest_unattended_run(log_path: Path = UNATTENDED_UPGRADES_LOG) -> dict[str, object]:
    text = _read_text(log_path)
    latest = parse_latest_unattended_run(text)
    latest['log_path'] = log_path
    latest['log_available'] = bool(text)
    return latest


def _parse_apt_history_timestamp(value: str) -> dt.datetime | None:
    normalized = ' '.join((value or '').split())
    if not normalized:
        return None
    try:
        return dt.datetime.strptime(normalized, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.UTC)
    except ValueError:
        return None


def parse_apt_history_transactions(text: str) -> list[dict[str, object]]:
    transactions: list[dict[str, object]] = []
    current: dict[str, str] = {}

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if current:
                transactions.append(current)
                current = {}
            continue
        match = _APT_HISTORY_RE.match(line)
        if not match:
            continue
        current[match.group(1)] = match.group(2).strip()

    if current:
        transactions.append(current)

    parsed: list[dict[str, object]] = []
    for transaction in transactions:
        commandline = transaction.get('Commandline', '').strip()
        started_at = _parse_apt_history_timestamp(transaction.get('Start-Date', ''))
        completed_at = _parse_apt_history_timestamp(transaction.get('End-Date', ''))
        if not commandline and started_at is None and completed_at is None:
            continue
        parsed.append(
            {
                'commandline': commandline,
                'started_at': started_at,
                'completed_at': completed_at,
            }
        )
    return parsed


def load_latest_unattended_history_transaction(log_path: Path = APT_HISTORY_LOG) -> dict[str, object]:
    text = _read_text(log_path)
    transactions = parse_apt_history_transactions(text)
    unattended = [
        transaction
        for transaction in transactions
        if 'unattended-upgrade' in str(transaction.get('commandline', ''))
    ]
    latest = unattended[-1] if unattended else {'commandline': '', 'started_at': None, 'completed_at': None}
    latest['history_path'] = log_path
    latest['history_available'] = bool(text)
    return latest


def load_periodic_stamp_times(periodic_dir: Path = APT_PERIODIC_DIR) -> dict[str, object]:
    stamps: dict[str, object] = {'periodic_dir': periodic_dir}
    for key, filename in APT_PERIODIC_STAMP_FILES.items():
        stamps[key] = _read_mtime(periodic_dir / filename)
    return stamps


def load_systemd_unit_enablement(
    unit_name: str,
    *,
    systemd_etc_dir: Path = SYSTEMD_ETC_DIR,
    unit_dirs: tuple[Path, ...] = SYSTEMD_UNIT_DIRS,
) -> dict[str, object]:
    wants_link = systemd_etc_dir / 'timers.target.wants' / unit_name
    local_override = systemd_etc_dir / unit_name
    masked = False
    unit_path: Path | None = None

    if local_override.exists():
        unit_path = local_override
        if local_override.is_symlink() and local_override.resolve(strict=False) == Path('/dev/null'):
            masked = True

    if unit_path is None:
        for base in unit_dirs:
            candidate = base / unit_name
            if candidate.exists():
                unit_path = candidate
                break

    if masked:
        status = 'masked'
    elif wants_link.exists():
        status = 'enabled'
    elif unit_path is not None:
        status = 'disabled'
    else:
        status = 'missing'

    return {
        'unit': unit_name,
        'status': status,
        'wants_link': wants_link,
        'unit_path': unit_path,
    }


def load_apt_timer_statuses(
    *,
    systemd_etc_dir: Path = SYSTEMD_ETC_DIR,
    unit_dirs: tuple[Path, ...] = SYSTEMD_UNIT_DIRS,
    timer_units: tuple[str, ...] = APT_TIMER_UNITS,
) -> dict[str, dict[str, object]]:
    return {
        unit_name: load_systemd_unit_enablement(
            unit_name,
            systemd_etc_dir=systemd_etc_dir,
            unit_dirs=unit_dirs,
        )
        for unit_name in timer_units
    }


def summarize_apt_timer_statuses(timer_statuses: dict[str, dict[str, object]]) -> str:
    expected = [timer_statuses.get(unit) for unit in APT_TIMER_UNITS]
    active_statuses = [status for status in expected if status]
    if active_statuses and all(status.get('status') == 'enabled' for status in active_statuses):
        joined = ', '.join(str(status.get('unit', 'timer')) for status in active_statuses)
        return f'INFO: auto-update timers enabled at boot ({joined})'

    details: list[str] = []
    for unit_name in APT_TIMER_UNITS:
        status = timer_statuses.get(unit_name)
        if not status:
            details.append(f'{unit_name}=unknown')
            continue
        unit_state = str(status.get('status', 'unknown'))
        if unit_state == 'enabled':
            continue
        detail = f'{unit_name}={unit_state}'
        unit_path = status.get('unit_path')
        if isinstance(unit_path, Path):
            detail += f' ({unit_path})'
        details.append(detail)

    if not details:
        return 'INFO: auto-update timer visibility unavailable'
    return 'RISK: auto-update timers not enabled at boot: ' + '; '.join(details)


def parse_upgradable_packages(package_lines: list[str]) -> list[str]:
    packages: list[str] = []
    for raw in package_lines:
        line = raw.strip()
        if '/' not in line:
            continue
        package = line.split('/', 1)[0].strip()
        if package and package not in packages:
            packages.append(package)
    return packages


def summarize_security_sensitive_packages(package_names: list[str]) -> str:
    groups: list[str] = []
    for label, pattern in SECURITY_SENSITIVE_PACKAGE_GROUPS:
        matched = [name for name in package_names if pattern.match(name)]
        if matched:
            groups.append(f'{label}={", ".join(matched)}')
    return '; '.join(groups)


def format_elapsed_seconds(seconds: int) -> str:
    remaining = max(0, int(seconds))
    days, remaining = divmod(remaining, 86400)
    hours, remaining = divmod(remaining, 3600)
    minutes, _ = divmod(remaining, 60)
    parts: list[str] = []
    if days:
        parts.append(f'{days}d')
    if hours:
        parts.append(f'{hours}h')
    if minutes or not parts:
        parts.append(f'{minutes}m')
    return ' '.join(parts)


def parse_package_manager_processes(text: str) -> list[dict[str, object]]:
    processes: list[dict[str, object]] = []
    for raw in text.splitlines():
        parts = raw.strip().split(None, 3)
        if len(parts) < 4:
            continue
        pid_text, etimes_text, comm, args = parts
        if not pid_text.isdigit() or not etimes_text.isdigit():
            continue

        args_lower = args.lower()
        role = ''
        active = True
        if 'unattended-upgrade-shutdown' in args_lower:
            role = 'unattended-upgrade-shutdown'
            active = False
        elif 'unattended-upgrade' in args_lower:
            role = 'unattended-upgrade'
        elif comm.lower() in {'apt', 'apt-get', 'aptitude', 'dpkg'}:
            role = comm.lower()
        elif re.search(r'\b(?:apt|apt-get|aptitude|dpkg)\b', args_lower):
            role_match = re.search(r'\b(apt-get|aptitude|apt|dpkg)\b', args_lower)
            role = role_match.group(1) if role_match else comm.lower()
        if not role:
            continue

        processes.append(
            {
                'pid': int(pid_text),
                'elapsed_seconds': int(etimes_text),
                'comm': comm,
                'args': args,
                'role': role,
                'active': active,
            }
        )
    return processes


def load_package_manager_processes() -> list[dict[str, object]]:
    try:
        output = subprocess.run(
            PACKAGE_MANAGER_COMMAND,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return []

    text = (output.stdout or output.stderr or '').strip()
    if not text:
        return []
    return parse_package_manager_processes(text)


def summarize_active_package_manager_processes(processes: list[dict[str, object]]) -> str:
    active = [process for process in processes if process.get('active')]
    if not active:
        return 'INFO: package-manager activity: no active apt/dpkg/unattended-upgrades process visible'

    parts: list[str] = []
    for process in active[:3]:
        role = str(process.get('role', 'process'))
        pid = process.get('pid', '?')
        elapsed = format_elapsed_seconds(int(process.get('elapsed_seconds', 0)))
        parts.append(f'{role}(pid={pid}, runtime={elapsed})')
    if len(active) > 3:
        parts.append(f'+{len(active) - 3} more')
    return 'INFO: package-manager activity: ' + '; '.join(parts)


def _latest_timestamp(*timestamps: object) -> dt.datetime | None:
    parsed = [value for value in timestamps if isinstance(value, dt.datetime)]
    return max(parsed) if parsed else None


def _format_timestamp(value: dt.datetime) -> str:
    return value.strftime('%Y-%m-%d %H:%M UTC')


def render_auto_update_health(
    pending_count: int,
    *,
    now: dt.datetime | None = None,
    config: dict[str, object] | None = None,
    latest_run: dict[str, object] | None = None,
    latest_history: dict[str, object] | None = None,
    periodic_stamps: dict[str, object] | None = None,
    timer_statuses: dict[str, dict[str, object]] | None = None,
    package_lines: list[str] | None = None,
    reboot_required: bool | None = None,
    reboot_required_path: Path = REBOOT_REQUIRED,
    package_manager_processes: list[dict[str, object]] | None = None,
) -> str:
    reference_now = now or dt.datetime.now(dt.UTC)
    current_config = config if config is not None else load_auto_update_config()
    current_run = latest_run if latest_run is not None else load_latest_unattended_run()
    current_history = latest_history if latest_history is not None else load_latest_unattended_history_transaction()
    current_periodic_stamps = periodic_stamps if periodic_stamps is not None else load_periodic_stamp_times()
    current_timer_statuses = timer_statuses if timer_statuses is not None else load_apt_timer_statuses()
    package_names = parse_upgradable_packages(package_lines or [])
    sensitive_packages = summarize_security_sensitive_packages(package_names)
    reboot_required_now = reboot_required if reboot_required is not None else reboot_required_path.exists()
    lines = [f'{pending_count} pending updates' if pending_count > 0 else 'No pending updates']

    enabled = bool(current_config.get('enabled'))
    settings = current_config.get('settings', {})
    update_value = settings.get('APT::Periodic::Update-Package-Lists', 'unset')
    unattended_value = settings.get('APT::Periodic::Unattended-Upgrade', 'unset')
    if enabled:
        lines.append(
            'INFO: auto-updates enabled '
            f'(APT::Periodic::Update-Package-Lists={update_value}, '
            f'APT::Periodic::Unattended-Upgrade={unattended_value})'
        )
        lines.append(summarize_apt_timer_statuses(current_timer_statuses))
    else:
        reasons: list[str] = []
        missing_required = current_config.get('missing_required', {})
        if missing_required:
            for key, expected in missing_required.items():
                actual = settings.get(key, 'unset')
                reasons.append(f'{key}={actual} (expected {expected})')
        missing_origins = current_config.get('missing_origins', [])
        if missing_origins:
            reasons.append(f'missing origins: {", ".join(missing_origins)}')
        detail = '; '.join(reasons) if reasons else 'required unattended-upgrades settings missing'
        lines.append(f'RISK: auto-updates disabled or drifted ({detail})')

    started_at = current_run.get('started_at')
    completed_at = current_run.get('completed_at')
    status = current_run.get('status', 'missing')
    completion_line = str(current_run.get('completion_line', '')).strip()
    history_started_at = current_history.get('started_at')
    history_completed_at = current_history.get('completed_at')
    history_commandline = str(current_history.get('commandline', '')).strip()
    periodic_update_at = _latest_timestamp(
        current_periodic_stamps.get('update'),
        current_periodic_stamps.get('update_success'),
        current_periodic_stamps.get('download_upgradeable'),
    )
    periodic_completion_at = _latest_timestamp(
        current_periodic_stamps.get('unattended_upgrades'),
        current_periodic_stamps.get('upgrade'),
    )
    history_confirms_completion = (
        status == 'incomplete'
        and isinstance(started_at, dt.datetime)
        and isinstance(history_completed_at, dt.datetime)
        and history_completed_at >= started_at
        and 'unattended-upgrade' in history_commandline
    )
    periodic_confirms_completion = (
        status == 'incomplete'
        and isinstance(started_at, dt.datetime)
        and isinstance(periodic_completion_at, dt.datetime)
        and periodic_completion_at >= started_at
    )
    if history_confirms_completion:
        completed_at = history_completed_at
        status = 'completed'
        completion_line = 'apt history recorded a completed unattended-upgrade transaction'
    elif periodic_confirms_completion:
        completed_at = periodic_completion_at
        status = 'completed'
        completion_line = 'apt periodic stamps recorded a newer unattended-upgrades/upgrade completion'

    if status == 'completed' and isinstance(completed_at, dt.datetime):
        age = reference_now - completed_at
        age_hours = max(0, int(age.total_seconds() // 3600))
        lines.append(
            'INFO: unattended-upgrades last completed at '
            f'{_format_timestamp(completed_at)} ({age_hours}h ago): {completion_line}'
        )
    elif status == 'incomplete' and isinstance(started_at, dt.datetime):
        age = reference_now - started_at
        age_hours = max(0, int(age.total_seconds() // 3600))
        processes = package_manager_processes if package_manager_processes is not None else load_package_manager_processes()
        active_processes = [process for process in processes if process.get('active')]
        severity = 'WARN' if pending_count > 0 else 'INFO'
        suffix = (
            'but no completion was logged'
            if pending_count > 0
            else 'but no completion was logged; no pending updates remain'
        )
        lines.append(
            f'{severity}: unattended-upgrades last started at '
            f'{_format_timestamp(started_at)} ({age_hours}h ago) {suffix}'
        )
        lines.append(summarize_active_package_manager_processes(processes))
        if (
            pending_count > 0
            and isinstance(periodic_update_at, dt.datetime)
            and periodic_update_at >= started_at - AUTO_UPDATE_PERIODIC_STAMP_SKEW
            and (
                not isinstance(periodic_completion_at, dt.datetime)
                or periodic_completion_at < started_at
            )
        ):
            completion_desc = (
                _format_timestamp(periodic_completion_at)
                if isinstance(periodic_completion_at, dt.datetime)
                else 'none recorded'
            )
            lines.append(
                'WARN: apt periodic stamps recorded fresh update discovery at '
                f'{_format_timestamp(periodic_update_at)} but no newer unattended-upgrades/upgrade completion '
                f'stamp was written (latest completion stamp: {completion_desc})'
            )
        if pending_count > 0 and not active_processes and age >= AUTO_UPDATE_STALLED_AFTER:
            lines.append(
                'RISK: unattended-upgrades appears stalled; '
                f'last start was {_format_timestamp(started_at)} and '
                'no active package-manager process is visible'
            )
    else:
        log_path = current_run.get('log_path', UNATTENDED_UPGRADES_LOG)
        lines.append(f'WARN: unattended-upgrades run history unavailable ({log_path})')

    if reboot_required_now:
        lines.append(f'WARN: reboot required by previously installed updates ({reboot_required_path})')

    if pending_count <= 0:
        return '\n'.join(lines)

    if not enabled:
        lines.append('RISK: pending updates are waiting while auto-updates are disabled')
    elif status == 'incomplete' and not any(
        line.startswith('RISK: unattended-upgrades appears stalled;') for line in lines
    ):
        lines.append('RISK: pending updates remain after an incomplete unattended-upgrades run')
    elif isinstance(completed_at, dt.datetime):
        age = reference_now - completed_at
        if age > AUTO_UPDATE_STALE_AFTER:
            lines.append(
                'RISK: pending updates remain and unattended-upgrades has not completed recently '
                f'({int(age.total_seconds() // 3600)}h old)'
            )
        else:
            lines.append('INFO: pending updates should clear on the next successful unattended-upgrades run')
    elif status == 'missing':
        lines.append('WARN: pending updates detected but unattended-upgrades completion history is unavailable')

    if sensitive_packages:
        lines.append(f'RISK: security-sensitive updates pending: {sensitive_packages}')
        if 'kernel=' in sensitive_packages:
            lines.append('HARDENING: schedule a maintenance reboot after these updates land')

    return '\n'.join(lines)
