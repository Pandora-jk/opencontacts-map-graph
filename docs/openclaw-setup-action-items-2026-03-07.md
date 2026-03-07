# OpenClaw Setup Action Items

Created: 2026-03-07 UTC
Source: live runtime audit, official OpenClaw docs, and community best-practice review

## Immediate
- [x] Apply the staged low-risk config plan to make heartbeat actually proactive and to fix broken status-push behavior.
  Applied: 2026-03-07 12:12 UTC via `config-protocol.py` (`Plan ID: d1c52e999847` after restaging to match the installed heartbeat schema).
  Runtime changes: `agents.defaults.heartbeat.target = "last"`, `every = "30m"`, Sydney `activeHours`, proactive heartbeat prompt, `Coding Status Push.delivery.mode = "announce"`, and corrected coding/finance status-push prompts.
  Verification: live runtime JSON now reflects the new settings and the gateway is healthy.
  Caveat: a fresh heartbeat cycle has not fired yet, so heartbeat delivery itself still needs confirmation on the next cycle.
- [x] Lock down the runtime config file permissions on `~/.openclaw/openclaw.json`.
  Verified: current mode is `600`, and `openclaw security audit --deep` no longer reports config-file writability.
- [x] Fix `Coding Status Push` delivery behavior in `~/.openclaw/cron/jobs.json`.
  Applied: `delivery.mode = "announce"` and the prompt now returns script stdout exactly.
  Follow-up hardening: switched `payload.model` from `zai/glm-4.7-Flash` to `nvidia/qwen/qwen3.5-397b-a17b` after repeated provider `network_error` runs.
  Verification: manual debug run on 2026-03-07 12:29 UTC finished `status: ok` with `deliveryStatus: delivered`.
- [x] Fix `Finance Status Push` final-response prompt so it returns the script output instead of `NO_REPLY`.
  Applied: prompt now returns script stdout exactly instead of allowing `NO_REPLY`.
  Verification: manual debug run on 2026-03-07 12:22 UTC finished `status: ok` with `deliveryStatus: delivered`.

## High Priority
- [x] Fix the broken retention script in [tools/session-retention.sh](/home/ubuntu/.openclaw/workspace/tools/session-retention.sh).
  Fixed: removed the broken hand-built JSON path, added `SESSIONS_DIR` override for safe testing, and emit cleanup actions through `jq`.
  Verification: `bash -n tools/session-retention.sh` passed; temp-directory test removed only the stale file and returned valid JSON; live run on 2026-03-07 12:18 UTC removed 1 stale deleted transcript and returned `SESSION_RETENTION_OK`.
  Follow-up hardening: `Daily Session Retention Cleanup` now pins `payload.model = "nvidia/qwen/qwen3.5-397b-a17b"`, returns script stdout exactly, and runs with `delivery.mode = "none"` so it no longer fails on missing Telegram targets.
  Remaining caveat: a manual verification rerun was still in progress at the close of this pass, so the post-fix cron row itself still needs one completed green run.
- [x] Clean up session-state drift reported by `openclaw doctor`.
  Applied:
  - `openclaw doctor --fix --non-interactive` canonicalized the remaining safe legacy key
  - removed 4 dead session-store entries that pointed at missing transcripts
  - renamed 3 orphan `.jsonl` transcripts to `.jsonl.deleted.*` with backup-first cleanup
  - reran retention cleanup to purge the 2 tombstoned files already older than 24h
  Backup: `/tmp/sessions.json.backup-2026-03-07T12-33-37.365287Z`
  Verification: `openclaw doctor` no longer reports legacy state or session integrity warnings; main session store is now 13 live entries.
- [x] Decide on one proactive architecture and retire the drift.
  Applied: retired the legacy proactive shell path, disabled heartbeat as an outbound delivery target (`agents.defaults.heartbeat.target = "none"`), repurposed the dormant `Infra Findings Push` job into `Proactive Pulse`, and updated [oc-self-heal.sh](/home/ubuntu/.openclaw/workspace/scripts/oc-self-heal.sh) plus the retired stub scripts to treat `Proactive Pulse` as the healthy owner of outbound proactive delivery.
  Verification: the legacy scripts now exit with a Proactive Pulse deprecation notice, no real user crontab or user timer schedules them, and the new `Proactive Pulse` job finished `status: ok` with `deliveryStatus: delivered` on 2026-03-07 13:42 UTC.
- [ ] Fix the coding-day-loop blocker caused by GitHub secret scanning.
  Issue: the coding department is working, but autonomous pushes are being blocked by exposed secrets in branch history.
  Progress applied on 2026-03-07 14:17 UTC:
  - sanitized live tracked secret-bearing files in the workspace repo (provider keys, GitHub token fallback, archived setup docs, and a secret-bearing tracked backup)
  - added [git-secret-scan.py](/home/ubuntu/.openclaw/workspace/tools/git-secret-scan.py) and wired [coding-git-enforce.sh](/home/ubuntu/.openclaw/workspace/tools/coding-git-enforce.sh) to:
    - exclude logs, session summaries, backups, and `__pycache__` noise from autonomous staging
    - fail fast on staged/tracked secret patterns before push
    - fail fast on secret-bearing branch history before push
  Verification:
  - `python3 tools/git-secret-scan.py --repo /home/ubuntu/.openclaw/workspace` now returns `SECRET_SCAN_OK`
  - `python3 tools/git-secret-scan.py --repo /home/ubuntu/.openclaw/workspace --history-ref HEAD --max-commits 400` still fails, confirming the remaining blocker is historical commits, not the live tree
  - the current feature branch also has no merge base with `origin/main`, so a normal rebase cleanup path is not available
  Remaining fix: create a clean branch snapshot (or orphan rescue branch) from the sanitized current tree, then push that clean history instead of the poisoned branch.
  Success: coding runs can push successfully without secret-scanning failures.

## Security Hardening
- [x] Remove or restrict small-model fallbacks for tool-using sessions.
  Applied: removed `groq/llama-3.3-70b-versatile` and `cerebras/gpt-oss-120b` from `agents.defaults.model.fallbacks`.
  Resulting fallback chain: `google/gemini-2.5-flash`, `zai/glm-4.7-Flash`, `nvidia/moonshotai/kimi-k2-thinking`.
  Verification: `openclaw security audit --deep` now reports `0 critical`.
- [ ] Review whether browser control should stay enabled for the main assistant.
  Recommendation: keep it only if you actively use it; otherwise reduce attack surface.
- [ ] Resolve the recurring OpenRouter `HTTP 401` noise.
  Success: provider quota checks no longer report stale auth failures for unused/broken providers.

## Reliability
- [x] Reduce hard dependency on `zai/glm-4.7-Flash` for unattended cron jobs.
  Applied:
  - switched `Coding Status Push`, `Infra Autopilot Loop`, `Night Infra Delegation`, and `Travel Autopilot Loop` to `nvidia/qwen/qwen3.5-397b-a17b`
  - later also pinned `Daily Session Retention Cleanup`, `Daily Config Hygiene`, and `Weekly Agent Drift Report` to `nvidia/qwen/qwen3.5-397b-a17b`
  - kept the model changes targeted to the unattended jobs rather than rewriting every agent default at once
  Verification:
  - `Coding Status Push` manual run: `status: ok`, `deliveryStatus: delivered`
  - `Infra Autopilot Loop` manual run: `status: ok`, summary `INFRA_LOOP_OK`
  - `Travel Autopilot Loop` manual run: `status: ok`, summary `TRAVEL_LOOP_OK`
  - `Daily Session Retention Cleanup` manual run: `status: ok`, summary includes `SESSION_RETENTION_OK`
  Remaining note: some lower-priority reminder/default paths still use non-pinned model selection, but the unattended infra housekeeping and previously failing loops are now on the reliable path.
- [x] Audit the custom gateway patch layer in [tools/patch-openclaw-reply.py](/home/ubuntu/.openclaw/workspace/tools/patch-openclaw-reply.py).
  Applied: refreshed the helper to target the actual current bundles (`reply-*`, `pi-embedded-*`, `subagent-registry-*`, and `image-*`), added env overrides so it can be tested safely against a temp dist copy, and kept the patch idempotent.
  Verification: temp-dist test applied the reply/image patches cleanly, and the real gateway restart on 2026-03-07 13:03 UTC no longer logged the stale `ctx% targets not found` / `prefix-spacing target not found` warnings.
- [x] Stop leaving cron child processes behind during gateway restarts.
  Applied: installed a managed user override at [openclaw-gateway.override.conf](/home/ubuntu/.openclaw/workspace/systemd/openclaw-gateway.override.conf) and synced it to the live user unit override so gateway restarts now use `KillMode=control-group` with `TimeoutStopSec=15`.
  Verification: after the 2026-03-07 13:13 UTC restart, the orphaned `Night Coding Delegation` `bash` / `timeout` / `codex` tree was gone and the stale cron `runningAtMs` markers for `Night Coding Delegation` and `Daily Session Retention Cleanup` were cleared on startup.
- [x] Fix the misleading `SSH Hardening Reminder` cron error state.
  Applied: changed the job payload to return Telegram-ready text only and explicitly not call messaging tools, leaving the actual send to `delivery.mode = "announce"`.
  Verification: manual run at 2026-03-07 13:23 UTC finished `status: ok` with `lastDelivered = true` and `lastDeliveryStatus = delivered`.
- [x] Reduce provider-quota report noise from stale legacy providers.
  Applied: updated [check-provider-quota.py](/home/ubuntu/.openclaw/workspace/tools/check-provider-quota.py) to ignore legacy-only providers from `agents/main/agent/models.json` when they have no active sessions.
  Verification: local `python3 tools/check-provider-quota.py --stdout` no longer includes the stale `openrouter` error section.
- [ ] Verify transcript retention and cron output delivery after the next full day of runs.
  Partial verification complete: retention cleanup, coding status push, finance status push, and SSH reminder all now have fresh green runs.
  Success: no new retention timeouts, no `NO_REPLY` status-push failures, and no unexplained `not-delivered` states after a full day of runs.

## Proactivity Improvements
- [x] Replace heartbeat-based outbound delivery with a deterministic proactive pulse.
  Applied: set `agents.defaults.heartbeat.target = "none"` and repurposed `Infra Findings Push` into `Proactive Pulse`, a Sydney daytime Telegram cron job backed by [proactive-pulse.py](/home/ubuntu/.openclaw/workspace/tools/proactive-pulse.py).
  Verification: manual run at 2026-03-07 13:42 UTC finished `status: ok` with `deliveryStatus: delivered`, proving the new proactive path works without heartbeat.
- [x] Make proactive suggestions state-aware.
  Applied: [proactive-pulse.py](/home/ubuntu/.openclaw/workspace/tools/proactive-pulse.py) ranks real runtime issues from cron state, infra artifacts, runtime config, and unresolved high-priority action items, then emits exactly one Telegram-ready suggestion or `NO_REPLY`.
  Verification: the first live run sent the still-open GitHub secret-scanning blocker, and the immediate follow-up dry-run returned `NO_REPLY`, confirming duplicate suppression.
- [ ] Reduce token burn for `Proactive Pulse` if the hourly cost is too high.
  Observation: the first live run used `27,037` input tokens because isolated cron jobs in this OpenClaw build still require `payload.kind = "agentTurn"`.
  Recommendation: if that ongoing cost matters, move the pulse to a lean dedicated agent or reduce its daytime cadence.
- [ ] Add a weekly review of automation drift.
  Recommendation: review delivery failures, provider errors, stale scripts, and broken prompts every week.
  Success: proactive quality improves over time instead of decaying through config drift.

## Suggested Order
1. Apply the staged low-risk config plan.
2. Lock down `openclaw.json` permissions.
3. Fix `tools/session-retention.sh`.
4. Fix coding and finance status-push delivery correctness.
5. Clean session-store drift.
6. Remove or sandbox risky small-model fallbacks.
7. Resolve ZAI cron fragility.
8. Retire legacy proactive shell scripts.
