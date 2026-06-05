# AI Companion 개발 계획 및 기술 스택

작성일: 2026-06-03

관련 문서:

- `Docs/개발/02-Bottleneck-reuse-and-mobile-stack.md`
  - 병목 지점, PromptMotionLab 실제 코드 재사용 판단, Flutter/React Native/SwiftUI 비교 기준.
- `Docs/기획/16-Mobile-user-journey-and-screen-IA.md`
  - 첫 release 모바일 사용자 여정, 화면 IA, 화면 상태, UX acceptance criteria.
- `Docs/기획/17-Mobile-API-contract.md`
  - 모바일 API 계약, 공통 error/idempotency 규칙, endpoint별 책임.
- `Docs/기획/18-DB-schema-and-ledger-migration-plan.md`
  - PostgreSQL migration 수준의 테이블, 제약, 인덱스, transaction 기준.
- `Docs/기획/19-Date-event-rule-spec.md`
  - 첫 release 3개 date event의 rule engine 구현 기준.
- `Docs/기획/20-Credit-plan-allowance-policy.md`
  - Free/Plus/Premium/Credit/Ads 제공량과 실패/환불 정책.
- `Docs/기획/21-Admin-minimum-screen-spec.md`
  - 첫 release 필수 admin 화면, RBAC, audit, moderation 기준.
- `Docs/기획/22-Airi-character-profile-v1.md`
  - Airi personality, tone, safety, voice, visual profile 기준.
- `Docs/기획/23-Relationship-memory-rule-table.md`
  - relationship update, level progression, memory extraction/retrieval 기준.
- `Docs/기획/24-Commercial-development-readiness-audit.md`
  - 개발 착수/상용 출시/100k 확장 readiness 점검 기준.
- `Docs/기획/25-OpenAPI-Pydantic-schema-plan.md`
  - FastAPI/Pydantic schema naming, enum, DTO, OpenAPI contract test 기준.
- `Docs/기획/26-Backend-skeleton-service-boundary-plan.md`
  - backend skeleton layout, service/repository/provider boundary, transaction/test 기준.
- `Docs/기획/27-Scale-load-test-SLO-capacity-plan.md`
  - 100k+ 확장을 고려한 load test, SLO, autoscaling, DB/provider capacity 기준.
- `Docs/기획/28-Store-legal-privacy-launch-checklist.md`
  - Store policy, legal/privacy, AI disclosure, deletion, subscription/credit launch checklist.
- `Docs/기획/29-Provider-evaluation-cost-simulation-plan.md`
  - LLM/STT/TTS/image provider benchmark, cost/user/day, plan margin simulation 기준.
- `Docs/기획/30-Production-ops-security-observability-analytics-plan.md`
  - Production ops, security, observability, analytics, deployment, incident/backup 기준.
- `Docs/기획/31-Mobile-admin-wireframe-design-system-spec.md`
  - Mobile/admin wireframe, component baseline, design token, permission copy, store screenshot 기준.
- `Docs/기획/32-QA-test-release-verification-plan.md`
  - Unit/integration/mobile/billing/safety/provider/load QA, release evidence, blocker 기준.
- `Docs/기획/33-Commercial-v1-decision-register.md`
  - PM/engineering decision register, development defaults, beta/commercial launch blockers.
- `Docs/개발/03-Modular-monolith-and-service-boundary.md`
  - Python/FastAPI modular monolith 개발 규칙, service boundary, future split 기준.

## 목적

이 문서는 `Docs/기획`의 상용 서비스 기획을 실제 개발 기준으로 바꾸기 위한 1차 개발 계획이다.

첫 릴리즈는 "기능을 많이 넣는 앱"이 아니라, 다음 핵심 루프가 실제로 동작하는 상용형 MVP를 목표로 한다.

```text
사용자 진입
-> Airi와 chat
-> 기억/관계 상태 반영
-> date event 제안
-> deterministic mini-game/event 진행
-> 관계 상태/보상 갱신
-> reward gallery / diary / memory에 누적
-> 다음 접속에서 기억과 관계 변화 반영
```

## 첫 릴리즈 범위

### 포함

- Airi 1명
- Chat-first UX
- 짧은 voice input
- 제한된 TTS
- 3개 official date event
- 8~12단계 relationship level
- affinity, trust, mood 중심 관계 상태
- memory summary 3~5개부터 시작
- weekly/basic image reward
- Airi diary/note
- Free/Plus/Premium/Credit 구조
- rewarded ad 보상 구조
- credit ledger
- provider usage/cost logging
- basic admin ops
- report/block/delete request
- store-safe romantic/suggestive 수위

### 제외

- UGC marketplace
- video generation
- live voice call
- multi-character world
- custom character marketplace
- self-hosted LLM
- explicit adult content
- LLM 기반 게임 판정/보상 판정

## 핵심 개발 원칙

1. LLM은 대화, 감정 반응, 힌트, diary, memory summary만 담당한다.
2. 게임 결과, 점수, reward unlock, credit 차감은 rule engine과 ledger가 담당한다.
3. 모든 고비용 기능은 quota, credit, provider usage logging을 먼저 통과한다.
4. credit은 단순 balance update가 아니라 append-only ledger로 관리한다.
5. provider는 교체 가능한 adapter 구조로 둔다.
6. image, TTS, memory extraction은 queue 기반 async job으로 처리한다.
7. admin access, credit 조정, moderation 처리는 audit log를 남긴다.
8. Free는 핵심 재미를 보여주되 high-cost 기능은 hard cap으로 보호한다.

## 권장 기술 스택

### Mobile app

권장: Flutter

이유:

- iOS/Android 동시 출시 속도가 빠르다.
- chat, gallery, shop, subscription, voice button 중심 UI에 적합하다.
- 초기 팀 규모가 작을 때 native iOS/Android를 각각 운영하는 비용을 줄일 수 있다.

대안:

- React Native: 웹/TypeScript 인력이 강하면 선택 가능.
- Native iOS/Android: 성능과 플랫폼 UX는 좋지만 초기 개발/운영 비용이 크다.

초기 판단:

```text
Flutter 우선.
단, live call을 첫 릴리즈에 넣지 않는다는 전제가 필요하다.
기존 팀이 TypeScript/React Native에 강하면 React Native도 가능하다.
iOS-first premium 전략이면 SwiftUI도 검토한다.
```

### Backend API

권장: FastAPI + Python

이유:

- AI provider 연동, prompt orchestration, async job, Python SDK 사용성이 좋다.
- 기존 PromptMotionLab의 Python provider 구조를 참고하기 쉽다.
- Pydantic 기반 request/response schema 관리가 명확하다.

대안:

- NestJS + TypeScript: 대규모 백오피스/API 조직에는 좋지만 AI provider 실험 속도는 Python보다 느릴 수 있다.

초기 판단:

```text
FastAPI 우선.
API contract와 service layer를 분리해서 추후 일부 서비스를 Node/NestJS로 분리 가능하게 둔다.
```

### Database

권장: PostgreSQL

이유:

- user, relationship, message, ledger, subscription, admin audit log를 안정적으로 처리할 수 있다.
- pgvector를 붙이면 초기 memory search를 별도 vector DB 없이 시작할 수 있다.

필수 설계:

- credit_ledger는 append-only
- messages는 장기적으로 partitioning 고려
- memories는 원문 대화와 summary를 분리
- admin_audit_logs는 모든 운영자 조작에 연결

### Cache / Queue

권장:

- Redis: rate limit, session cache, short-lived job state
- Celery 또는 RQ: 초기 async worker

추후 scale:

- Redis Queue 한계가 보이면 RabbitMQ, SQS, Pub/Sub, Kafka 중 실제 트래픽에 맞춰 전환

초기 queue:

- chat_turn_queue
- tts_queue
- image_generation_queue
- memory_extraction_queue
- moderation_queue

### Object storage / CDN

권장:

- S3 호환 storage 또는 Azure Blob Storage
- Cloudflare CDN 또는 cloud-native CDN

저장 대상:

- reward image
- TTS audio
- generated media
- moderation 대상 asset

원칙:

- DB에는 binary를 저장하지 않고 storage URI와 moderation status만 저장한다.
- media 접근은 signed URL 기반으로 제한한다.

### AI providers

초기 권장:

- LLM: OpenAI low-cost/standard route
- STT: OpenAI 또는 ElevenLabs/Azure 비교 후 선택
- TTS: ElevenLabs 우선 검토, 비용 절감을 위해 Azure/Google fallback 검토
- Image: OpenAI Image 또는 별도 image provider 1개 이상 비교

provider route 예시:

```text
short_social -> low-cost LLM
default_chat -> standard LLM
date_event_reaction -> standard LLM
memory_extraction -> low-cost LLM or rule-assisted LLM
media_prompt -> standard LLM
```

주의:

- provider 가격과 정책은 바뀔 수 있으므로 출시 전 공식 가격/정책 재확인이 필요하다.
- 특정 provider에 종속되지 않도록 interface와 usage logging을 먼저 만든다.

### Admin / Backoffice

초기 권장:

- 내부 admin web: React + Vite 또는 Next.js
- API는 backend admin route로 분리

최소 화면:

- user lookup
- credit ledger viewer
- provider cost dashboard
- queue monitor
- moderation review
- admin audit log viewer

초기에는 미려한 UI보다 운영 사고를 막는 기능이 우선이다.

### Monitoring / Logging

초기 필수:

- structured application log
- provider_usage_events
- request_id / user_id / feature route 추적
- queue backlog metric
- p50/p90 latency
- provider failure/fallback rate
- cost per user/day

권장 도구:

- Sentry: client/backend error
- OpenTelemetry: trace 기반 확장
- Grafana/Prometheus 또는 cloud monitoring

## 서버 모듈 구조 초안

```text
app/
  api/
    routes/
      auth.py
      chat.py
      characters.py
      relationship.py
      memories.py
      date_events.py
      rewards.py
      media.py
      credits.py
      billing.py
      reports.py
      admin.py
  services/
    chat_orchestrator.py
    character_dialogue_service.py
    relationship_state_service.py
    memory_service.py
    date_event_service.py
    game_rule_engine.py
    reward_unlock_service.py
    credit_ledger_service.py
    quota_service.py
    media_generation_service.py
    safety_service.py
    provider_usage_service.py
  providers/
    llm/
    stt/
    tts/
    image/
  workers/
    tts_worker.py
    image_worker.py
    memory_extraction_worker.py
    moderation_worker.py
  models/
  schemas/
  repositories/
  admin/
```

원칙:

- API route는 request/response와 auth/rate limit만 담당한다.
- business logic은 service layer에 둔다.
- DB 접근은 repository로 분리한다.
- provider API key는 server-side에서만 사용한다.

## 주요 데이터 모델

1차 구현 대상:

- users
- user_devices
- characters
- personality_profiles
- conversations
- messages
- character_relationship_snapshots
- relationship_events
- memories
- date_event_templates
- date_game_sessions
- game_moves
- reward_events
- media_assets
- subscriptions
- credit_ledger
- provider_usage_events
- admin_audit_logs
- safety_events

먼저 구현해야 할 모델:

```text
users
characters
character_relationship_snapshots
relationship_events
conversations
messages
memories
credit_ledger
provider_usage_events
admin_audit_logs
```

## API 개발 순서

### Phase 0: 개발 기반

- 프로젝트 skeleton
- env/config 구조
- DB migration
- auth/session skeleton
- provider adapter interface
- logging/request_id
- 테스트 구조

검증:

- local server boot
- health check
- migration apply/rollback
- basic unit test

### Phase 1: 상태/ledger 기반

- users
- characters
- relationship snapshot/event
- conversations/messages
- credit ledger
- provider usage events
- admin audit logs

검증:

- credit ledger idempotency
- relationship event -> snapshot 반영
- provider usage event 기록

### Phase 2: Chat + memory

- `POST /chat/turn`
- CharacterDialogueService
- ChatOrchestrator
- MemoryService
- relationship state injection
- short memory summary

검증:

- Airi 말투 QA
- 같은 사용자에게 memory 반영
- token/cost logging
- fallback response

### Phase 3: Date event + rule engine

- date event template 3개
- event start/move/finish API
- deterministic result
- relationship delta
- reward unlock event

검증:

- LLM이 결과를 바꾸지 못함
- 같은 입력은 같은 rule 결과를 냄
- reward/relationship 기록이 DB에 남음

### Phase 4: TTS/image/reward

- TTS job queue
- image reward job queue
- media asset status
- reward gallery API
- moderation status

검증:

- provider 실패 시 pending/retry/fallback
- credit 차감/환불 기준
- media asset 접근 제한

### Phase 5: monetization

- plan/quota service
- Free/Plus/Premium allowance
- credit purchase skeleton
- rewarded ad reward skeleton
- subscription webhook skeleton

검증:

- Free hard cap
- paid allowance 우선순위
- duplicate webhook/idempotency

### Phase 6: admin/safety

- user lookup
- credit ledger viewer
- provider cost dashboard
- moderation review
- report/block
- memory delete
- account deletion request

검증:

- admin action audit log
- report -> moderation queue
- memory delete 반영

## 모바일 화면 우선순위

모바일 화면 IA는 `Docs/기획/16-Mobile-user-journey-and-screen-IA.md`를 기준으로 한다.

1. onboarding / age gate
2. main chat
3. voice button / TTS playback
4. relationship status
5. date event entry
6. date event play screen
7. reward gallery
8. memory / Airi note
9. shop / subscription / credit
10. settings / privacy / report

첫 화면 구성:

```text
main chat
-> Airi greeting with remembered context
-> visible voice button
-> small relationship level/status
-> today's date/reward hint
```

하단 탭:

```text
Chat
Date
Rewards
Profile
```

Shop은 독립 탭으로 두지 않는다. quota 초과, reward 잠금, Profile plan 영역에서 진입시킨다.

각 화면은 정상 상태만 구현하면 안 된다. 다음 상태는 첫 release에서 UI/API/DB 상태값으로 연결되어야 한다.

- chat sending/thinking/streaming/provider degraded/quota exceeded/safety blocked
- voice permission needed/recording/processing/failed/limit reached
- TTS pending/ready/failed
- date session active/expired/finished/duplicate finish
- reward locked/progress/pending/unlocked/rejected
- payment pending/webhook delayed/duplicate purchase
- memory extraction delayed/delete pending

## 정책/안전 기준

첫 릴리즈 수위:

- store-safe romantic/suggestive maximum
- explicit adult content 제외
- minor-like character 금지
- generated media moderation 필수
- report/block/delete path 제공

필수 safety flow:

```text
user input
-> precheck
-> normal / soft-safe / crisis route
-> LLM response
-> post-validation
-> safety event log
```

## 비용 보호 장치

MVP부터 필요한 cap:

- user daily LLM turns
- user daily voice seconds
- user daily/monthly TTS characters
- weekly/monthly image reward count
- provider daily/monthly budget
- feature route cost cap
- free user total monthly cap

kill switch:

- free image generation pause
- TTS downgrade/text-only fallback
- expensive model route downgrade
- provider fallback disable/enable
- image queue pause
- rewarded ad credit reward 조정

## 검증 기준

Product:

- Free 사용자가 핵심 재미를 체감하는가
- Airi가 이전 대화/이벤트를 기억하는가
- date event 결과가 관계/보상으로 이어지는가
- reward가 단순 갤러리가 아니라 관계 루프와 연결되는가

Engineering:

- p50/p90 latency 측정 가능
- provider failure fallback 가능
- credit ledger 검증 가능
- admin audit log 기록
- queue backlog 확인 가능
- smoke/regression test 존재

Cost:

- cost/user/day 측정 가능
- plan별 gross margin 계산 가능
- provider별 spend 추적 가능
- heavy user top 1% 비용 확인 가능

Safety:

- report/block 가능
- memory delete 가능
- account deletion request 가능
- media moderation 가능
- crisis response route 존재

## 다음 작업

현재 구현 상태:

- `Server/` backend skeleton 생성 완료.
- FastAPI app factory 생성 완료.
- settings/config 생성 완료.
- request_id middleware 생성 완료.
- JSON structured logging 생성 완료.
- `/health`, `/ready`, `/api/mobile/v1/app/bootstrap` smoke endpoint 생성 완료.
- SQLAlchemy base와 Alembic skeleton 생성 완료.
- mock LLM provider interface 생성 완료.
- `/api/mobile/v1`, `/api/admin/v1`, `/api/webhooks/v1` prefix boundary 생성 완료.
- guest auth/session persistence 생성 완료.
- `users`, `user_sessions` SQLAlchemy model과 Alembic migration 생성 완료.
- character, conversation/message, relationship snapshot/event, memory, credit ledger, provider usage, admin audit log 최소 SQLAlchemy model과 Alembic migration 생성 완료.
- bootstrap endpoint 인증 적용 완료.
- Airi character seed와 사용자별 초기 relationship snapshot을 보장하는 authenticated bootstrap 확장 완료.
- authenticated `POST /api/mobile/v1/chat/turn` mock provider, conversation/message persistence 구현 완료.
- mock chat turn provider usage event logging과 assistant message 연결 완료.
- chat 기반 first relationship event/snapshot update와 preference memory candidate 생성 완료.
- credit ledger grant/spend/refund/replay service와 daily quota counter 기반 chat text_turn 제한 구현 완료.
- 3개 official date event list/start/move/finish, deterministic rule scoring, relationship/reward event output 구현 완료.
- memory list/activate/delete API와 DB-backed memory_extraction async job skeleton 구현 완료.
- admin auth dependency skeleton 생성 완료.
- billing webhook signature skeleton 생성 완료.
- pytest smoke test 통과.
- modular monolith/service boundary 기준은 `03-Modular-monolith-and-service-boundary.md`를 따른다.

다음 구현 순서:

1. reward/media async job skeleton 구현
2. billing webhook -> credit ledger integration 구현
3. admin minimum backend/API 구현
4. provider cost dashboard data path 구현
5. provider benchmark/cost simulation 실행
6. chat/write idempotency replay 저장 구조 보강
7. store/legal/privacy launch checklist 반영
8. production ops/security/observability/analytics baseline 구현
9. mobile/admin UI baseline 구현
10. QA/release verification baseline 구현
11. PM/engineering decision register 반영

PromptMotionLab 재사용은 `02-Bottleneck-reuse-and-mobile-stack.md`의 판단을 따른다. 특히 provider routing, Airi profile, timeout/fallback, segmented TTS, latency metric은 우선 재사용 후보이고, in-memory session/job/audio/CSV 구조는 상용 서비스용으로 재설계한다.

## 개발 판단

현재 기획은 상용 서비스 개발로 진행 가능하다. 다만 첫 개발 목표는 "AI companion 전체 플랫폼"이 아니라 "Airi 1명으로 관계 progression + date event + reward/media + memory loop가 검증되는 모바일 상용형 MVP"여야 한다.

이 루프가 검증되기 전에는 캐릭터 확장, UGC, video, live call, custom marketplace를 개발하지 않는다.
