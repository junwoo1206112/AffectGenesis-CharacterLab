# AffectGenesis CharacterLab

작은 로컬 포트폴리오 데모입니다. 동일한 합성 캐릭터와 동일한 합성 실패·회복 경험을 두 조건으로 비교합니다.

- `unapproved_learning`: 기록된 경험을 인용하지 않는 고정 안전 대처
- `approved_learning`: 같은 기록을 읽기 전용으로 인용해 계획적 재시도를 추가한 대처

모든 제안은 미리 정의된 안전 대처(`pause_and_check`, `ask_for_support`, `retry_with_plan`)만 사용합니다. 이 앱은 외부 서비스·API 키·실제 사용자 데이터를 쓰지 않습니다.

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

이것은 합성 경험에 따른 **기능적 대처 제안**을 보여 주는 결정론적 데모입니다. 실제 감정, 의식, 인간 발달, 임상적 안전성의 증거가 아닙니다. This is not evidence of actual emotion, consciousness, or human development. `approved_learning`도 읽기 전용 비교 표식일 뿐 실제 캐릭터 상태, 권한, 외형을 자동으로 바꾸지 않습니다.
