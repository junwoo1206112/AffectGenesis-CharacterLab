"""Read-only validation for the optional local Phase 1 UI screenshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_SCREENSHOTS = (
    "blocked_first_attempt.png",
    "uncertain_next_step.png",
    "planned_retry.png",
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FUNCTIONAL_PHASE_STATUS = "implemented"


def evidence_directory(repository_root: Path) -> Path:
    """Return the fixed, local-only directory reserved for optional captures."""

    return repository_root / "docs" / "phase1_ui"


def _is_png(path: Path) -> bool:
    try:
        return path.is_file() and path.read_bytes().startswith(PNG_SIGNATURE)
    except OSError:
        return False


def ui_evidence_status(repository_root: Path) -> dict[str, Any]:
    """Describe evidence availability without creating, changing, or uploading files."""

    directory = evidence_directory(repository_root)
    valid = [name for name in EXPECTED_SCREENSHOTS if _is_png(directory / name)]
    missing = [name for name in EXPECTED_SCREENSHOTS if name not in valid]
    return {
        "schema": "characterlab-phase1-ui-evidence-2",
        "functional_phase_status": FUNCTIONAL_PHASE_STATUS,
        "persisted_capture_required_for_functional_phase": False,
        "evidence_directory": str(directory),
        "expected_files": list(EXPECTED_SCREENSHOTS),
        "valid_files": valid,
        "missing_or_invalid_files": missing,
        "complete": not missing,
        "scope": "local static UI observation only",
        "non_claim": (
            "Screenshots document rendered local display states only; they do not prove "
            "emotion, learning, personality, consciousness, human development, or safety."
        ),
    }


def public_ui_evidence_status(repository_root: Path) -> dict[str, Any]:
    """Return the status safe to display in the local web view.

    The CLI can include a local absolute path to help a person resume work. The
    web/API representation deliberately excludes that host-specific path.
    """

    status = ui_evidence_status(repository_root)
    return {
        key: status[key]
        for key in (
            "schema",
            "functional_phase_status",
            "persisted_capture_required_for_functional_phase",
            "expected_files",
            "valid_files",
            "missing_or_invalid_files",
            "complete",
            "scope",
            "non_claim",
        )
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect optional local Phase 1 UI evidence.")
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path.cwd(),
        help="CharacterLab repository root (defaults to the current directory).",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return a nonzero exit status when any required screenshot is missing or invalid.",
    )
    args = parser.parse_args()
    status = ui_evidence_status(args.repository_root.resolve())
    print(json.dumps(status, ensure_ascii=False, sort_keys=True))
    return 0 if status["complete"] or not args.require_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
