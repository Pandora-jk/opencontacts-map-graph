#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from infra_network import (
    LIVE_MDNS_DROPIN,
    MANAGED_MDNS_DROPIN,
    MDNS_RESOLVED_DROPIN,
    has_external_mdns_listener,
    inspect_mdns_exposure,
    live_mdns_dropin_status,
    mdns_listener_processes,
    managed_mdns_dropin_status,
    mdns_listener_owners,
    staged_mdns_dropin_status,
    run_cmd,
    unexpected_mdns_listener_owners,
)

DEFAULT_STAGE_DIR = Path('/tmp/openclaw-mdns-stage')


def current_port_lines() -> str:
    return run_cmd(
        ['bash', '-lc', "ss -H -tuln 2>/dev/null | awk '{print $1, $5}' | sort -u | sed -n '1,80p'"],
        max_chars=4000,
    )


def write_dropin(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(MDNS_RESOLVED_DROPIN, encoding='utf-8')
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass


def install_managed_dropin(target: Path) -> None:
    if not MANAGED_MDNS_DROPIN.exists():
        raise FileNotFoundError(f'managed drop-in missing: {MANAGED_MDNS_DROPIN}')
    content = MANAGED_MDNS_DROPIN.read_text(encoding='utf-8')
    if content != MDNS_RESOLVED_DROPIN:
        raise ValueError(f'managed drop-in drift: {MANAGED_MDNS_DROPIN}')
    write_dropin(target)


def staged_dropin_path(stage_dir: Path) -> Path:
    return stage_dir / LIVE_MDNS_DROPIN.name


def _resolved_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def is_live_dropin_path(path: Path) -> bool:
    return _resolved_path(path) == _resolved_path(LIVE_MDNS_DROPIN)


def validate_stage_dir(stage_dir: Path) -> None:
    if _resolved_path(stage_dir) == _resolved_path(LIVE_MDNS_DROPIN.parent):
        raise ValueError(
            f'--stage-dir must not point at the live resolved drop-in directory: {stage_dir}'
        )


def validate_install_target(target: Path, *, allow_live_install: bool) -> None:
    if is_live_dropin_path(target) and not allow_live_install:
        raise ValueError(
            f'--install-to matches the live resolved drop-in path: {target}; '
            'use the staged workflow first or pass --allow-live-install explicitly'
        )


def is_live_validation_target(live_dropin: Path, resolved_conf: Path, resolved_dropins_dir: Path, nsswitch_path: Path) -> bool:
    return (
        live_dropin == LIVE_MDNS_DROPIN
        and resolved_conf == Path('/etc/systemd/resolved.conf')
        and resolved_dropins_dir == Path('/etc/systemd/resolved.conf.d')
        and nsswitch_path == Path('/etc/nsswitch.conf')
    )


def _status_is_installed(status_line: str, *, label: str) -> bool:
    return status_line.startswith(f'{label} drop-in installed:')


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a safe mDNS hardening drop-in preview.')
    parser.add_argument('--write-dropin', type=Path, help='Write the suggested resolved.conf drop-in to this path')
    parser.add_argument('--write-managed-dropin', action='store_true', help='Write the managed workspace drop-in')
    parser.add_argument('--install-to', type=Path, help='Install the managed workspace drop-in to this target path')
    parser.add_argument('--allow-live-install', action='store_true', help='Allow --install-to to target the live /etc drop-in path')
    parser.add_argument(
        '--stage-dir',
        type=Path,
        help=f'Stage the managed drop-in in this directory for validation without touching /etc (example: {DEFAULT_STAGE_DIR})',
    )
    parser.add_argument('--live-dropin-path', type=Path, default=LIVE_MDNS_DROPIN, help='Override the live drop-in path used during validation')
    parser.add_argument('--resolved-conf', type=Path, default=Path('/etc/systemd/resolved.conf'), help='Override the base resolved.conf path used during validation')
    parser.add_argument('--resolved-dropins-dir', type=Path, default=Path('/etc/systemd/resolved.conf.d'), help='Override the resolved.conf.d directory used during validation')
    parser.add_argument('--nsswitch-path', type=Path, default=Path('/etc/nsswitch.conf'), help='Override the nsswitch.conf path used during validation')
    parser.add_argument('--stdout', action='store_true', help='Print the suggested drop-in content')
    parser.add_argument('--validate-live', action='store_true', help='Report managed/live drop-in status plus current listener state')
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

    effective_live_dropin = args.live_dropin_path
    effective_resolved_dropins_dir = args.resolved_dropins_dir
    if args.stage_dir:
        staged_path = staged_dropin_path(args.stage_dir)
        install_managed_dropin(staged_path)
        print(f'STAGED_DROPIN {staged_path}')
        if args.live_dropin_path == LIVE_MDNS_DROPIN:
            effective_live_dropin = staged_path
        if args.resolved_dropins_dir == Path('/etc/systemd/resolved.conf.d'):
            effective_resolved_dropins_dir = args.stage_dir

    live_target = is_live_validation_target(
        effective_live_dropin,
        args.resolved_conf,
        effective_resolved_dropins_dir,
        args.nsswitch_path,
    )

    port_lines = current_port_lines()
    print(
        inspect_mdns_exposure(
            port_lines,
            live_dropin=effective_live_dropin,
            applied_dropin_label='live' if live_target else 'staged',
            resolved_conf=args.resolved_conf,
            resolved_dropins_dir=effective_resolved_dropins_dir,
            nsswitch_path=args.nsswitch_path,
        )
    )
    print()
    print('Suggested resolved drop-in:')
    print(MDNS_RESOLVED_DROPIN, end='')
    print()
    print('Validation after applying on the host:')
    print(
        'sudo install -D -m 0644 '
        f'{MANAGED_MDNS_DROPIN} {LIVE_MDNS_DROPIN}'
    )
    print('sudo systemctl restart systemd-resolved')
    print('python3 tools/infra_mdns_hardening.py --validate-live')
    print('Safe staging outside /etc:')
    print(
        'python3 tools/infra_mdns_hardening.py '
        f'--stage-dir {DEFAULT_STAGE_DIR} '
        '--validate-live'
    )

    if args.write_dropin:
        write_dropin(args.write_dropin)
        print()
        print(f'WROTE_DROPIN {args.write_dropin}')
    if args.write_managed_dropin:
        write_dropin(MANAGED_MDNS_DROPIN)
        print()
        print(f'WROTE_MANAGED_DROPIN {MANAGED_MDNS_DROPIN}')
    if args.install_to:
        install_managed_dropin(args.install_to)
        print()
        print(f'INSTALLED_DROPIN {args.install_to}')
    if args.validate_live:
        print()
        print(f"Validation target: {'live' if live_target else 'staged'}")
        print('Managed status:')
        print(managed_mdns_dropin_status())
        print('Applied drop-in status:')
        applied_status: str
        if live_target:
            applied_status = live_mdns_dropin_status(effective_live_dropin)
        else:
            applied_status = staged_mdns_dropin_status(effective_live_dropin)
        print(applied_status)
        listener_detail = run_cmd(['bash', '-lc', "ss -H -ulpn 'sport = :5353' 2>/dev/null | sed -n '1,10p'"], max_chars=1200)
        print('Listener check:')
        print(listener_detail)
        if live_target:
            if not _status_is_installed(applied_status, label='live'):
                print('ERROR: live validation requires the managed /etc drop-in to be installed cleanly before the host can be marked remediated')
                print('LIVE_VALIDATION_FAILED')
                return 1
            if has_external_mdns_listener(port_lines):
                listener_processes = mdns_listener_processes(listener_detail)
                nonstandard_owners = unexpected_mdns_listener_owners(mdns_listener_owners(listener_detail))
                if nonstandard_owners:
                    owners_label = ', '.join(nonstandard_owners)
                    print(
                        'ERROR: external udp/5353 is still exposed after live validation; '
                        f'non-standard listener owner(s): {owners_label}'
                    )
                    print(
                        'ERROR: the systemd-resolved drop-in alone is insufficient while that '
                        'service still binds udp/5353; inspect/reconfigure it or block the port upstream'
                    )
                    listener_pids = [pid for owner, pid in listener_processes if pid and owner in nonstandard_owners]
                    if listener_pids:
                        print(
                            'ERROR: inspect the owning process before further /etc changes: '
                            f"`ps -fp {' '.join(listener_pids)}`"
                        )
                else:
                    print('ERROR: external udp/5353 is still exposed after live validation; investigate avahi-daemon/systemd-resolved state or block the port upstream')
                print('LIVE_VALIDATION_FAILED')
                return 1
            print('LIVE_VALIDATION_DONE')
        else:
            if not _status_is_installed(applied_status, label='staged'):
                print('ERROR: staged validation did not produce a valid staged drop-in')
                print('STAGED_VALIDATION_FAILED')
                return 1
            print('NOTE: staged validation only confirms the managed drop-in content/path; external udp/5353 can remain exposed until the live /etc install and service restart.')
            print('STAGED_VALIDATION_READY')
    elif args.stdout or (not args.write_dropin and not args.write_managed_dropin and not args.install_to and not args.stage_dir):
        print()
        print('DROPIN_STDOUT_OK')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
