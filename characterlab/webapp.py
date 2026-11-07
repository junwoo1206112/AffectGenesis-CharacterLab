"""Standard-library web view for the local portfolio demo."""

from __future__ import annotations

import argparse
import json
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .model import build_comparison, is_allowlisted_read_only_comparison


def page() -> str:
    report = build_comparison()
    cards = "".join(
        "<section><h2>{}</h2><p>{}</p><p><strong>표시 제안 순서:</strong> {}</p>"
        "<p class=\"note\">{}</p><p class=\"boundary\">사전작성 표시 변형입니다. 실제 특성·진단·학습·개인화가 아닙니다.</p></section>".format(
            escape(profile["display_name"]),
            escape(profile["static_wording"]),
            escape(", ".join(profile["suggestions"])),
            escape(profile["difference_explanation"]),
        )
        for profile in report["display_profiles"]
    )
    limitations = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    return f"""<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\">
<title>AffectGenesis CharacterLab</title>
<style>body{{font-family:system-ui;max-width:980px;margin:3rem auto;padding:0 1rem;background:#101827;color:#e8eefc}}.profiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}section{{border:1px solid #5f7aa5;border-radius:12px;padding:1rem;background:#18253a}}code{{color:#a9d3ff}}.note{{color:#b8c7df}}.boundary{{color:#ffe0a6;font-size:.9rem}}</style>
<main><p class=\"note\">{escape(report["comparison_label"])}</p><h1>AffectGenesis CharacterLab</h1>
<p>같은 합성 상황·같은 허용 목록에서, 사전작성된 표시 순서와 설명만 비교합니다. 자동 학습·저장·권한·외형·행동 실행은 없습니다.</p>
<p class=\"boundary\">실제 감정·의식·성격·인간 발달의 증거가 아닙니다. 허용 목록은 임상적 또는 실제 안전의 보증이 아닙니다.</p>
<p class=\"note\">{escape(report["shared_context"])}</p><div class=\"profiles\">{cards}</div>
<h2>한계</h2><ul>{limitations}</ul><p class=\"note\">JSON: <code>/api/comparison</code></p></main></html>"""


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract
        if self.path == "/":
            body = page().encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif self.path == "/api/comparison":
            report = build_comparison()
            body = json.dumps(
                {**report, "allowlisted_actions_only": is_allowlisted_read_only_comparison(report)},
                ensure_ascii=False,
            ).encode("utf-8")
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
