#!/usr/bin/env python3
"""
TODO Manager - Simple CLI for managing TODO.md
Usage:
    python3 tools/todo.py add "Task description"
    python3 tools/todo.py list
    python3 tools/todo.py complete 1
    python3 tools/todo.py remove 1
    python3 tools/todo.py status
"""
import sys
import os
import re
from pathlib import Path
from datetime import datetime

TODO_FILE = Path("/home/ubuntu/.openclaw/workspace/TODO.md")

def read_todos():
    """Read all TODOs from file"""
    if not TODO_FILE.exists():
        return []
    
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    todos = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Match: - [ ] Task or - [x] Task or - [~] Task
        match = re.match(r'^- \[([ x~-])\] (.+)$', line)
        if match:
            status = match.group(1)
            task = match.group(2)
            todos.append({
                'line': i,
                'status': status,
                'task': task,
                'raw': line
            })
    
    return todos

def write_todos(todos, content):
    """Write updated TODOs back to file"""
    lines = content.split('\n')
    
    # Update lines with todos
    for todo in todos:
        if todo['line'] < len(lines):
            status_char = todo['status']
            lines[todo['line']] = f"- [{status_char}] {todo['task']}"
    
    # Write back
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def add_task(task_text):
    """Add a new task"""
    if not TODO_FILE.exists():
        TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TODO_FILE, 'w') as f:
            f.write("# TODO List\n\n## Active Tasks\n")
    
    # Add to "Active Tasks" section or create it
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find "Active Tasks" section or "Backlog"
    if "## Active Tasks" in content:
        # Insert after "## Active Tasks"
        lines = content.split('\n')
        insert_line = 0
        for i, line in enumerate(lines):
            if line.startswith("## Active Tasks"):
                insert_line = i + 1
                # Skip empty lines and existing todos
                while insert_line < len(lines):
                    if lines[insert_line].strip() == '' or lines[insert_line].startswith('- ['):
                        insert_line += 1
                    else:
                        break
                break
        
        lines.insert(insert_line, f"- [ ] {task_text}")
        new_content = '\n'.join(lines)
    else:
        new_content = content + "\n## Active Tasks\n- [ ] " + task_text + "\n"
    
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Added: {task_text}")

def list_tasks(show_completed=False):
    """List all tasks"""
    todos = read_todos()
    
    if not todos:
        print("No tasks found.")
        return
    
    print(f"\n📋 TODO List ({len(todos)} items)\n")
    
    active = [t for t in todos if t['status'] == ' ']
    in_progress = [t for t in todos if t['status'] == '~']
    completed = [t for t in todos if t['status'] == 'x']
    
    if active:
        print("🔵 Active:")
        for i, t in enumerate(active):
            print(f"  {i+1}. {t['task']}")
        print()
    
    if in_progress:
        print("🟡 In Progress:")
        for i, t in enumerate(in_progress):
            print(f"  {i+1}. {t['task']}")
        print()
    
    if show_completed and completed:
        print("🟢 Completed:")
        for i, t in enumerate(completed):
            print(f"  {i+1}. {t['task']}")
        print()
    
    print(f"Summary: {len(active)} active, {len(in_progress)} in progress, {len(completed)} completed")

def complete_task(index):
    """Mark a task as completed"""
    todos = read_todos()
    
    # Get active tasks only
    active = [t for t in todos if t['status'] == ' ']
    
    if index < 1 or index > len(active):
        print(f"Invalid index. Choose 1-{len(active)}")
        return
    
    target = active[index - 1]
    target['status'] = 'x'
    
    # Read full content and update
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    write_todos(todos, content)
    print(f"✅ Completed: {target['task']}")

def remove_task(index):
    """Remove a task"""
    todos = read_todos()
    
    if index < 1 or index > len(todos):
        print(f"Invalid index. Choose 1-{len(todos)}")
        return
    
    target = todos[index - 1]
    
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove the line
    if target['line'] < len(lines):
        lines.pop(target['line'])
    
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"🗑️ Removed: {target['task']}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'add':
        if len(sys.argv) < 3:
            print("Usage: todo.py add <task description>")
            sys.exit(1)
        task = ' '.join(sys.argv[2:])
        add_task(task)
    
    elif cmd == 'list':
        show_completed = '--completed' in sys.argv or '-c' in sys.argv
        list_tasks(show_completed)
    
    elif cmd == 'complete':
        if len(sys.argv) < 3:
            print("Usage: todo.py complete <index>")
            sys.exit(1)
        try:
            index = int(sys.argv[2])
            complete_task(index)
        except ValueError:
            print("Index must be a number")
            sys.exit(1)
    
    elif cmd == 'remove':
        if len(sys.argv) < 3:
            print("Usage: todo.py remove <index>")
            sys.exit(1)
        try:
            index = int(sys.argv[2])
            remove_task(index)
        except ValueError:
            print("Index must be a number")
            sys.exit(1)
    
    elif cmd == 'status':
        todos = read_todos()
        active = len([t for t in todos if t['status'] == ' '])
        completed = len([t for t in todos if t['status'] == 'x'])
        print(f"📊 Status: {active} active, {completed} completed")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == '__main__':
    main()
