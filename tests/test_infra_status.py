import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra-status.py")
SPEC = importlib.util.spec_from_file_location("infra_status", MODULE_PATH)
infra_status = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(infra_status)


class InfraStatusTests(unittest.TestCase):
    def test_check_open_ports_uses_supplied_raw_port_lines(self) -> None:
        result = infra_status.check_open_ports("udp 0.0.0.0:5353\nudp 127.0.0.1:323")

        self.assertIn("ALERT: Unexpected externally exposed listeners (1): udp/5353", result)

    def test_generate_report_uses_raw_port_lines_for_mdns_detection(self) -> None:
        with mock.patch.object(infra_status, "current_port_lines", return_value="udp 0.0.0.0:5353"), mock.patch.object(
            infra_status, "check_system_updates", return_value="No pending updates"
        ), mock.patch.object(
            infra_status, "check_disk_usage", return_value="Disk usage nominal"
        ), mock.patch.object(
            infra_status, "check_firewall_status", return_value="Firewall nominal"
        ), mock.patch.object(
            infra_status, "check_ssh_config", return_value="SSH nominal"
        ), mock.patch.object(
            infra_status, "check_failed_logins", return_value="No failed authentication attempts found in sampled logs"
        ), mock.patch.object(
            infra_status, "check_backup_integrity", return_value="Backup nominal"
        ), mock.patch.object(
            infra_status, "check_service_health", return_value="service-manager: unavailable"
        ), mock.patch.object(
            infra_status, "run_cmd", return_value="UNCONN 0 0 0.0.0.0:5353 0.0.0.0:*"
        ), mock.patch(
            "infra_network._service_state", return_value=None
        ):
            md_content, summary_lines = infra_status.generate_report()

        self.assertIn("## Multicast DNS Exposure", md_content)
        self.assertIn("ALERT: External mDNS listener detected on udp/5353", md_content)
        self.assertTrue(
            any("mDNS: ALERT: External mDNS listener detected on udp/5353" in line for line in summary_lines)
        )


if __name__ == "__main__":
    unittest.main()
