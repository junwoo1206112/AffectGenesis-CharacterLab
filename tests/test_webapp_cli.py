import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.request import urlopen


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class WebappCliTests(unittest.TestCase):
    def test_ephemeral_port_output_matches_a_live_health_endpoint(self):
        process = subprocess.Popen(
            [sys.executable, "-u", "-m", "characterlab.webapp", "--port", "0"],
            cwd=REPOSITORY_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            assert process.stdout is not None
            line = process.stdout.readline().strip()
            matched = re.fullmatch(r"CharacterLab: http://127\.0\.0\.1:(\d+)", line)
            self.assertIsNotNone(matched, line)
            assert matched is not None
            with urlopen(f"http://127.0.0.1:{matched.group(1)}/healthz", timeout=3) as response:
                payload = json.load(response)
            self.assertEqual(response.status, 200)
            self.assertTrue(payload["ready"])
        finally:
            process.terminate()
            process.wait(timeout=3)
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
