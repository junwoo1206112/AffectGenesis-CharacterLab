"""Inspect the fixed v0.1.0 portfolio baseline without changing Git state.

The first public CharacterLab release was created in GitHub's web interface.
That workflow produced a lightweight tag.  A lightweight tag is still a
reference to a commit, but it is not an annotated tag object.  This module
makes that distinction visible instead of treating the two forms as equal.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


RELEASE_TAG = "v0.1.0"
RELEASE_TARGET_SHA = "0e5b3168e5dbd151841b184a7856f52af384d206"
RELEASE_URL = "https://github.com/junwoo1206112/AffectGenesis-CharacterLab/releases/tag/v0.1.0"
RELEASE_ID = 438182316
SCHEMA = "characterlab-release-receipt-1"


def _git(repository_root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise ValueError(detail)
    return completed.stdout.strip()


def release_receipt(repository_root: Path) -> dict[str, Any]:
    """Return an auditable, read-only tag-binding receipt for the published baseline."""

    repository_root = repository_root.resolve()
    try:
        object_type = _git(repository_root, "cat-file", "-t", RELEASE_TAG)
        resolved_target = _git(repository_root, "rev-parse", f"{RELEASE_TAG}^{{}}")
    except ValueError as error:
        return {
            "schema": SCHEMA,
            "complete": False,
            "reason": "tag_unavailable",
            "detail": str(error),
            "tag": RELEASE_TAG,
            "expected_target_sha": RELEASE_TARGET_SHA,
            "non_claim": _NON_CLAIM,
        }

    tag_kind = {"commit": "lightweight", "tag": "annotated"}.get(object_type, "unsupported")
    target_matches = resolved_target == RELEASE_TARGET_SHA
    accepted = tag_kind in {"lightweight", "annotated"} and target_matches
    return {
        "schema": SCHEMA,
        "complete": accepted,
        "status": "verified_release_baseline" if accepted else "release_baseline_not_verified",
        "tag": RELEASE_TAG,
        "tag_object_type": object_type,
        "tag_kind": tag_kind,
        "resolved_target_sha": resolved_target,
        "expected_target_sha": RELEASE_TARGET_SHA,
        "target_matches": target_matches,
        "release_url": RELEASE_URL,
        "release_id": RELEASE_ID,
        "prior_seed_status": "unmet_annotated_tag_requirement",
        "scope": "local git tag binding only",
        "non_claim": _NON_CLAIM,
    }


_NON_CLAIM = (
    "This receipt verifies only the local Git reference binding. It does not by itself verify "
    "GitHub release metadata, CI state, emotion, learning, personality, consciousness, human "
    "development, or safety."
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect the read-only v0.1.0 release receipt.")
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path.cwd(),
        help="CharacterLab repository root (defaults to the current directory).",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return nonzero unless the tag resolves to the fixed published target.",
    )
    args = parser.parse_args()
    receipt = release_receipt(args.repository_root)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if receipt.get("complete") or not args.require_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
