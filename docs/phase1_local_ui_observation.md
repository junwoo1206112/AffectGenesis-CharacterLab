# Phase 1 local UI observation

**Observed:** 2026-11-08 KST
**Scope:** local static CharacterLab comparison only
**Source revision:** `c0fa5e742c4fc61c27f2b51abaa814d908a10d1d` (`feat: add static scenario evidence contract`)

## What was exercised

The local server was restarted from the source revision above with:

```powershell
python -m characterlab.webapp --port 8766
```

The following three browser routes were then opened in a controlled local Chrome session:

1. `/?scenario=blocked_first_attempt`
2. `/?scenario=uncertain_next_step`
3. `/?scenario=planned_retry`

For all three routes, the rendered page exposed:

- the selected fixed synthetic scenario title;
- the fixed synthetic-input panel (situation, displayed action label, and pre-authored outcome label);
- the two display-only profiles, `확인 우선 표시` and `계획 다음 표시`;
- the same five canonical boundary statements; and
- the explicit limitation text that this is not evidence of actual emotion, personality, learning, consciousness, or human development.

The second route was captured after navigation and showed `pause_and_check` as its displayed action label. The third route was captured after a fresh server restart and showed `retry_with_plan` as its displayed action label. The first route was checked after the same restart for its selected title, input panel, both profiles, and canonical boundary text.

## Read-only API check

On the restarted local server, two consecutive reads of:

```text
/api/comparison?scenario=blocked_first_attempt
```

returned byte-identical bodies (`3257` characters at observation time). `POST`, `PUT`, `PATCH`, and `DELETE` to that route each returned `405`.

This confirms only the exercised local read-only surface. It does not prove broad state immutability, learning behavior, real-world safety, or any human-like emotional capability.

## Evidence limitation and completion status

The controlled-browser tool displayed full-page screenshots during this observation, but its available interface did not provide a supported way to persist those image bytes in this repository. Therefore no PNG files are claimed here.

**Phase 1 functional delivery: complete.** The actual browser observation, read-only API check, and regression tests are the functional completion evidence. The three-PNG archive is optional portfolio material, not a gate on the functional phase.

**Optional persisted-screenshot archive: complete.** On 2026-11-08 KST, the local capture CLI produced and the verifier accepted these three actual Chrome-rendered PNGs:

- `docs/phase1_ui/blocked_first_attempt.png`
- `docs/phase1_ui/uncertain_next_step.png`
- `docs/phase1_ui/planned_retry.png`

The capture output recorded `complete: true`, with all three files in `valid_files`; `python -m characterlab.evidence --require-complete` also exited `0`.

## Resume procedure

The next phase is an optional, evidence-only capture intake. It does not change a character, execute a suggestion, or claim that the display is a learned emotional system. Its absence does not reopen or block the functional phase.

1. Start the local server with `python -m characterlab.webapp --port 8766`.
2. Capture the three routes listed in `docs/phase1_ui/README.md` and save each PNG under `docs/phase1_ui/` with its required name.
3. Run `Set-Location C:\AI\AffectGenesis-CharacterLab` first, then run `python -m characterlab.evidence --require-complete`.
4. Only if that command reports `"complete": true` and exits `0`, update this document with the capture date and run the usual unittest and `git diff --check` verification.

The verifier is read-only: missing or invalid files remain `incomplete` rather than being synthesized or silently accepted.

### Capture automation history

An earlier controlled-browser attempt captured the local `blocked_first_attempt` page as JPEG bytes but could not persist them through the Windows capture editor. That limitation is now superseded by the project-local Chrome headless capture CLI.

Restart condition: if a later capture is needed, retain the existing files unless an explicit replacement policy is chosen. The capture CLI refuses to overwrite them. Run `python -m characterlab.evidence --require-complete` after any deliberate replacement; do not substitute generated or unrelated images.

The project now also provides `python -m characterlab.capture`, which renders the same three fixed local routes in an ephemeral local Chrome session and writes only verified PNGs. It refuses to overwrite existing capture files and can be followed by the existing evidence verification command.

## Next phase: evidence-status surface

The optional evidence-intake phase now has two read-only local surfaces:

- homepage panel: `http://127.0.0.1:8766/` → `보관 화면 증거`;
- machine-readable status: `http://127.0.0.1:8766/api/evidence-status`.

The panel and API deliberately separate the functional static display from optional persisted PNG evidence. At this observation, the panel reported `기능 단계: 구현됨` and `선택 보관 PNG 증거: 확인 불가 (0/3)`, then listed all three required filenames. It did not change a character, memory, authority, appearance, or action state, and the API excludes the machine-specific evidence-directory path.

This follows the narrow transparency principle that repeatable checks and their limitations should be documented separately from system claims; it is not a claim of NIST compliance or of actual emotion. See the [NIST AI RMF Measure guidance](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/).

## Interview connection check

The Ouroboros interview service returned a new session and a Korean question in this same task. Local A/B/C role review agreed this proves current-session reachability only; it is not a completed interview, an external expert review, or a guarantee of future-session availability.
