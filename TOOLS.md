# TOOLS.md - Local Notes

## Current Capabilities (what you can actually do)

| Capability | Status | How |
|---|---|---|
| Send Telegram messages | [OK] Working | `message` tool |
| Send email | [OK] Working | `exec python3 tools/send-email.py` — Brevo SMTP, real delivery |
| Bitwarden vault | [OK] Working | `exec bash tools/bw-get.sh "item" field` — auto-unlocks, see below |
| Read Outlook email | [OK] Working | Graph API via Maton (`MATON_API_KEY`) — see Email section |
| Read Gmail | [OK] Working | Gmail API via Maton (`MATON_API_KEY`) — see Email section |
| Read/write files | [OK] Working | `read` / `write` tools |
| Run shell commands | [OK] Working | `exec` tool |
| Web search / fetch | [OK] Working | `web_search` / `web_fetch` tools |
| SMS / WhatsApp | [FAIL] Not configured | No plugin installed |
| Calendar | [FAIL] Not configured | No tool installed |
| Browser automation | [FAIL] Not configured | No browser plugin |

**If a task requires something marked [FAIL] or [WARN] — say so before attempting. Don't fake it.**

---

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Bitwarden

**IMPORTANT: Never try to manage BW sessions manually. Always use the scripts below.**

The vault credentials (API key + master password) are stored in `~/.openclaw/credentials/bitwarden.json`.
Sessions are cached at `~/.openclaw/credentials/.bw_session` and auto-refreshed when expired.

```bash
# List all vault items
bash tools/bw-get.sh --list

# Get a password
bash tools/bw-get.sh "Pandora outlook" password

# Get a username
bash tools/bw-get.sh "Pandora outlook" username

# Get a custom field
bash tools/bw-get.sh "Brevo key" apiKey
```

**If BW access fails:**
- Do NOT try to run `bw login`, `bw unlock`, or manage `BW_SESSION` manually
- Just re-run `bash tools/bw-session.sh` — it handles everything automatically
- The scripts work in non-interactive shells (exec tool context)

**Why not `.bashrc`?**
The `bw-unlock` function in `.bashrc` only works in interactive terminals. The exec tool runs
non-interactive shells where `.bashrc` is not sourced. Always use the script files.

---

## Email

**Send** emails (via Gmail API — lands in inbox, not spam):
```bash
python3 tools/send-email.py --to "recipient@example.com" --subject "Subject" --body "Body text"
python3 tools/send-email.py --to "recipient@example.com" --subject "Subject" --body "<h1>Hello</h1>" --html
```
- **Sender:** Pandora <jim.cooding@gmail.com> via Gmail API (Maton)
- **Auth:** `MATON_API_KEY` (gateway env, BW item: "maton api")

**Read/manage** Outlook (email + calendar + contacts):
- **Skill:** `skills/outlook-api/SKILL.md`
- **Account:** Pandora_jk@outlook.com

**Read/manage** Gmail:
- **Skill:** `skills/gmail/SKILL.md`
- **Account:** jim.cooding@gmail.com

---

## Codex Tool (for OC)

Use the wrapper script (not raw ad-hoc commands) when OC should run Codex:

```bash
bash tools/oc-codex.sh --workdir /path/to/repo --task "Implement feature X and add tests"
```

Flags:
- `--model <name>`: override Codex model
- `--init-git`: initialize git if directory is not a repo
- `--yolo`: no sandbox/no approvals (use only when explicitly requested)
- `--timeout <sec>`: hard timeout

Notes:
- Codex requires a git repo/trusted directory.
- Default mode is `codex exec --full-auto` for deterministic non-interactive runs.

---

## Department Commands

On-demand department command tool:

```bash
python3 tools/department-commands.py help
python3 tools/department-commands.py status all
python3 tools/department-commands.py status finance
python3 tools/department-commands.py todo coding --limit 5
python3 tools/department-commands.py run infra
```

Telegram shorthand to map:
- `/dept status all`
- `/dept status <department>`
- `/dept todo <department>`
- `/dept run <department>`

Add whatever helps you do your job. This is your cheat sheet.
