# Phase 1 local UI screenshots

This directory is intentionally empty until a person captures the three local, static pages below. Do not place user data, browser history, credentials, or unrelated desktop content in these images.

With the local server running, capture one full-page PNG for each route and save it with the exact filename:

| Route | Required filename |
| --- | --- |
| `http://127.0.0.1:8766/?scenario=blocked_first_attempt` | `blocked_first_attempt.png` |
| `http://127.0.0.1:8766/?scenario=uncertain_next_step` | `uncertain_next_step.png` |
| `http://127.0.0.1:8766/?scenario=planned_retry` | `planned_retry.png` |

Then run this from the repository root. `characterlab` is a local package, not a globally installed Python package, so changing to this directory is required:

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
& C:\Users\kjunw\AppData\Local\Programs\Python\Python312\python.exe -m characterlab.evidence --require-complete
```

It prints a local JSON status and exits with `0` only when all three files have PNG signatures. Before captures exist, `--require-complete` intentionally exits with `1`; omit that option for a non-failing status check. It neither creates screenshots nor uploads or changes any character data.

The screenshots are local UI evidence only. They do not demonstrate actual emotion, personality, learning, consciousness, human development, or safety.
