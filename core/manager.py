#!/usr/bin/env python3
"""
Pandora Core Manager
Automates spawning specialist agents for each department.

Usage: python3 core/manager.py <department> <task>
Departments: finance, coding, travel, infra
"""

import os
import sys

DEPT_CONFIG = {
    "finance": {
        "prompt_file": "departments/finance/SOUL.md",
        "context_files": ["departments/finance/MEMORY.md", "departments/finance/TODO.md"],
        "model": "nvidia/moonshotai/kimi-k2-thinking",
        "label": "finance-specialist"
    },
    "coding": {
        "prompt_file": "departments/coding/SOUL.md", 
        "context_files": ["departments/coding/MEMORY.md", "departments/coding/TODO.md"],
        "model": "nvidia/qwen/qwen3.5-397b-a17b",
        "label": "coding-specialist"
    },
    "travel": {
        "prompt_file": "departments/travel/SOUL.md",
        "context_files": ["departments/travel/MEMORY.md", "departments/travel/TODO.md"],
        "model": "nvidia/openai/gpt-4o",
        "label": "travel-specialist"
    },
    "infra": {
        "prompt_file": "departments/infra/SOUL.md",
        "context_files": ["departments/infra/MEMORY.md", "departments/infra/TODO.md"],
        "model": "nvidia/moonshotai/kimi-k2-thinking",
        "label": "infra-specialist"
    }
}

WORKSPACE = "/home/ubuntu/.openclaw/workspace"

def load_context(dept, task):
    """Load SOUL.md and context files."""
    config = DEPT_CONFIG[dept]
    
    # Load SOUL.md
    soul_path = os.path.join(WORKSPACE, config['prompt_file'])
    with open(soul_path, 'r') as f:
        soul = f.read()
    
    # Load context files
    context_parts = []
    for ctx_file in config['context_files']:
        full_path = os.path.join(WORKSPACE, ctx_file)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                context_parts.append(f"\n--- {ctx_file} ---\n{f.read()}")
    
    return soul, context_parts

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 core/manager.py <department> <task>")
        print("Departments: finance, coding, travel, infra")
        sys.exit(1)
    
    dept = sys.argv[1]
    task = sys.argv[2]
    
    if dept not in DEPT_CONFIG:
        print(f"❌ Unknown department: {dept}")
        print(f"Available: {list(DEPT_CONFIG.keys())}")
        sys.exit(1)
    
    config = DEPT_CONFIG[dept]
    soul, ctx_parts = load_context(dept, task)
    
    print(f"🚀 Spawning {config['label']}...")
    print(f"📚 SOUL: {len(soul)} chars")
    print(f"📋 Context files: {len(ctx_parts)}")
    print(f"💻 Model: {config['model']}")
    
    print("\n--- COMMAND ---")
    print(f'sessions_spawn --label "{config["label"]}" --agent "{dept}" --model "{config["model"]}" --mode run --task "{task}"')

if __name__ == "__main__":
    main()
