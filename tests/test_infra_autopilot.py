import datetime as dt
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra-autopilot.py")
SPEC = importlib.util.spec_from_file_location("infra_autopilot", MODULE_PATH)
infra_autopilot = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(infra_autopilot)


class InfraAutopilotTests(unittest.TestCase):
    def test_score_task_from_status_ignores_stale_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "20260310T153953Z-infra-status.md"
            artifact.write_text("CRITICAL: Root filesystem usage is 100%", encoding="utf-8")
            stale_now = dt.datetime(2026, 3, 11, 11, 30, tzinfo=dt.timezone.utc)
            stale_mtime = (stale_now - dt.timedelta(hours=20)).timestamp()
            artifact.touch()
            Path(artifact).chmod(0o600)
            os.utime(artifact, (stale_mtime, stale_mtime))

            score, reason = infra_autopilot.score_task_from_status(
                "Monitor disk usage: Alert if >80%.",
                artifact,
            )

        self.assertEqual(score, 0)
        self.assertIn("is stale", reason)

    def test_select_task_prefers_non_stale_security_risk_over_stale_disk_status(self) -> None:
        tasks = [
            "Run security audit: Check for open ports, SSH config, failed logins.",
            "Monitor disk usage: Alert if >80%.",
        ]
        state = {"cursor": 0}
        stale_status = Path("/tmp/stale-status.md")

        with mock.patch.object(
            infra_autopilot,
            "latest_status_artifact",
            return_value=stale_status,
        ), mock.patch.object(
            infra_autopilot,
            "latest_artifact_for_task",
            side_effect=lambda task: Path("/tmp/security.md") if "security audit" in task else Path("/tmp/disk.md"),
        ), mock.patch.object(
            infra_autopilot,
            "score_task_from_status",
            side_effect=lambda task, artifact: (0, "stale status") if artifact == stale_status else (0, "no status"),
        ), mock.patch.object(
            infra_autopilot,
            "score_task_from_artifact",
            side_effect=lambda task, artifact: (85, "unexpected udp/5353 listener still exposed")
            if "security audit" in task
            else (0, "latest artifact has no active risk markers"),
        ):
            task, reason = infra_autopilot.select_task(tasks, state)

        self.assertEqual(tasks[0], task)
        self.assertEqual("risk-based priority: unexpected udp/5353 listener still exposed", reason)


if __name__ == "__main__":
    unittest.main()
