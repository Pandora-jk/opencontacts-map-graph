import datetime as dt
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/proactive-pulse.py")
SPEC = importlib.util.spec_from_file_location("proactive_pulse", MODULE_PATH)
proactive_pulse = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(proactive_pulse)


class ProactivePulseTests(unittest.TestCase):
    def test_current_digest_slot_recognizes_morning_and_evening_sydney_windows(self) -> None:
        morning = dt.datetime(2026, 3, 13, 8, 20, tzinfo=proactive_pulse.SYDNEY_TZ)
        evening = dt.datetime(2026, 3, 13, 18, 20, tzinfo=proactive_pulse.SYDNEY_TZ)
        midday = dt.datetime(2026, 3, 13, 13, 20, tzinfo=proactive_pulse.SYDNEY_TZ)

        self.assertEqual("morning", proactive_pulse.current_digest_slot(morning)["name"])
        self.assertEqual("evening", proactive_pulse.current_digest_slot(evening)["name"])
        self.assertIsNone(proactive_pulse.current_digest_slot(midday))

    def test_extract_memory_sections_returns_titles_and_summaries(self) -> None:
        text = """# 2026-03-13

## First Event
- Did the first thing

## Second Event
Plain summary line
"""

        result = proactive_pulse.extract_memory_sections(text)

        self.assertEqual(
            [("First Event", "Did the first thing"), ("Second Event", "Plain summary line")],
            result,
        )

    def test_select_digest_items_prefers_recent_activity_and_human_todo(self) -> None:
        candidates = [
            {
                "kind": "cron_failure",
                "priority": 100,
                "headline": "Automation issue: Finance Status Push failing",
                "human_action": False,
            },
            {
                "kind": "recent_activity",
                "priority": 70,
                "headline": "Infra auto-update reconciliation finished",
                "human_action": False,
                "fingerprint": "memory:Infra auto-update reconciliation finished",
            },
            {
                "kind": "browser_review",
                "priority": 20,
                "headline": "Browser control is still enabled for main",
                "todo": "decide whether to keep browser control enabled",
                "human_action": True,
            },
        ]

        result = proactive_pulse.select_digest_items(candidates)

        self.assertEqual(["browser_review", "recent_activity"], [item["kind"] for item in result])

    def test_select_digest_items_skips_previously_sent_human_todo(self) -> None:
        candidates = [
            {
                "kind": "recent_activity",
                "priority": 70,
                "headline": "Infra auto-update reconciliation finished",
                "human_action": False,
                "fingerprint": "memory:Infra auto-update reconciliation finished",
            },
            {
                "kind": "browser_review",
                "priority": 20,
                "headline": "Browser control is still enabled for main",
                "todo": "decide whether to keep browser control enabled",
                "human_action": True,
                "fingerprint": "security:browser-enabled",
            },
        ]

        result = proactive_pulse.select_digest_items(
            candidates,
            {"last_human_fingerprints": ["security:browser-enabled"]},
        )

        self.assertEqual(["recent_activity"], [item["kind"] for item in result])

    def test_build_digest_message_marks_human_todo_as_important(self) -> None:
        slot = {"name": "evening", "label": "Evening update"}
        candidates = [
            {
                "kind": "browser_review",
                "priority": 20,
                "headline": "Browser control is still enabled for main",
                "todo": "decide whether to keep browser control enabled",
                "human_action": True,
            },
            {
                "kind": "recent_activity",
                "priority": 70,
                "headline": "Infra auto-update reconciliation finished",
                "human_action": False,
                "fingerprint": "memory:Infra auto-update reconciliation finished",
            },
        ]

        result = proactive_pulse.build_digest_message(candidates, slot)

        self.assertIn("IMPORTANT: Evening update", result)
        self.assertIn("TODO: decide whether to keep browser control enabled.", result)
        self.assertIn("Infra auto-update reconciliation finished.", result)

    def test_build_digest_message_returns_no_reply_when_there_are_no_material_issues(self) -> None:
        slot = {"name": "morning", "label": "Morning update"}

        result = proactive_pulse.build_digest_message([], slot)

        self.assertEqual("NO_REPLY", result)

    def test_select_immediate_decision_returns_new_human_action(self) -> None:
        candidates = [
            {
                "kind": "recent_activity",
                "priority": 70,
                "headline": "Infra auto-update reconciliation finished",
                "human_action": False,
                "fingerprint": "memory:Infra auto-update reconciliation finished",
            },
            {
                "kind": "browser_review",
                "priority": 20,
                "headline": "Browser control is still enabled for main",
                "todo": "decide whether to keep browser control enabled",
                "human_action": True,
                "fingerprint": "security:browser-enabled",
            },
        ]

        result = proactive_pulse.select_immediate_decision(candidates, {})

        self.assertEqual("security:browser-enabled", result["fingerprint"])

    def test_build_immediate_decision_message_formats_important_todo(self) -> None:
        candidate = {
            "kind": "browser_review",
            "priority": 20,
            "headline": "Browser control is still enabled for main",
            "todo": "decide whether to keep browser control enabled",
            "human_action": True,
            "fingerprint": "security:browser-enabled",
        }

        result = proactive_pulse.build_immediate_decision_message(candidate)

        self.assertIn("IMPORTANT: Decision needed", result)
        self.assertIn("TODO: decide whether to keep browser control enabled.", result)
        self.assertIn("Browser control is still enabled for main.", result)

    def test_already_sent_for_slot_uses_slot_key(self) -> None:
        state = {"last_slot_key": "2026-03-13:morning"}

        self.assertTrue(proactive_pulse.already_sent_for_slot(state, "2026-03-13:morning"))
        self.assertFalse(proactive_pulse.already_sent_for_slot(state, "2026-03-13:evening"))


if __name__ == "__main__":
    unittest.main()
