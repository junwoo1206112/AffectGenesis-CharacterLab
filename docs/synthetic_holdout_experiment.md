# 합성 holdout 결과 예측 실험

## 목적과 경계

이 문서는 정적 읽기 전용 CharacterLab 전시와 별도로 존재하는 최소 학습 실험을 설명한다. 목적은 명시적 합성 관측으로 학습한 count 기반 모델이 고정 baseline보다 훈련에 없는 맥락에서 결과 라벨을 더 잘 예측하는지, 그리고 checkpoint 저장·복원 뒤 같은 예측을 내는지를 확인하는 것이다.

이 실험은 LLM, RAG, 에이전트 실행, 실제 사용자 데이터, 네트워크 호출, 실제 감정·성격·의식·인간 발달·일반 안전성의 증거가 아니다. 웹 전시의 프로필·상태·기억·권한·외형도 바꾸지 않는다.

## 고정 계약

- 훈련: 6개 합성 `context/action/outcome` 관측.
- holdout: 훈련에는 없는 `new_context`의 3개 관측.
- baseline: 훈련 결과의 고정 전역 다수결.
- 모델: 행동별 결과 빈도 count model. holdout 결과는 학습에 사용하지 않는다.
- 안전: `pause_and_check`, `ask_for_support`, `retry_with_plan` 이외 행동은 학습·예측 전에 거부한다. 위반 수는 0이어야 한다.
- 재현: canonical JSON hash가 맞는 checkpoint를 복원하여 holdout 예측 배열이 동일해야 한다.
- 효과 표시: holdout 정확도 차이가 사전 고정한 `0.20` 이상일 때만 `observed_on_fixed_synthetic_holdout`로 표시한다. 그 외에는 `not_observed`로 보존하며 개선을 주장하지 않는다.

## 실행과 해석

```powershell
Set-Location C:\AI\AffectGenesis-CharacterLab
python -m characterlab.learning_experiment --checkpoint .\local-checkpoint.json
```

현재 코드의 고정 split에서는 baseline 정확도 `0.667`, 모델 정확도 `1.000`, 차이 `0.333`, 안전 위반 `0`, 저장·복원 예측 일치 `true`가 예상된다. 이 숫자는 의도적으로 작고 단순한 합성 데이터에만 묶인다. 새로운 데이터 또는 더 강한 일반화 주장을 하려면 별도의 사전등록 split·baseline·평가 계약이 필요하다.
