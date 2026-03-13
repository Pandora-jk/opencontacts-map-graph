import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/department-commands.py")
SPEC = importlib.util.spec_from_file_location("department_commands", MODULE_PATH)
department_commands = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(department_commands)


class DepartmentCommandsTests(unittest.TestCase):
    def test_run_department_infra_refreshes_status_before_autopilot(self) -> None:
        calls: list[str] = []

        def fake_run_script(script_name: str, *, emit_telegram: bool = True) -> str:
            calls.append(f"{script_name}:{emit_telegram}")
            if script_name == "infra-status.py":
                return "[INFRA FINDINGS]\nRisk: none detected by current checks"
            if script_name == "infra-autopilot.py":
                return "[INFRA UPDATE]\nTask: Monitor disk usage: Alert if >80%."
            raise AssertionError(f"unexpected script {script_name}")

        with mock.patch.object(department_commands, "run_script", side_effect=fake_run_script):
            output = department_commands.run_department("infra")

        self.assertEqual(["infra-status.py:False", "infra-autopilot.py:True"], calls)
        self.assertIn("[INFRA UPDATE]", output)

    def test_run_department_infra_reports_status_refresh_failure(self) -> None:
        def fake_run_script(script_name: str, *, emit_telegram: bool = True) -> str:
            if script_name == "infra-status.py":
                return "infra-status.py: run failed (1) permission denied"
            if script_name == "infra-autopilot.py":
                return "[INFRA UPDATE]\nTask: Run security audit: Check for open ports, SSH config, failed logins."
            raise AssertionError(f"unexpected script {script_name}")

        with mock.patch.object(department_commands, "run_script", side_effect=fake_run_script):
            output = department_commands.run_department("infra")

        self.assertIn("[INFRA UPDATE]", output)
        self.assertIn("Status refresh:", output)

    def test_add_reminder_uses_isolated_telegram_cron_job(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                '{"job":{"id":"abc123","createdAtMs":1773397800000,'
                '"schedule":{"kind":"at","at":"2026-03-13T10:40:00.000Z"}}}'
            ),
            stderr="",
        )

        with (
            mock.patch.object(department_commands, "run_cli", return_value=completed) as run_cli,
            mock.patch.object(department_commands, "default_telegram_target", return_value="156480904"),
        ):
            output = department_commands.add_reminder("10m", "Brush your teeth")

        run_cli.assert_called_once_with(
            [
                "openclaw",
                "cron",
                "add",
                "--name",
                "Reminder: Brush your teeth",
                "--at",
                "10m",
                "--session",
                "isolated",
                "--message",
                "Return exactly: Reminder: Brush your teeth",
                "--announce",
                "--channel",
                "telegram",
                "--to",
                "156480904",
                "--model",
                "nvidia/qwen/qwen3.5-397b-a17b",
                "--delete-after-run",
                "--json",
            ]
        )
        self.assertIn("reminder created: id=abc123", output)
        self.assertIn("scheduled=10m", output)
        self.assertIn("next_run=2026-03-13T10:40:00.000Z", output)

    def test_reminder_matches_only_isolated_telegram_at_jobs(self) -> None:
        matching_job = {
            "id": "abc123",
            "name": "Reminder: Brush your teeth",
            "sessionTarget": "isolated",
            "schedule": {"kind": "at", "at": "2026-03-13T10:40:00.000Z"},
            "payload": {"kind": "agentTurn", "message": "Return exactly: Reminder: Brush your teeth"},
            "delivery": {"mode": "announce", "channel": "telegram", "to": "156480904"},
        }
        non_matching_job = {
            "id": "def456",
            "name": "Coding Day Loop",
            "sessionTarget": "isolated",
            "schedule": {"kind": "cron", "expr": "*/10 * * * *"},
            "payload": {"kind": "agentTurn", "message": "Run coding"},
            "delivery": {"mode": "none", "channel": "last"},
        }

        self.assertTrue(department_commands.reminder_matches(matching_job))
        self.assertFalse(department_commands.reminder_matches(non_matching_job))

    def test_format_reminder_list_shows_text_and_schedule(self) -> None:
        output = department_commands.format_reminder_list(
            [
                {
                    "id": "abc123",
                    "name": "Reminder: Brush your teeth",
                    "sessionTarget": "isolated",
                    "schedule": {"kind": "at", "at": "2026-03-13T10:40:00.000Z"},
                    "payload": {"kind": "agentTurn", "message": "Return exactly: Reminder: Brush your teeth"},
                    "delivery": {"mode": "announce", "channel": "telegram", "to": "156480904"},
                }
            ]
        )

        self.assertIn("id=abc123", output)
        self.assertIn("scheduled=2026-03-13T10:40:00.000Z", output)
        self.assertIn("text=Brush your teeth", output)


if __name__ == "__main__":
    unittest.main()
