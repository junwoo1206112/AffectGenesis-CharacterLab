"""Standard-library web view for the local portfolio demo."""

from __future__ import annotations

import argparse
import json
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .model import build_comparison, is_safe_comparison


def page() -> str:
    report = build_comparison()
    cards = "".join(
        "<section><h2>{}</h2><p>{}</p><p><strong>기억 사용:</strong> {}</p>"
        "<p><strong>제안:</strong> {}</p></section>".format(
            escape(condition["condition"]),
            escape(condition["explanation"]),
            "예" if condition["memory_used"] else "아니오",
            escape(", ".join(condition["suggestions"])),
        )
        for condition in report["comparison_conditions"]
    )
    limitations = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    return f"""<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\">
<title>AffectGenesis CharacterLab</title>
<style>body{{font-family:system-ui;max-width:880px;margin:3rem auto;padding:0 1rem;background:#101827;color:#e8eefc}}section{{border:1px solid #5f7aa5;border-radius:12px;padding:1rem;margin:1rem 0;background:#18253a}}code{{color:#a9d3ff}}.note{{color:#b8c7df}}</style>
<main><p class=\"note\">LOCAL · SYNTHETIC · READ-ONLY</p><h1>AffectGenesis CharacterLab</h1>
<p>동일한 캐릭터와 합성 경험을 두 조건에서 비교합니다. 이 화면은 학습을 실행하거나 캐릭터를 변경하지 않습니다.</p>
{cards}<h2>한계</h2><ul>{limitations}</ul><p class=\"note\">JSON: <code>/api/comparison</code></p></main></html>"""


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract
        if self.path == "/":
            body = page().encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif self.path == "/api/comparison":
            report = build_comparison()
            body = json.dumps({**report, "safe": is_safe_comparison(report)}, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
        else:
            body = b"not found"
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        """Keep the portfolio demo quiet unless a caller adds logging."""


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local CharacterLab comparison demo.")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DemoHandler)
    print(f"CharacterLab: http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
