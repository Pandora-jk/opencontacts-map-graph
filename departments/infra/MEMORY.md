# Infrastructure Department - Memory Log

## Current State
- **Uptime:** 99.9% (AWS EC2)
- **Disk Usage:** 92% on `/` (Critical)
- **Last Backup:** 2026-03-01 03:00 AEDT
- **Security Status:** Alert (`udp/5353` externally exposed, `ufw` unavailable from host checks, 1 pending update)

## Recent Activity
- **2026-03-01:** 
  - Department created.
  - Noted pending system updates (2 packages).
  - Flagged missing UFW firewall.
- **2026-03-07 11:38 UTC:**
  - Hardened `tools/infra-autopilot.py` to select the highest-risk autonomous task from recent per-task artifacts plus the latest `infra-status` artifact instead of rotating blindly.
  - Hardened `tools/infra-status.py` and `tools/infra-autopilot.py` security-audit output with firewall visibility reporting and explicit `udp/5353` mDNS guidance.
  - Verification passed: `python3 -m py_compile tools/infra-autopilot.py tools/infra-status.py`.
  - Live infra findings now show root `/` at `92%` used, `udp/5353` still exposed, `ufw` unavailable, and `1` pending package update.
- **2026-03-07 12:53 UTC:**
  - Confirmed `Monitor disk usage` is still the top autonomous infra task from TODO + latest artifacts because `infra-status` reports `/` at `92%` used.
  - Added shared disk triage in `tools/infra_disk.py` and wired both `tools/infra-status.py` and `tools/infra-autopilot.py` to use it.
  - High-pressure disk artifacts now include reviewable reclaim candidates, stale `/tmp` entries older than 24h, and deleted-but-open file detection.
  - Verification passed: `python3 -m py_compile tools/infra_disk.py tools/infra-status.py tools/infra-autopilot.py`, `python3 tools/infra-status.py`, and `python3 tools/department-commands.py run infra`.
  - Live reclaim candidates now surface `/tmp` (`989M`, including stale `/tmp/gradle-home` at `913M`), `/var/cache/apt` (`661M`), `/home/ubuntu/.cache` (`366M`), and `/var/log/journal` (`130M`); no deleted-but-open files detected.

## Known Issues
- Root filesystem `/` is at `92%` usage and needs space reclamation.
- Unexpected external `udp/5353` listener remains exposed.
- `ufw` unavailable and no host firewall tool detected from current host checks.
- 1 system update pending.

## Backup Status
- **Frequency:** Daily (03:00 AEDT)
- **Destination:** S3 / Local (verify config)
- **Last Test Restore:** `INCOME-ENGINE.md` verified successfully on 2026-03-07 11:36 UTC.
