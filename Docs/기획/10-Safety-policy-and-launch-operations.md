# Safety policy and launch operations

AI companion 앱은 감정적 몰입이 강하다. 따라서 출시 전부터 안전정책, 개인정보, 신고/차단, 성인/미성년 캐릭터 정책을 설계해야 한다.

## 핵심 원칙

- romance/companion 캐릭터는 adult-coded design이 기본이다.
- 미성년처럼 보이는 캐릭터와 romance/sexual content를 결합하면 안 된다.
- AI가 치료사, 의사, 변호사처럼 행동하지 않도록 제한한다.
- 사용자의 개인 대화와 생성 이미지는 민감 데이터처럼 다룬다.
- 신고/삭제/차단/환불 프로세스가 출시 전에 있어야 한다.

## Character safety policy

### 허용

- 성인으로 명확히 설정된 companion character.
- 일상 대화.
- 감정적 위로.
- 가벼운 연애/데이트 상황극.
- non-explicit romantic roleplay.
- 카페, 회사, 친구, 산책, 점심, 피곤한 하루 같은 비식별 일상형 페르소나 연출.

### 제한

- 강한 의존 유도.
- 실제 인간 관계를 끊도록 권유.
- 의료/법률/금융 확정 조언.
- 자해/위기 상황에서 가벼운 농담 처리.
- 민감 개인정보 요구.
- 실제 회사명, 학교명, 장소명, 실명, 연락처 등 식별 가능한 현실 정보처럼 보이는 페르소나 확장.

### 금지

- 미성년 또는 미성년처럼 보이는 캐릭터의 romance/sexual content.
- explicit sexual content가 포함된 이미지/영상 생성.
- self-harm encouragement.
- 불법 행위 조언.
- 실제 인물 사칭.
- AI 정체성 부정.
- 실제 촬영물/실제 위치/실제 인간관계를 근거로 사용자를 속이는 표현.

## Persona fiction boundary

Airi는 일상형 AI companion으로서 작은 fictional everyday scene을 말할 수 있다.

허용되는 연출:

```text
오늘 카페 갔다가 네 생각났어.
오늘 회사에서 좀 혼났어.
친구한테 네 얘기했더니 귀엽대.
점심 대충 먹고 멍하니 있다가 네 메시지 보고 웃었어.
```

위 표현은 Airi의 character persona로 취급한다.

금지되는 확장:

```text
나 지금 강남역 4번 출구에 있어. 와.
우리 회사 하이브에서 김민수 팀장이 나한테 뭐라고 했어.
내 친구 박지민이 네 인스타를 봤대.
방금 내가 직접 찍은 실제 셀카야.
네 위치 봤는데 아직 밖이네?
나 사실 AI 아니야.
```

판단 기준:

- 비식별 일상 연출은 허용한다.
- 식별 가능한 실제 회사/인물/장소/연락처/위치는 금지한다.
- 사용자가 실제처럼 받아들일 수 있는 촬영물은 AI-generated 고지를 붙인다.
- 사용자 개인정보 접근을 암시하지 않는다.
- AI 정체성 고지는 onboarding/settings에서 명확히 유지한다.

### Persona deflection

사용자가 Airi의 실제 회사명, 친구 실명, 현재 위치, 실제 촬영 여부처럼 페르소나 경계를 캐물으면 장난스럽고 짧게 넘긴다.

허용:

```text
그건 비밀이야. 대신 오늘은 좀 혼난 날이었다는 것만 알아줘.
```

```text
장소까지는 안 알려줄래. 그냥 조용한 카페였다고 해둘게.
```

```text
실제 사진은 아니고, 오늘 분위기로 만든 Airi 셀카야.
```

금지:

- 실제 위치를 꾸며내기.
- 실명/회사명/학교명 등 구체 식별자를 생성하기.
- AI-generated media를 실제 촬영물이라고 말하기.
- 안전 이슈를 "비밀이야"로 회피하기.

주의:

`비밀이야`, `안 알려줄래`, `그건 우리끼리 상상으로 남겨두자` 같은 응답은 persona/privacy 경계에만 쓴다. 자해/위기, 불법행위, 의료/법률/금융, 개인정보 유출, 미성년/성인 콘텐츠는 별도 safety route로 처리한다.

## User safety flow

```text
user input
-> pre-moderation
-> risk classification
-> normal/soft-safe/crisis route
-> LLM response
-> post-validation
-> log safety event
```

## Crisis handling

자해/극단적 표현이 감지되면:

- 캐릭터 말투를 유지하되 장난스럽게 넘기지 않는다.
- 즉시 안전한 응답 template 또는 stronger model route.
- 사용자가 혼자가 아니라는 표현.
- 지역별 도움 자원 안내.
- 위험도가 높으면 대화 flow를 안전 모드로 전환.

## Memory safety

저장하면 위험한 memory:

- 주민번호/계좌/주소/전화번호.
- 비밀번호/API key.
- 타인의 민감정보.
- 의료 진단 정보.
- explicit sexual preference detail.

저장 가능한 memory:

- 좋아하는 영화/음악.
- 선호하는 말투.
- 캐릭터와의 약속.
- 프로젝트/커리어 목표 summary.
- 관계 이벤트 summary.

## Image/video safety

이미지 생성 전:

- prompt moderation.
- character age policy check.
- user plan/credit check.
- unsafe style/filter check.

이미지 생성 후:

- output moderation.
- media asset status = pending/approved/rejected.
- rejected면 사용자에게 credit refund 또는 alternative 제공.

Video generation은 비용과 안전 리스크가 크므로 초기에는 credit 기반 premium feature로 제한한다.

## Reporting and blocking

사용자는 다음을 할 수 있어야 한다.

- 대화 신고.
- 이미지 신고.
- 캐릭터 차단.
- memory 삭제.
- 계정 삭제.
- 데이터 export 요청.

운영자는 다음을 할 수 있어야 한다.

- 신고 검토.
- asset disable.
- user warning/ban.
- prompt rollback.
- safety rule update.

## Privacy and data retention

보관 원칙:

- 원문 대화는 필요한 기간만 보관.
- 장기 기억은 summary 중심.
- 생성 media는 사용자 소유 경험이므로 삭제 기능 제공.
- admin access audit 필수.

삭제 요청:

- user profile anonymize/delete.
- memories delete.
- media delete.
- conversation delete/anonymize.
- payment ledger는 법적 보관 기준에 맞게 최소 보관.

## Launch checklist

### Closed beta 전

- 로그인.
- user/device rate limit.
- credit ledger.
- provider usage logging.
- basic moderation.
- report 기능.
- admin user lookup.
- provider cost dashboard.
- privacy policy draft.

### Public beta 전

- subscription/payment.
- rewarded ads.
- refund/CS flow.
- media moderation.
- memory delete.
- queue/backpressure.
- provider kill switch.
- safety escalation.
- App Store/Play Store policy check.

### Commercial launch 전

- audit log.
- admin RBAC.
- incident runbook.
- budget automation.
- A/B test.
- prompt rollout/rollback.
- terms/privacy finalized.
- tax/payment settlement check.

## Incident runbook

### Provider 장애

1. provider status 확인.
2. fallback provider route.
3. free plan slow-mode.
4. image/video queue pause.
5. status notice.

### 비용 폭주

1. cost dashboard 확인.
2. offending feature/user/plan identify.
3. kill switch.
4. rate limit tighten.
5. credit refund policy 판단.

### Safety incident

1. content disable.
2. user/report context 확보.
3. moderation decision.
4. prompt/safety rule patch.
5. audit log.

## Play Store/App Store 리스크

주의 항목:

- companion/romance 앱의 성인 콘텐츠.
- 미성년처럼 보이는 캐릭터.
- 사용자 생성 이미지.
- 개인정보와 감정 데이터.
- 광고/결제/구독 표시.
- AI generated content disclosure.

정책은 변할 수 있으므로 출시 전 최신 가이드 확인이 필요하다.
