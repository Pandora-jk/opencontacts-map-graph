# Bitwarden Skill - Password Manager Integration

## Purpose
Securely manage passwords, API keys, and sensitive data via Bitwarden CLI.

## Capabilities
- [OK] List, create, edit, delete items
- [OK] Create/manage folders and collections
- [OK] Share items via organizations
- [OK] Auto-unlock vault with session key
- [OK] Support for EU server (vault.bitwarden.eu)

## Configuration
**Server:** https://vault.bitwarden.eu  
**CLI:** `bw` (Bitwarden CLI v2026.1.0+)  
**Session Key:** Stored in environment or `~/.bitwarden/session.txt` (chmod 600)

## Usage Patterns

### Login & Unlock
```bash
# Login (one-time or when session expires)
bw login <email> <password> --server https://vault.bitwarden.eu

# Unlock vault
export BW_SESSION="$(bw unlock --raw)"

# Check status
bw unlock --check
```

### List Items
```bash
# List all items
bw list items

# Search items
bw list items --search "keyword"

# Get specific item
bw get item <item-id>

# List folders
bw list folders

# List organizations
bw list organizations

# List collections
bw list collections
```

### Create Items
```bash
# Create login item (base64 encoded JSON)
echo 'eyJuYW1lIjoiTXkgTG9naW4iLCJ0eXBlIjoxLCJsb2dpbiI6eyJ1c2VybmFtZSI6InVzZXIiLCJwYXNzd29yZCI6InBhc3MifX0=' | bw create item

# Create folder
echo 'eyJuYW1lIjoiTXkgRm9sZGVyIn0=' | bw create folder

# Create collection (requires organization ID)
echo 'eyJuYW1lIjoiTXkgQ29sbGVjdGlvbiIsIm9yZ2FuaXphdGlvbklkIjoi123456"'}' | bw create org-collection
```

### Share with Organization
```bash
# Move item to organization
bw move <item-id> <organization-id>

# Share item (deprecated, use move)
bw share <item-id> <organization-id>
```

## Session Key Management
**Option 1: Environment Variable**
```bash
export BW_SESSION="your-session-key"
```

**Option 2: File (secure)**
```bash
# Store session key
echo "your-session-key" > ~/.bitwarden/session.txt
chmod 600 ~/.bitwarden/session.txt

# Load session key
export BW_SESSION="$(cat ~/.bitwarden/session.txt)"
```

## Security Notes
- Never commit session keys to git
- Session keys expire after logout or 24h (configurable)
- Use `bw lock` to lock vault when done
- Always use `--raw` flag for programmatic access
- EU server users must configure: `bw config server https://vault.bitwarden.eu`

## Common Tasks

### Add API Key for Pandora
```bash
# Create item with name "Pandora - API Key - ServiceName"
# Store in "Pandora" folder or collection
```

### Retrieve Password
```bash
bw get item <item-name-or-id> | jq '.login.password'
```

### Export Vault (backup)
```bash
bw export --output backup.json --format json
```

## Troubleshooting
- **"Invalid master password"**: Check server setting, re-login
- **"Vault is locked"**: Run `bw unlock`
- **"Session expired"**: Re-login with `bw login`
- **"Organization not found"**: Create via web UI first

## Skills to Chain
- `mcporter` - For MCP server integration if available
- `coding-agent` - For scripting complex operations
- `healthcheck` - For security audits of stored credentials
