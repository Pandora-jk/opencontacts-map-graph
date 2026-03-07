# Heartbeat Checklist

Check memory/heartbeat-state.json to see what was last checked and when. Update it after each run.

## Every Heartbeat
- Read memory/2026-MM-DD.md for today and write anything notable
- Update memory/heartbeat-state.json with current timestamps

## Rotating Checks (do 2-4 per day, skip if checked <3h ago)
- **Email** — Any urgent unread at jimknopf8jk@gmail.com? (use send-email.py tool or check inbox)
- **Projects** — Any active work in ~/codex/ or ~/go/? Git status, uncommitted changes?
- **Memory maintenance** — Every few days: distill daily notes into MEMORY.md, prune old entries

## Nightly Self-Improvement (Auto-run at 03:00 AEDT)
- [OK] Cron job: `0 16 * * *` → `/home/ubuntu/.openclaw/workspace/scripts/self-improve.sh`
- [OK] Reports: `memory/self-improve-YYYY-MM-DD.md`
- [OK] Actions: Security audit, cleanup, script health, memory maintenance, proactive suggestions

## Proactive Outreach
If it has been more than 8 hours since the last Telegram message to Jim (ID: 156480904) and something useful came up, reach out with a brief update. Do not reach out just to say nothing is happening — only if there is something worth saying.

## Stay Quiet (reply HEARTBEAT_OK) if:
- Sydney time is between 23:00 and 08:00 and nothing is urgent
- Last check was less than 25 minutes ago
- There is genuinely nothing new or actionable
