# Operations Runbook

Canonical operations reference for this workspace.

## Runtime Source Of Truth
- Live gateway config: `~/.openclaw/openclaw.json`
- Live cron jobs: `~/.openclaw/cron/jobs.json`
- Preferred mutation path: `openclaw config ...`, `openclaw agents ...`, `openclaw cron ...`
- `*.md` files define behavior intent; they do not change runtime by themselves.

## Active Agent Topology
- `main` (default orchestration)
- `coding` -> workspace `departments/coding`
- `finance` -> workspace `departments/finance`
- `infra` -> workspace `departments/infra`
- `travel` -> workspace `departments/travel`

All autonomous department jobs should run as `sessionTarget=isolated` with explicit `agentId`.

## Tooling/Sandbox Baseline
- Default sandbox: `agents.defaults.sandbox = { mode: "all", scope: "agent" }`
- Per-agent tool allowlists:
  - `coding`: `web.search`, `web.fetch`
  - `infra`: `web.search`, `web.fetch`
  - `finance`: `web.search`
  - `travel`: `web.search`

## Coding Department Execution Rules
- Daytime and nighttime coding both continue.
- Always use `feature/*` branches.
- Always run tests.
- Always commit and push to GitHub `origin`.
- Enforcement script: `tools/coding-git-enforce.sh`

## Safe Config Workflow
1. Inspect current runtime state (`openclaw config get`, `openclaw cron list`, `openclaw agents list`).
2. Apply minimal change with CLI.
   - For job schedules, prefer `tools/config-protocol.py` with stable name-based paths such as `cron.jobs["Coding Day Loop"].schedule.expr`.
3. Verify applied values in runtime files.
4. Restart gateway if required:
   - `systemctl --user restart openclaw-gateway`
5. Re-check status.

## Automation Health Checks
- Gateway status: `systemctl --user is-active openclaw-gateway`
- Cron status/list: `openclaw cron status`, `openclaw cron list`
- Department on-demand status:
  - `python3 tools/department-commands.py status all`

## Housekeeping
- Archive-only historical docs are under `docs/archive/`.
- Keep root docs lean; avoid adding parallel setup guides.
