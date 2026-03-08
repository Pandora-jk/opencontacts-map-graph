import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

from infra_network import (
    MDNS_RESOLVED_DROPIN,
    inspect_mdns_exposure,
    live_mdns_dropin_status,
    managed_mdns_dropin_status,
)


class InfraNetworkTests(unittest.TestCase):
    def test_dropin_status_reports_ready_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dropin = Path(temp_dir) / "99-openclaw-no-mdns.conf"
            dropin.write_text(MDNS_RESOLVED_DROPIN, encoding="utf-8")
            dropin.chmod(0o644)

            self.assertEqual(
                managed_mdns_dropin_status(dropin),
                f"managed drop-in ready: {dropin} (mode 0644)",
            )
            self.assertEqual(
                live_mdns_dropin_status(dropin),
                f"live drop-in installed: {dropin} (mode 0644)",
            )

    def test_dropin_status_flags_permission_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dropin = Path(temp_dir) / "99-openclaw-no-mdns.conf"
            dropin.write_text(MDNS_RESOLVED_DROPIN, encoding="utf-8")
            dropin.chmod(0o666)

            status = managed_mdns_dropin_status(dropin)

            self.assertIn("WARN: managed drop-in permissions are 0666", status)
            self.assertIn(str(dropin), status)

    def test_mdns_exposure_uses_override_paths_in_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            managed = root / "managed.conf"
            live = root / "resolved.conf.d" / "99-openclaw-no-mdns.conf"
            resolved_conf = root / "resolved.conf"
            nsswitch = root / "nsswitch.conf"

            managed.write_text(MDNS_RESOLVED_DROPIN, encoding="utf-8")
            managed.chmod(0o644)
            live.parent.mkdir(parents=True, exist_ok=True)
            live.write_text(MDNS_RESOLVED_DROPIN, encoding="utf-8")
            live.chmod(0o644)
            resolved_conf.write_text("", encoding="utf-8")
            nsswitch.write_text("hosts: files dns\n", encoding="utf-8")

            with mock.patch("infra_network.run_cmd", return_value="UNCONN 0 0 0.0.0.0:5353 0.0.0.0:*"), mock.patch(
                "infra_network._service_state", return_value=None
            ):
                result = inspect_mdns_exposure(
                    "udp 0.0.0.0:5353",
                    managed_dropin=managed,
                    live_dropin=live,
                    resolved_conf=resolved_conf,
                    resolved_dropins_dir=live.parent,
                    nsswitch_path=nsswitch,
                )

            self.assertIn(f"managed drop-in ready: {managed} (mode 0644)", result)
            self.assertIn(f"live drop-in installed: {live} (mode 0644)", result)
            self.assertIn(
                "HARDENING: stage/test the install outside /etc with `python3 tools/infra_mdns_hardening.py --stage-dir /tmp/openclaw-mdns-stage --validate-live`",
                result,
            )
            self.assertIn(
                "HARDENING: only install to /etc after the staged validation reports the staged drop-in installed and STAGED_VALIDATION_DONE",
                result,
            )
            self.assertIn(
                "HARDENING: restart resolved and verify with `sudo systemctl restart systemd-resolved && python3 tools/infra_mdns_hardening.py --validate-live` (expect LIVE_VALIDATION_DONE)",
                result,
            )


if __name__ == "__main__":
    unittest.main()
