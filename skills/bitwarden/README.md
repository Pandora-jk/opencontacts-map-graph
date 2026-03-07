# Bitwarden Skill for Pandora AI

## Overview
Complete Bitwarden CLI integration for secure password management, created for Jim's Bitwarden EU account.

## Files
- `SKILL.md` - Skill documentation and usage patterns
- `config.sh` - Configuration constants
- `bw-helper.sh` - Interactive helper script
- `README.md` - This file

## Quick Start

### 1. Load the skill
```bash
cd /home/ubuntu/.openclaw/workspace/skills/bitwarden
source config.sh
```

### 2. Check status
```bash
./bw-helper.sh status
```

### 3. Unlock vault (if needed)
```bash
export BW_SESSION=$(cat ~/.bitwarden/session.txt)
bw unlock --check
```

### 4. Common operations
```bash
# List all items
./bw-helper.sh list

# Search for items
./bw-helper.sh search "api"

# Create folder
./bw-helper.sh create-folder "My Folder"

# Check session status
./bw-helper.sh check
```

## Current Setup
- **Server:** https://vault.bitwarden.eu
- **Account:** jim.cooding@gmail.com
- **Folder:** Pandora (ID: fac438b1-5bf8-4b78-bb88-b3fd010c9fc0)
- **Test Item:** Test Login (ID: 451a5d22-e974-44a9-9b19-b3fd010cb9dd)

## Next Steps
1. [OK] Create organization "Pandora" via web UI (https://vault.bitwarden.eu)
2. [OK] Invite main account to organization
3. [OK] Create collections for sharing
4. ⏳ Add real credentials to vault

## Security Notes
- Session key stored in `~/.bitwarden/session.txt` (chmod 600)
- Session expires after 24h or logout
- Never commit credentials to git
- Use `bw lock` when done

## Skills to Chain
- `mcporter` - For MCP server integration
- `coding-agent` - For scripting complex operations
- `healthcheck` - For security audits
