import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from characterlab.model import SAFE_ACTIONS, build_comparison, is_safe_comparison
from characterlab.webapp import DemoHandler, page


class PortfolioDemoTests(unittest.TestCase):
    def test_identical_inputs_have_read_only_approved_comparison(self):
        report = build_comparison()
        self.assertTrue(is_safe_comparison(report))
        self.assertEqual(report["character"]["character_id"], "mira-01")
        unapproved, approved = report["comparison_conditions"]
        self.assertFalse(unapproved["learning_approved"])
        self.assertFalse(unapproved["memory_used"])
        self.assertTrue(approved["learning_approved"])
        self.assertTrue(approved["memory_used"])
        self.assertEqual(approved["suggestions"][-1], "retry_with_plan")
        self.assertTrue(all(action in SAFE_ACTIONS for item in report["comparison_conditions"] for action in item["suggestions"]))

    def test_page_states_boundaries(self):
        rendered = page()
        self.assertIn("학습을 실행하거나 캐릭터를 변경하지 않습니다", rendered)
        self.assertIn("actual emotion", rendered)
        self.assertNotIn("<button", rendered)

    def test_http_api_is_read_only_and_safe(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/api/comparison", timeout=3) as response:
                payload = json.load(response)
            self.assertTrue(payload["safe"])
            self.assertEqual(len(payload["comparison_conditions"]), 2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
