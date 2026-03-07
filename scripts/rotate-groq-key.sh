#!/bin/bash
# Rotate GROQ API Key - Security Incident Response
# Run this AFTER generating a new key on Groq console

echo "GROQ API Key Rotation Script"
echo "============================="
echo ""
echo "IMPORTANT: Generate a new key first:"
echo "1. Go to: https://console.groq.com/keys"
echo "2. Revoke the previously exposed GROQ key"
echo "3. Create a new key"
echo "4. Copy the new key"
echo ""
read -p "Enter your NEW GROQ API key: " NEW_KEY

if [ -z "$NEW_KEY" ]; then
    echo "No key provided. Exiting."
    exit 1
fi

# Update .env file
echo "Updating ~/.openclaw/.env..."
sed -i "s/^OPENCLAW_GROQ_API_KEY=.*/OPENCLAW_GROQ_API_KEY=$NEW_KEY/" ~/.openclaw/.env

echo "Tracked workspace templates now reference OPENCLAW_GROQ_API_KEY via environment variables."

echo ""
echo "✅ Key rotated successfully!"
echo ""
echo "Next steps:"
echo "1. Test the new key: python3 /home/ubuntu/.openclaw/workspace/tools/test-all-providers.py"
echo "2. Review git history if repo is tracked"
