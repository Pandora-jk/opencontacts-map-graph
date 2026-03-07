#!/bin/bash
# Bitwarden Helper Script for Pandora AI
# Usage: ./bw-helper.sh <command> [args]

set -e

BW_SESSION_FILE="$HOME/.bitwarden/session.txt"
BW_SERVER="https://vault.bitwarden.eu"
BW_EMAIL="jim.cooding@gmail.com"

# Ensure session directory exists
mkdir -p "$HOME/.bitwarden"

# Load session key from file
load_session() {
    if [ -f "$BW_SESSION_FILE" ]; then
        export BW_SESSION=$(cat "$BW_SESSION_FILE")
        return 0
    fi
    return 1
}

# Check if logged in
check_session() {
    # Try to load session from file first
    load_session
    
    if bw unlock --check >/dev/null 2>&1; then
        echo "✅ Vault is unlocked"
        return 0
    else
        echo "⚠️  Vault is locked or session expired"
        return 1
    fi
}

# Login
do_login() {
    echo "🔐 Logging in to Bitwarden EU..."
    bw login "$BW_EMAIL" --server "$BW_SERVER"
    echo "✅ Logged in successfully"
}

# Unlock vault
do_unlock() {
    echo "🔓 Unlocking vault..."
    if bw unlock --check >/dev/null 2>&1; then
        echo "✅ Already unlocked"
        return 0
    fi
    
    # Try to use stored session key
    if [ -f "$BW_SESSION_FILE" ]; then
        export BW_SESSION=$(cat "$BW_SESSION_FILE")
        if bw unlock --check >/dev/null 2>&1; then
            echo "✅ Unlocked with stored session"
            return 0
        fi
    fi
    
    # Need to unlock manually
    echo "Please enter your master password:"
    read -s BW_PASSWORD
    echo
    
    RESULT=$(bw unlock "$BW_PASSWORD" --raw 2>/dev/null)
    if [ $? -eq 0 ]; then
        export BW_SESSION="$RESULT"
        echo "$RESULT" > "$BW_SESSION_FILE"
        chmod 600 "$BW_SESSION_FILE"
        echo "✅ Vault unlocked"
    else
        echo "❌ Failed to unlock"
        return 1
    fi
}

# List items
do_list() {
    check_session || return 1
    echo "📋 Listing items..."
    bw list items --pretty
}

# Search items
do_search() {
    check_session || return 1
    if [ -z "$1" ]; then
        echo "Usage: $0 search <keyword>"
        return 1
    fi
    echo "🔍 Searching for: $1"
    bw list items --search "$1" --pretty
}

# Create item
do_create_item() {
    check_session || return 1
    echo "📝 Create item (JSON format):"
    echo "Example: {\"name\":\"My Login\",\"type\":1,\"login\":{\"username\":\"user\",\"password\":\"pass\"}}"
    read -p "Enter JSON: " JSON_INPUT
    ENCODED=$(echo "$JSON_INPUT" | base64 -w0)
    bw create item "$ENCODED"
    echo "✅ Item created"
}

# Create folder
do_create_folder() {
    check_session || return 1
    FOLDER_NAME="${1:-Pandora}"
    echo "{\"name\":\"$FOLDER_NAME\"}" | base64 -w0 | xargs bw create folder
    echo "✅ Folder created: $FOLDER_NAME"
}

# Show status
do_status() {
    echo "📊 Bitwarden Status"
    echo "Server: $BW_SERVER"
    echo "Email: $BW_EMAIL"
    bw status 2>/dev/null || echo "Not logged in"
    check_session
}

# Main command handler
case "${1:-status}" in
    login)
        do_login
        ;;
    unlock)
        do_unlock
        ;;
    list)
        do_list
        ;;
    search)
        do_search "$2"
        ;;
    create-item)
        do_create_item
        ;;
    create-folder)
        do_create_folder "$2"
        ;;
    status)
        do_status
        ;;
    check)
        check_session
        ;;
    *)
        echo "Bitwarden Helper for Pandora AI"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  status          Show current status"
        echo "  login           Login to Bitwarden"
        echo "  unlock          Unlock vault"
        echo "  list            List all items"
        echo "  search <term>   Search items"
        echo "  create-item     Create new item (interactive)"
        echo "  create-folder   Create new folder"
        echo "  check           Check if vault is unlocked"
        echo ""
        echo "Examples:"
        echo "  $0 status"
        echo "  $0 unlock"
        echo "  $0 search 'api'"
        echo "  $0 create-folder 'My Folder'"
        ;;
esac
