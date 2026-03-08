#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

from infra_network import (
    LIVE_MDNS_DROPIN,
    MANAGED_MDNS_DROPIN,
    MDNS_RESOLVED_DROPIN,
    inspect_mdns_exposure,
    live_mdns_dropin_status,
    managed_mdns_dropin_status,
    run_cmd,
)


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


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a safe mDNS hardening drop-in preview.')
    parser.add_argument('--write-dropin', type=Path, help='Write the suggested resolved.conf drop-in to this path')
    parser.add_argument('--write-managed-dropin', action='store_true', help='Write the managed workspace drop-in')
    parser.add_argument('--install-to', type=Path, help='Install the managed workspace drop-in to this target path')
    parser.add_argument('--live-dropin-path', type=Path, default=LIVE_MDNS_DROPIN, help='Override the live drop-in path used during validation')
    parser.add_argument('--resolved-conf', type=Path, default=Path('/etc/systemd/resolved.conf'), help='Override the base resolved.conf path used during validation')
    parser.add_argument('--resolved-dropins-dir', type=Path, default=Path('/etc/systemd/resolved.conf.d'), help='Override the resolved.conf.d directory used during validation')
    parser.add_argument('--nsswitch-path', type=Path, default=Path('/etc/nsswitch.conf'), help='Override the nsswitch.conf path used during validation')
    parser.add_argument('--stdout', action='store_true', help='Print the suggested drop-in content')
    parser.add_argument('--validate-live', action='store_true', help='Report managed/live drop-in status plus current listener state')
    args = parser.parse_args()

    port_lines = current_port_lines()
    print(
        inspect_mdns_exposure(
            port_lines,
            live_dropin=args.live_dropin_path,
            resolved_conf=args.resolved_conf,
            resolved_dropins_dir=args.resolved_dropins_dir,
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
        '--install-to /tmp/resolved.conf.d/99-openclaw-no-mdns.conf '
        '--validate-live '
        '--live-dropin-path /tmp/resolved.conf.d/99-openclaw-no-mdns.conf '
        '--resolved-dropins-dir /tmp/resolved.conf.d'
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
        print('Managed status:')
        print(managed_mdns_dropin_status())
        print('Live status:')
        print(live_mdns_dropin_status(args.live_dropin_path))
        listener_detail = run_cmd(['bash', '-lc', "ss -H -ulpn 'sport = :5353' 2>/dev/null | sed -n '1,10p'"], max_chars=1200)
        print('Listener check:')
        print(listener_detail)
        print('LIVE_VALIDATION_DONE')
    elif args.stdout or (not args.write_dropin and not args.write_managed_dropin and not args.install_to):
        print()
        print('DROPIN_STDOUT_OK')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
