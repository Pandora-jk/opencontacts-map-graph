# HEARTBEAT.md

# Coding heartbeat checklist (autonomous build mode)
# If nothing actionable is found, return HEARTBEAT_OK.

## Every heartbeat
- Check `departments/coding/TODO.md` and `departments/coding/kanban/*.md`.
- If an item is in `Ready`, start it on a new feature branch.
- Ensure each in-progress card has explicit tests listed.
- Move one task forward at least one Kanban stage (Ready -> In Progress -> Review -> Done).

## Every 4th heartbeat
- Re-prioritize backlog by impact vs effort.
- Add at least one new improvement task discovered from codebase drift, debt, or bugs.
- Run one lightweight security/dependency audit checkpoint.

## Question policy
- Ask questions only for blockers that need human access/approval.
- Ask one concise blocker question with recommended default action.
