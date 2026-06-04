# Data model, state, and ledger design

상용 AI companion 앱은 "대화"보다 **상태 관리**가 더 중요하다. 캐릭터가 기억하고, 관계가 변하고, reward가 unlock되고, 결제가 차감되는 구조는 모두 데이터 모델로 증명되어야 한다.

실제 PostgreSQL migration 수준의 테이블/제약/인덱스/transaction 기준은 `18-DB-schema-and-ledger-migration-plan.md`를 따른다.

## 핵심 원칙

- 사용자의 돈과 credit은 append-only ledger로 관리한다.
- 캐릭터 관계 상태는 계산 가능한 event log와 현재 snapshot을 함께 둔다.
- memory는 원문 대화와 분리해 summary/embedding/visibility를 관리한다.
- admin access는 audit log를 남긴다.
- 개인정보 삭제 요청에 대응할 수 있어야 한다.
- 모든 외부 결제/webhook/reward 지급/credit 차감은 idempotency key를 가진다.
- 모든 고비용 provider 호출은 provider_usage_events에 기록한다.
- 상태값은 문자열 free-form이 아니라 enum/check constraint 또는 application enum으로 제한한다.
- 대규모 트래픽을 고려해 messages, provider_usage_events, admin_audit_logs는 partitioning 가능성을 열어둔다.

## 공통 설계 규칙

모든 주요 테이블 공통:

- `id`: UUID 또는 ULID. 외부 노출 가능성이 있으면 sequential integer를 피한다.
- `created_at`, `updated_at`: server time 기준.
- `deleted_at`: 개인정보/사용자 컨텐츠는 soft delete 후 background hard delete 가능.
- `request_id`: 외부 요청 추적이 필요한 event/log성 테이블에 저장.

권장 인덱스 원칙:

- 사용자 화면 조회는 `(user_id, created_at desc)` 기준 인덱스를 기본으로 둔다.
- character별 상태는 `(user_id, character_id)` composite key를 기본으로 둔다.
- ledger/event/log성 테이블은 `created_at` 기준 partitioning을 고려한다.
- admin 조회가 필요한 테이블은 user_id, status, created_at 조합을 둔다.

금지:

- balance, relationship level, reward state를 event 없이 직접 overwrite만 하는 구조.
- 결제 성공 처리와 credit 지급을 분리하면서 idempotency 없이 재시도하는 구조.
- 대화 원문과 장기 memory를 같은 테이블에 섞는 구조.
- provider 비용을 로그 파일에만 남기고 DB/metric으로 추적하지 않는 구조.

## 주요 엔티티

### users

사용자 기본 계정.

- id
- auth_provider
- email_hash
- display_name
- country
- age_gate_status
- created_at
- deleted_at

추가 권장:

- status: active, suspended, deletion_requested, deleted
- guest_linked_at
- last_login_at
- locale
- timezone

제약:

- `email_hash`는 nullable. guest user를 허용하기 때문이다.
- 계정 삭제 요청 후 payment/ledger 보관 대상과 personal data 삭제 대상을 분리해야 한다.

### user_devices

기기 식별과 abuse/rate limit에 사용.

- id
- user_id
- device_fingerprint_hash
- platform
- app_version
- first_seen_at
- last_seen_at

제약/인덱스:

- unique(user_id, device_fingerprint_hash)
- index(device_fingerprint_hash)
- index(user_id, last_seen_at desc)

주의:

- device fingerprint는 원문 저장하지 않고 hash만 저장한다.
- abuse/rate limit 목적 외 추적은 privacy policy와 맞아야 한다.

### characters

상용 캐릭터 정의.

- id
- public_name
- internal_code
- age_policy_label
- personality_profile_id
- voice_profile_id
- media_profile_id
- enabled

추가 권장:

- release_status: draft, beta, public, disabled
- safety_profile_id
- visual_profile_id
- default_relationship_profile_id

제약:

- unique(internal_code)
- index(enabled, release_status)

주의:

- 미성년처럼 보이는 캐릭터를 romance/sexual companion으로 운영하면 심사와 안전 리스크가 크다.
- 상용 앱은 adult-coded character policy가 필요하다.

### personality_profiles

캐릭터 말투/관점/금지 표현.

- id
- name
- base_prompt_version
- style_tags
- fewshot_pack_id
- safety_profile_id

추가 권장:

- version
- rollout_percentage
- created_by_admin_id
- retired_at

주의:

- prompt/profile 변경은 배포와 같으므로 versioning과 rollback이 필요하다.

### conversations

대화 세션.

- id
- user_id
- character_id
- started_at
- ended_at
- client_platform
- model_route_summary

추가 권장:

- status: active, closed, deleted
- last_message_at
- message_count
- summary

인덱스:

- index(user_id, character_id, last_message_at desc)
- index(user_id, started_at desc)

### messages

대화 원문.

- id
- conversation_id
- role
- content
- content_type
- provider
- model
- token_count
- latency_ms
- safety_result
- created_at

추가 권장:

- idempotency_key
- request_id
- source: text, voice_transcript, system, date_event
- safety_status: unchecked, allowed, soft_blocked, blocked, escalated
- moderation_event_id
- deleted_at

보관 정책:

- 원문 대화는 개인정보 위험이 있으므로 retention policy가 필요하다.
- 장기 기억은 원문 대신 summary 중심으로 저장하는 것이 안전하다.

인덱스/partition:

- index(conversation_id, created_at)
- index(user_id, created_at desc)는 denormalization 또는 conversation join 비용을 보고 결정한다.
- 대규모에서는 created_at 월 단위 partitioning을 검토한다.

주의:

- voice input 원본 audio는 messages에 직접 저장하지 않는다.
- message content 암호화 여부는 privacy/security 설계에서 결정한다.

### character_relationship_snapshots

현재 관계 상태 snapshot.

- user_id
- character_id
- affinity
- trust
- familiarity
- distance
- jealousy
- mood
- energy
- last_interaction_at
- updated_at

추가 권장:

- relationship_level
- next_unlock_hint
- version

제약:

- primary key 또는 unique(user_id, character_id)
- affinity/trust/familiarity 등 수치는 min/max constraint를 둔다.

주의:

- snapshot은 조회 최적화용이다. 원천은 relationship_events다.

### relationship_events

관계 변화 이벤트 로그.

- id
- user_id
- character_id
- event_type
- delta_json
- reason
- source_message_id
- created_at

추가 권장:

- source_type: chat, date_event, reward, absence, admin_adjustment
- source_id
- idempotency_key
- rule_version

인덱스:

- index(user_id, character_id, created_at desc)
- unique(user_id, character_id, idempotency_key) where idempotency_key is not null

예:

- daily_chat_completed
- comfort_given
- date_game_won
- date_game_failed
- user_absent_7_days
- reward_unlocked

### memories

장기 기억.

- id
- user_id
- character_id
- memory_type
- summary
- importance
- emotional_valence
- source_message_ids
- embedding_id
- visibility
- created_at
- expires_at
- deleted_at

추가 권장:

- status: candidate, active, hidden, deleted, rejected
- sensitivity: normal, sensitive, disallowed
- source_type: chat, date_event, onboarding, admin
- confidence
- last_used_at

인덱스:

- index(user_id, character_id, status, importance desc)
- index(user_id, character_id, last_used_at desc)

삭제:

- 사용자가 memory를 삭제하면 UI에서 즉시 hidden/deleted 처리한다.
- embedding과 source link도 background delete 대상에 넣는다.

memory_type 예:

- user_preference
- personal_fact
- relationship_moment
- promise
- boundary
- story_event

### memory_embeddings

Vector DB 또는 managed embedding store에 연결.

- id
- memory_id
- provider
- model
- vector_ref
- created_at

주의:

- embedding vector 원본을 DB에 둘지 pgvector에 둘지는 트래픽/운영 난이도로 결정한다.
- 삭제 요청 시 vector_ref도 삭제 가능해야 한다.

### date_event_templates

데이트형 콘텐츠 정의.

- id
- title
- event_type
- required_relationship_level
- entry_cost
- reward_policy_id
- script_pack_id
- enabled

추가 권장:

- version
- status: draft, beta, public, disabled
- estimated_minutes
- cooldown_policy_id
- safety_profile_id

제약:

- unique(event_type, version)
- public event는 immutable version으로 운영한다.

주의:

- 운영 중 template을 수정하면 기존 date_game_sessions의 재현성이 깨진다.
- 배포 후 수정은 새 version으로 만든다.

### date_game_sessions

실제 플레이 기록.

- id
- user_id
- character_id
- template_id
- started_at
- ended_at
- result
- score
- state_json

추가 권장:

- status: active, completed, expired, cancelled, failed
- template_version
- idempotency_key
- completed_at
- reward_event_id
- relationship_event_id

인덱스:

- index(user_id, character_id, started_at desc)
- index(user_id, status, started_at desc)

제약:

- 같은 user/template의 중복 active session을 막을지 정책 결정이 필요하다.

### game_moves

게임 내 선택/행동.

- id
- session_id
- actor
- move_type
- payload_json
- rule_result_json
- created_at

추가 권장:

- sequence_no
- idempotency_key
- llm_reaction_message_id

제약:

- unique(session_id, sequence_no)
- unique(session_id, idempotency_key) where idempotency_key is not null

LLM이 게임 판정을 직접 하면 안 된다. 게임 결과는 rule engine이 판단하고, LLM은 대사/감정/힌트만 맡는 것이 안전하다.

### reward_events

보상 발생 기록.

- id
- user_id
- character_id
- source_type
- source_id
- reward_type
- reward_ref
- created_at

추가 권장:

- status: pending, unlocked, rejected, revoked
- idempotency_key
- credit_ledger_id
- media_asset_id
- rule_version

인덱스/제약:

- index(user_id, character_id, created_at desc)
- unique(user_id, source_type, source_id, reward_type) where status != 'revoked'

주의:

- reward는 LLM 응답 문장만으로 지급하면 안 된다.
- rule engine과 ledger/event 기록이 원천이어야 한다.

### media_assets

이미지/음성/영상 보상.

- id
- user_id
- character_id
- media_type
- provider
- prompt_version
- storage_uri
- moderation_status
- created_at

추가 권장:

- status: queued, generating, pending_moderation, approved, rejected, failed, deleted
- job_id
- prompt_hash
- safety_result
- width
- height
- duration_ms
- credit_ledger_id
- expires_at
- deleted_at

인덱스:

- index(user_id, character_id, created_at desc)
- index(status, created_at)
- index(moderation_status, created_at)

주의:

- storage_uri는 public URL이 아니라 private object key 또는 signed URL 생성용 reference로 둔다.
- rejected asset은 사용자에게 노출하지 않는다.

### subscriptions

구독 상태.

- id
- user_id
- platform
- plan
- status
- started_at
- renews_at
- cancelled_at

추가 권장:

- platform_transaction_id
- original_transaction_id
- current_period_started_at
- current_period_ends_at
- grace_period_ends_at
- last_webhook_event_id

제약:

- unique(platform, platform_transaction_id)
- index(user_id, status)

주의:

- 앱스토어/플레이스토어 webhook은 중복/지연/역순 도착 가능성을 전제로 한다.

### credit_ledger

credit은 절대 단순 balance update만 하면 안 된다.

- id
- user_id
- currency_type
- amount
- balance_bucket
- reason
- source_type
- source_id
- idempotency_key
- expires_at
- created_at

balance는 ledger 합계로 계산하거나 materialized snapshot으로 캐시한다.

credit type:

- free_daily
- ad_reward
- subscription_allowance
- purchased
- promo

차감 우선순위:

1. free_daily
2. ad_reward
3. subscription_allowance
4. purchased

구매 credit은 법적/CS 이슈가 있으므로 만료 정책을 조심해야 한다.

추가 원칙:

- amount는 지급이면 양수, 차감이면 음수다.
- source_type/source_id는 결제, 광고, reward, provider job, admin adjustment와 연결한다.
- idempotency_key는 필수에 가깝게 본다. 운영자 수동 조정도 reason과 audit log가 필요하다.
- balance snapshot을 둘 경우 ledger replay와 정합성 검증 job이 필요하다.

권장 보조 테이블:

- credit_balance_snapshots
  - user_id
  - currency_type
  - balance_bucket
  - balance
  - updated_at
  - ledger_version

제약/인덱스:

- unique(user_id, idempotency_key) where idempotency_key is not null
- index(user_id, currency_type, created_at desc)
- index(expires_at) where expires_at is not null

환불 기준:

- provider 호출 전 실패: 차감하지 않는다.
- provider 호출 후 실패: 실패 원인과 media/job 상태에 따라 refund ledger를 추가한다.
- moderation rejected: 정책상 사용자 귀책이 아니면 refund 또는 alternative reward를 제공한다.

### provider_usage_events

AI 비용 추적.

- id
- user_id
- provider
- model
- feature
- input_units
- output_units
- estimated_cost_usd
- latency_ms
- request_id
- created_at

추가 권장:

- route
- feature_id
- plan
- input_tokens
- output_tokens
- audio_seconds
- image_count
- fallback_used
- error_code
- status: success, failed, timeout, cancelled

인덱스/partition:

- index(user_id, created_at desc)
- index(provider, model, created_at desc)
- index(route, created_at desc)
- created_at 기준 partitioning 검토.

주의:

- 비용 계산에 필요한 raw unit을 저장한다. estimated_cost_usd만 저장하면 가격 변경/재계산이 어렵다.

### admin_audit_logs

운영자 접근 기록.

- id
- admin_user_id
- action
- target_type
- target_id
- reason
- ip_hash
- created_at

추가 권장:

- request_id
- before_hash
- after_hash
- approval_id

제약/인덱스:

- index(admin_user_id, created_at desc)
- index(target_type, target_id, created_at desc)

주의:

- 대화 원문/이미지 열람은 action reason이 필수다.
- admin audit log는 삭제하지 않는 것을 원칙으로 한다. 단, 개인정보 최소화가 필요하다.

## 추가 필수 엔티티

### safety_events

정책/신고/차단/위기 대응 기록.

- id
- user_id
- character_id
- source_type
- source_id
- risk_type
- severity
- action_taken
- model_or_rule_version
- created_at

인덱스:

- index(user_id, created_at desc)
- index(risk_type, severity, created_at desc)

### reports

사용자 신고.

- id
- reporter_user_id
- target_type
- target_id
- reason
- note
- status: open, reviewing, resolved, rejected
- moderation_result
- created_at
- resolved_at

인덱스:

- index(status, created_at)
- index(reporter_user_id, created_at desc)

### quota_counters

일/월 단위 사용량 제한.

- id
- user_id
- plan
- feature
- period_type: daily, weekly, monthly
- period_start
- used_amount
- limit_amount
- updated_at

제약:

- unique(user_id, feature, period_type, period_start)

주의:

- Redis counter만 두면 장애/재시작/정산 추적이 어렵다.
- Redis는 fast path, DB는 reconciliation source로 둔다.

### async_jobs

TTS, image, memory extraction, moderation 작업 상태.

- id
- user_id
- job_type
- status: queued, running, succeeded, failed, cancelled, dead_letter
- priority
- attempts
- provider
- source_type
- source_id
- result_ref
- error_code
- created_at
- started_at
- finished_at

인덱스:

- index(user_id, created_at desc)
- index(job_type, status, priority, created_at)

주의:

- UI에서 pending/failed 상태를 보여주려면 job 상태가 조회 가능해야 한다.
- queue backend만 믿지 말고 사용자-facing job 상태를 저장한다.

### plan_allowances

플랜별 제공량 정의.

- id
- plan
- feature
- period_type
- limit_amount
- reset_policy
- enabled
- version

주의:

- 코드 상수만으로 관리하면 가격/정책 변경이 어렵다.
- 변경 이력과 rollout 기준이 필요하다.

## 상태 업데이트 흐름

```text
user message
-> safety precheck
-> memory retrieval
-> LLM response
-> behavior/reply validation
-> message save
-> memory extraction candidate
-> relationship event
-> relationship snapshot update
-> reward rule evaluation
-> credit/provider usage save
```

세부 원칙:

- message save와 provider_usage_events는 request_id로 연결한다.
- relationship event와 snapshot update는 같은 transaction 또는 재시도 가능한 job으로 처리한다.
- reward unlock과 credit 차감은 ledger/event를 먼저 기록하고 UI는 그 결과를 표시한다.
- memory extraction은 chat 응답 path에서 분리하고 async 처리한다.

## 100k 사용자 기준 데이터 리스크

대규모에서 먼저 커지는 테이블:

- messages
- provider_usage_events
- media_assets
- async_jobs
- credit_ledger
- admin_audit_logs

대응:

- messages/provider_usage_events/admin_audit_logs는 partitioning 기준을 미리 정한다.
- 오래된 원문 messages는 summary/memory와 분리해 retention 정책으로 관리한다.
- media binary는 DB에 저장하지 않는다.
- provider_usage_events는 cost 재계산 가능하도록 raw unit을 보존한다.
- ledger는 append-only라 커질 수 있으므로 user/time index와 snapshot cache가 필요하다.

상용 출시 전 검증:

- credit ledger replay로 balance 재계산 가능.
- relationship_events replay로 snapshot 재계산 가능.
- duplicate webhook/reward/date finish 재시도 시 중복 지급 없음.
- memory delete 시 embedding/source link 삭제 가능.
- account deletion request 후 payment ledger 최소 보관과 personal data 삭제가 분리됨.

## 삭제/개인정보 정책

사용자 삭제 요청 시:

- auth/user profile 삭제 또는 anonymize.
- messages 삭제 또는 anonymize.
- memories 삭제.
- media assets 삭제.
- provider logs는 저장하지 않는 방향이 가장 안전.
- credit/payment ledger는 법적 보관 기간에 맞춰 최소 정보만 보관.

## PromptMotionLab에서 재활용 가능한 부분

- CharacterProfile 구조.
- RuntimeCharacterService의 profile/state 개념.
- session conversation history 개념.
- provider usage/latency logging 방향.

재작성해야 하는 부분:

- in-memory session state.
- in-memory rate limit.
- 단순 session history.
- user authentication 없는 API 구조.
