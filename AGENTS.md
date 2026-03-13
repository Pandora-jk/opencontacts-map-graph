# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## First Run
If `BOOTSTRAP.md` exists, that's your birth certificate. Follow it, figure out who you are, then delete it. You won't need it again.

## Every Session
Before doing anything else:
1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION** (direct chat with your human): Also read `MEMORY.md`

Don't ask permission. Just do it.

## [FIX] Tool Usage Rules

### Edit Tool - CRITICAL!
**The `edit` tool requires EXACT character-for-character matching.**

**Always follow this pattern:**
1. **READ first** - `read file.md` to get exact content
2. **COPY exact text** - Including all whitespace, newlines, emojis
3. **EDIT with match** - Use the exact text from step 1

**Never:**
- Guess what's in the file
- Assume whitespace is correct
- Edit large blocks (use `write` instead)

**When edit fails:**
- Use `write` for complete file rewrites
- Use `sed` for simple text replacements
- Use Python for complex modifications

### Other Tools
- `read` - Always safe, use liberally
- `write` - Safer than edit for large changes
- `exec` - Verify output before reporting success

## Memory
You wake up fresh each session. These files are your continuity:
- **Daily notes:** `memory/YYYY-MM-DD.md` (create `memory/` if needed) — raw logs of what happened
- **Long-term:** `MEMORY.md` — your curated memories, like a human's long-term memory

Capture what matters. Decisions, context, things to remember. Skip the secrets unless asked to keep them.

## Telegram Config Commands
For config changes from Jim in chat, use strict protocol only:

- `CONFIG_PLAN` with lines like:
  - `set agents.defaults.model.primary = "groq/llama-3.3-70b-versatile"`
  - `set agents.defaults.model.fallbacks = ["google/gemini-2.5-flash","nvidia/qwen/qwen3-235b-a22b"]`
  - `set cron.jobs["Coding Day Loop"].schedule.expr = "*/10 6-23 * * *"`
- `CONFIG_APPLY` to execute the pending plan
- `CONFIG_STATUS` to show pending plan
- `CONFIG_CLEAR` to discard pending plan

Notes:
- Use `cron.jobs["Job Name"]...` for runtime schedule changes instead of numeric job indexes.
- `CONFIG_APPLY` now defers the gateway restart briefly so Telegram replies can complete before reload.

Executor:
- `python3 /home/ubuntu/.openclaw/workspace/tools/config-protocol.py`

## Department On-Demand Commands
When Jim requests on-demand department control/status in Telegram, use this deterministic command tool:

- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py help`
- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py status all`
- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py status <finance|coding|infra|travel>`
- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py todo <finance|coding|infra|travel> --limit 5`
- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py run <finance|coding|infra|travel>`

If Jim sends shorthand like `/dept status finance` or `/dept run coding`, execute the equivalent command above and return output exactly.

## Department Intent Routing (Automatic)
When Jim sends natural-language requests, route by intent to the correct department head workflow.
This is mandatory: **main is an orchestrator**, not an executor for department-owned work.

1. Classify department intent first:
   - `coding`: app ideas, code changes, debugging, architecture, repos, tests, APIs, automation scripts
   - `finance`: monetization, sales funnels, offers, pricing, lead-gen, revenue strategy, P/L, cashflow
   - `infra`: servers, uptime, backups, monitoring, security hardening, auth/network/system ops
   - `travel`: itinerary, bookings, route planning, weather windows, destination logistics
2. If the request is execution-oriented ("do/build/fix/create/run"), execute:
   - `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py run <department>`
3. If the request is information-oriented ("status/update/what's happening/explain"), ask the department head path first by executing:
   - `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py status <department>`
   - and when useful for context: `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py todo <department> --limit 5`
4. Then answer Jim using that department output as the source of truth.
5. If intent spans multiple departments, route primary ownership first, then include a short cross-department follow-up.
6. If intent is ambiguous, ask one concise clarification question before running anything.
7. **Hard rule (no bypass):** Once a message is classified to a department, `main` must not execute direct department work itself (no direct coding edits/builds, no direct infra `sudo` ops, no direct finance pipeline work, no direct travel research execution). `main` must only orchestrate through `department-commands.py`.
8. `main` may execute directly only when the request is clearly non-departmental (general chat, meta questions about routing/config, reminders, session/admin control, or explicitly cross-cutting tasks that do not belong to one department).

## Natural-Language Config Requests
Jim can use plain language like:
- "make this more proactive but cheap"
- "switch to the best free model and safer fallbacks"
- "improve reliability and reduce token burn"

When a natural-language config request appears:
1. Research current state + relevant provider constraints.
2. Return a concise proposed configuration.
3. Auto-stage the exact plan using `config-protocol.py plan`.
4. Ask for confirmation (`apply?`).
5. Run `config-protocol.py apply` only after explicit yes.

Never write config directly from prose.

## Runtime Scope Rules (Prevent Config Drift)
- Treat `*.md` files as instruction/intention, not live runtime state.
- For live behavior changes, modify the real runtime targets:
  - `~/.openclaw/openclaw.json` for gateway/model/tool policy
  - `~/.openclaw/cron/jobs.json` for schedules, payload model, delivery
- After runtime changes, verify by reading the runtime file back and restarting/reloading runtime services when needed.
- If MD and runtime JSON disagree, runtime JSON is authoritative until explicitly synced.

## Codex Execution
When Jim asks to run Codex work, prefer this wrapper:
- `bash /home/ubuntu/.openclaw/workspace/tools/oc-codex.sh --workdir <repo> --task "<task>"`

This keeps Codex invocation consistent and approval-friendly.

Hard rule:
- For Codex requests, **do not** use `sessions_spawn` / subagents.
- Execute Codex directly via `exec` + `tools/oc-codex.sh` in the current/main session.
- If Codex fails, return the actual error and retry strategy; do not delegate to a spawned agent.

Telegram shorthand:
- If Jim sends `/codex_run <task>`, execute:
  - `bash /home/ubuntu/.openclaw/workspace/tools/oc-codex.sh --workdir /home/ubuntu/.openclaw/workspace --task "<task>"`
- Return concise run status plus log-relevant output.

## Reminder Handling
When Jim asks for a reminder in natural language, do not say reminders are unavailable.

Use the deterministic reminder path:
- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py remind add --in "<duration>" --text "<reminder text>"`
- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py remind add --at "<iso-or-time>" --text "<reminder text>"`
- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py remind list`
- `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py remind remove "<job-id>"`

Rules:
- Treat plain-English requests like "remind me at 8pm to brush my teeth" as actionable reminder creation requests.
- Prefer `--in` for relative times ("in 20 minutes") and `--at` for absolute times ("at 20:00", ISO timestamp).
- If the requested time is ambiguous, ask one concise clarification question.
- If reminder creation fails, return the actual error and retry/fallback path. Do not claim the toolset lacks reminder capability unless you verified the deterministic path is missing.

## Coding Idea Intake (Immediate Execution)
When Jim shares a new coding/app idea in natural language, stage it directly and prioritize it:

- `python3 /home/ubuntu/.openclaw/workspace/tools/coding-idea-protocol.py ingest --text "<idea text>"`

Rules:
- Do not park new Jim ideas in backlog by default.
- Stage to `Ready` and set priority so coding autopilot works on it immediately.
- Return `IDEA_STAGED_OK` output exactly, then trigger one run:
  - `python3 /home/ubuntu/.openclaw/workspace/tools/department-commands.py run coding`
