# Infrastructure Department - Memory Log

## Current State
- **Uptime:** 99.9% (AWS EC2)
- **Disk Usage:** 88% on `/` (Alert)
- **Last Backup:** 2026-03-01 03:00 AEDT
- **Security Status:** Alert (`udp/5353` externally exposed, `ufw` unavailable from host checks, no pending package updates)

## Recent Activity
- **2026-03-08 15:35 UTC:**
  - Reconfirmed `Run security audit` remained the top infra task from TODO + latest logs/artifacts because public `udp/5353` exposure still dominates fresh runs 25 and 26.
  - Hardened the repo-side mDNS remediation flow so validation now fails closed instead of treating unresolved live exposure as a success:
    - `tools/infra_network.py` now ignores local-only `127.0.0.1/[::1]:5353` sockets when deciding whether external mDNS exposure exists
    - `tools/infra_mdns_hardening.py --validate-live` now returns `LIVE_VALIDATION_FAILED` unless the managed live `/etc` drop-in is installed cleanly and external `udp/5353` is no longer exposed
    - staged validation now ends with `STAGED_VALIDATION_READY` and explicitly warns that staging does not clear the live host listener
    - `tools/infra-status.py` now passes raw socket lines into `inspect_mdns_exposure`, fixing a brief mismatch where the mDNS subsection could say `No external mDNS listener detected` while the open-port section still flagged `udp/5353`
  - Added regression coverage in `tests/test_infra_mdns_hardening.py`, `tests/test_infra_network.py`, and new `tests/test_infra_status.py`.
  - Verification passed: `python3 -m unittest tests.test_infra_network tests.test_infra_mdns_hardening tests.test_infra_status`, `python3 -m py_compile tools/infra_network.py tools/infra_mdns_hardening.py tools/infra-status.py tools/infra-autopilot.py`, `python3 tools/infra_mdns_hardening.py --stage-dir /tmp/openclaw-mdns-stage --validate-live`, `python3 tools/infra_mdns_hardening.py --validate-live` (expected exit 1 with `LIVE_VALIDATION_FAILED`), `python3 tools/infra-status.py`, and `python3 tools/department-commands.py run infra`.
  - Fresh artifacts: `20260308T153549Z-infra-status.md` and `20260308T153559Z-r26-run-security-audit-check-for-open-ports-ssh-config-faile.md`.
- **2026-03-08 14:33 UTC:**
  - Reconfirmed `Run security audit` is still the top infra task from TODO + latest artifacts because `udp/5353` remains externally exposed in fresh runs 22 and 23.
  - Hardened `tools/infra_mdns_hardening.py` so the helper cannot quietly bypass the staged-first workflow:
    - added `--allow-live-install` as an explicit opt-in for `--install-to` when the target is the real `/etc/systemd/resolved.conf.d/99-openclaw-no-mdns.conf`
    - blocked `--stage-dir` from pointing at the live resolved drop-in directory
    - blocked meaningless `--allow-live-install` usage without `--install-to`
  - Added regression coverage in `tests/test_infra_mdns_hardening.py` for the new live-path and stage-dir guardrails.
  - Verification passed: `python3 -m unittest tests.test_infra_network tests.test_infra_mdns_hardening`, `python3 -m py_compile tools/infra_network.py tools/infra_mdns_hardening.py tools/infra-status.py tools/infra-autopilot.py`, `python3 tools/infra_mdns_hardening.py --stage-dir /tmp/openclaw-mdns-stage --validate-live`, `python3 tools/infra_mdns_hardening.py --install-to /etc/systemd/resolved.conf.d/99-openclaw-no-mdns.conf` (expected exit 2), `python3 tools/infra-status.py`, and `python3 tools/department-commands.py run infra`.
  - Fresh artifacts: `20260308T143328Z-infra-status.md` and `20260308T143328Z-r23-run-security-audit-check-for-open-ports-ssh-config-faile.md`.
- **2026-03-08 13:34 UTC:**
  - Reconfirmed `Run security audit` is still the top infra task from TODO + latest artifacts because `udp/5353` remains externally exposed.
  - Hardened the mDNS remediation workflow so staged validation no longer claims a `/tmp` drop-in is live:
    - added explicit `staged drop-in installed` status in `tools/infra_network.py`
    - updated `tools/infra_mdns_hardening.py` to label validation targets as `staged` vs `live` and emit `STAGED_VALIDATION_DONE` only for staged checks
    - updated guidance strings so `/etc` install is gated on staged validation, while post-install verification explicitly expects `LIVE_VALIDATION_DONE`
  - Verification passed: `python3 -m unittest tests.test_infra_network tests.test_infra_mdns_hardening`, `python3 -m py_compile tools/infra_network.py tools/infra_mdns_hardening.py tools/infra-autopilot.py tools/infra-status.py`, `python3 tools/infra_mdns_hardening.py --stage-dir /tmp/openclaw-mdns-stage --validate-live`, `python3 tools/infra-status.py`, and `python3 tools/department-commands.py run infra`.
  - Fresh artifacts `20260308T133410Z-infra-status.md` and `20260308T133409Z-r20-run-security-audit-check-for-open-ports-ssh-config-faile.md` now tell the operator to expect `STAGED_VALIDATION_DONE` before `/etc` install and `LIVE_VALIDATION_DONE` only after the real host restart.
- **2026-03-01:** 
  - Department created.
  - Noted pending system updates (2 packages).
  - Flagged missing UFW firewall.
- **2026-03-07 14:33 UTC:**
  - Hardened `tools/infra-autopilot.py` and `tools/infra-status.py` auth parsing to ignore self-generated `sudo` log-inspection commands when scoring SSH/auth risk.
  - Verification passed: `python3 -m py_compile tools/infra-autopilot.py tools/infra-status.py`, targeted sample-log parsing, `python3 tools/infra-status.py`, and `python3 tools/department-commands.py run infra`.
  - Fresh artifacts `20260307T143316Z-infra-status.md` and `20260307T143315Z-r80-run-security-audit-check-for-open-ports-ssh-config-faile.md` now show `No failed authentication attempts found in sampled logs (auth.log)` and keep `udp/5353` as the top remaining security issue.
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
- Root filesystem `/` is at `88%` usage and still needs space reclamation.
- Unexpected external `udp/5353` listener remains exposed.
- `ufw` unavailable and no host firewall tool detected from current host checks.

## Backup Status
- **Frequency:** Daily (03:00 AEDT)
- **Destination:** S3 / Local (verify config)
- **Last Test Restore:** `INCOME-ENGINE.md` verified successfully on 2026-03-07 11:36 UTC.
