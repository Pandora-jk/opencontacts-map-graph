#!/usr/bin/env python3
"""
Coding autonomous loop with concrete artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

from coding_feedback_loop import audit_feedback_loop, build_snapshot, choose_feedback_item

ROOT = Path('/home/ubuntu/.openclaw/workspace')
CODING_DIR = ROOT / 'departments' / 'coding'
KANBAN_DIR = CODING_DIR / 'kanban'
STATUS_FILE = CODING_DIR / 'STATUS.md'
ACTIVITY_LOG = ROOT / 'logs' / 'coding-activity.log'
STATE_FILE = ROOT / 'memory' / 'coding-autopilot-state.json'
PRIORITY_FILE = ROOT / 'memory' / 'coding-priority.json'
ART_DIR = CODING_DIR / 'artifacts'


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {'runs': 0, 'cursor': 0, 'progress': {}}
    try:
        state = json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {'runs': 0, 'cursor': 0, 'progress': {}}
    if 'runs' not in state:
        state['runs'] = 0
    if 'cursor' not in state:
        state['cursor'] = 0
    if 'progress' not in state or not isinstance(state['progress'], dict):
        state['progress'] = {}
    return state


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def load_priority() -> dict | None:
    if not PRIORITY_FILE.exists():
        return None
    try:
        data = json.loads(PRIORITY_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    title = data.get('title')
    boosts = data.get('boosts_remaining')
    if not isinstance(title, str) or not title.strip():
        return None
    if not isinstance(boosts, int) or boosts < 1:
        return None
    return data


def save_priority(data: dict | None) -> None:
    if not data:
        if PRIORITY_FILE.exists():
            PRIORITY_FILE.unlink()
        return
    PRIORITY_FILE.parent.mkdir(parents=True, exist_ok=True)
    PRIORITY_FILE.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def parse_ready_cards(board_text: str) -> list[dict[str, str]]:
    m = re.search(r'^## Ready\n([\s\S]*?)(?=^## |\Z)', board_text, flags=re.M)
    if not m:
        return []
    block = m.group(1)
    cards: list[dict[str, str]] = []
    title = ''
    branch = ''
    tests = ''
    for raw in block.splitlines():
        line = raw.strip()
        if line.startswith('- [ ]'):
            title = re.sub(r'^- \[ \]\s*', '', line).strip()
            branch = ''
            tests = ''
        elif line.startswith('- branch:'):
            branch = line.split(':', 1)[1].strip().strip('`')
        elif line.startswith('- tests:'):
            tests = line.split(':', 1)[1].strip()
            if title:
                cards.append({'title': title, 'branch': branch, 'tests': tests})
                title = ''
                branch = ''
                tests = ''
    return cards


def gather_ready() -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    if not KANBAN_DIR.exists():
        return cards
    for p in sorted(KANBAN_DIR.glob('*.md')):
        if p.name == 'README.md':
            continue
        txt = p.read_text(encoding='utf-8')
        for c in parse_ready_cards(txt):
            c['board'] = str(p.relative_to(ROOT))
            cards.append(c)
    return cards


def choose_card(ready: list[dict[str, str]], state: dict) -> tuple[dict[str, str] | None, dict | None]:
    if not ready:
        return None, None
    priority = load_priority()
    if priority:
        wanted = str(priority.get('title', ''))
        for c in ready:
            if c.get('title') == wanted:
                return c, priority
    idx = int(state.get('cursor', 0)) % len(ready)
    return ready[idx], None


def write_artifact(run: int, card: dict[str, str]) -> Path:
    ts = dt.datetime.now(dt.UTC).replace(microsecond=0)
    slug = re.sub(r'[^a-z0-9]+', '-', card['title'].lower()).strip('-')[:48] or 'coding-task'
    rel = Path('briefs') / f"{ts:%Y%m%dT%H%M%SZ}-r{run}-{slug}.md"
    out = ART_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    content = [
        f"# Coding Execution Brief (Run {run})",
        '',
        f"- UTC: {ts.isoformat().replace('+00:00','Z')}",
        f"- Board: {card.get('board','n/a')}",
        f"- Task: {card.get('title','n/a')}",
        f"- Branch: `{card.get('branch','') or 'TBD'}`",
        f"- Tests: {card.get('tests','n/a')}",
        '',
        '## Concrete Next Step',
        '1. Create/switch to branch listed above.',
        '2. Implement one atomic code change.',
        '3. Run the listed tests and capture exact output.',
        '4. Update kanban card with test evidence.',
        '',
    ]
    out.write_text('\n'.join(content), encoding='utf-8')
    return out


def write_feedback_artifact(run: int, item: dict[str, object]) -> Path:
    ts = dt.datetime.now(dt.UTC).replace(microsecond=0)
    slug = re.sub(r'[^a-z0-9]+', '-', str(item.get('branch', '')).lower()).strip('-')[:48] or 'feedback-task'
    rel = Path('feedback') / f"{ts:%Y%m%dT%H%M%SZ}-r{run}-{slug}.md"
    out = ART_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    status = str(item.get('status', 'coding_needed'))
    if status == 'merge_ready':
        next_steps = [
            '1. Review the branch diff against main.',
            '2. Re-run the recorded tests on the branch.',
            '3. Merge only if the rerun stays green and the diff still matches the card.',
            '4. Delete the merged feature branch and move the card to Done.',
        ]
    elif status == 'review_needed':
        next_steps = [
            '1. Review the branch diff and the linked card evidence.',
            '2. Resolve the blocker called out below.',
            '3. Re-check merge readiness after evidence or rebasing is updated.',
        ]
    else:
        next_steps = [
            '1. Switch to the branch listed below.',
            '2. Finish the missing implementation, tests, or card linkage.',
            '3. Push the updated branch and move it to Review when evidence exists.',
        ]
    content = [
        f"# Coding Feedback Brief (Run {run})",
        '',
        f"- UTC: {ts.isoformat().replace('+00:00','Z')}",
        f"- Repo: {item.get('repo', 'n/a')}",
        f"- Branch: `{item.get('branch', 'n/a')}`",
        f"- Owner: {item.get('owner', 'n/a')}",
        f"- Status: {status}",
        f"- Lane: {item.get('lane', 'Untracked')}",
        f"- Card: {item.get('title', '') or 'Untracked branch'}",
        f"- Board: {item.get('board', 'n/a') or 'n/a'}",
        f"- Ahead of main: {item.get('ahead_of_main', 0)}",
        f"- Behind main: {item.get('behind_main', 0)}",
        f"- Remote branch: {'yes' if item.get('remote_exists') else 'no'}",
        f"- Merge conflicts: {'yes' if item.get('merge_conflicts') else 'no'}",
        f"- Reason: {item.get('reason', 'n/a')}",
        '',
        '## Concrete Next Step',
        *next_steps,
        '',
    ]
    out.write_text('\n'.join(content), encoding='utf-8')
    return out


def append_activity(line: str) -> None:
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
    with ACTIVITY_LOG.open('a', encoding='utf-8') as f:
        f.write(f'[{now}] {line}\n')


def clean_text(value: str) -> str:
    txt = re.sub(r'[`*_]+', '', value or '')
    return re.sub(r'\s+', ' ', txt).strip()


def build_status(
    state: dict,
    card: dict[str, str] | None,
    artifact: Path | None,
    total_ready: int,
    feedback_summary: dict[str, int] | None = None,
    active_mode: str = 'coding_card',
) -> tuple[str, str]:
    now = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    title = clean_text(card['title']) if card else 'No ready coding card'
    board = clean_text(card.get('board', 'n/a')) if card else 'n/a'
    progress = state.get('progress', {})
    raw_title = card['title'] if card else ''
    count = int(progress.get(raw_title, 0)) if card else 0
    art_rel = str(artifact.relative_to(ROOT)) if artifact else 'none'
    md = [
        '# Coding Status',
        '',
        f'- Last run (UTC): {now}',
        f"- Run count: {state.get('runs',0)}",
        f'- Ready cards: {total_ready}',
        f'- Active card: {title}',
        f'- Active mode: {active_mode}',
        f'- Board: {board}',
        f'- Progress count (card): {count}',
        f'- Last artifact: {art_rel}',
    ]
    if feedback_summary:
        md.append(f"- Feedback loop: {build_snapshot(feedback_summary)}")
    md.append('')
    tg = [
        '[CODING UPDATE]',
        f'Time (UTC): {now}',
        f'Run: {state.get("runs",0)}',
        f'Card: {title}',
        f'Mode: {active_mode}',
        f'Board: {board}',
        f'Progress: {count}',
        f'Ready Queue: {total_ready}',
        f'Artifact: {art_rel}',
    ]
    if feedback_summary:
        tg.append(
            "Feedback: "
            f"unmerged={feedback_summary['unmerged_total']} "
            f"merge_ready={feedback_summary['merge_ready']} "
            f"review_needed={feedback_summary['review_needed']} "
            f"coding_needed={feedback_summary['coding_needed']}"
        )
    return '\n'.join(md) + '\n', '\n'.join(tg)


def main() -> int:
    parser = argparse.ArgumentParser(description='Coding autopilot')
    parser.add_argument('--emit-telegram', action='store_true')
    args = parser.parse_args()

    ready = gather_ready()
    feedback_items, feedback_summary = audit_feedback_loop()
    feedback_item = choose_feedback_item(feedback_items)
    state = load_state()
    state['runs'] = int(state.get('runs', 0)) + 1
    card = None
    artifact = None
    active_mode = 'coding_card'

    if feedback_item:
        card = {
            'title': str(feedback_item.get('title') or feedback_item.get('branch') or 'Feedback loop task'),
            'board': str(feedback_item.get('board') or feedback_item.get('repo') or 'n/a'),
        }
        artifact = write_feedback_artifact(state['runs'], feedback_item)
        progress = state.setdefault('progress', {})
        progress[card['title']] = int(progress.get(card['title'], 0)) + 1
        active_mode = str(feedback_item.get('status', 'coding_needed'))
        append_activity(
            f"run={state['runs']} feedback_branch='{feedback_item.get('branch','')}' "
            f"repo='{feedback_item.get('repo','')}' status='{feedback_item.get('status','')}' "
            f"artifact='{artifact.relative_to(ROOT)}' ready={len(ready)}"
        )
    elif ready:
        card, used_priority = choose_card(ready, state)
        if card is None:
            append_activity(f"run={state['runs']} card='none' ready=0")
            status_text, telegram_text = build_status(
                state,
                None,
                None,
                len(ready),
                feedback_summary=feedback_summary,
                active_mode='idle',
            )
            STATUS_FILE.write_text(status_text, encoding='utf-8')
            save_state(state)
            if args.emit_telegram:
                print(telegram_text)
            else:
                print(status_text)
            return 0
        if used_priority:
            used_priority['boosts_remaining'] = int(used_priority.get('boosts_remaining', 1)) - 1
            if used_priority['boosts_remaining'] <= 0:
                save_priority(None)
            else:
                save_priority(used_priority)
        else:
            idx = int(state.get('cursor', 0)) % len(ready)
            state['cursor'] = idx + 1
        artifact = write_artifact(state['runs'], card)
        progress = state.setdefault('progress', {})
        progress[card['title']] = int(progress.get(card['title'], 0)) + 1
        src = 'priority' if used_priority else 'round_robin'
        append_activity(
            f"run={state['runs']} card='{card['title']}' board='{card.get('board','')}' "
            f"artifact='{artifact.relative_to(ROOT)}' ready={len(ready)} source={src}"
        )
    else:
        append_activity(f"run={state['runs']} card='none' ready=0")

    status_text, telegram_text = build_status(
        state,
        card,
        artifact,
        len(ready),
        feedback_summary=feedback_summary,
        active_mode=active_mode,
    )
    STATUS_FILE.write_text(status_text, encoding='utf-8')
    save_state(state)

    if args.emit_telegram:
        print(telegram_text)
    else:
        print(status_text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
