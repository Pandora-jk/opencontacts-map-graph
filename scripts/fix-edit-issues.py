#!/usr/bin/env python3
"""
Fix edit tool failures by normalizing markdown files.
Issues addressed:
1. Remove or replace problematic UTF-8 emojis
2. Normalize line endings
3. Ensure consistent encoding
"""
import os
from pathlib import Path

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", "/home/ubuntu/.openclaw/workspace"))

# Map of problematic emojis to ASCII replacements
EMOJI_REPLACEMENTS = {
    '✅': '[OK]',
    '❌': '[FAIL]',
    '⚠️': '[WARN]',
    '📌': '[NOTE]',
    '🔮': '[P]',
    '📋': '[TODO]',
    '🔒': '[SEC]',
    '🧹': '[CLN]',
    '🔧': '[FIX]',
    '📝': '[MEM]',
    '💡': '[IDEA]',
    '📧': '[MAIL]',
    '📱': '[PHONE]',
    '🌙': '[NIGHT]',
    '📊': '[CTX]',
    '📁': '[DIR]',
    '📂': '[FLD]',
    '✨': '[STAR]',
    '🎯': '[TGT]',
    '🚀': '[GO]',
    '💾': '[SAVE]',
    '⏰': '[TIME]',
    '🕐': '[CLOCK]',
}

def normalize_file(filepath):
    """Normalize a markdown file"""
    if not filepath.endswith('.md'):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # Replace emojis with ASCII
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                changes.append(f"Replaced {emoji} with {replacement}")
        
        # Normalize line endings (ensure Unix-style)
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Ensure trailing newline
        if not content.endswith('\n'):
            content += '\n'
            changes.append("Added trailing newline")
        
        # Write back if changed
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            for change in changes:
                print(f"  - {change}")
            return True
        else:
            print(f"✓ No changes needed: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    print("🔧 Fixing edit tool issues in workspace...\n")
    
    fixed_count = 0
    
    # Process all markdown files
    for md_file in WORKSPACE.rglob('*.md'):
        if normalize_file(str(md_file)):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} file(s)")
    print("\nNote: Emojis replaced with ASCII codes to prevent edit tool failures.")
    print("Files should now work correctly with the edit tool.")

if __name__ == '__main__':
    main()
