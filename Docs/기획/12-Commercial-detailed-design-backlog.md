# Commercial detailed design backlog

이 문서는 상용앱 큰 구조 이후에 어떤 세부 설계를 어떤 순서로 해야 하는지 정리한다.

현재 `00~11` 문서는 **상용 제품/기술 방향의 1차 설계**다. 바로 개발에 들어가기에는 아직 API, DB, 운영툴, 결제, 안전정책의 세부 스펙이 부족하다.

## 결론

세부 설계는 지금 바로 가능하다. 다만 한 번에 전부 만들면 문서만 비대해지고 구현 우선순위가 흐려진다.

추천 순서:

1. Product scope lock
2. Mobile user journey and screen IA
3. DB schema
4. API contract
5. Queue/provider runtime
6. Credit/payment
7. Admin ops
8. Safety/moderation
9. Launch checklist

## 1. Product scope lock

결정된 것:

- 첫 상용 버전은 모바일 앱 기준으로 설계한다.
- 첫 release는 Airi 1명으로 시작한다.
- 첫 화면은 Chat 중심으로 간다.
- date mini-game은 첫 release에 넣되, 3개 official event로 제한한다.
- Free도 text/voice/TTS/memory/reward를 제한적으로 제공한다.
- explicit adult content는 제외하고 store-safe romantic/suggestive 범위로 제한한다.

기준 문서:

- `15-First-release-scope-decisions.md`
- `16-Mobile-user-journey-and-screen-IA.md`

아직 정해야 하는 것:

- plan별 allowance의 정확한 숫자.
- 3개 date event의 rule table.
- reward image 1장 평균 원가 기준 credit 가격.
- guest user의 memory/credit 보존 정책.
- age gate에서 미성년 사용자 처리 방식.

산출물:

- feature scope table
- plan별 allowance table
- first release user journey

첫 release user journey와 화면 IA는 `16-Mobile-user-journey-and-screen-IA.md`를 기준으로 한다.

## 2. Mobile user journey and screen IA

필요 문서:

- `16-Mobile-user-journey-and-screen-IA.md`

목표:

- 신규 사용자가 1분 안에 Airi와 첫 대화를 시작한다.
- 첫 세션 안에 memory/relationship/reward 연결을 체감한다.
- Chat, Date, Rewards, Profile 중심의 모바일 IA를 확정한다.
- quota, queue, provider degraded, moderation rejected 같은 예외 상태를 화면 설계에 포함한다.

주의:

- 화면 목록만으로는 개발 착수 기준이 되지 않는다.
- 각 화면은 목적, CTA, 상태, 서버 요구사항을 가져야 한다.
- Shop은 독립 홈이 아니라 quota/reward/plan 맥락에서 진입시키는 게 첫 release에 적합하다.

## 3. DB schema design

기준 문서:

- `07-Data-model-state-and-ledger-design.md`
- `18-DB-schema-and-ledger-migration-plan.md`

필요 문서:

- `users`
- `characters`
- `character_relationship_snapshots`
- `relationship_events`
- `conversations`
- `messages`
- `memories`
- `date_game_sessions`
- `reward_events`
- `media_assets`
- `subscriptions`
- `credit_ledger`
- `provider_usage_events`
- `admin_audit_logs`

세부까지 정해야 할 것:

- primary key
- index
- unique constraint
- deletion policy
- retention policy
- partitioning 필요 여부

`18-DB-schema-and-ledger-migration-plan.md`에서 first release migration phase, 주요 테이블 columns, constraints, indexes, transaction rules를 정의한다.

주의:

- credit ledger는 append-only로 설계해야 한다.
- 대화 원문과 장기 memory summary는 분리해야 한다.
- admin audit log는 나중에 붙이면 운영 리스크가 크다.

## 4. API contract

기준 문서:

- `17-Mobile-API-contract.md`

필요 API:

- auth/session
- chat turn
- streaming chat
- voice input
- TTS playback ticket
- character profile
- relationship state
- memory CRUD
- date event start/move/finish
- reward unlock
- media generation request/status
- credit balance/ledger
- subscription webhook
- report/block
- user deletion/export

각 API마다 정해야 할 것:

- request schema
- response schema
- error code
- idempotency key
- rate limit
- auth scope
- audit 필요 여부

`17-Mobile-API-contract.md`에서 첫 release 기준 공통 response/error, idempotency, chat, voice/TTS, date event, reward/media, credit/billing, report/delete endpoint 기준을 정의한다.

## 5. Queue and provider runtime

상용 구조에서는 expensive job을 모두 queue로 관리해야 한다.

Queue:

- chat_turn_queue
- voice_stt_queue
- tts_queue
- image_generation_queue
- video_generation_queue
- memory_extraction_queue
- moderation_queue

세부 설계:

- priority
- retry policy
- timeout
- dead letter queue
- provider fallback
- user notification
- queue backlog dashboard

## 6. Credit and payment

기준 문서:

- `20-Credit-plan-allowance-policy.md`

필요 설계:

- free daily allowance
- ad reward credit
- subscription allowance
- purchased credit
- refund flow
- chargeback flow
- Google Play billing webhook
- Apple IAP webhook
- fraud detection

위험:

- 사용자가 이미 결제했는데 credit 지급 실패.
- rewarded ad 중복 지급.
- provider 실패 시 credit refund 기준 모호.
- 구매 credit 만료 정책 미정.

## 7. Admin ops

기준 문서:

- `09-Admin-ops-tooling-and-backoffice.md`
- `21-Admin-minimum-screen-spec.md`

필요 화면:

- user lookup
- conversation inspector
- memory manager
- credit ledger viewer
- provider cost dashboard
- queue monitor
- moderation review
- prompt/version manager
- content/event manager
- payment/refund console

최소 출시 전 반드시 필요한 것:

- user lookup
- credit ledger viewer
- provider cost dashboard
- moderation review
- admin audit log

## 8. Safety and moderation

필요 설계:

- character age policy
- romantic content policy
- self-harm/crisis response
- image prompt moderation
- generated media moderation
- user report
- block
- memory deletion
- account deletion
- admin review SLA

상용앱에서 safety를 나중에 붙이면 안 된다. AI companion은 감정 몰입도가 높기 때문에 초기부터 정책이 있어야 한다.

## 9. Launch readiness

출시 전 checklist:

- latency p50/p90 측정
- provider cost/user/day 측정
- free user cost cap
- paid conversion tracking
- crash-free rate
- refund flow
- privacy policy
- terms
- AI generated content disclosure
- app store data deletion path
- incident runbook

## 지금 바로 다음에 할 작업

다음 단계 1순위는 문서 추가가 아니라 `backend skeleton 실제 생성`과 `PM open decision 확정`이다.

이유:

- `15`에서 첫 release scope가 정리되었고, `16`에서 user journey와 screen IA가 정리되었다.
- `17`에서 모바일 API 계약 초안이 정리되었다.
- `18`에서 DB schema/ledger migration 기준이 정리되었다.
- `19`에서 3개 date event rule 기준이 정리되었다.
- `20`에서 plan allowance/credit policy 기준이 정리되었다.
- `21`에서 admin minimum screen 기준이 정리되었다.
- `22`에서 Airi character profile v1 기준이 정리되었다.
- `23`에서 relationship/memory rule 기준이 정리되었다.
- `24`에서 개발 착수/상용 출시/100k 확장 readiness가 점검되었다.
- `25`에서 OpenAPI/Pydantic schema 기준이 정리되었다.
- `26`에서 backend skeleton/service boundary 기준이 정리되었다.
- `27`에서 100k+ 확장을 고려한 load test/SLO/capacity 기준이 정리되었다.
- `28`에서 store/legal/privacy launch checklist가 정리되었다.
- `29`에서 provider evaluation/cost simulation 기준이 정리되었다.
- `30`에서 production ops/security/observability/analytics 기준이 정리되었다.
- `31`에서 mobile/admin wireframe/design 기준이 정리되었다.
- `32`에서 QA/test/release verification 기준이 정리되었다.
- `33`에서 PM/engineering decision register와 launch blocker 기준이 정리되었다.
- 특히 chat/date/reward/memory/credit 흐름은 idempotency와 event log가 없으면 상용 운영에서 깨진다.

개발 착수 작업:

1. `26` 기준 backend skeleton 생성.
2. `25` 기준 Pydantic schema 작성.
3. `18` 기준 Alembic migration 작성.
4. `19` 기준 date rule engine 구현.
5. `23` 기준 relationship/memory service 구현.
6. `20` 기준 quota/credit ledger service 구현.
7. `21` 기준 admin minimum API 구현.
8. `29` 기준 provider benchmark/cost simulation 실행.
9. `28` 기준 store/legal/privacy launch checklist 반영.
10. `30` 기준 production ops/security/observability/analytics baseline 구현.
11. `31` 기준 mobile/admin UI baseline 구현.
12. `32` 기준 QA/release verification baseline 구현.
13. `33` 기준 PM/engineering decision register 반영.

PM 결정이 필요한 질문:

1. Plus/Premium 실제 가격을 placeholder로 개발할지, 출시 전까지 확정할지.
2. guest user의 memory/credit 계정 전환 정책.
3. 미성년 사용자를 age gate에서 차단할지, romance 기능 제한 모드로 보낼지.
4. purchased credit 만료/환불 정책.
5. admin 배포 방식을 내부 VPN/private app/cloud auth 중 무엇으로 잡을지.

위 항목의 개발 기본값과 launch blocker는 `33-Commercial-v1-decision-register.md`를 따른다.
