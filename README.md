# AffectGenesis CharacterLab

작은 로컬 포트폴리오 데모입니다. **동일한 합성 상황**과 동일한 사전정의 허용 목록에서, 두 표시 프로필의 문구와 제안 순서만 나란히 비교합니다.

- `확인 우선 표시`: 확인·지원 요청이 먼저 보이는 사전작성 순서
- `계획 다음 표시`: 확인 뒤 계획적 재시도가 먼저 보이는 사전작성 순서

두 프로필은 실제 캐릭터 성격·감정·학습 결과가 아니라 화면용 정적 표시 변형입니다. 모든 제안은 사전정의 허용 목록(`pause_and_check`, `ask_for_support`, `retry_with_plan`) 안에 있으며, 외부 서비스·API 키·실제 사용자 데이터를 쓰지 않습니다.

## Run

Python 3.12 이상에서 다음을 실행합니다.

```powershell
python -m characterlab.webapp
```

브라우저에서 `http://127.0.0.1:8766/`을 엽니다. JSON 비교 결과는 `http://127.0.0.1:8766/api/comparison`에서 볼 수 있습니다.

## Verify

```powershell
python -m unittest discover -s tests -p "test_portfolio_*.py"
git diff --check
```

## Scope

이것은 합성 경험에 따른 **기능적 대처 제안의 표시 순서**를 보여 주는 결정론적 데모입니다. 실제 감정, 성격, 의식, 인간 발달, 학습, 임상적 안전성의 증거가 아닙니다. This is not evidence of actual emotion, personality, consciousness, learning, or human development. 모든 비교는 읽기 전용이며 캐릭터 상태·기억·권한·외형을 바꾸지 않고, 행동을 실행하지 않습니다. 허용 목록도 임상적 또는 실제 안전을 보증하지 않습니다.
