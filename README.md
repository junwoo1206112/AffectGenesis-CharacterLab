# AffectGenesis CharacterLab

`AffectGenesis CharacterLab`은 **고정된 합성 사례에서 안전한 대처 제안이 어떻게 표시되는지** 보여 주는 작은 로컬 포트폴리오 데모입니다. 사람처럼 실제 감정을 느끼는 AI, 자율 학습 캐릭터, 의식, 성격 또는 인간 발달을 구현하거나 증명하는 프로젝트가 아닙니다.

## 무엇을 볼 수 있나요?

세 개의 고정 합성 사례에서 같은 사전정의 허용 목록을 받는 두 표시 프로필을 나란히 비교합니다.

- **확인 우선 표시**: 상황 확인과 지원 요청을 먼저 보여 줍니다.
- **계획 다음 표시**: 상황을 확인한 뒤 계획적인 재시도를 먼저 보여 줍니다.

사례 전환은 URL로 이미 작성된 자료를 선택하는 동작일 뿐입니다. 화면은 입력을 저장하거나 계산하지 않고, 실제 행동을 실행하거나 캐릭터의 상태·기억·권한·외형을 변경하지 않습니다. 모든 제안은 `pause_and_check`, `ask_for_support`, `retry_with_plan`의 사전정의 허용 목록 안에 있습니다.

## 실행하기

Python 3.12 이상이 필요합니다. PowerShell에서 저장소 폴더로 이동한 뒤 아래 명령을 실행하세요.

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
python -m characterlab.webapp
```

명령을 실행한 창은 서버가 동작하는 동안 열어 둡니다. 그다음 브라우저에서 [http://127.0.0.1:8766/](http://127.0.0.1:8766/)을 여세요.

`사이트에 연결할 수 없음`이 보이면 서버가 실행 중이지 않거나 해당 포트를 다른 프로그램이 쓰는 상태입니다. 아래 중 하나로 확인할 수 있습니다.

```powershell
# 서버 준비 여부 확인
Invoke-WebRequest http://127.0.0.1:8766/healthz

# 포트 충돌을 피해서 임의 포트로 시작
python -m characterlab.webapp --port 0
```

두 번째 명령은 실제 포트 번호를 출력합니다. 출력된 `http://127.0.0.1:<포트>/` 주소를 브라우저에서 열면 됩니다. 사례별 JSON 비교 결과는 예를 들어 `http://127.0.0.1:8766/api/comparison?scenario=uncertain_next_step`에서 읽기 전용으로 볼 수 있습니다. 허용되지 않은 사례 ID와 변경 요청은 거부됩니다.

## 검증하기

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
python -m unittest discover -s tests
python -m characterlab.smoke
python -m characterlab.evidence --require-complete
python -m characterlab.release_receipt --require-complete
git diff --check
```

각 명령의 의미는 다음과 같습니다.

- `unittest`: 화면·API·읽기 전용 경계·문서 계약의 회귀를 확인합니다.
- `smoke`: 임시 loopback 서버에서 세 사례와 HTTP 읽기 전용 계약을 확인합니다.
- `evidence`: 저장된 UI PNG 세 장이 유효한지 확인합니다.
- `release_receipt`: 공개 `v0.1.0` tag가 고정 기준 commit으로 해석되는지 확인합니다.

## 공개 기준점과 Release

[v0.1.0 Release](https://github.com/junwoo1206112/AffectGenesis-CharacterLab/releases/tag/v0.1.0)는 공개 당시의 기준점으로 보존합니다. GitHub 웹에서 생성된 tag는 annotated tag가 아니라 **lightweight tag**이지만, 고정 commit으로 직접 해석됩니다. `python -m characterlab.release_receipt --require-complete`는 이 Git 결속을 확인하고 tag 형식을 숨기지 않고 출력합니다.

이전 annotated-tag 전용 Seed는 소급해 성공 처리하지 않고 미충족 상태로 남깁니다. 자세한 근거와 한계는 [v0.1.0 receipt 기록](docs/v0_1_0_release_receipt.md)에 있습니다.

## 자동 검증과 화면 증거

GitHub Actions는 push와 pull request마다 Ubuntu 및 Windows의 Python 3.12에서 전체 unittest, 임시 loopback HTTP smoke, commit diff 공백 검사를 실행합니다. 이 검증은 코드와 정적 HTTP 계약을 확인할 뿐, 실제 감정·학습·성격·의식·인간 발달·임상적 안전을 증명하지 않습니다.

로컬 화면 증거는 [관찰 기록](docs/phase1_local_ui_observation.md)과 세 장의 PNG로 보관합니다. 이 증거는 고정된 화면 렌더링만 보여 줍니다.

- [첫 실패 화면](docs/phase1_ui/blocked_first_attempt.png)
- [다음 단계가 불확실한 화면](docs/phase1_ui/uncertain_next_step.png)
- [계획된 재시도 화면](docs/phase1_ui/planned_retry.png)

Chrome이 설치된 환경에서는 아래 명령으로 기존 증거를 덮어쓰지 않는 별도 캡처 검증을 실행할 수 있습니다.

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
python -m characterlab.capture
python -m characterlab.evidence --require-complete
```

## 접근성 범위

정적 화면에는 건너뛰기 링크, 보이는 키보드 포커스, 선택 사례의 `aria-current="page"`, 좁은 화면용 레이아웃 규칙이 있습니다. 이는 제한된 소스 수준 기준이며, 전체 접근성 감사나 모든 기기·보조기술·WCAG 적합성을 뜻하지 않습니다.

## 라이선스와 범위

이 저장소의 원본 소스 코드, 문서, 로컬에서 생성한 UI 증거는 [MIT License](LICENSE)로 제공합니다. 향후 추가될 제3자 자료·데이터·상표·별도 귀속 자산에는 각각의 조건이 적용되며 이 저장소의 MIT 라이선스로 다시 허가되지 않습니다.

이 프로젝트는 합성 경험에 따른 **기능적 대처 제안의 표시 순서**를 보여 주는 결정론적·읽기 전용 데모입니다. 실제 감정, 학습, 성격, 의식, 인간 발달, 임상적 적합성 또는 일반 안전성의 증거가 아닙니다.
