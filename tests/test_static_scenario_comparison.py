import copy
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from characterlab.model import build_comparison, is_allowlisted_read_only_comparison, profile_ids, scenario_ids
from characterlab.webapp import DemoHandler, page


class ScenarioComparisonTests(unittest.TestCase):
    def test_three_scenarios_show_paired_results_rationales_and_summaries(self):
        self.assertEqual(
            scenario_ids(),
            ("blocked_first_attempt", "uncertain_next_step", "planned_retry"),
        )
        for scenario_id in scenario_ids():
            report = build_comparison(scenario_id)
            self.assertEqual(report["scenario_id"], scenario_id)
            self.assertEqual(len(report["display_profiles"]), 2)
            self.assertEqual(tuple(profile["profile_id"] for profile in report["display_profiles"]), profile_ids())
            self.assertTrue(report["comparison_summary"])
            self.assertTrue(all(profile["difference_explanation"] for profile in report["display_profiles"]))
            self.assertTrue(is_allowlisted_read_only_comparison(report))
            rendered = page(scenario_id)
            self.assertIn(report["scenario_display_name"], rendered)
            self.assertIn(report["comparison_summary"], rendered)

    def test_boundaries_and_non_claims_in_every_scenario(self):
        for scenario_id in scenario_ids():
            report = build_comparison(scenario_id)
            boundaries = " ".join(report["shared_boundaries"]).lower()
            self.assertIn("static", boundaries)
            self.assertIn("read-only", boundaries)
            self.assertIn("no state", boundaries)
            self.assertIn("no authority", boundaries)
            self.assertIn("no action", boundaries)
            self.assertIn("actual emotion", boundaries)
            self.assertIn("personality", boundaries)
            self.assertIn("learning", boundaries)
            self.assertIn("personalization", boundaries)
            self.assertIn("adaptation", boundaries)

    def test_all_transitions_preserve_payload_order_and_false_flags_without_side_effects(self):
        baseline = {scenario_id: build_comparison(scenario_id) for scenario_id in scenario_ids()}
        for scenario_id in (*scenario_ids(), *reversed(scenario_ids()), scenario_ids()[0]):
            report = build_comparison(scenario_id)
            self.assertEqual(report, baseline[scenario_id])
            self.assertTrue(is_allowlisted_read_only_comparison(report))
            for scope in [report, *report["display_profiles"]]:
                for field in ("state_fields", "authority_fields", "action_execution_fields"):
                    self.assertTrue(all(value is False for value in scope[field].values()))
        reordered = copy.deepcopy(baseline[scenario_ids()[0]])
        reordered["display_profiles"].reverse()
        self.assertFalse(is_allowlisted_read_only_comparison(reordered))

    def test_http_selector_only_returns_fixed_catalog_entries(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for scenario_id in scenario_ids():
                with urlopen(
                    f"http://127.0.0.1:{server.server_port}/api/comparison?scenario={scenario_id}", timeout=3
                ) as response:
                    payload = json.load(response)
                self.assertEqual(payload["scenario_id"], scenario_id)
                self.assertTrue(payload["allowlisted_actions_only"])
            with self.assertRaises(HTTPError) as raised:
                urlopen(f"http://127.0.0.1:{server.server_port}/api/comparison?scenario=user_input", timeout=3)
            self.assertEqual(raised.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
