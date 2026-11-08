# v0.1.0 공개 기준점 receipt

이 문서는 공개된 `v0.1.0`을 사후에 수정하지 않고 확인하는 기록이다.

## 확인된 사실

- Release: [AffectGenesis CharacterLab v0.1.0](https://github.com/junwoo1206112/AffectGenesis-CharacterLab/releases/tag/v0.1.0)
- GitHub Release ID: `438182316`
- 공개 대상 commit: `0e5b3168e5dbd151841b184a7856f52af384d206`
- 로컬·원격 `v0.1.0` ref: 같은 commit을 직접 가리키는 **lightweight tag**
- 기존 Seed `seed_a94b82a398a0`: annotated tag를 요구했으므로 이 Release에 대해서는 **미충족**으로 남는다. 이 문서는 그 결과를 성공으로 바꾸지 않는다.
- 선행 CI: [Verify run 42466792273](https://github.com/junwoo1206112/AffectGenesis-CharacterLab/actions/runs/42466792273)의 Ubuntu/Windows Python 3.12 job이 성공했다.

## 새 receipt 계약

`python -m characterlab.release_receipt --require-complete`는 GitHub 상태를 바꾸지 않고, 현재 checkout의 `v0.1.0`이 위의 고정 SHA로 해석되는지 확인한다.

- lightweight와 annotated tag를 서로 같은 객체라고 주장하지 않는다. 결과에 `tag_object_type`과 `tag_kind`를 모두 출력한다.
- 허용 조건은 tag 종류가 `lightweight` 또는 `annotated`이고, dereference된 SHA가 고정 대상과 일치하는 것이다.
- tag 누락, 지원하지 않는 object type, SHA 불일치는 실패다.
- Release 공개 상태·본문·CI 결과는 이 로컬 명령의 범위 밖이다. 이 문서의 공개 URL·ID·CI 링크는 별도 공개 관측 기록이다.

## 한계와 비주장

이 receipt는 Git reference 결속만 재현한다. 실제 감정, 학습, 성격, 의식, 인간 발달, 임상적 적합성 또는 안전을 증명하지 않는다. 또한 현재 GitHub Release/tag를 삭제·이동·수정·재게시하지 않는다.
