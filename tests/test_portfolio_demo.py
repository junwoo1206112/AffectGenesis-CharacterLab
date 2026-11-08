import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from characterlab.evidence import EXPECTED_SCREENSHOTS
from characterlab.model import ALLOWLISTED_COPING_SUGGESTIONS, build_comparison, is_allowlisted_read_only_comparison
from characterlab.webapp import DemoHandler, health_status, page


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
        self.assertIn("보관 화면 증거", rendered)
        self.assertIn("선택 보관 PNG 증거:</strong>", rendered)
        self.assertIn("기능 단계와 PNG 보관 증거는 별도 상태", rendered)
        self.assertIn("기능 단계:</strong> 구현됨", rendered)
        self.assertIn("별도 합성 holdout 실험", rendered)
        self.assertIn("학습을 실행하거나 캐릭터 상태를 바꾸지 않습니다", rendered)

    def test_experiment_report_api_is_read_only_and_bounded(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/api/experiment-report", timeout=3) as response:
                payload = json.load(response)
            self.assertEqual(payload["safety"]["violation_count"], 0)
            self.assertTrue(payload["checkpoint"]["restored_predictions_match"])
            self.assertIn("not an LLM", payload["non_claim"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_page_has_bounded_keyboard_and_small_screen_baseline(self):
        rendered = page("blocked_first_attempt")

        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', rendered)
        self.assertIn('href="#main-content">본문으로 건너뛰기</a>', rendered)
        self.assertIn('id="main-content" tabindex="-1"', rendered)
        self.assertIn("a:focus-visible", rendered)
        self.assertIn("@media (max-width:360px)", rendered)
        self.assertIn('aria-current="page"', rendered)
        self.assertEqual(rendered.count('aria-current="page"'), 1)

    def test_evidence_status_api_is_read_only_and_redacts_local_path(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/api/evidence-status", timeout=3) as response:
                payload = json.load(response)
            self.assertEqual(
                payload["complete"],
                len(payload["valid_files"]) == len(EXPECTED_SCREENSHOTS),
            )
            self.assertEqual(payload["functional_phase_status"], "implemented")
            self.assertFalse(payload["persisted_capture_required_for_functional_phase"])
            self.assertEqual(payload["expected_files"], list(EXPECTED_SCREENSHOTS))
            self.assertEqual(
                sorted(payload["valid_files"] + payload["missing_or_invalid_files"]),
                sorted(EXPECTED_SCREENSHOTS),
            )
            self.assertNotIn("evidence_directory", payload)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_health_endpoint_confirms_only_fixed_page_readiness(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/healthz", timeout=3) as response:
                payload = json.load(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(payload, health_status())
            self.assertTrue(payload["ready"])
            self.assertEqual(payload["fixed_scenario_count"], 3)
            self.assertIn("does not prove emotion", payload["non_claim"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_health_endpoint_fails_closed_without_exposing_render_details_then_recovers(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        endpoint = f"http://127.0.0.1:{server.server_port}/healthz"
        secret = r"C:\private\render-detail"
        try:
            with patch("characterlab.webapp.page", side_effect=RuntimeError(secret)):
                with self.assertRaises(HTTPError) as raised:
                    urlopen(endpoint, timeout=3)
                error = raised.exception
                self.assertEqual(error.code, 503)
                body = error.read().decode("utf-8")
                self.assertEqual(
                    json.loads(body),
                    {
                        "ready": False,
                        "reason": "static_page_render_unavailable",
                        "schema": "characterlab-health-1",
                        "scope": "local fixed-page readiness only",
                    },
                )
                self.assertNotIn(secret, body)
                self.assertNotIn(secret, str(error.headers))

            with urlopen(endpoint, timeout=3) as response:
                recovered = json.load(response)
            self.assertEqual(response.status, 200)
            self.assertTrue(recovered["ready"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_model_remains_read_only(self):
        self.assertTrue(is_allowlisted_read_only_comparison(build_comparison()))

    def test_mutating_methods_are_explicitly_rejected_without_changing_api_bytes(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/api/comparison?scenario=planned_retry"
        try:
            with urlopen(url, timeout=3) as response:
                before = response.read()
            for path in ("/", "/api/comparison?scenario=planned_retry"):
                for method in ("POST", "PUT", "PATCH", "DELETE"):
                    with self.assertRaises(HTTPError) as raised:
                        urlopen(Request(f"http://127.0.0.1:{server.server_port}{path}", method=method), timeout=3)
                    self.assertEqual(raised.exception.code, 405)
            with urlopen(url, timeout=3) as response:
                after = response.read()
            with urlopen(url, timeout=3) as response:
                repeated = response.read()
            self.assertEqual(before, after)
            self.assertEqual(after, repeated)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
