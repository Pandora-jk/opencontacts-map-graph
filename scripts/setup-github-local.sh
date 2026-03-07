#!/bin/bash
# One-Time GitHub Repo Setup Script
# Run this locally if Bitwarden CLI sync is failing.
# Requires: Git installed, GitHub CLI (gh) OR Personal Access Token.

echo "🔧 Pandora GitHub Setup Script"
echo "--------------------------------"

# Method 1: Using GitHub CLI (gh) - Preferred
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected."
    echo "🔑 Authenticating with GitHub..."
    gh auth login
    
    echo "📦 Creating repositories..."
    for repo in automation-scripts data-brokerage research-reports; do
        echo "   Creating $repo..."
        gh repo create "$repo" --public --description="Income generation: $repo" --source=. --push=false --remote=origin 2>/dev/null || echo "   ⚠️  $repo may already exist."
    done
    
    echo "✅ Setup complete! Check: https://github.com/Pandora-jk"
    exit 0
fi

# Method 2: Using Personal Access Token (Manual Entry)
echo "⚠️  GitHub CLI (gh) not found. Using Personal Access Token method."
read -p "Enter your GitHub Personal Access Token: " GH_TOKEN
read -p "Enter GitHub Username (e.g., Pandora-jk): " GH_USER

if [ -z "$GH_TOKEN" ] || [ -z "$GH_USER" ]; then
    echo "❌ Token and Username required."
    exit 1
fi

echo "📦 Creating repositories via API..."
for repo in automation-scripts data-brokerage research-reports; do
    echo "   Creating $repo..."
    curl -s -X POST \
        -H "Authorization: Bearer $GH_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"name\":\"$repo\",\"description\":\"Income generation: $repo\",\"private\":false,\"auto_init\":true}" \
        https://api.github.com/user/repos | jq -r '"   ✅ " + .html_url + " (" + .name + ")"'
done

echo "✅ Setup complete!"
