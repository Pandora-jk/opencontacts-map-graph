#!/bin/bash
# Create GitHub repos for Pandora's income generation

# Get token from Bitwarden
GH_TOKEN=$(bash tools/bw-get.sh "Pandora-jk" password 2>/dev/null)

if [ -z "$GH_TOKEN" ]; then
    GH_TOKEN=$(bash tools/bw-get.sh "GitHub" password 2>/dev/null)
fi

if [ -z "$GH_TOKEN" ] || [ ${#GH_TOKEN} -lt 10 ]; then
    echo "ERROR: GitHub token not found in Bitwarden"
    exit 1
fi

echo "✅ Token retrieved successfully"

# Test authentication
echo "🔑 Testing authentication..."
USER_INFO=$(curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/user)
USER_LOGIN=$(echo "$USER_INFO" | jq -r '.login')

if [ "$USER_LOGIN" == "null" ] || [ -z "$USER_LOGIN" ]; then
    echo "❌ Authentication failed"
    exit 1
fi

echo "✅ Authenticated as: $USER_LOGIN"

# Create repositories
REPOS=("automation-scripts" "data-brokerage" "research-reports")
DESCS=("Custom automation scripts for businesses" "Niche datasets and lead lists for sale" "Sample OSINT and market research reports")

for i in "${!REPOS[@]}"; do
    REPO=${REPOS[$i]}
    DESC=${DESCS[$i]}
    
    echo "📦 Creating $REPO..."
    
    RESULT=$(curl -s -X POST \
        -H "Authorization: Bearer $GH_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"name\":\"$REPO\",\"description\":\"$DESC\",\"private\":false,\"auto_init\":true}" \
        https://api.github.com/user/repos)
    
    REPO_NAME=$(echo "$RESULT" | jq -r '.name')
    REPO_URL=$(echo "$RESULT" | jq -r '.html_url')
    
    if [ "$REPO_NAME" == "null" ] || [ -z "$REPO_NAME" ]; then
        # Check if repo already exists (422 error)
        if echo "$RESULT" | jq -e '.message == "name already exists on this team"' > /dev/null 2>&1; then
            echo "⚠️  Repository '$REPO' already exists"
            echo "   URL: https://github.com/$USER_LOGIN/$REPO"
        else
            echo "❌ Failed to create '$REPO': $RESULT"
        fi
    else
        echo "✅ Created: $REPO"
        echo "   URL: $REPO_URL"
    fi
done

echo ""
echo "🎉 Repository creation complete!"
