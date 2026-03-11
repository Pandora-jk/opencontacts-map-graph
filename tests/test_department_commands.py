import importlib.util
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


if __name__ == "__main__":
    unittest.main()
