from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from characterlab.capture import _capture_command, capture_local_ui
from characterlab.evidence import EXPECTED_SCREENSHOTS, PNG_SIGNATURE, evidence_directory


class LocalCaptureTests(unittest.TestCase):
    def test_command_uses_loopback_headless_chrome_and_explicit_output(self):
        command = _capture_command(
            Path("C:/Chrome/chrome.exe"),
            "http://127.0.0.1:1234/?scenario=blocked_first_attempt",
            Path("C:/captures/blocked_first_attempt.png"),
            Path("C:/temporary/profile"),
        )

        self.assertIn("--headless=new", command)
        self.assertIn("--disable-background-networking", command)
        self.assertIn("--window-size=1440,3200", command)
        self.assertIn(f"--screenshot={Path('C:/captures/blocked_first_attempt.png')}", command)
        self.assertEqual(command[-1], "http://127.0.0.1:1234/?scenario=blocked_first_attempt")

    def test_capture_refuses_to_overwrite_existing_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            directory = evidence_directory(root)
            directory.mkdir(parents=True)
            (directory / EXPECTED_SCREENSHOTS[0]).write_bytes(PNG_SIGNATURE)

            with self.assertRaises(FileExistsError):
                capture_local_ui(root, Path("C:/Chrome/chrome.exe"))

    def test_capture_promotes_only_verified_staged_pngs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            def fake_run(command, **_kwargs):
                output_argument = next(item for item in command if item.startswith("--screenshot="))
                Path(output_argument.removeprefix("--screenshot=")).write_bytes(PNG_SIGNATURE + b"rendered")

                class Result:
                    returncode = 0
                    stderr = ""

                return Result()

            with patch("characterlab.capture.subprocess.run", side_effect=fake_run):
                result = capture_local_ui(root, Path("C:/Chrome/chrome.exe"))

            self.assertEqual(result["captured_files"], list(EXPECTED_SCREENSHOTS))
            self.assertTrue(result["evidence"]["complete"])
            self.assertEqual(
                sorted(path.name for path in evidence_directory(root).glob("*.png")),
                sorted(EXPECTED_SCREENSHOTS),
            )
