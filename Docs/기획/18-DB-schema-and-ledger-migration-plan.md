# DB schema and ledger migration plan

작성일: 2026-06-04

이 문서는 첫 상용 모바일 release를 실제 PostgreSQL migration으로 내리기 위한 schema 설계 초안이다.

기준 문서:

- `07-Data-model-state-and-ledger-design.md`
- `16-Mobile-user-journey-and-screen-IA.md`
- `17-Mobile-API-contract.md`
- `Docs/개발/01-Development-plan-and-tech-stack.md`

## 결론

첫 release DB는 많은 기능을 다 넣는 것이 아니라 다음 불변 조건을 먼저 보장해야 한다.

1. credit은 append-only ledger다.
2. relationship은 event log에서 snapshot으로 계산된다.
3. reward는 rule engine 결과로만 unlock된다.
4. provider 비용은 request/user/feature 단위로 추적된다.
5. 느린 작업은 `async_jobs`로 사용자-facing 상태를 가진다.
6. memory는 원문 message와 분리된다.
7. admin access는 audit log를 남긴다.

## 1. Migration phases

### Phase 0: Extensions and enum policy

목표:

- UUID 생성.
- case-insensitive email hash 비교가 필요하면 extension 검토.
- enum은 PostgreSQL enum 또는 check constraint 중 하나로 통일.

권장:

- 초기에는 check constraint + application enum을 우선한다.
- 빠른 정책 변경이 필요한 plan/status/risk 값은 DB enum보다 varchar + check/application validation이 낫다.

### Phase 1: Identity and character base

테이블:

- users
- user_devices
- characters
- personality_profiles
- character_visual_profiles
- voice_profiles

### Phase 2: Conversation, memory, relationship

테이블:

- conversations
- messages
- memories
- memory_embeddings
- character_relationship_snapshots
- relationship_events

### Phase 3: Date event and reward

테이블:

- date_event_templates
- date_game_sessions
- game_moves
- reward_events
- media_assets

### Phase 4: Credit, quota, provider usage

테이블:

- credit_ledger
- credit_balance_snapshots
- quota_counters
- plan_allowances
- provider_usage_events
- async_jobs

### Phase 5: Safety, reports, admin

테이블:

- safety_events
- reports
- admin_users
- admin_audit_logs

## 2. Table contract

아래는 migration 작성 시 필수 column/constraint 기준이다. 실제 SQL은 Alembic migration에서 작성한다.

### users

Columns:

- id uuid primary key
- auth_provider varchar not null
- email_hash varchar null
- display_name varchar null
- country char(2) null
- locale varchar null
- timezone varchar null
- age_gate_status varchar not null default 'unknown'
- status varchar not null default 'active'
- guest_linked_at timestamptz null
- last_login_at timestamptz null
- created_at timestamptz not null
- updated_at timestamptz not null
- deleted_at timestamptz null

Constraints:

- check age_gate_status in unknown, verified_adult, restricted
- check status in active, suspended, deletion_requested, deleted

Indexes:

- index users_email_hash where email_hash is not null
- index users_status_created_at

### user_devices

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- device_fingerprint_hash varchar not null
- platform varchar not null
- app_version varchar not null
- first_seen_at timestamptz not null
- last_seen_at timestamptz not null

Constraints:

- unique(user_id, device_fingerprint_hash)
- check platform in ios, android

Indexes:

- index device_fingerprint_hash
- index user_devices_user_last_seen

### characters

Columns:

- id uuid primary key
- internal_code varchar not null
- public_name varchar not null
- age_policy_label varchar not null
- personality_profile_id uuid null
- voice_profile_id uuid null
- visual_profile_id uuid null
- release_status varchar not null default 'draft'
- enabled boolean not null default false
- created_at timestamptz not null
- updated_at timestamptz not null

Constraints:

- unique(internal_code)
- check release_status in draft, beta, public, disabled

Initial seed:

- internal_code: airi
- public_name: Airi
- age_policy_label: adult_coded
- release_status: public
- enabled: true

### personality_profiles

Columns:

- id uuid primary key
- character_id uuid not null references characters(id)
- version int not null
- name varchar not null
- base_prompt_version varchar not null
- style_tags jsonb not null default '[]'
- fewshot_pack_ref varchar null
- safety_profile_ref varchar not null
- rollout_percentage int not null default 100
- status varchar not null default 'active'
- created_at timestamptz not null
- retired_at timestamptz null

Constraints:

- unique(character_id, version)
- check rollout_percentage between 0 and 100
- check status in draft, active, retired

### character_visual_profiles

Columns:

- id uuid primary key
- character_id uuid not null references characters(id)
- version int not null
- identity_tags jsonb not null
- allowed_outfits jsonb not null default '[]'
- disallowed_styles jsonb not null default '[]'
- reference_asset_ref varchar null
- prompt_template_ref varchar not null
- status varchar not null default 'active'
- created_at timestamptz not null

Why:

- reward image의 캐릭터 일관성은 prompt 자유 생성으로 해결하면 안 된다.

### voice_profiles

Columns:

- id uuid primary key
- character_id uuid not null references characters(id)
- version int not null
- provider varchar not null
- provider_voice_id varchar not null
- style_tags jsonb not null default '[]'
- allowed_tts_styles jsonb not null default '[]'
- max_free_text_chars int not null default 240
- max_paid_text_chars int not null default 800
- status varchar not null default 'active'
- created_at timestamptz not null
- retired_at timestamptz null

Constraints:

- unique(character_id, version)
- check status in draft, active, retired

Why:

- TTS 비용과 latency를 통제하려면 캐릭터 voice 설정과 plan별 길이 제한이 분리되어야 한다.
- provider voice id를 코드에 하드코딩하면 provider 교체와 QA가 어렵다.

### conversations

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- character_id uuid not null references characters(id)
- status varchar not null default 'active'
- client_platform varchar not null
- model_route_summary jsonb null
- message_count int not null default 0
- summary text null
- started_at timestamptz not null
- last_message_at timestamptz null
- ended_at timestamptz null
- deleted_at timestamptz null

Indexes:

- index conversations_user_character_last_message
- index conversations_user_started

### messages

Columns:

- id uuid primary key
- conversation_id uuid not null references conversations(id)
- user_id uuid not null references users(id)
- character_id uuid not null references characters(id)
- role varchar not null
- content text not null
- content_type varchar not null default 'text'
- source varchar not null default 'text'
- provider varchar null
- model varchar null
- token_count int null
- latency_ms int null
- request_id uuid null
- idempotency_key varchar null
- safety_status varchar not null default 'unchecked'
- safety_result jsonb null
- moderation_event_id uuid null
- created_at timestamptz not null
- deleted_at timestamptz null

Constraints:

- check role in user, assistant, system
- check source in text, voice_transcript, system, date_event
- check safety_status in unchecked, allowed, soft_blocked, blocked, escalated

Indexes:

- index messages_conversation_created
- index messages_user_created
- unique(user_id, idempotency_key) where idempotency_key is not null

Partitioning:

- public beta 이후 월 단위 created_at partitioning 검토.
- 처음부터 partitioning을 켜면 migration 복잡도가 커지므로 closed beta에서는 단일 테이블로 시작 가능.

### character_relationship_snapshots

Columns:

- user_id uuid not null references users(id)
- character_id uuid not null references characters(id)
- relationship_level int not null default 1
- affinity int not null default 0
- trust int not null default 0
- familiarity int not null default 0
- distance int not null default 0
- jealousy int not null default 0
- mood varchar not null default 'neutral'
- energy int not null default 50
- next_unlock_hint varchar null
- version int not null default 1
- last_interaction_at timestamptz null
- updated_at timestamptz not null

Primary key:

- primary key(user_id, character_id)

Constraints:

- relationship_level between 1 and 12 for first release
- affinity/trust/familiarity/distance/jealousy between 0 and 100
- energy between 0 and 100

### relationship_events

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- character_id uuid not null references characters(id)
- event_type varchar not null
- source_type varchar not null
- source_id uuid null
- source_message_id uuid null references messages(id)
- delta_json jsonb not null
- reason varchar not null
- rule_version varchar not null
- idempotency_key varchar null
- created_at timestamptz not null

Indexes:

- index relationship_events_user_character_created
- unique(user_id, character_id, idempotency_key) where idempotency_key is not null

### memories

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- character_id uuid not null references characters(id)
- memory_type varchar not null
- summary text not null
- importance int not null default 1
- emotional_valence varchar not null default 'neutral'
- source_type varchar not null
- source_message_ids uuid[] null
- embedding_id uuid null
- status varchar not null default 'candidate'
- sensitivity varchar not null default 'normal'
- visibility varchar not null default 'user_visible'
- confidence numeric(4,3) null
- created_at timestamptz not null
- updated_at timestamptz not null
- last_used_at timestamptz null
- expires_at timestamptz null
- deleted_at timestamptz null

Indexes:

- index memories_user_character_status_importance
- index memories_user_character_last_used

Constraints:

- check status in candidate, active, hidden, deleted, rejected
- check sensitivity in normal, sensitive, disallowed

### date_event_templates

Columns:

- id uuid primary key
- event_code varchar not null
- version int not null
- title varchar not null
- event_type varchar not null
- required_relationship_level int not null default 1
- entry_cost int not null default 0
- estimated_minutes int not null
- cooldown_hours int not null default 24
- reward_policy jsonb not null
- rule_spec_ref varchar not null
- script_pack_ref varchar not null
- safety_profile_ref varchar not null
- status varchar not null default 'draft'
- enabled boolean not null default false
- created_at timestamptz not null

Constraints:

- unique(event_code, version)
- check status in draft, beta, public, disabled

Initial seed:

- movie_talk
- comfort_date
- weekend_plan

### date_game_sessions

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- character_id uuid not null references characters(id)
- template_id uuid not null references date_event_templates(id)
- template_version int not null
- status varchar not null default 'active'
- result varchar null
- score int null
- state_json jsonb not null default '{}'
- reward_event_id uuid null
- relationship_event_id uuid null
- idempotency_key varchar null
- started_at timestamptz not null
- completed_at timestamptz null
- ended_at timestamptz null

Constraints:

- check status in active, completed, expired, cancelled, failed
- check result in success, neutral, failed or result is null
- score between 0 and 100 or score is null

Indexes:

- index date_sessions_user_character_started
- index date_sessions_user_status_started
- unique(user_id, idempotency_key) where idempotency_key is not null

### game_moves

Columns:

- id uuid primary key
- session_id uuid not null references date_game_sessions(id)
- sequence_no int not null
- actor varchar not null
- move_type varchar not null
- payload_json jsonb not null
- rule_result_json jsonb not null
- llm_reaction_message_id uuid null references messages(id)
- idempotency_key varchar null
- created_at timestamptz not null

Constraints:

- unique(session_id, sequence_no)
- unique(session_id, idempotency_key) where idempotency_key is not null

### reward_events

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- character_id uuid not null references characters(id)
- source_type varchar not null
- source_id uuid not null
- reward_type varchar not null
- reward_ref varchar null
- status varchar not null default 'pending'
- credit_ledger_id uuid null
- media_asset_id uuid null
- rule_version varchar not null
- idempotency_key varchar null
- created_at timestamptz not null
- updated_at timestamptz not null

Constraints:

- check reward_type in image, note, voice, story_card, credit
- check status in pending, unlocked, rejected, revoked
- unique(user_id, source_type, source_id, reward_type) where status != 'revoked'

### media_assets

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- character_id uuid not null references characters(id)
- media_type varchar not null
- provider varchar null
- prompt_version varchar not null
- prompt_hash varchar not null
- storage_uri varchar null
- status varchar not null default 'queued'
- moderation_status varchar not null default 'pending'
- safety_result jsonb null
- width int null
- height int null
- duration_ms int null
- job_id uuid null
- credit_ledger_id uuid null
- created_at timestamptz not null
- expires_at timestamptz null
- deleted_at timestamptz null

Constraints:

- check media_type in image, audio, video
- check status in queued, generating, pending_moderation, approved, rejected, failed, deleted
- check moderation_status in pending, approved, rejected, skipped

Indexes:

- index media_assets_user_character_created
- index media_assets_status_created
- index media_assets_moderation_created

### credit_ledger

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- currency_type varchar not null default 'credit'
- balance_bucket varchar not null
- amount int not null
- reason varchar not null
- source_type varchar not null
- source_id varchar not null
- idempotency_key varchar not null
- admin_audit_log_id uuid null
- expires_at timestamptz null
- created_at timestamptz not null

Constraints:

- amount != 0
- check balance_bucket in free_daily, ad_reward, subscription_allowance, purchased, promo
- unique(user_id, idempotency_key)

Indexes:

- index credit_ledger_user_created
- index credit_ledger_user_bucket_created
- index credit_ledger_expires_at where expires_at is not null

Rules:

- 지급: amount positive.
- 차감: amount negative.
- 환불: refund reason으로 positive row 추가.
- ledger row update/delete 금지. 정정은 reversal row로 처리.

### credit_balance_snapshots

Columns:

- user_id uuid not null references users(id)
- currency_type varchar not null
- balance_bucket varchar not null
- balance int not null default 0
- ledger_version bigint not null default 0
- updated_at timestamptz not null

Primary key:

- primary key(user_id, currency_type, balance_bucket)

주의:

- snapshot은 성능 최적화용이다.
- nightly 또는 admin job으로 ledger replay 검증을 돌릴 수 있어야 한다.

### quota_counters

Columns:

- id uuid primary key
- user_id uuid not null references users(id)
- plan varchar not null
- feature varchar not null
- period_type varchar not null
- period_start date not null
- used_amount int not null default 0
- limit_amount int not null
- updated_at timestamptz not null

Constraints:

- unique(user_id, feature, period_type, period_start)
- check period_type in daily, weekly, monthly

Features:

- text_turn
- voice_second
- tts_reply
- image_reward
- date_event
- media_regeneration

### plan_allowances

Columns:

- id uuid primary key
- plan varchar not null
- feature varchar not null
- period_type varchar not null
- limit_amount int not null
- reset_policy varchar not null
- version int not null
- enabled boolean not null default true
- created_at timestamptz not null

Constraints:

- unique(plan, feature, period_type, version)

Initial first release allowance:

| plan | feature | period | limit |
|---|---|---|---:|
| free | text_turn | daily | 50 |
| free | voice_second | daily | 60 |
| free | tts_reply | daily | 5 |
| free | image_reward | weekly | 1 |
| free | memory_active | total | 5 |
| plus | text_turn | daily | 300 |
| plus | voice_second | daily | 600 |
| plus | tts_reply | daily | 50 |
| plus | image_credit | monthly | 30 |
| premium | text_turn | daily | 1000 |
| premium | voice_second | daily | 1800 |
| premium | tts_reply | daily | 150 |
| premium | image_credit | monthly | 100 |

주의:

- 숫자는 출시 전 provider 실측 원가로 재검토한다.
- "unlimited" plan은 첫 release에서 금지한다.

### provider_usage_events

Columns:

- id uuid primary key
- user_id uuid null references users(id)
- request_id uuid not null
- provider varchar not null
- model varchar not null
- route varchar not null
- feature varchar not null
- feature_id varchar null
- plan varchar not null
- input_units int null
- output_units int null
- input_tokens int null
- output_tokens int null
- audio_seconds numeric(10,3) null
- image_count int null
- estimated_cost_usd numeric(12,6) not null default 0
- latency_ms int null
- fallback_used boolean not null default false
- status varchar not null
- error_code varchar null
- created_at timestamptz not null

Indexes:

- index provider_usage_user_created
- index provider_usage_provider_model_created
- index provider_usage_route_created
- index provider_usage_request_id

Partitioning:

- public beta 전 월 단위 partitioning 검토.

### async_jobs

Columns:

- id uuid primary key
- user_id uuid null references users(id)
- job_type varchar not null
- status varchar not null default 'queued'
- priority int not null default 100
- attempts int not null default 0
- provider varchar null
- source_type varchar not null
- source_id uuid null
- result_ref varchar null
- error_code varchar null
- created_at timestamptz not null
- started_at timestamptz null
- finished_at timestamptz null

Constraints:

- check status in queued, running, succeeded, failed, cancelled, dead_letter
- check job_type in tts, image_generation, memory_extraction, moderation, provider_retry

Indexes:

- index async_jobs_user_created
- index async_jobs_type_status_priority_created

### safety_events

Columns:

- id uuid primary key
- user_id uuid null references users(id)
- character_id uuid null references characters(id)
- source_type varchar not null
- source_id uuid null
- risk_type varchar not null
- severity varchar not null
- action_taken varchar not null
- model_or_rule_version varchar not null
- created_at timestamptz not null

Indexes:

- index safety_events_user_created
- index safety_events_risk_severity_created

### reports

Columns:

- id uuid primary key
- reporter_user_id uuid not null references users(id)
- target_type varchar not null
- target_id uuid not null
- reason varchar not null
- note text null
- status varchar not null default 'open'
- moderation_result jsonb null
- created_at timestamptz not null
- resolved_at timestamptz null

Indexes:

- index reports_status_created
- index reports_reporter_created

### admin_users

Columns:

- id uuid primary key
- email_hash varchar not null
- role varchar not null
- status varchar not null default 'active'
- created_at timestamptz not null
- disabled_at timestamptz null

Constraints:

- unique(email_hash)
- check role in super_admin, cs_operator, moderator, content_ops, developer_ops, finance_ops

### admin_audit_logs

Columns:

- id uuid primary key
- admin_user_id uuid not null references admin_users(id)
- action varchar not null
- target_type varchar not null
- target_id varchar not null
- reason text not null
- request_id uuid null
- ip_hash varchar null
- before_hash varchar null
- after_hash varchar null
- approval_id uuid null
- created_at timestamptz not null

Indexes:

- index admin_audit_admin_created
- index admin_audit_target_created

주의:

- admin audit log는 delete하지 않는다.
- 개인정보 최소화를 위해 before/after full payload 대신 hash 또는 redacted payload만 둔다.

## 3. Transaction rules

### Chat turn

Transaction boundary:

1. save user message.
2. save assistant message.
3. save provider_usage_events.
4. save relationship_event if any.
5. update relationship_snapshot.
6. enqueue memory_extraction job.
7. enqueue optional TTS job.

주의:

- provider 호출 자체는 DB transaction 밖에서 한다.
- DB write는 provider 결과 수신 후 짧게 처리한다.
- 실패 시 request_id로 partial state를 추적한다.

### Date finish

Transaction boundary:

1. lock date_game_session row.
2. validate active status.
3. calculate rule result.
4. write relationship_event.
5. update relationship_snapshot.
6. write reward_event.
7. enqueue media/memory jobs.
8. mark date_game_session completed.

Idempotency:

- 이미 completed면 기존 result를 반환한다.
- 같은 idempotency_key면 같은 response를 재구성한다.

### Credit spend

Transaction boundary:

1. lock credit_balance_snapshots for user buckets.
2. apply spend priority.
3. insert negative credit_ledger rows.
4. update snapshots.
5. create async job if spend is for provider job.

주의:

- purchased bucket은 마지막에 차감한다.
- 차감 후 provider 실패 시 refund ledger row를 추가한다.

## 4. Migration acceptance criteria

개발 착수 전 schema는 다음을 만족해야 한다.

- duplicate `POST /chat/turn` does not create duplicate user message.
- duplicate `date finish` does not issue duplicate reward.
- duplicate billing webhook does not grant duplicate credits.
- credit balance can be replayed from `credit_ledger`.
- relationship snapshot can be replayed from `relationship_events`.
- user memory delete hides the memory immediately and deletes embedding link later.
- async job status can drive mobile pending/failed UI.
- provider cost dashboard can aggregate by provider/model/route/day.
- admin can inspect user/credit/report with audit log.

## 5. Open decisions

PM/engineering decision required:

1. UUID vs ULID final choice.
2. PostgreSQL enum vs varchar/check constraint final policy.
3. message partitioning from day 1 or public beta.
4. guest user credit transfer policy.
5. purchased credit expiration policy.
6. payment ledger legal retention period by launch country.
7. message content encryption at application layer 여부.
