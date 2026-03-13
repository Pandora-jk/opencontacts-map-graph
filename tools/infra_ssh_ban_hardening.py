#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from infra_network import run_cmd

FAIL2BAN_SSH_JAIL = (
    "[sshd]\n"
    "enabled = true\n"
    "port = ssh\n"
    "backend = auto\n"
    "logpath = %(sshd_log)s\n"
    "maxretry = 3\n"
    "findtime = 10m\n"
    "bantime = 4h\n"
)
WORKSPACE_ROOT = Path('/home/ubuntu/.openclaw/workspace')
MANAGED_FAIL2BAN_CONFIG = WORKSPACE_ROOT / 'fail2ban' / '99-openclaw-sshd.local'
LIVE_FAIL2BAN_CONFIG = Path('/etc/fail2ban/jail.d/99-openclaw-sshd.local')
FAIL2BAN_SOCKET = Path('/var/run/fail2ban/fail2ban.sock')
DEFAULT_STAGE_DIR = Path('/tmp/openclaw-fail2ban-stage')


def write_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(FAIL2BAN_SSH_JAIL, encoding='utf-8')
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass


def install_managed_config(target: Path) -> None:
    if not MANAGED_FAIL2BAN_CONFIG.exists():
        raise FileNotFoundError(f'managed config missing: {MANAGED_FAIL2BAN_CONFIG}')
    content = MANAGED_FAIL2BAN_CONFIG.read_text(encoding='utf-8')
    if content != FAIL2BAN_SSH_JAIL:
        raise ValueError(f'managed config drift: {MANAGED_FAIL2BAN_CONFIG}')
    write_config(target)


def staged_config_path(stage_dir: Path) -> Path:
    return stage_dir / LIVE_FAIL2BAN_CONFIG.name


def _resolved_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def is_live_config_path(path: Path) -> bool:
    return _resolved_path(path) == _resolved_path(LIVE_FAIL2BAN_CONFIG)


def validate_stage_dir(stage_dir: Path) -> None:
    if _resolved_path(stage_dir) == _resolved_path(LIVE_FAIL2BAN_CONFIG.parent):
        raise ValueError(
            f'--stage-dir must not point at the live fail2ban jail directory: {stage_dir}'
        )


def validate_install_target(target: Path, *, allow_live_install: bool) -> None:
    if is_live_config_path(target) and not allow_live_install:
        raise ValueError(
            f'--install-to matches the live fail2ban path: {target}; '
            'use the staged workflow first or pass --allow-live-install explicitly'
        )


def _config_mode(path: Path) -> int | None:
    try:
        return path.stat().st_mode & 0o777
    except OSError:
        return None


def _config_status(path: Path, *, label: str, ready_word: str) -> str:
    if not path.exists():
        return f'WARN: {label} config missing: {path}'
    try:
        content = path.read_text(encoding='utf-8')
    except OSError as exc:
        return f'WARN: {label} config unreadable: {exc}'
    if content != FAIL2BAN_SSH_JAIL:
        return f'WARN: {label} config drift: {path}'
    mode = _config_mode(path)
    if mode is None:
        return f'{label} config {ready_word}: {path}'
    if mode != 0o644:
        return f'WARN: {label} config permissions are {mode:04o} (expected 0644): {path}'
    return f'{label} config {ready_word}: {path} (mode 0644)'


def managed_config_status(path: Path = MANAGED_FAIL2BAN_CONFIG) -> str:
    return _config_status(path, label='managed', ready_word='ready')


def live_config_status(path: Path = LIVE_FAIL2BAN_CONFIG) -> str:
    return _config_status(path, label='live', ready_word='installed')


def staged_config_status(path: Path) -> str:
    return _config_status(path, label='staged', ready_word='installed')


def fail2ban_policy_status() -> str:
    return 'INFO: managed fail2ban sshd jail policy: maxretry=3, findtime=10m, bantime=4h'


def fail2ban_socket_status(path: Path = FAIL2BAN_SOCKET) -> str:
    if not path.exists():
        return f'WARN: fail2ban socket missing: {path}'
    details: list[str] = []
    mode = _config_mode(path)
    if mode is not None:
        details.append(f'mode {mode:04o}')
    try:
        stat_result = path.stat()
        if stat_result.st_uid == 0 and stat_result.st_gid == 0:
            details.append('owner root:root')
        else:
            details.append(f'uid={stat_result.st_uid} gid={stat_result.st_gid}')
    except OSError:
        pass
    if details:
        return f'INFO: fail2ban socket present: {path} ({", ".join(details)})'
    return f'INFO: fail2ban socket present: {path}'


def fail2ban_binary_status() -> str:
    lookup = run_cmd(
        [
            'bash',
            '-lc',
            'if command -v fail2ban-client >/dev/null 2>&1; then command -v fail2ban-client; '
            'elif test -x /usr/bin/fail2ban-client; then printf "/usr/bin/fail2ban-client\\n"; fi',
        ],
        max_chars=120,
    )
    if lookup in {'n/a', ''} or lookup.startswith('Error:'):
        return 'WARN: fail2ban-client not visible from this shell'
    return f'fail2ban-client: {lookup.strip()}'


def fail2ban_service_status() -> str:
    status = run_cmd(
        ['bash', '-lc', 'systemctl is-enabled fail2ban 2>/dev/null && systemctl is-active fail2ban 2>/dev/null'],
        max_chars=120,
    )
    if status not in {'n/a', ''} and not status.startswith('Error:'):
        lines = [line.strip() for line in status.splitlines() if line.strip()]
        if len(lines) >= 2:
            return f'fail2ban service: enabled={lines[0]}, active={lines[1]}'
        if len(lines) == 1:
            return f'fail2ban service: {lines[0]}'
    status = run_cmd(['bash', '-lc', 'service fail2ban status 2>/dev/null | sed -n "1,3p"'], max_chars=180)
    if status not in {'n/a', ''} and not status.startswith('Error:'):
        return f'fail2ban service: {" ".join(status.split())}'
    socket_status = fail2ban_socket_status()
    if socket_status.startswith('INFO: fail2ban socket present:'):
        return socket_status.replace(
            'INFO: fail2ban socket present:',
            'INFO: fail2ban service state not visible from current shell; socket present:',
            1,
        )
    return 'WARN: fail2ban service state unavailable from current shell'


def fail2ban_sshd_status() -> str:
    status = run_cmd(['bash', '-lc', 'fail2ban-client status sshd 2>&1 | sed -n "1,20p"'], max_chars=400)
    if 'Permission denied to socket' in status:
        socket_status = fail2ban_socket_status()
        if socket_status.startswith('INFO: fail2ban socket present:'):
            return socket_status.replace(
                'INFO: fail2ban socket present:',
                'INFO: fail2ban sshd jail status requires root; socket present:',
                1,
            )
        return 'WARN: fail2ban sshd jail status requires root but the fail2ban socket is not visible'
    if status in {'n/a', ''} or status.startswith('Error:'):
        socket_status = fail2ban_socket_status()
        if socket_status.startswith('INFO: fail2ban socket present:'):
            return socket_status.replace(
                'INFO: fail2ban socket present:',
                'WARN: fail2ban sshd jail status unavailable from current shell; socket present:',
                1,
            )
        return 'WARN: fail2ban sshd jail unavailable from current shell'
    return f'fail2ban sshd jail:\n{status}'


def current_auth_probe_summary() -> str:
    log = run_cmd(['bash', '-lc', 'tail -n 80 /var/log/auth.log 2>/dev/null | grep -Ei "invalid user|failed|authentication failure|error: pam" | tail -n 8'], max_chars=1200)
    if log in {'n/a', ''} or log.startswith('Error:'):
        return 'Recent auth probe sample unavailable'
    return f'Recent auth probe sample:\n{log}'


def is_live_validation_target(live_config: Path, live_jail_dir: Path) -> bool:
    return live_config == LIVE_FAIL2BAN_CONFIG and live_jail_dir == LIVE_FAIL2BAN_CONFIG.parent


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a safe fail2ban SSH jail preview.')
    parser.add_argument('--write-config', type=Path, help='Write the suggested fail2ban config to this path')
    parser.add_argument('--write-managed-config', action='store_true', help='Write the managed workspace fail2ban config')
    parser.add_argument('--install-to', type=Path, help='Install the managed workspace config to this target path')
    parser.add_argument('--allow-live-install', action='store_true', help='Allow --install-to to target the live /etc fail2ban path')
    parser.add_argument(
        '--stage-dir',
        type=Path,
        help=f'Stage the managed config in this directory for validation without touching /etc (example: {DEFAULT_STAGE_DIR})',
    )
    parser.add_argument('--live-config-path', type=Path, default=LIVE_FAIL2BAN_CONFIG, help='Override the live fail2ban config path used during validation')
    parser.add_argument('--live-jail-dir', type=Path, default=LIVE_FAIL2BAN_CONFIG.parent, help='Override the fail2ban jail.d directory used during validation')
    parser.add_argument('--stdout', action='store_true', help='Print the suggested fail2ban config content')
    parser.add_argument('--validate-live', action='store_true', help='Report managed/live config status plus local fail2ban visibility')
    args = parser.parse_args()

    try:
        if args.allow_live_install and not args.install_to:
            raise ValueError('--allow-live-install requires --install-to')
        if args.stage_dir:
            validate_stage_dir(args.stage_dir)
        if args.install_to:
            validate_install_target(args.install_to, allow_live_install=args.allow_live_install)
    except ValueError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

    effective_live_config = args.live_config_path
    effective_live_jail_dir = args.live_jail_dir
    if args.stage_dir:
        staged_path = staged_config_path(args.stage_dir)
        install_managed_config(staged_path)
        print(f'STAGED_CONFIG {staged_path}')
        if args.live_config_path == LIVE_FAIL2BAN_CONFIG:
            effective_live_config = staged_path
        if args.live_jail_dir == LIVE_FAIL2BAN_CONFIG.parent:
            effective_live_jail_dir = args.stage_dir

    live_target = is_live_validation_target(effective_live_config, effective_live_jail_dir)

    print(fail2ban_binary_status())
    print(fail2ban_service_status())
    print(current_auth_probe_summary())
    print()
    print('Suggested fail2ban jail:')
    print(FAIL2BAN_SSH_JAIL, end='')
    print(fail2ban_policy_status())
    print()
    print('Validation after applying on the host:')
    print(
        'sudo install -D -m 0644 '
        f'{MANAGED_FAIL2BAN_CONFIG} {LIVE_FAIL2BAN_CONFIG}'
    )
    print('sudo systemctl restart fail2ban')
    print('python3 tools/infra_ssh_ban_hardening.py --validate-live')
    print('Safe staging outside /etc:')
    print(
        'python3 tools/infra_ssh_ban_hardening.py '
        f'--stage-dir {DEFAULT_STAGE_DIR} '
        '--validate-live'
    )

    if args.stdout:
        print()
        print('STDOUT_CONFIG_BEGIN')
        print(FAIL2BAN_SSH_JAIL, end='')
        print('STDOUT_CONFIG_END')
    if args.write_config:
        write_config(args.write_config)
        print()
        print(f'WROTE_CONFIG {args.write_config}')
    if args.write_managed_config:
        write_config(MANAGED_FAIL2BAN_CONFIG)
        print()
        print(f'WROTE_MANAGED_CONFIG {MANAGED_FAIL2BAN_CONFIG}')
    if args.install_to:
        install_managed_config(args.install_to)
        print()
        print(f'INSTALLED_CONFIG {args.install_to}')
    if args.validate_live:
        print()
        print(f"Validation target: {'live' if live_target else 'staged'}")
        print('Managed status:')
        print(managed_config_status())
        print('Applied config status:')
        if live_target:
            applied_status = live_config_status(effective_live_config)
        else:
            applied_status = staged_config_status(effective_live_config)
        print(applied_status)
        print('Live jail visibility:')
        print(fail2ban_sshd_status())
        if live_target:
            if not applied_status.startswith('live config installed:'):
                print('ERROR: live validation requires the managed /etc fail2ban jail to be installed cleanly before the host can be marked remediated')
                print('LIVE_VALIDATION_FAILED')
                return 1
            print('LIVE_VALIDATION_DONE')
        else:
            if not applied_status.startswith('staged config installed:'):
                print('ERROR: staged validation requires the staged config to match the managed content')
                print('STAGED_VALIDATION_FAILED')
                return 1
            print('NOTE: staged validation only confirms the managed config content/path; it does not enable host bans until the live /etc install and fail2ban restart.')
            print('STAGED_VALIDATION_READY')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
