#!/bin/bash
# sync-obsidian-bidirectional.sh
# Bidirectional sync: AWS ↔ GitHub ↔ Obsidian (Phone)
# Runs every 10 minutes

WORKSPACE="/home/ubuntu/.openclaw/workspace"
GH_USER="Pandora-jk"
GH_REPO="pandora-obsidian-vault"
TOKEN="${OPENCLAW_GITHUB_TOKEN:-}"

if [ -z "$TOKEN" ]; then
  echo "❌ OPENCLAW_GITHUB_TOKEN is not set" >&2
  exit 1
fi

cd "$WORKSPACE" || exit 1

echo "🔄 [$(date)] Starting bidirectional sync..."

# Step 1: Pull latest changes from GitHub (phone edits, other devices)
echo "⬇️  Pulling changes from GitHub..."
git fetch origin main

# Check if there are changes to merge
if ! git merge --ff-only origin/main --no-commit --no-edit &>/dev/null; then
  echo "⚠️  Merge conflict detected. Phone changes will be preserved."
  # Abort merge to avoid conflicts, phone edits are source of truth
  git merge --abort 2>/dev/null || true
fi

# Check for incoming changes
if git diff HEAD..origin/main --quiet; then
  echo "✅ No new changes from GitHub"
else
  echo "📥 New changes found on GitHub (from phone)"
  git merge origin/main --no-edit
  echo "✅ Merged phone changes into workspace"
fi

# Step 2: Check for local changes (agent runs, logs, new files)
if git diff --quiet && git diff --cached --quiet; then
  echo "✅ No local changes to sync"
else
  echo "📤 Local changes detected (logs, new files, etc.)"
  git add -A
  git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')" || echo "No changes to commit"
  
  # Push to GitHub without writing the token into the repo config.
  echo "⬆️  Pushing to GitHub..."
  AUTH_HEADER="$(printf '%s:%s' "$GH_USER" "$TOKEN" | base64 | tr -d '\n')"
  git -c "http.https://github.com/.extraheader=AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
  
  if [ $? -eq 0 ]; then
    echo "✅ Pushed to GitHub"
  else
    echo "❌ Push failed. Will retry next cycle."
  fi
fi

echo "✅ Sync complete at $(date)"
