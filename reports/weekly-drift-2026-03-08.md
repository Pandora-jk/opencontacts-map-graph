# Weekly Agent Drift Report

**Generated:** 2026-03-08 17:16:55 UTC
**Period:** 2026-03-01 to 2026-03-08
**Runner:** tools/weekly-drift-report.sh

---

## Executive Summary

## Infrastructure Department

**Activity Metrics:**
- Total log entries: 37
- Alerts triggered: 29
- Warnings: 28
- Errors: 0
0

**Top Risk Patterns:**
```
RISK: No host firewall tool detected (ufw/nft/iptables unavailable)
RISK: local host resolution does not reference mdns
RISK: udp/5353 is mDNS/MulticastDNS
```

**Persistent Issues (by frequency):**
```
     29 ALERT: Unexpected externally exposed listeners (1): udp/5353
     29 ALERT: External mDNS listener detected on udp/5353
     23 ALERT: 5 suspicious auth lines found in sampled logs (auth.log)
```

## Coding Department

**Activity Metrics:**
- Total log entries: 95
- Unique branches: 0
0
- PR references: 0
0

## Finance Department

**Activity Metrics:**
- Total log entries: 54

## Configuration Drift Detection

⚠️ **Uncommitted changes detected:**
```
 M departments/coding/STATUS.md
 M departments/finance/STATUS.md
 M departments/infra/STATUS.md
 M logs/coding-activity.log
 M logs/finance-activity.log
 M logs/infra-activity.log
 M logs/travel-activity.log
 M memory/2026-03-08.md
 M memory/coding-autopilot-state.json
 M memory/finance-autopilot-state.json
 M memory/infra-autopilot-state.json
 M tests/test_infra_mdns_hardening.py
 M tests/test_infra_network.py
 M tools/__pycache__/infra_mdns_hardening.cpython-312.pyc
 M tools/__pycache__/infra_network.cpython-312.pyc
 M tools/infra_mdns_hardening.py
 M tools/infra_network.py
?? departments/coding/artifacts/feedback/20260308T162917Z-r94-feature-automation-scripts-unit-tests-core-conve.md
?? departments/coding/artifacts/feedback/20260308T170118Z-r95-feature-automation-scripts-unit-tests-core-conve.md
?? departments/finance/artifacts/bounties/bounty-scan-20260308-r54.md
?? departments/finance/artifacts/delivery/first-client-checklist-20260308-r53.md
?? departments/finance/artifacts/demos/demo-script-20260308-r52.md
?? departments/finance/campaigns/__pycache__/
?? departments/infra/artifacts/checks/20260308T163058Z-r28-run-security-audit-check-for-open-ports-ssh-config-faile.md
?? departments/infra/artifacts/checks/20260308T163343Z-r29-run-security-audit-check-for-open-ports-ssh-config-faile.md
?? departments/infra/artifacts/checks/20260308T163344Z-infra-status.md
?? departments/infra/artifacts/checks/20260308T164449Z-r30-run-security-audit-check-for-open-ports-ssh-config-faile.md
?? logs/.weekly-drift.lock
?? logs/infra-cron.log
?? logs/night-coding.log
?? logs/night-infra.log
?? reports/
?? tests/__pycache__/
?? tools/__pycache__/coding-autopilot.cpython-312.pyc
?? tools/__pycache__/coding_feedback_loop.cpython-312.pyc
?? tools/__pycache__/department-commands.cpython-312.pyc
?? tools/__pycache__/finance-autopilot.cpython-312.pyc
?? tools/__pycache__/infra-autopilot.cpython-312.pyc
?? tools/__pycache__/infra-status.cpython-312.pyc
?? tools/weekly-drift-report.sh
```

## Recent File Modifications (Last 7 Days)

```
/home/ubuntu/.openclaw/workspace/departments/finance/IDENTITY.md
/home/ubuntu/.openclaw/workspace/departments/finance/CORE-OFFER.md
/home/ubuntu/.openclaw/workspace/departments/finance/products/lead-qual-service/SALESKIT.md
/home/ubuntu/.openclaw/workspace/departments/finance/MEMORY.md
/home/ubuntu/.openclaw/workspace/departments/finance/WEB-DESIGN-ANALYSIS-2026-03-08.md
/home/ubuntu/.openclaw/workspace/departments/finance/FINANCE-HEAD.md
/home/ubuntu/.openclaw/workspace/departments/finance/assets/README.md
/home/ubuntu/.openclaw/workspace/departments/finance/AGENTS.md
/home/ubuntu/.openclaw/workspace/departments/finance/DEPLOY-NOW.md
/home/ubuntu/.openclaw/workspace/departments/finance/README.md
/home/ubuntu/.openclaw/workspace/departments/finance/CAMPAIGN-STATUS.md
/home/ubuntu/.openclaw/workspace/departments/finance/DROPSHIPPING-ANALYSIS-2026-03-08.md
/home/ubuntu/.openclaw/workspace/departments/finance/legal/dpa-template.md
/home/ubuntu/.openclaw/workspace/departments/finance/legal/privacy-policy.md
/home/ubuntu/.openclaw/workspace/departments/finance/legal/service-agreement-template.md
/home/ubuntu/.openclaw/workspace/departments/finance/STRATEGY-SYNTHESIS-2026-03-08.md
/home/ubuntu/.openclaw/workspace/departments/finance/HEARTBEAT.md
/home/ubuntu/.openclaw/workspace/departments/finance/EXPANSION-COMPLETE.md
/home/ubuntu/.openclaw/workspace/departments/finance/outreach/founder-led-agency-playbook.md
/home/ubuntu/.openclaw/workspace/departments/finance/TOOLS.md
None found
```

## Night Session Activity

**Night Infra Log:**
- Entries: 29593
- Log size: 1.5M

---

## Recommendations

- 🔴 **Address 29 infrastructure alerts** - Review persistent security warnings
- ⚠️ **Review 28 infrastructure warnings** - Check firewall and port configurations
- 🔒 **mDNS exposure** - Consider disabling MulticastDNS/LLMNR on public hosts
- 🛡️ **Host firewall** - No host firewall tool detected, consider enabling ufw/nftables

---

_Report generated by weekly-drift-report.sh_
