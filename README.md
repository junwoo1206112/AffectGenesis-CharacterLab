# AffectGenesis CharacterLab

작은 로컬 포트폴리오 데모입니다. 정확히 3개의 **고정 합성 사례**에서, 동일한 사전정의 허용 목록을 받는 두 표시 프로필의 문구와 제안 순서만 나란히 비교합니다. 사례 전환은 URL 링크로 사전작성 자료를 선택하는 것뿐이며 입력·저장·계산·행동 실행을 하지 않습니다.

- `확인 우선 표시`: 확인·지원 요청이 먼저 보이는 사전작성 순서
- `계획 다음 표시`: 확인 뒤 계획적 재시도가 먼저 보이는 사전작성 순서

두 프로필은 실제 캐릭터 성격·감정·학습 결과가 아니라 화면용 정적 표시 변형입니다. 각 사례에는 사전작성된 비교 요약, 고정 합성 입력(`situation`, `observed_action`, `outcome`), 그리고 공통 경계가 함께 표시됩니다. 모든 제안은 사전정의 허용 목록(`pause_and_check`, `ask_for_support`, `retry_with_plan`) 안에 있으며, 외부 서비스·API 키·실제 사용자 데이터를 쓰지 않습니다.

## Boundary contract

모델 보고서, JSON API, 화면, 고정 합성 입력 패널은 하나의 순서 있는 canonical boundary/non-claim 목록을 공유합니다. 목록의 누락·추가·순서 변경·문구 변형은 읽기 전용 검증을 실패하게 합니다. 화면 검증은 HTML 태그·엔티티·공백만 정규화하며, 숨김 텍스트·의역·축약은 경계 표시의 근거로 인정하지 않습니다.

## Run

Python 3.12 이상에서 다음을 실행합니다.

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
python -m characterlab.webapp
```

브라우저에서 `http://127.0.0.1:8766/`을 엽니다. 사례별 JSON 비교 결과는 예를 들어 `http://127.0.0.1:8766/api/comparison?scenario=uncertain_next_step`에서 볼 수 있습니다. 허용된 사례 ID 이외의 값은 거부됩니다.

## Verify

```powershell
python -m unittest discover -s tests
git diff --check
```

## Optional local UI evidence

`docs/phase1_local_ui_observation.md` records the completed local observation and its evidence boundary. If a portfolio needs persisted screenshots, save the three local-only PNGs described in `docs/phase1_ui/README.md`, then inspect them without changing character data:

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
python -m characterlab.evidence --require-complete
```

The local homepage and `http://127.0.0.1:8766/api/evidence-status` show the same screenshot-evidence status without exposing a machine-specific file path. The functional static phase is marked `implemented`; a missing optional screenshot archive remains `확인 불가` and does not change the display, character, memory, authority, or action state.

To create the optional three-PNG archive locally with an installed Chrome, run:

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
python -m characterlab.capture
python -m characterlab.evidence --require-complete
```

The capture command starts an ephemeral loopback server, renders only the three fixed local scenarios in Chrome headless mode, refuses to overwrite existing captures, and performs no upload or character-state change.

## Scope

이것은 합성 경험에 따른 **기능적 대처 제안의 표시 순서**를 보여 주는 결정론적 데모입니다. 실제 감정, 성격, 의식, 인간 발달, 학습, 임상적 안전성의 증거가 아닙니다. This is not evidence of actual emotion, personality, consciousness, learning, or human development. 모든 비교는 읽기 전용이며 캐릭터 상태·기억·권한·외형을 바꾸지 않고, 행동을 실행하지 않습니다. 허용 목록도 임상적 또는 실제 안전을 보증하지 않습니다.
