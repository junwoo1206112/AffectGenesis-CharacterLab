"""Standard-library web view for the local portfolio demo."""

from __future__ import annotations

import argparse
import json
from html import escape
from html.parser import HTMLParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .evidence import public_ui_evidence_status
from .learning_experiment import evaluate as evaluate_synthetic_holdout
from .model import build_comparison, canonical_boundaries, is_allowlisted_read_only_comparison, scenario_ids


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class _VisibleTextParser(HTMLParser):
    """Collect text that is not hidden by a basic HTML/CSS visibility mechanism."""

    _NON_VISIBLE_TAGS = {"script", "style", "template"}
    _HIDDEN_CLASS_NAMES = {"hidden", "visually-hidden", "sr-only"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._hidden_stack: list[bool] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value or "" for name, value in attrs}
        style = "".join(values.get("style", "").lower().split())
        classes = set(values.get("class", "").lower().split())
        hidden = (
            tag.lower() in self._NON_VISIBLE_TAGS
            or "hidden" in values
            or values.get("aria-hidden", "").lower() == "true"
            or bool(classes & self._HIDDEN_CLASS_NAMES)
            or "display:none" in style
            or "visibility:hidden" in style
            or (self._hidden_stack[-1] if self._hidden_stack else False)
        )
        self._hidden_stack.append(hidden)

    def handle_endtag(self, _tag: str) -> None:
        if self._hidden_stack:
            self._hidden_stack.pop()

    def handle_data(self, data: str) -> None:
        if not (self._hidden_stack[-1] if self._hidden_stack else False):
            self.parts.append(data)


def normalized_visible_text(html: str) -> str:
    """Normalize only tags/entities/whitespace for the visibility contract."""

    parser = _VisibleTextParser()
    parser.feed(html)
    parser.close()
    return " ".join(" ".join(parser.parts).split())


def has_visible_canonical_boundaries(html: str) -> bool:
    """Require every canonical statement in visible, normalized page text."""

    visible = normalized_visible_text(html)
    return all(boundary in visible for boundary in canonical_boundaries())


def health_status() -> dict[str, object]:
    """Report whether this process can render the fixed static portfolio page.

    The receipt intentionally stops at local page readiness. It is not a model,
    learning, emotion, or safety assessment.
    """

    try:
        rendered = page()
    except Exception:
        return {
            "schema": "characterlab-health-1",
            "ready": False,
            "reason": "static_page_render_unavailable",
            "scope": "local fixed-page readiness only",
        }
    boundaries_ready = has_visible_canonical_boundaries(rendered)
    return {
        "schema": "characterlab-health-1",
        "ready": "<main id=\"main-content\"" in rendered and boundaries_ready,
        "reason": "ready" if boundaries_ready else "canonical_boundary_unavailable",
        "fixed_scenario_count": len(scenario_ids()),
        "scope": "local fixed-page readiness only",
        "non_claim": (
            "This endpoint does not prove emotion, learning, personality, consciousness, "
            "human development, or safety."
        ),
    }


def synthetic_input_panel(report: dict[str, object]) -> str:
    """Render the fixed exhibition input and the same boundary contract."""

    experience = report["synthetic_experience"]
    assert isinstance(experience, dict)
    boundary_items = "".join(
        f"<li>{escape(boundary)}</li>" for boundary in canonical_boundaries()
    )
    return (
        '<section class="synthetic-input"><h2>고정 합성 입력 (전시용)</h2>'
        f'<p><strong>상황:</strong> {escape(str(experience["situation"]))}</p>'
        f'<p><strong>표시된 행동 라벨:</strong> {escape(str(experience["observed_action"]))}</p>'
        f'<p><strong>사전작성 결과 라벨:</strong> {escape(str(experience["outcome"]))}</p>'
        '<p class="boundary">사전작성·합성·읽기 전용 자료이며 결과 산출·저장·상태/권한/실행 변경이 없습니다.</p>'
        f'<ul class="boundary canonical-boundaries">{boundary_items}</ul></section>'
    )


def evidence_status_panel(status: dict[str, object]) -> str:
    """Render optional capture status without treating it as a model result."""

    expected = status["expected_files"]
    valid = status["valid_files"]
    missing = status["missing_or_invalid_files"]
    assert isinstance(expected, list)
    assert isinstance(valid, list)
    assert isinstance(missing, list)
    complete = status["complete"] is True
    headline = "완료" if complete else "확인 불가"
    missing_items = "".join(f"<li><code>{escape(str(filename))}</code></li>" for filename in missing)
    details = (
        "세 파일의 PNG 서명이 모두 확인되었습니다."
        if complete
        else "보관 PNG가 없거나 형식이 확인되지 않았습니다. 이는 정적 전시의 동작 상태를 바꾸지 않습니다."
    )
    return (
        '<section class="evidence-status"><h2>보관 화면 증거</h2>'
        '<p class="note">기능 단계와 PNG 보관 증거는 별도 상태입니다. PNG는 기능 완료의 필수 조건이 아닙니다.</p>'
        '<p><strong>기능 단계:</strong> 구현됨 (고정·읽기 전용 전시)</p>'
        f'<p><strong>선택 보관 PNG 증거:</strong> {headline} ({len(valid)}/{len(expected)})</p>'
        f'<p>{escape(details)}</p>'
        + (f'<p><strong>누락 또는 무효 파일</strong></p><ul>{missing_items}</ul>' if missing else "")
        + '<p class="boundary">스크린샷은 렌더링된 로컬 화면만 기록하며 실제 감정·학습·성격·의식·인간 발달·안전을 증명하지 않습니다.</p>'
        '<p class="note">JSON: <code>/api/evidence-status</code></p></section>'
    )


def experiment_status_panel(report: dict[str, object]) -> str:
    """Render the isolated synthetic result without invoking any training."""
    baseline = report["baseline"]
    learned = report["learned"]
    safety = report["safety"]
    checkpoint = report["checkpoint"]
    assert isinstance(baseline, dict) and isinstance(learned, dict)
    assert isinstance(safety, dict) and isinstance(checkpoint, dict)
    return (
        '<section class="experiment-status"><h2>별도 합성 holdout 실험</h2>'
        '<p class="note">이 결과는 읽기 전용입니다. 학습을 실행하거나 캐릭터 상태를 바꾸지 않습니다.</p>'
        f'<p><strong>baseline / 모델 정확도:</strong> {baseline["holdout_accuracy"]:.3f} / {learned["holdout_accuracy"]:.3f}</p>'
        f'<p><strong>차이 / 사전 기준:</strong> {report["improvement"]:.3f} / {report["minimum_improvement"]:.2f}</p>'
        f'<p><strong>안전 위반 / checkpoint 복원:</strong> {safety["violation_count"]} / {checkpoint["restored_predictions_match"]}</p>'
        '<p class="boundary">고정 합성 split 결과이며 LLM·RAG·에이전트·실제 감정·인간 발달·실사용 안전을 뜻하지 않습니다.</p>'
        '<p class="note">JSON: <code>/api/experiment-report</code></p></section>'
    )


def page(scenario_id: str | None = None) -> str:
    report = build_comparison(scenario_id)
    evidence_status = public_ui_evidence_status(REPOSITORY_ROOT)
    experiment_report = evaluate_synthetic_holdout()
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
    boundaries = "".join(f"<li>{escape(item)}</li>" for item in report["canonical_boundary_non_claims"])
    scenario_links = "".join(
        '<a class="scenario{}" href="/?scenario={}"{}>{}</a>'.format(
            " selected" if scenario_id == report["scenario_id"] else "",
            escape(scenario_id),
            ' aria-current="page"' if scenario_id == report["scenario_id"] else "",
            escape(build_comparison(scenario_id)["scenario_display_name"]),
        )
        for scenario_id in scenario_ids()
    )
    return f"""<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>AffectGenesis CharacterLab</title>
<style>*{{box-sizing:border-box}}body{{font-family:system-ui;max-width:980px;margin:3rem auto;padding:0 1rem;background:#101827;color:#e8eefc;overflow-wrap:anywhere}}.skip-link{{position:absolute;left:-9999px;top:auto}}.skip-link:focus{{left:1rem;top:1rem;z-index:1;background:#fff;color:#101827;padding:.6rem}}a:focus-visible{{outline:3px solid #fff;outline-offset:3px}}.profiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}section{{border:1px solid #5f7aa5;border-radius:12px;padding:1rem;background:#18253a}}code{{color:#a9d3ff}}.note{{color:#b8c7df}}.boundary{{color:#ffe0a6;font-size:.9rem}}.scenarios{{display:flex;gap:.6rem;flex-wrap:wrap}}.scenario{{padding:.45rem .7rem;border:1px solid #5f7aa5;border-radius:999px;color:#e8eefc;text-decoration:none}}.scenario.selected{{background:#365a87;font-weight:700}}@media (max-width:360px){{body{{margin:1rem auto;padding:0 .75rem}}.profiles{{grid-template-columns:1fr}}section{{padding:.75rem}}}}</style>
<a class=\"skip-link\" href=\"#main-content\">본문으로 건너뛰기</a><main id=\"main-content\" tabindex=\"-1\"><p class=\"note\">{escape(report["comparison_label"])}</p><h1>AffectGenesis CharacterLab</h1>
<p>3개의 고정 합성 사례에서, 같은 합성 상황·같은 허용 목록을 받은 두 사전작성 표시 프로필의 문구와 제안 순서만 비교합니다. 자동 학습·저장·권한·외형·행동 실행은 없습니다.</p>
<p class=\"boundary\">실제 감정·의식·성격·인간 발달의 증거가 아닙니다. 허용 목록은 임상적 또는 실제 안전의 보증이 아닙니다.</p>
<nav class=\"scenarios\" aria-label=\"고정 합성 사례\">{scenario_links}</nav><h2>{escape(report["scenario_display_name"])}</h2>
<p class=\"note\">{escape(report["shared_context"])}</p><p class=\"note\">{escape(report["comparison_summary"])}</p>{synthetic_input_panel(report)}<div class=\"profiles\">{cards}</div>
<h2>공통 경계</h2><ul class=\"boundary\">{boundaries}</ul>
<h2>한계</h2><ul>{limitations}</ul>{experiment_status_panel(experiment_report)}{evidence_status_panel(evidence_status)}<p class=\"note\">JSON: <code>/api/comparison</code></p></main></html>"""


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract
        parsed = urlparse(self.path)
        requested = parse_qs(parsed.query).get("scenario", [None])[0]
        try:
            if parsed.path == "/":
                body = page(requested).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
            elif parsed.path == "/api/comparison":
                report = build_comparison(requested)
                body = json.dumps(
                    {**report, "allowlisted_actions_only": is_allowlisted_read_only_comparison(report)},
                    ensure_ascii=False,
                ).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
            elif parsed.path == "/api/evidence-status":
                body = json.dumps(
                    public_ui_evidence_status(REPOSITORY_ROOT), ensure_ascii=False, sort_keys=True
                ).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
            elif parsed.path == "/api/experiment-report":
                body = json.dumps(evaluate_synthetic_holdout(), ensure_ascii=False, sort_keys=True).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
            elif parsed.path == "/healthz":
                status = health_status()
                body = json.dumps(status, ensure_ascii=False, sort_keys=True).encode("utf-8")
                self.send_response(HTTPStatus.OK if status["ready"] else HTTPStatus.SERVICE_UNAVAILABLE)
                self.send_header("Content-Type", "application/json; charset=utf-8")
            else:
                raise ValueError("Unknown route")
        except ValueError:
            body = b"not found"
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _method_not_allowed(self) -> None:
        """Reject every mutating method instead of relying on stdlib defaults."""

        body = b"method not allowed"
        self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_header("Allow", "GET")
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_POST = _method_not_allowed
    do_PUT = _method_not_allowed
    do_PATCH = _method_not_allowed
    do_DELETE = _method_not_allowed

    def log_message(self, _format: str, *_args: object) -> None:
        """Keep the portfolio demo quiet unless a caller adds logging."""


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local CharacterLab comparison demo.")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DemoHandler)
    print(f"CharacterLab: http://127.0.0.1:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
