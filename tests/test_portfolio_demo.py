import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from characterlab.model import ALLOWLISTED_COPING_SUGGESTIONS, build_comparison, is_allowlisted_read_only_comparison
from characterlab.webapp import DemoHandler, page


class PortfolioDemoTests(unittest.TestCase):
    def test_http_api_is_read_only_and_allowlisted(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/api/comparison", timeout=3) as response:
                payload = json.load(response)
            self.assertTrue(payload["allowlisted_actions_only"])
            self.assertEqual(payload["coping_allowlist"], list(ALLOWLISTED_COPING_SUGGESTIONS))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_page_states_boundaries(self):
        rendered = page()
        self.assertIn("같은 합성 상황", rendered)
        self.assertIn("자동 학습·저장·권한·외형·행동 실행은 없습니다", rendered)
        self.assertIn("실제 감정·의식·성격", rendered)
        self.assertNotIn("<button", rendered)
        self.assertNotIn("<form", rendered)
        self.assertNotIn("fetch(", rendered)

    def test_model_remains_read_only(self):
        self.assertTrue(is_allowlisted_read_only_comparison(build_comparison()))
