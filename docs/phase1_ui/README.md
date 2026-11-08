# Phase 1 local UI screenshots

**Current status: complete (3/3).** The three local, static pages below were captured with the project-local Chrome automation and accepted by `python -m characterlab.evidence --require-complete`. This archive is optional portfolio material; it documents rendered fixed UI routes only and does not prove emotion, learning, personality, consciousness, human development, or safety. Do not place user data, browser history, credentials, or unrelated desktop content in any replacement images.

The completed archive contains one full-page PNG for each fixed route:

| Route | Required filename |
| --- | --- |
| `http://127.0.0.1:8766/?scenario=blocked_first_attempt` | `blocked_first_attempt.png` |
| `http://127.0.0.1:8766/?scenario=uncertain_next_step` | `uncertain_next_step.png` |
| `http://127.0.0.1:8766/?scenario=planned_retry` | `planned_retry.png` |

Audit the current archive from the repository root. `characterlab` is a local package, not a globally installed Python package, so changing to this directory is required:

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
& C:\Users\kjunw\AppData\Local\Programs\Python\Python312\python.exe -m characterlab.evidence --require-complete
```

It prints a local JSON status and exits with `0` only when all three files have PNG signatures. It neither creates screenshots nor uploads or changes any character data.

## Automated local capture

If a deliberate replacement is approved and local Chrome is installed, the project can create the three captures without browser-window automation:

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
python -m characterlab.capture
python -m characterlab.evidence --require-complete
```

The command uses an ephemeral `127.0.0.1` server and a temporary Chrome profile, captures only the fixed local scenario routes, validates PNG signatures, and refuses to overwrite any existing capture PNG. It intentionally stops while the current archive exists; do not delete or replace evidence without an explicit replacement policy. Set `CHARACTERLAB_CHROME_PATH` or pass `--chrome-path` only when Chrome is installed in a nonstandard local location.

The screenshots are local UI evidence only. They do not demonstrate actual emotion, personality, learning, consciousness, human development, or safety.
