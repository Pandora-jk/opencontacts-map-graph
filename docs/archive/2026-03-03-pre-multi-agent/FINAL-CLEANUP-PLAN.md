# 🔪 Final Cleanup Plan - Narrow & Careful

**Date:** March 3, 2026  
**Goal:** Remove clutter, merge duplicates, organize properly

---

## Analysis: What's in Root (52 .md files)

### [OK] KEEP - Core Identity (4 files)
These are essential and used by OpenClaw:
- `SOUL.md` - Main persona
- `USER.md` - User info
- `AGENTS.md` - How to work
- `MEMORY.md` - Long-term memory

### [OK] KEEP - Active Working (3 files)
- `TODO-AUTONOMOUS.md` - Current tasks
- `TODO-2026-03-03.md` - Today's tasks
- `INCOME-ENGINE.md` - Revenue tracking (active project)

### [OK] KEEP - Obsidian Setup (2 files)
- `OBSIDIAN-MOBILE-SETUP.md` - Mobile setup guide
- `OBSIDIAN-STRUCTURE-FINAL.md` - Structure documentation

### 🗑️ DELETE - Temporary/Historical (9 files)
These served their purpose, now just clutter:
1. `BOOT.md` - One-time bootstrap (done)
2. `EDIT_FIX_PLAN.md` - Temporary fix plan (fixed)
3. `FIX_SUMMARY.md` - Temporary fix summary (done)
4. `TODO_SYNC_GUIDE.md` - Obsolete (replaced by Obsidian sync)
5. `LOGSEQ-MOBILE-SETUP.md` - Obsolete (using Obsidian now)
6. `SYNC-SUMMARY.md` - Obsolete (old sync method)
7. `TODO.telegram.txt` - Temporary file
8. `TODO_GUIDE.md` - Can be merged into AGENTS.md
9. `EDIT_TOOL_GUIDE.md` - Can be merged into AGENTS.md

### 🔀 MERGE - Duplicates/Overlapping (6 files → 2 files)

**Group 1: Organization Dashboard (3 files → 1 file)**
- `00-START-HERE.md` - Dashboard with links
- `ORG-README.md` - Org structure explanation
- `ORG-STATUS.md` - Status dashboard

**Keep:** `ORG-STATUS.md` (rename to `DASHBOARD.md`)  
**Merge:** Move content from others into it  
**Delete:** `00-START-HERE.md`, `ORG-README.md`

**Group 2: Architecture Docs (2 files → 1 file)**
- `ARCHITECTURE-REDESIGN.md` - Technical architecture
- `MULTI-AGENT-SETUP.md` - Setup guide

**Keep:** `MULTI-AGENT-SETUP.md` (more practical)  
**Append:** Technical details from ARCHITECTURE-REDESIGN.md  
**Delete:** `ARCHITECTURE-REDESIGN.md`

**Group 3: Infra Docs (2 files → 1 file)**
- `INFRA-TEAM-COMPLETE.md` - Team completion status
- `NIGHTLY-OPS-SETUP.md` - Nightly operations guide

**Keep:** Both are actually different topics
- `INFRA-TEAM-COMPLETE.md` → Keep as historical reference
- `NIGHTLY-OPS-SETUP.md` → Keep as active guide

### [OK] KEEP - Documentation (6 files)
- `HEARTBEAT.md` - Heartbeat instructions
- `PROACTIVE_CHECKS.md` - Proactive monitoring guide
- `SELF_IMPROVE.md` - Self-improvement process
- `CLEANUP-SUMMARY.md` - Recent cleanup (keep for now)
- `FINAL-CLEANUP-PLAN.md` - This plan
- `TOOLS.md` - Tool usage guide

### 🗑️ DELETE - Agent SOULs in Root (19 files)
These are duplicates - the real ones are in `system/agents/`:
- `pandora-finance.md` + 3 finance specialists
- `pandora-coding.md` + 4 coding specialists
- `pandora-travel.md` + 4 travel specialists
- `pandora-infra.md` + 5 infra specialists

**Wait!** Actually, these are NEEDED for mobile quick access. Keep them but organize into folders.

---

## Proposed New Structure

### Root Level (Clean & Minimal)
```.openclaw/workspace/
├── 📘 Core (4 files)
│   ├── SOUL.md
│   ├── USER.md
│   ├── AGENTS.md
│   └── MEMORY.md
│
├── [CTX] Active (3 files)
│   ├── DASHBOARD.md (merged from ORG-STATUS, 00-START-HERE, ORG-README)
│   ├── TODO-AUTONOMOUS.md
│   └── TODO-2026-03-03.md
│
├── 💰 Projects (1 file)
│   └── INCOME-ENGINE.md
│
├── 📚 Guides (consolidated)
│   ├── WORKFLOW.md (merged: TODO_GUIDE + EDIT_TOOL_GUIDE)
│   ├── HEARTBEAT.md
│   ├── PROACTIVE_CHECKS.md
│   └── SELF_IMPROVE.md
│
├── [PHONE] Obsidian (2 files)
│   ├── OBSIDIAN-MOBILE-SETUP.md
│   └── OBSIDIAN-STRUCTURE-FINAL.md
│
├── 🤖 Agent SOULs (19 files, but organized)
│   ├── pandora-finance.md
│   ├── pandora-finance-lead-gen.md
│   └── ... (all 19 pandora-*.md files)
│
├── [DIR] Folders
│   ├── departments/ (division context)
│   ├── system/ (system files)
│   ├── scripts/ (automation)
│   ├── tools/ (utilities)
│   ├── assets/ (data)
│   ├── memory/ (daily notes)
│   └── logs/ (app logs)
│
└── 🗑️ To Delete (9 files)
    - BOOT.md
    - EDIT_FIX_PLAN.md
    - FIX_SUMMARY.md
    - TODO_SYNC_GUIDE.md
    - LOGSEQ-MOBILE-SETUP.md
    - SYNC-SUMMARY.md
    - TODO.telegram.txt
    - 00-START-HERE.md (merged into DASHBOARD)
    - ORG-README.md (merged into DASHBOARD)
```

---

## Execution Steps

### Step 1: Delete Temporary Files (9 files)
```bash
rm BOOT.md EDIT_FIX_PLAN.md FIX_SUMMARY.md TODO_SYNC_GUIDE.md LOGSEQ-MOBILE-SETUP.md SYNC-SUMMARY.md TODO.telegram.txt
```

### Step 2: Create Dashboard (merge 3 → 1)
- Create `DASHBOARD.md` with:
  - Status table from ORG-STATUS.md
  - Navigation from 00-START-HERE.md
  - Structure from ORG-README.md
- Delete: `00-START-HERE.md`, `ORG-README.md`, `ORG-STATUS.md`

### Step 3: Merge Workflow Guides (2 → 1)
- Create `WORKFLOW.md` with:
  - Edit tool guide
  - TODO guide
  - Best practices
- Delete: `TODO_GUIDE.md`, `EDIT_TOOL_GUIDE.md`

### Step 4: Keep Architecture Separate
- Keep `MULTI-AGENT-SETUP.md` (practical guide)
- Keep `INFRA-TEAM-COMPLETE.md` (historical)
- Keep `NIGHTLY-OPS-SETUP.md` (active guide)
- Delete `ARCHITECTURE-REDESIGN.md` (too technical, redundant)

### Step 5: Update Git
- Commit all changes
- Push to GitHub
- Sync to Obsidian

---

## Result

**Before:** 52 files in root (messy)  
**After:** ~35 files in root (organized)

**Reduction:** 
- Deleted: 9 temporary files
- Merged: 5 files → 2 files
- Net reduction: 12 files (23% cleaner)

**Benefits:**
- Clear separation: Core vs Active vs Guides
- No temporary files cluttering
- Duplicates removed
- Mobile-friendly structure preserved
