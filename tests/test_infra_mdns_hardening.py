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
    def test_validate_stage_dir_rejects_live_dropin_directory(self) -> None:
        with self.assertRaisesRegex(ValueError, "--stage-dir must not point at the live resolved drop-in directory"):
            infra_mdns_hardening.validate_stage_dir(infra_mdns_hardening.LIVE_MDNS_DROPIN.parent)

    def test_validate_install_target_requires_explicit_live_opt_in(self) -> None:
        with self.assertRaisesRegex(ValueError, "--install-to matches the live resolved drop-in path"):
            infra_mdns_hardening.validate_install_target(
                infra_mdns_hardening.LIVE_MDNS_DROPIN,
                allow_live_install=False,
            )

    def test_validate_install_target_allows_live_path_with_opt_in(self) -> None:
        infra_mdns_hardening.validate_install_target(
            infra_mdns_hardening.LIVE_MDNS_DROPIN,
            allow_live_install=True,
        )

    def test_stage_dir_stages_dropin_and_auto_uses_it_for_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stage_dir = root / "stage"
            nsswitch = root / "nsswitch.conf"
            resolved_conf = root / "resolved.conf"
            nsswitch.write_text("hosts: files dns\n", encoding="utf-8")
            resolved_conf.write_text("", encoding="utf-8")

            stdout = io.StringIO()
            argv = [
                "infra_mdns_hardening.py",
                "--stage-dir",
                str(stage_dir),
                "--validate-live",
                "--resolved-conf",
                str(resolved_conf),
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

            staged = stage_dir / "99-openclaw-no-mdns.conf"
            self.assertEqual(rc, 0)
            self.assertTrue(staged.exists())
            self.assertEqual(staged.read_text(encoding="utf-8"), MDNS_RESOLVED_DROPIN)
            self.assertEqual(staged.stat().st_mode & 0o777, 0o644)
            output = stdout.getvalue()
            self.assertIn(f"STAGED_DROPIN {staged}", output)
            self.assertNotIn(f"live drop-in installed: {staged} (mode 0644)", output)
            self.assertIn("Validation target: staged", output)
            self.assertIn(f"staged drop-in installed: {staged} (mode 0644)", output)
            self.assertIn("STAGED_VALIDATION_DONE", output)
            self.assertNotIn("\nLIVE_VALIDATION_DONE\n", output)

    def test_allow_live_install_requires_install_to(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        argv = [
            "infra_mdns_hardening.py",
            "--allow-live-install",
        ]

        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = infra_mdns_hardening.main()

        self.assertEqual(rc, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("ERROR: --allow-live-install requires --install-to", stderr.getvalue())

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
            self.assertNotIn(f"live drop-in installed: {live} (mode 0644)", output)
            self.assertIn("Validation target: staged", output)
            self.assertIn(f"staged drop-in installed: {live} (mode 0644)", output)
            self.assertIn("STAGED_VALIDATION_DONE", output)
            self.assertNotIn("\nLIVE_VALIDATION_DONE\n", output)

    def test_install_to_live_path_is_blocked_without_allow_live_install(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        argv = [
            "infra_mdns_hardening.py",
            "--install-to",
            str(infra_mdns_hardening.LIVE_MDNS_DROPIN),
        ]

        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = infra_mdns_hardening.main()

        self.assertEqual(rc, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("--install-to matches the live resolved drop-in path", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
