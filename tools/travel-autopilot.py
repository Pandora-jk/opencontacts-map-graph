#!/usr/bin/env python3
"""
Travel autonomous loop with itinerary/cost artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path('/home/ubuntu/.openclaw/workspace')
TRAVEL = ROOT / 'departments' / 'travel'
TODO_FILE = TRAVEL / 'TODO.md'
STATUS_FILE = TRAVEL / 'STATUS.md'
STATE_FILE = ROOT / 'memory' / 'travel-autopilot-state.json'
ACTIVITY_LOG = ROOT / 'logs' / 'travel-activity.log'
ART_DIR = TRAVEL / 'artifacts'


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {'runs': 0, 'cursor': 0, 'progress': {}}
    try:
        state = json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {'runs': 0, 'cursor': 0, 'progress': {}}
    state.setdefault('runs', 0)
    state.setdefault('cursor', 0)
    if not isinstance(state.get('progress'), dict):
        state['progress'] = {}
    return state


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def parse_auto_tasks(text: str) -> list[str]:
    out: list[str] = []
    section = ''
    for raw in text.splitlines():
        line = raw.strip()
        if 'Autonomous Queue' in line:
            section = 'auto'
            continue
        if line.startswith('## '):
            section = ''
            continue
        if section == 'auto' and line.startswith('- [ ]'):
            out.append(re.sub(r'^- \[ \]\s*', '', line).strip())
    return out


def write_artifact(task: str, run_id: int) -> Path:
    now = dt.datetime.now(dt.UTC)
    slug = re.sub(r'[^a-z0-9]+', '-', task.lower()).strip('-')[:56] or 'travel-task'
    rel = Path('plans') / f"{now:%Y%m%dT%H%M%SZ}-r{run_id}-{slug}.md"
    p = ART_DIR / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    content = [
        f"# Travel Execution Note (Run {run_id})",
        '',
        f"- UTC: {now.isoformat().replace('+00:00','Z')}",
        f"- Task: {task}",
        '',
        '## Action Slice',
        '- Define one booking/research action for next stop.',
        '- Estimate cost range and timing window.',
        '- Record fallback option to keep route flexible.',
        '',
        '## Draft',
        '- Primary option: low-cost operator/campsite shortlist (3 choices).',
        '- Fallback: free-camp + next-day retry plan.',
    ]
    p.write_text('\n'.join(content) + '\n', encoding='utf-8')
    return p


def append_activity(msg: str) -> None:
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
    with ACTIVITY_LOG.open('a', encoding='utf-8') as f:
        f.write(f'[{now}] {msg}\n')


def clean_text(value: str) -> str:
    txt = re.sub(r'[`*_]+', '', value or '')
    return re.sub(r'\s+', ' ', txt).strip()


def build_status(state: dict, task: str, artifact_rel: str, queue: int) -> tuple[str, str]:
    now = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    count = int(state.get('progress', {}).get(task, 0)) if task else 0
    task_clean = clean_text(task or 'none')
    md = [
        '# Travel Status',
        '',
        f'- Last run (UTC): {now}',
        f"- Run count: {state.get('runs',0)}",
        f'- Active task: {task or "none"}',
        f'- Task progress count: {count}',
        f'- Last artifact: {artifact_rel or "none"}',
        f'- Autonomous open queue: {queue}',
        '',
    ]
    tg = [
        '[TRAVEL UPDATE]',
        f'Time (UTC): {now}',
        f'Run: {state.get("runs",0)}',
        f'Task: {task_clean}',
        f'Progress: {count}',
        f'Queue: {queue}',
        f'Artifact: {artifact_rel or "none"}',
    ]
    return '\n'.join(md) + '\n', '\n'.join(tg)


def main() -> int:
    parser = argparse.ArgumentParser(description='Travel autopilot')
    parser.add_argument('--emit-telegram', action='store_true')
    args = parser.parse_args()

    todo = TODO_FILE.read_text(encoding='utf-8') if TODO_FILE.exists() else ''
    tasks = parse_auto_tasks(todo)
    state = load_state()
    state['runs'] = int(state.get('runs', 0)) + 1

    task = ''
    rel = ''
    if tasks:
        idx = int(state.get('cursor', 0)) % len(tasks)
        task = tasks[idx]
        state['cursor'] = idx + 1
        art = write_artifact(task, int(state['runs']))
        rel = str(art.relative_to(ROOT))
        prog = state.setdefault('progress', {})
        prog[task] = int(prog.get(task, 0)) + 1
        append_activity(f"run={state['runs']} task='{task}' artifact='{rel}' queue={len(tasks)}")
    else:
        append_activity(f"run={state['runs']} task='none' queue=0")

    status_text, telegram_text = build_status(state, task, rel, len(tasks))
    STATUS_FILE.write_text(status_text, encoding='utf-8')
    save_state(state)

    if args.emit_telegram:
        print(telegram_text)
    else:
        print(status_text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
