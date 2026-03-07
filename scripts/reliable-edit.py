#!/usr/bin/env python3
"""
Reliable file editor that handles the edit tool's exact matching requirement.
Usage: python3 scripts/reliable-edit.py <file> <old_text_base64> <new_text_base64>
"""
import sys
import base64
from pathlib import Path

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 reliable-edit.py <file> <old_b64> <new_b64>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    old_text = base64.b64decode(sys.argv[2]).decode('utf-8')
    new_text = base64.b64decode(sys.argv[3]).decode('utf-8')
    
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try exact match first
    if old_text in content:
        new_content = content.replace(old_text, new_text)
    else:
        # Try fuzzy match - normalize whitespace
        import re
        old_normalized = re.sub(r'\s+', r'\\s+', old_text)
        if re.search(old_normalized, content):
            new_content = re.sub(old_normalized, new_text, content)
        else:
            print(f"Error: Could not find text to replace in {filepath}")
            print(f"Looking for: {old_text[:100]}...")
            sys.exit(1)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Successfully updated {filepath}")

if __name__ == '__main__':
    main()
