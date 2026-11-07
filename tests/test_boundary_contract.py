import copy
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from characterlab.model import canonical_boundaries, build_comparison, is_allowlisted_read_only_comparison, scenario_ids
from characterlab.webapp import DemoHandler


class BoundaryContractTests(unittest.TestCase):
    def test_every_scenario_and_profile_uses_the_exact_canonical_boundary_order(self):
        expected = list(canonical_boundaries())
        for scenario_id in scenario_ids():
            report = build_comparison(scenario_id)
            self.assertEqual(report["canonical_boundary_non_claims"], expected)
            self.assertEqual(report["shared_boundaries"], expected)
            for profile in report["display_profiles"]:
                self.assertIn(profile["profile_id"], {"check_first", "plan_next"})
                self.assertTrue(is_allowlisted_read_only_comparison(report))

    def test_api_serializes_only_the_same_canonical_boundary_contract(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for scenario_id in scenario_ids():
                with urlopen(
                    f"http://127.0.0.1:{server.server_port}/api/comparison?scenario={scenario_id}", timeout=3
                ) as response:
                    payload = json.load(response)
                self.assertEqual(payload["canonical_boundary_non_claims"], list(canonical_boundaries()))
                self.assertEqual(payload["shared_boundaries"], list(canonical_boundaries()))
                self.assertTrue(payload["allowlisted_actions_only"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_contract_changes_fail_closed(self):
        baseline = build_comparison()
        cases = []
        missing = copy.deepcopy(baseline)
        missing["shared_boundaries"].pop()
        cases.append(missing)
        added = copy.deepcopy(baseline)
        added["canonical_boundary_non_claims"].append("Extra boundary")
        cases.append(added)
        reordered = copy.deepcopy(baseline)
        reordered["shared_boundaries"].reverse()
        cases.append(reordered)
        altered = copy.deepcopy(baseline)
        altered["canonical_boundary_non_claims"][0] = "Static material."
        cases.append(altered)
        for report in cases:
            self.assertFalse(is_allowlisted_read_only_comparison(report))
