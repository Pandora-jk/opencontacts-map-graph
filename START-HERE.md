# Start Here

Use this as the clean entrypoint for multi-agent operations.

## Core Runtime Files
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `MEMORY.md`
- `TODO.md`
- `OPERATIONS.md`
- `system/openclaw.json` (reference config)

## Config Scope (Critical)
- **MD files (`SOUL.md`, `AGENTS.md`, department docs):** behavior instructions and intent only.
- **Runtime gateway config:** `~/.openclaw/openclaw.json` (actual provider/model/tool behavior).
- **Runtime schedules/jobs:** `~/.openclaw/cron/jobs.json` (actual cron payloads, model per job, delivery mode).
- **Deterministic config workflow:** use `tools/config-protocol.py` (`CONFIG_PLAN` -> review -> `CONFIG_APPLY`).
  - For cron changes, target the runtime jobs file via `cron.jobs["Job Name"]...` paths.
  - `CONFIG_APPLY` now defers the gateway restart briefly so Telegram replies can finish before reload.
- Never assume editing an MD file changes live runtime behavior.

## Canonical Agent Definitions
- `system/agents/` (workspace reference copies)
- `~/.openclaw/agents/` (runtime source used by OpenClaw)

Do not use root-level `pandora-*.md` in this workspace; those were archived as duplicates.

## Active Automation Scripts
- `scripts/oc-self-heal.sh`
- `scripts/proactive-check.sh`
- `scripts/proactive-morning.sh`
- `scripts/self-improve.sh`

## Deterministic Config Changes
- `tools/config-protocol.py`
- Flow: `CONFIG_PLAN` -> review -> `CONFIG_APPLY`

## Archive
- Archived cleanup/setup/duplicate docs:
  - `docs/archive/2026-03-03-pre-multi-agent/`
