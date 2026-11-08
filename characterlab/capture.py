"""Create optional, local-only PNG captures of the static CharacterLab pages."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
from http.server import ThreadingHTTPServer
from typing import Any

from .evidence import EXPECTED_SCREENSHOTS, PNG_SIGNATURE, evidence_directory, ui_evidence_status
from .model import scenario_ids
from .webapp import DemoHandler


CAPTURE_HEIGHT = 3200
CAPTURE_WIDTH = 1440
_WINDOWS_CHROME_PATHS = (
    ("ProgramFiles", "Google", "Chrome", "Application", "chrome.exe"),
    ("ProgramFiles(x86)", "Google", "Chrome", "Application", "chrome.exe"),
    ("LocalAppData", "Google", "Chrome", "Application", "chrome.exe"),
)


def find_chrome() -> Path | None:
    """Locate a locally installed Chrome executable without downloading anything."""

    configured = os.environ.get("CHARACTERLAB_CHROME_PATH")
    candidates = [Path(configured)] if configured else []
    resolved = shutil.which("chrome.exe") or shutil.which("chrome")
    if resolved:
        candidates.append(Path(resolved))
    for environment_name, *parts in _WINDOWS_CHROME_PATHS:
        base = os.environ.get(environment_name)
        if base:
            candidates.append(Path(base).joinpath(*parts))
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def _capture_command(chrome: Path, url: str, output: Path, profile: Path) -> list[str]:
    return [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-default-apps",
        "--hide-scrollbars",
        "--no-first-run",
        f"--user-data-dir={profile}",
        f"--window-size={CAPTURE_WIDTH},{CAPTURE_HEIGHT}",
        f"--screenshot={output}",
        url,
    ]


def _is_png(path: Path) -> bool:
    return path.is_file() and path.read_bytes().startswith(PNG_SIGNATURE)


def capture_local_ui(repository_root: Path, chrome: Path | None = None) -> dict[str, Any]:
    """Render the three local pages in Chrome and atomically add their PNGs.

    Existing capture PNGs are never overwritten. The running server and character
    state are not used: an ephemeral loopback server serves only the static demo.
    """

    repository_root = repository_root.resolve()
    output_directory = evidence_directory(repository_root)
    existing = [name for name in EXPECTED_SCREENSHOTS if (output_directory / name).exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite existing capture(s): {', '.join(existing)}")
    chrome = chrome or find_chrome()
    if chrome is None:
        raise FileNotFoundError("local Chrome was not found; set CHARACTERLAB_CHROME_PATH")

    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory(prefix="characterlab-capture-") as temporary_directory:
            temporary_root = Path(temporary_directory)
            profile = temporary_root / "chrome-profile"
            staged: list[Path] = []
            for scenario_id, filename in zip(scenario_ids(), EXPECTED_SCREENSHOTS, strict=True):
                output = temporary_root / filename
                url = f"http://127.0.0.1:{server.server_port}/?scenario={scenario_id}"
                result = subprocess.run(
                    _capture_command(chrome, url, output, profile),
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
                if result.returncode != 0 or not _is_png(output):
                    raise RuntimeError(
                        f"Chrome capture failed for {scenario_id}: exit={result.returncode}; "
                        f"stderr={result.stderr.strip()[:300]}"
                    )
                staged.append(output)
            output_directory.mkdir(parents=True, exist_ok=True)
            for output in staged:
                output.replace(output_directory / output.name)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

    return {
        "schema": "characterlab-local-capture-1",
        "captured_files": list(EXPECTED_SCREENSHOTS),
        "evidence": ui_evidence_status(repository_root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture local CharacterLab static UI pages as PNG files.")
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--chrome-path", type=Path, help="Optional Chrome executable path.")
    args = parser.parse_args()
    result = capture_local_ui(args.repository_root, args.chrome_path)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
