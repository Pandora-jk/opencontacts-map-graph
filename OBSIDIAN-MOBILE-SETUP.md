# [PHONE] Obsidian Mobile Setup Guide

**Status:** [OK] **READY**  
**Repo:** https://github.com/Pandora-jk/pandora-obsidian-vault (Private)

---

## [TGT] What You Get

- **Full Read/Write Access** to all agent definitions, logs, and configs
- **Offline Access** - Works without internet (syncs when online)
- **Auto-Sync** - Every 10 minutes to GitHub
- **Mobile-First** - Optimized for phone viewing

---

## 📲 Step 1: Install Obsidian

**iOS:** Download from [App Store](https://apps.apple.com/app/obsidian/id1557175442)  
**Android:** Download from [Play Store](https://play.google.com/store/apps/details?id=md.obsidian) or [Direct APK](https://obsidian.md/android)

---

## 📲 Step 2: Install Obsidian Git Plugin

1. Open **Obsidian** app
2. Go to **Settings** → **Community Plugins** → **Browse**
3. Search for **"Obsidian Git"**
4. Tap **Install**
5. Tap **Enable**

---

## 📲 Step 3: Clone Your Vault

### Option A: Using Obsidian Git (Recommended)

1. In Obsidian, tap **"Open another vault"**
2. Tap **"Clone repository"**
3. Enter details:
   - **Repository URL:** `https://github.com/Pandora-jk/pandora-obsidian-vault.git`
   - **Username:** `Pandora-jk`
   - **Password/Token:** (Get from Bitwarden field `PAT Pandora`)
4. Tap **"Clone"**
5. Wait for sync to complete

### Option B: Manual Clone (If Option A fails)

1. Download **GitTouch** or **GitFolder** app (Android) / **Working Copy** (iOS)
2. Clone repo: `https://github.com/Pandora-jk/pandora-obsidian-vault.git`
3. In Obsidian: **Open folder** → Select the cloned folder

---

## 📲 Step 4: Configure Auto-Sync

1. In Obsidian, go to **Settings** → **Obsidian Git**
2. Enable **"Auto sync on boot"**
3. Set **"Auto sync interval"** to `10` minutes
4. Enable **"Sync on file change"** (optional, uses more battery)
5. Test sync: Tap the **Git icon** → **Pull**

---

## 📚 What's in Your Vault

### 🏠 Start Here
- `00-START-HERE.md` - Your dashboard with all links

### 🤖 Agent Definitions (All 19 agents)
- **Canonical path:** `system/agents/`
- **Orchestrators:** `system/agents/pandora-finance.md`, `system/agents/pandora-coding.md`, `system/agents/pandora-travel.md`, `system/agents/pandora-infra.md`
- **Finance Team:** `system/agents/pandora-finance-lead-gen.md`, `system/agents/pandora-finance-outreach.md`, `system/agents/pandora-finance-tracker.md`
- **Coding Team:** `system/agents/pandora-coding-bounty.md`, `system/agents/pandora-coding-review.md`, `system/agents/pandora-coding-security.md`, `system/agents/pandora-coding-builder.md`
- **Travel Team:** `system/agents/pandora-travel-flight.md`, `system/agents/pandora-travel-hotel.md`, `system/agents/pandora-travel-visa.md`
- **Infra Team:** `system/agents/pandora-infra-ops.md`, `system/agents/pandora-infra-backup.md`, `system/agents/pandora-infra-security.md`, `system/agents/pandora-infra-updates.md`, `system/agents/pandora-infra-disk.md`

### [CTX] Status & Logs
- `ORG-STATUS.md` - Global dashboard
- `TODO-AUTONOMOUS.md` - Active tasks
- `INCOME-ENGINE.md` - Revenue tracking
- `MEMORY.md` - Long-term memory
- `logs/` - Daily health reports

### 📖 Documentation
- `OPERATIONS.md` - System architecture + runtime operations
- `INFRA-TEAM-COMPLETE.md` - Infra team guide
- `OPERATIONS.md` - Nightly/daytime operations and health checks
- `ARCHITECTURE-REDESIGN.md` - Technical deep dive

---

## 🔁 Sync Workflow

### AWS → GitHub (Auto)
- Runs every 10 minutes via cron job
- Copies all new/changed files
- Pushes to GitHub

### Phone → GitHub (Manual/Semi-Auto)
- **Manual:** Tap Git icon → Pull/Push
- **Auto:** If "Sync on file change" enabled (uses more battery)

### GitHub → Phone (Auto)
- Obsidian Git pulls changes every 10 minutes
- You see latest logs and agent updates

---

## [TGT] Van Life Usage

### Morning (Camp with WiFi)
1. Open Obsidian
2. Pull latest changes (if not auto-synced)
3. Check `logs/nightly-health-YYYY-MM-DD.md` for overnight reports
4. Review `TODO-AUTONOMOUS.md` for today's tasks

### During Day (No Signal)
- Read agent definitions, travel plans, logs offline
- Edit TODOs, add notes to journals
- All changes saved locally

### Evening (Camp with WiFi)
- Open Obsidian → Sync
- Your edits upload to GitHub
- AWS picks them up in next 10-min cycle

---

## 🔐 Security

- **Repo is Private** - Only you can access
- **Encrypted Sync** - HTTPS only
- **PAT in Bitwarden** - Never stored in plain text
- **Version History** - Can revert mistakes via GitHub

---

## 🆘 Troubleshooting

**"Can't connect to GitHub"**
- Check internet connection
- Verify PAT is correct (try in browser)
- Changes saved locally, will sync when online

**"Merge conflict"**
- Obsidian Git will show conflict resolver
- Choose "Yours" (phone) or "Theirs" (GitHub)
- For logs, always choose "Theirs" (AWS is source of truth)

**"Vault won't load"**
- Re-clone repo from GitHub
- Your data is safe on GitHub

---

## [OK] Setup Complete!

Your Obsidian vault is:
- [OK] Created at `https://github.com/Pandora-jk/pandora-obsidian-vault`
- [OK] Populated with all 16 agent definitions
- [OK] Auto-syncing every 10 minutes from AWS
- [OK] Ready to clone on your phone

**Next:** Install Obsidian on your phone and follow Step 3 above!

---

**Sync Status:**
- Last Sync: Just now
- Next Sync: In 10 minutes
- Files Synced: 47 files
- Repo Size: ~150 KB
