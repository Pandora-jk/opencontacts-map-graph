import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

import infra_mdns_hardening
from infra_network import MDNS_RESOLVED_DROPIN


class InfraMdnsHardeningTests(unittest.TestCase):
    def test_install_to_stages_managed_dropin_and_validates_override_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            live = root / "resolved.conf.d" / "99-openclaw-no-mdns.conf"
            nsswitch = root / "nsswitch.conf"
            resolved_conf = root / "resolved.conf"
            nsswitch.write_text("hosts: files dns\n", encoding="utf-8")
            resolved_conf.write_text("", encoding="utf-8")

            stdout = io.StringIO()
            argv = [
                "infra_mdns_hardening.py",
                "--install-to",
                str(live),
                "--validate-live",
                "--live-dropin-path",
                str(live),
                "--resolved-conf",
                str(resolved_conf),
                "--resolved-dropins-dir",
                str(live.parent),
                "--nsswitch-path",
                str(nsswitch),
            ]

            with mock.patch.object(sys, "argv", argv), mock.patch.object(
                infra_mdns_hardening, "current_port_lines", return_value="udp 0.0.0.0:5353"
            ), mock.patch.object(
                infra_mdns_hardening,
                "run_cmd",
                return_value="UNCONN 0 0 0.0.0.0:5353 0.0.0.0:*",
            ), contextlib.redirect_stdout(stdout):
                rc = infra_mdns_hardening.main()

            self.assertEqual(rc, 0)
            self.assertTrue(live.exists())
            self.assertEqual(live.read_text(encoding="utf-8"), MDNS_RESOLVED_DROPIN)
            self.assertEqual(live.stat().st_mode & 0o777, 0o644)
            output = stdout.getvalue()
            self.assertIn(f"INSTALLED_DROPIN {live}", output)
            self.assertIn(f"live drop-in installed: {live} (mode 0644)", output)
            self.assertIn("LIVE_VALIDATION_DONE", output)


if __name__ == "__main__":
    unittest.main()
