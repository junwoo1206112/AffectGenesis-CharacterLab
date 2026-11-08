"""Run a bounded live-HTTP smoke check for the static local portfolio."""

from __future__ import annotations

import json
import threading
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .model import ALLOWLISTED_COPING_SUGGESTIONS, scenario_ids
from .webapp import DemoHandler


def run_smoke() -> dict[str, object]:
    """Verify the fixed read-only HTTP surface through an ephemeral loopback server.

    This is an HTTP contract check only.  It does not capture screenshots, mutate
    character state, perform learning, or establish any claim about emotion or safety.
    """

    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    checked_scenarios: list[str] = []
    rejected_methods: list[str] = []
    try:
        with urlopen(f"{base_url}/healthz", timeout=3) as response:
            health = json.load(response)
        if health["ready"] is not True:
            raise RuntimeError("health endpoint is not ready")
        if health["fixed_scenario_count"] != len(scenario_ids()):
            raise RuntimeError("health scenario count mismatch")

        for scenario_id in scenario_ids():
            endpoint = f"{base_url}/api/comparison?scenario={scenario_id}"
            with urlopen(endpoint, timeout=3) as response:
                first = response.read()
                payload = json.loads(first)
            with urlopen(endpoint, timeout=3) as response:
                repeated = response.read()
            if payload["scenario_id"] != scenario_id:
                raise RuntimeError(f"scenario mismatch: {scenario_id}")
            if payload["coping_allowlist"] != list(ALLOWLISTED_COPING_SUGGESTIONS):
                raise RuntimeError(f"allowlist mismatch: {scenario_id}")
            if payload["allowlisted_actions_only"] is not True:
                raise RuntimeError(f"non-allowlisted action: {scenario_id}")
            if first != repeated:
                raise RuntimeError(f"GET response changed: {scenario_id}")
            checked_scenarios.append(scenario_id)

        for method in ("POST", "PUT", "PATCH", "DELETE"):
            try:
                urlopen(Request(f"{base_url}/api/comparison", method=method), timeout=3)
            except HTTPError as error:
                if error.code != HTTPStatus.METHOD_NOT_ALLOWED:
                    raise RuntimeError(f"{method} returned {error.code}") from error
            else:
                raise RuntimeError(f"{method} unexpectedly succeeded")
            rejected_methods.append(method)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

    return {
        "schema": "characterlab-live-http-smoke-1",
        "checked_scenarios": checked_scenarios,
        "health_ready": True,
        "get_responses_stable": True,
        "rejected_mutation_methods": rejected_methods,
        "scope": "ephemeral loopback HTTP contract only",
        "non_claim": (
            "This check does not prove emotion, learning, personality, consciousness, "
            "human development, or safety."
        ),
    }


def main() -> None:
    """Print the smoke receipt as JSON and use a nonzero exit for failures."""

    print(json.dumps(run_smoke(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
