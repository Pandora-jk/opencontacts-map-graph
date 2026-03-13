#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from infra_network import run_cmd

SSHD_HARDENING_CONFIG = (
    "PasswordAuthentication no\n"
    "PermitRootLogin prohibit-password\n"
    "PermitEmptyPasswords no\n"
    "KbdInteractiveAuthentication no\n"
    "X11Forwarding no\n"
    "AllowTcpForwarding no\n"
    "AllowAgentForwarding no\n"
    "AllowStreamLocalForwarding no\n"
    "PermitTunnel no\n"
    "MaxAuthTries 3\n"
    "LoginGraceTime 30\n"
    "MaxStartups 10:30:60\n"
)
WORKSPACE_ROOT = Path('/home/ubuntu/.openclaw/workspace')
MANAGED_SSHD_CONFIG = WORKSPACE_ROOT / 'ssh' / '99-openclaw-hardening.conf'
LIVE_SSHD_CONFIG = Path('/etc/ssh/sshd_config.d/99-openclaw-hardening.conf')
DEFAULT_STAGE_DIR = Path('/tmp/openclaw-sshd-stage')
KNOWN_SSHD_PATHS = (
    Path('/usr/sbin/sshd'),
    Path('/usr/local/sbin/sshd'),
    Path('/sbin/sshd'),
)
KNOWN_SSH_KEYGEN_PATHS = (
    Path('/usr/bin/ssh-keygen'),
    Path('/bin/ssh-keygen'),
)


def write_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SSHD_HARDENING_CONFIG, encoding='utf-8')
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass


def install_managed_config(target: Path) -> None:
    if not MANAGED_SSHD_CONFIG.exists():
        raise FileNotFoundError(f'managed config missing: {MANAGED_SSHD_CONFIG}')
    content = MANAGED_SSHD_CONFIG.read_text(encoding='utf-8')
    if content != SSHD_HARDENING_CONFIG:
        raise ValueError(f'managed config drift: {MANAGED_SSHD_CONFIG}')
    write_config(target)


def staged_config_path(stage_dir: Path) -> Path:
    return stage_dir / LIVE_SSHD_CONFIG.name


def _resolved_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def is_live_config_path(path: Path) -> bool:
    return _resolved_path(path) == _resolved_path(LIVE_SSHD_CONFIG)


def validate_stage_dir(stage_dir: Path) -> None:
    if _resolved_path(stage_dir) == _resolved_path(LIVE_SSHD_CONFIG.parent):
        raise ValueError(
            f'--stage-dir must not point at the live sshd drop-in directory: {stage_dir}'
        )


def validate_install_target(target: Path, *, allow_live_install: bool) -> None:
    if is_live_config_path(target) and not allow_live_install:
        raise ValueError(
            f'--install-to matches the live sshd path: {target}; '
            'use the staged workflow first or pass --allow-live-install explicitly'
        )


def _config_mode(path: Path) -> int | None:
    try:
        return path.stat().st_mode & 0o777
    except OSError:
        return None


def _config_status(path: Path, *, label: str, ready_word: str) -> str:
    if not path.exists():
        return f'{label} config missing: {path}'
    try:
        content = path.read_text(encoding='utf-8')
    except OSError as exc:
        return f'{label} config unreadable: {exc}'
    if content != SSHD_HARDENING_CONFIG:
        return f'{label} config drift: {path}'
    mode = _config_mode(path)
    if mode is None:
        return f'{label} config {ready_word}: {path}'
    if mode != 0o644:
        return f'WARN: {label} config permissions are {mode:04o} (expected 0644): {path}'
    return f'{label} config {ready_word}: {path} (mode 0644)'


def managed_config_status(path: Path = MANAGED_SSHD_CONFIG) -> str:
    return _config_status(path, label='managed', ready_word='ready')


def live_config_status(path: Path = LIVE_SSHD_CONFIG) -> str:
    return _config_status(path, label='live', ready_word='installed')


def staged_config_status(path: Path) -> str:
    return _config_status(path, label='staged', ready_word='installed')


def find_sshd_binary_path() -> Path | None:
    sshd = shutil.which('sshd')
    if sshd:
        return Path(sshd)
    for candidate in KNOWN_SSHD_PATHS:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    return None


def find_ssh_keygen_binary_path() -> Path | None:
    ssh_keygen = shutil.which('ssh-keygen')
    if ssh_keygen:
        return Path(ssh_keygen)
    for candidate in KNOWN_SSH_KEYGEN_PATHS:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    return None


def validation_hostkey_path(stage_dir: Path) -> Path:
    return stage_dir / 'ssh_host_ed25519_key'


def validation_config_path(stage_dir: Path) -> Path:
    return stage_dir / 'sshd_config'


def validation_main_config(stage_dir: Path) -> str:
    hostkey = validation_hostkey_path(stage_dir)
    pidfile = stage_dir / 'sshd.pid'
    return f'HostKey {hostkey}\nPidFile {pidfile}\nInclude {stage_dir}/*.conf\n'


def _one_line(value: str, max_len: int = 160) -> str:
    compact = ' '.join((value or '').split())
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 1] + '…'


def stage_sshd_configtest(stage_dir: Path) -> str:
    sshd = find_sshd_binary_path()
    if not sshd:
        return 'WARN: sshd config test unavailable from this shell'

    ssh_keygen = find_ssh_keygen_binary_path()
    if not ssh_keygen:
        return 'WARN: ssh-keygen unavailable from this shell; skipped staged sshd config test'

    hostkey = validation_hostkey_path(stage_dir)
    config_path = validation_config_path(stage_dir)
    if not hostkey.exists():
        hostkey.parent.mkdir(parents=True, exist_ok=True)
        generated = subprocess.run(
            [str(ssh_keygen), '-q', '-N', '', '-t', 'ed25519', '-f', str(hostkey)],
            capture_output=True,
            text=True,
            check=False,
        )
        if generated.returncode != 0:
            details = generated.stderr.strip() or generated.stdout.strip() or 'unknown error'
            return f'WARN: ssh-keygen failed for staged sshd config test: {_one_line(details)}'

    config_path.write_text(validation_main_config(stage_dir), encoding='utf-8')
    try:
        os.chmod(config_path, 0o644)
    except OSError:
        pass

    checked = subprocess.run(
        [str(sshd), '-t', '-f', str(config_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if checked.returncode == 0:
        return f'sshd config test: syntax ok ({config_path})'

    details = checked.stderr.strip() or checked.stdout.strip() or 'unknown error'
    return f'ERROR: sshd config test failed for {config_path}: {_one_line(details)}'


def sshd_binary_status() -> str:
    lookup = find_sshd_binary_path()
    if not lookup:
        return 'WARN: sshd binary not visible from this shell'
    return f'sshd binary: {lookup}'


def ssh_service_status() -> str:
    status = run_cmd(
        ['bash', '-lc', 'systemctl is-enabled ssh 2>/dev/null && systemctl is-active ssh 2>/dev/null'],
        max_chars=120,
    )
    if status not in {'n/a', ''} and not status.startswith('Error:'):
        lines = [line.strip() for line in status.splitlines() if line.strip()]
        if len(lines) >= 2:
            return f'ssh service: enabled={lines[0]}, active={lines[1]}'
        if len(lines) == 1:
            return f'ssh service: {lines[0]}'
    status = run_cmd(['bash', '-lc', 'service ssh status 2>/dev/null | sed -n "1,3p"'], max_chars=180)
    if status not in {'n/a', ''} and not status.startswith('Error:'):
        return f'ssh service: {" ".join(status.split())}'
    return 'ssh service: unavailable from current shell'


def current_auth_probe_summary() -> str:
    log = run_cmd(
        [
            'bash',
            '-lc',
            'tail -n 80 /var/log/auth.log 2>/dev/null | grep -Ei "invalid user|failed|authentication failure|error: pam" | tail -n 8',
        ],
        max_chars=1200,
    )
    if log in {'n/a', ''} or log.startswith('Error:'):
        return 'Recent auth probe sample unavailable'
    return f'Recent auth probe sample:\n{log}'


def is_live_validation_target(live_config: Path, live_config_dir: Path) -> bool:
    return live_config == LIVE_SSHD_CONFIG and live_config_dir == LIVE_SSHD_CONFIG.parent


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a safe sshd hardening drop-in preview.')
    parser.add_argument('--write-config', type=Path, help='Write the suggested sshd drop-in to this path')
    parser.add_argument('--write-managed-config', action='store_true', help='Write the managed workspace sshd config')
    parser.add_argument('--install-to', type=Path, help='Install the managed workspace config to this target path')
    parser.add_argument('--allow-live-install', action='store_true', help='Allow --install-to to target the live /etc sshd path')
    parser.add_argument(
        '--stage-dir',
        type=Path,
        help=f'Stage the managed config in this directory for validation without touching /etc (example: {DEFAULT_STAGE_DIR})',
    )
    parser.add_argument('--live-config-path', type=Path, default=LIVE_SSHD_CONFIG, help='Override the live sshd config path used during validation')
    parser.add_argument('--live-config-dir', type=Path, default=LIVE_SSHD_CONFIG.parent, help='Override the sshd config.d directory used during validation')
    parser.add_argument('--stdout', action='store_true', help='Print the suggested sshd config content')
    parser.add_argument('--validate-live', action='store_true', help='Report managed/live config status plus local ssh service visibility')
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
    effective_live_config_dir = args.live_config_dir
    if args.stage_dir:
        staged_path = staged_config_path(args.stage_dir)
        install_managed_config(staged_path)
        print(f'STAGED_CONFIG {staged_path}')
        if args.live_config_path == LIVE_SSHD_CONFIG:
            effective_live_config = staged_path
        if args.live_config_dir == LIVE_SSHD_CONFIG.parent:
            effective_live_config_dir = args.stage_dir

    live_target = is_live_validation_target(effective_live_config, effective_live_config_dir)

    print(sshd_binary_status())
    print(ssh_service_status())
    print(current_auth_probe_summary())
    print()
    print('Suggested sshd drop-in:')
    print(SSHD_HARDENING_CONFIG, end='')
    print()
    print('Validation after applying on the host:')
    print(
        'sudo install -D -m 0644 '
        f'{MANAGED_SSHD_CONFIG} {LIVE_SSHD_CONFIG}'
    )
    print('sudo systemctl reload ssh')
    print('python3 tools/infra_sshd_hardening.py --validate-live')
    print('Safe staging outside /etc:')
    print(
        'python3 tools/infra_sshd_hardening.py '
        f'--stage-dir {DEFAULT_STAGE_DIR} '
        '--validate-live'
    )

    if args.stdout:
        print()
        print('STDOUT_CONFIG_BEGIN')
        print(SSHD_HARDENING_CONFIG, end='')
        print('STDOUT_CONFIG_END')
    if args.write_config:
        write_config(args.write_config)
        print()
        print(f'WROTE_CONFIG {args.write_config}')
    if args.write_managed_config:
        write_config(MANAGED_SSHD_CONFIG)
        print()
        print(f'WROTE_MANAGED_CONFIG {MANAGED_SSHD_CONFIG}')
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
        if live_target:
            if not applied_status.startswith('live config installed:'):
                print('ERROR: live validation requires the managed /etc sshd drop-in to be installed cleanly before the host can be marked remediated')
                print('LIVE_VALIDATION_FAILED')
                return 1
            print('LIVE_VALIDATION_DONE')
        else:
            if not applied_status.startswith('staged config installed:'):
                print('ERROR: staged validation requires the staged config to match the managed content')
                print('STAGED_VALIDATION_FAILED')
                return 1
            config_test_status = stage_sshd_configtest(effective_live_config_dir)
            print(config_test_status)
            if config_test_status.startswith('ERROR:'):
                print('STAGED_VALIDATION_FAILED')
                return 1
            print('NOTE: staged validation only confirms the managed config content/path; it does not reload the live ssh service.')
            print('STAGED_VALIDATION_READY')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
