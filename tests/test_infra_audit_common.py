import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

COMMON_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra_audit_common.py")
COMMON_SPEC = importlib.util.spec_from_file_location("infra_audit_common", COMMON_PATH)
infra_audit_common = importlib.util.module_from_spec(COMMON_SPEC)
assert COMMON_SPEC.loader is not None
COMMON_SPEC.loader.exec_module(infra_audit_common)

STATUS_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra-status.py")
STATUS_SPEC = importlib.util.spec_from_file_location("infra_status", STATUS_PATH)
infra_status = importlib.util.module_from_spec(STATUS_SPEC)
assert STATUS_SPEC.loader is not None
STATUS_SPEC.loader.exec_module(infra_status)

AUTOPILOT_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra-autopilot.py")
AUTOPILOT_SPEC = importlib.util.spec_from_file_location("infra_autopilot", AUTOPILOT_PATH)
infra_autopilot = importlib.util.module_from_spec(AUTOPILOT_SPEC)
assert AUTOPILOT_SPEC.loader is not None
AUTOPILOT_SPEC.loader.exec_module(infra_autopilot)


class InfraAuditCommonTests(unittest.TestCase):
    def test_auth_log_tail_commands_use_shared_limit(self) -> None:
        self.assertEqual(400, infra_audit_common.AUTH_LOG_SAMPLE_LIMIT)
        self.assertEqual(12000, infra_audit_common.AUTH_LOG_SAMPLE_MAX_CHARS)
        self.assertEqual(
            ['bash', '-lc', 'tail -n 400 /var/log/auth.log 2>/dev/null'],
            infra_audit_common.auth_log_tail_command(),
        )
        self.assertEqual(
            ['bash', '-lc', "journalctl -u ssh --since '24 hours ago' --no-pager 2>/dev/null | tail -n 400"],
            infra_audit_common.journalctl_ssh_tail_command(),
        )

    def test_status_and_autopilot_share_auth_log_sampling_limit(self) -> None:
        self.assertEqual(infra_audit_common.AUTH_LOG_SAMPLE_LIMIT, infra_status.AUTH_LOG_SAMPLE_LIMIT)
        self.assertEqual(infra_audit_common.AUTH_LOG_SAMPLE_MAX_CHARS, infra_status.AUTH_LOG_SAMPLE_MAX_CHARS)
        self.assertEqual(infra_audit_common.AUTH_LOG_SAMPLE_LIMIT, infra_autopilot.AUTH_LOG_SAMPLE_LIMIT)
        self.assertEqual(infra_audit_common.AUTH_LOG_SAMPLE_MAX_CHARS, infra_autopilot.AUTH_LOG_SAMPLE_MAX_CHARS)
        self.assertEqual(infra_status.auth_log_tail_command(), infra_autopilot.auth_log_tail_command())
        self.assertEqual(infra_status.journalctl_ssh_tail_command(), infra_autopilot.journalctl_ssh_tail_command())


if __name__ == "__main__":
    unittest.main()
