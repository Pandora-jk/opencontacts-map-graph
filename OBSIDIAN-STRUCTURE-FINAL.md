# [PHONE] Obsidian Structure - Final Version

**Date:** March 2, 2026  
**Status:** [OK] Complete - System files included

---

## What You See in Obsidian (Mobile)

Your Obsidian vault now shows **both** user docs AND system files, organized cleanly:

```.openclaw/workspace/          ← Your Obsidian vault root
│
├── 📄 SOUL.md                ← Your main persona
├── 📄 USER.md                ← User info (Jim)
├── 📄 AGENTS.md              ← How to work
├── 📄 MEMORY.md              ← Long-term memory
├── 📄 TODO-AUTONOMOUS.md     ← Active tasks
├── 📄 INCOME-ENGINE.md       ← Revenue tracking
│
├── [DIR] departments/           ← Division context
│   ├── finance/SOUL.md
│   ├── coding/SOUL.md
│   ├── travel/SOUL.md
│   └── infra/SOUL.md
│
├── [DIR] pandora-*.md           ← Agent SOULs (19 files, mobile-friendly)
│
├── [DIR] system/                ← NEW: System files for reference
│   ├── README.md            ← Usage instructions
│   ├── openclaw.json        ← Main config
│   └── agents/              ← Agent definitions
│       ├── pandora-finance.md
│       ├── pandora-coding.md
│       ├── pandora-travel.md
│       ├── pandora-infra.md
│       └── ... (15 more)
│
├── [DIR] scripts/               ← Automation scripts
├── [DIR] tools/                 ← Utility scripts
├── [DIR] assets/                ← Data files, templates
└── [DIR] memory/                ← Daily notes
```

---

## Why This Structure Works

### [OK] Before (Messy):
- 47 duplicate files everywhere
- System files mixed with user docs
- Couldn't tell what was what
- Git tracked everything (bad)

### [OK] After (Clean):
- **User docs** in root (`SOUL.md`, `MEMORY.md`, etc.)
- **System files** in `system/` folder (read-only reference)
- **Agent SOULs** in both places:
  - `system/agents/` - Source of truth (OpenClaw reads these)
  - `pandora-*.md` - Mobile-friendly copies
- **Git** tracks only `workspace/` (clean)
- **No duplicates** in the same folder

---

## What Each Folder Is For

### Root Folders (Your Daily Work):
- `departments/` - Division-specific context and memory
- `scripts/` - Your automation scripts
- `tools/` - Utility scripts
- `assets/` - Data files, templates, leads
- `memory/` - Daily notes and journals

### System Folder (Reference Only):
- `system/openclaw.json` - View config, model settings
- `system/agents/` - All 19 agent definition files
- **[WARN] Don't edit directly** - These are reference copies

### Agent Files (Two Locations):
1. **`system/agents/pandora-*.md`** - Source of truth
2. **`pandora-*.md`** (root level) - Mobile-friendly copies

Canonical source is `system/agents/`. Root-level `pandora-*.md` duplicates were archived.

---

## How to Use on Mobile

### Reading Agent Definitions:
Navigate to `system/agents/pandora-finance.md` (and other `system/agents/*` files).

### Viewing Config:
- Tap `system/openclaw.json`
- See current model, settings, quotas

### Editing:
- **User docs** (`SOUL.md`, `TODO.md`, etc.): Edit freely [OK]
- **System files** (`system/`): Don't edit in Obsidian [WARN]
  - To edit config: Use terminal or edit source files
  - Changes in Obsidian will be overwritten on next sync

---

## Sync Behavior

### Every 10 Minutes:
1. AWS pulls latest from GitHub (your phone edits)
2. AWS commits any new logs, changes
3. AWS pushes to GitHub
4. Phone pulls updates

### What Gets Synced:
- [OK] All `.md` files in `workspace/`
- [OK] All files in `system/` folder
- [OK] Scripts, tools, assets
- [FAIL] Session data (too much noise)
- [FAIL] Credentials (security)
- [FAIL] System logs (too large)

---

## Files Included in Obsidian

### User Docs (28 files):
- Core: `SOUL.md`, `USER.md`, `AGENTS.md`, `MEMORY.md`
- Tasks: `TODO-AUTONOMOUS.md`, `TODO.md`
- Finance: `INCOME-ENGINE.md`
- Setup: `OPERATIONS.md`, `INFRA-TEAM-COMPLETE.md`
- Mobile: `OBSIDIAN-MOBILE-SETUP.md`, `OBSIDIAN-SYNC-SUMMARY.md`
- +18 more docs

### System Files (21 files):
- `system/openclaw.json`
- `system/agents/pandora-*.md` (19 files)
- `system/agents/main/agent/` (config files)

### Division Context (12 files):
- `departments/*/SOUL.md` (4 files)
- `departments/*/MEMORY.md` (4 files)
- `departments/*/TODO.md` (4 files)

### Agent SOULs (19 files):
- Finance: 4 files
- Coding: 4 files
- Travel: 4 files
- Infra: 7 files

**Total:** ~80 files visible in Obsidian

---

## Security Notes

### What's NOT in Obsidian:
- [FAIL] `credentials/` folder (secrets)
- [FAIL] Session data (privacy)
- [FAIL] System logs (sensitive info)
- [FAIL] `.bashrc`, `.env` files

### What IS Safe:
- [OK] `openclaw.json` - No secrets, just config
- [OK] Agent definitions - Public knowledge, no secrets
- [OK] Your notes - Your own writing

---

## Next Steps

1. **On your phone:**
   - Close Obsidian
   - Re-clone the repo
   - You'll see the new `system/` folder

2. **Explore:**
   - Open `system/README.md` for guidance
   - Browse `system/agents/` for agent definitions
   - Check `system/openclaw.json` for config

3. **Edit safely:**
   - User docs: Edit freely
   - System files: Reference only

---

## Summary

**You now have:**
- [OK] All system files visible in Obsidian
- [OK] Clean organization (no duplicates)
- [OK] Proper separation (user docs vs system)
- [OK] Mobile-friendly access
- [OK] Secure (no secrets synced)

**Status:** COMPLETE [OK]
