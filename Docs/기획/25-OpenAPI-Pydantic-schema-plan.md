# OpenAPI and Pydantic schema plan

작성일: 2026-06-04

이 문서는 `17-Mobile-API-contract.md`를 실제 FastAPI/Pydantic schema로 구현하기 위한 naming, enum, DTO 기준을 정의한다.

기준 문서:

- `17-Mobile-API-contract.md`
- `18-DB-schema-and-ledger-migration-plan.md`
- `19-Date-event-rule-spec.md`
- `20-Credit-plan-allowance-policy.md`
- `23-Relationship-memory-rule-table.md`

## 결론

첫 backend skeleton에서는 모든 endpoint를 완성하지 않더라도, schema 명명과 공통 response/error/idempotency 계약은 처음부터 고정한다.

이유:

- 모바일 앱과 backend가 동시에 개발되면 response shape가 흔들리기 쉽다.
- credit/date/reward 계열 write API는 idempotency가 깨지면 운영 사고로 이어진다.
- OpenAPI spec이 흔들리면 Flutter client code generation과 QA가 늦어진다.

## 1. Package structure

권장 위치:

```text
app/
  schemas/
    common.py
    auth.py
    app_bootstrap.py
    characters.py
    chat.py
    voice.py
    tts.py
    memories.py
    date_events.py
    rewards.py
    media.py
    credits.py
    plans.py
    reports.py
    admin.py
```

원칙:

- DB model과 API schema를 섞지 않는다.
- request/response schema는 route layer에서만 사용한다.
- service layer는 내부 command/result DTO를 별도로 둘 수 있다.
- public mobile schema와 admin schema를 분리한다.

## 2. Common schema

### ApiMeta

Fields:

- request_id: UUID
- server_time: datetime

### ApiResponse[T]

Fields:

- data: T
- meta: ApiMeta

### ApiError

Fields:

- code: ErrorCode
- message: str
- retryable: bool
- details: dict[str, Any]

### ApiErrorResponse

Fields:

- error: ApiError
- meta: ApiMeta

### PageCursor

Fields:

- cursor: str | None
- limit: int

Constraints:

- limit min 1.
- limit max 100.

## 3. Shared enums

### ErrorCode

Values:

- UNAUTHENTICATED
- FORBIDDEN
- AGE_RESTRICTED
- QUOTA_EXCEEDED
- CREDIT_REQUIRED
- IDEMPOTENCY_CONFLICT
- SAFETY_BLOCKED
- PROVIDER_DEGRADED
- JOB_PENDING
- NOT_FOUND
- VALIDATION_ERROR
- INTERNAL_ERROR

### Platform

- ios
- android

### PlanCode

- free
- plus
- premium

### AgeGateStatus

- unknown
- verified_adult
- restricted

### CharacterEmotion

- warm
- playful
- concerned
- shy
- neutral

### AiriIntent

- chat
- date_invite
- comfort
- memory_recall
- reward_hint
- diary_note
- fallback
- soft_safe
- crisis_safe

### JobStatus

- queued
- running
- succeeded
- failed
- cancelled
- dead_letter

### RewardStatus

- locked
- progress
- pending
- unlocked
- rejected
- revoked

### MediaStatus

- queued
- generating
- pending_moderation
- approved
- rejected
- failed
- deleted

### DateSessionStatus

- active
- completed
- expired
- cancelled
- failed

### DateResult

- success
- neutral
- failed

## 4. Auth schemas

### DeviceContext

Fields:

- device_id: str
- platform: Platform
- app_version: str
- locale: str
- timezone: str

### CreateSessionRequest

Fields:

- auth_provider: Literal["guest", "apple", "google", "email"]
- provider_token: str | None
- device: DeviceContext

### UserSessionView

Fields:

- id: UUID
- status: str
- is_guest: bool
- age_gate_status: AgeGateStatus

### CreateSessionResponse

Fields:

- access_token: str
- refresh_token: str
- user: UserSessionView

### AgeGateRequest

Fields:

- birth_year: int
- country: str
- confirmation: bool

Constraints:

- birth_year reasonable range.
- country ISO-3166 alpha-2.

### AgeGateResponse

Fields:

- age_gate_status: AgeGateStatus
- romance_allowed: bool

## 5. Bootstrap schemas

### BootstrapUserView

Fields:

- id: UUID
- plan: PlanCode
- age_gate_status: AgeGateStatus

### BootstrapCharacterView

Fields:

- id: str
- name: str
- status: str

### RelationshipSummaryView

Fields:

- level: int
- affinity: int
- trust: int
- familiarity: int
- mood: str
- next_unlock_hint: str | None

### QuotaSummaryView

Fields:

- text_turns_remaining: int
- voice_seconds_remaining: float
- tts_replies_remaining: int
- image_rewards_remaining: int | None

### DailyHintView

Fields:

- greeting: str
- date_hint: dict[str, Any] | None
- reward_hint: dict[str, Any] | None

### AppBootstrapResponse

Fields:

- user: BootstrapUserView
- character: BootstrapCharacterView
- relationship: RelationshipSummaryView
- quota: QuotaSummaryView
- daily: DailyHintView

## 6. Chat schemas

### ChatInput

Fields:

- type: Literal["text", "voice_transcript"]
- text: str

Constraints:

- text min length 1.
- text max length by plan/quota service.

### ChatClientContext

Fields:

- screen: Literal["chat", "date_result"]
- local_time: datetime | None

### ChatTtsRequest

Fields:

- requested: bool
- style: Literal["warm", "soft", "playful", "careful"] | None

### ChatTurnRequest

Fields:

- character_id: str
- conversation_id: UUID | None
- input: ChatInput
- client_context: ChatClientContext
- tts: ChatTtsRequest | None

Headers:

- Idempotency-Key required.

### AiriReplyView

Fields:

- message_id: UUID
- text: str
- emotion: CharacterEmotion
- intent: AiriIntent

### RelationshipFeedbackView

Fields:

- changed: bool
- summary: str | None
- event_id: UUID | None

### MemoryFeedbackView

Fields:

- candidate_created: bool
- summary: str | None

### DateSuggestionView

Fields:

- event_id: str
- title: str

### ChatTurnResponse

Fields:

- conversation_id: UUID
- message_id: UUID
- reply: AiriReplyView
- relationship_feedback: RelationshipFeedbackView | None
- memory_feedback: MemoryFeedbackView | None
- date_suggestion: DateSuggestionView | None
- tts_job: JobView | None

## 7. Job and TTS schemas

### JobView

Fields:

- job_id: UUID
- status: JobStatus
- estimated_wait_seconds: int | None
- error_code: str | None

### CreateTtsRequest

Fields:

- character_id: str
- source_message_id: UUID
- style: Literal["warm", "soft", "playful", "careful"]

Headers:

- Idempotency-Key required.

### TtsJobResponse

Fields:

- job_id: UUID
- status: JobStatus
- audio: AudioPlaybackView | None
- error_code: str | None

### AudioPlaybackView

Fields:

- playback_url: str
- expires_at: datetime

## 8. Memory schemas

### MemoryView

Fields:

- id: UUID
- summary: str
- memory_type: str
- importance: int
- created_at: datetime

### MemoryListResponse

Fields:

- items: list[MemoryView]

### DeleteMemoryResponse

Fields:

- memory_id: UUID
- status: Literal["deleted"]

## 9. Date event schemas

### DateEventView

Fields:

- id: str
- title: str
- estimated_minutes: int
- status: Literal["available", "locked", "cooldown"]
- reward_preview: dict[str, Any] | None
- entry_cost: int

### DateStepChoiceView

Fields:

- choice_id: str
- label: str

### DateStepView

Fields:

- sequence_no: int
- airi_line: str
- choices: list[DateStepChoiceView]

### StartDateEventResponse

Fields:

- session_id: UUID
- event_id: str
- step: DateStepView

### DateMoveRequest

Fields:

- session_id: UUID
- sequence_no: int
- choice_id: str
- free_text: str | None

Headers:

- Idempotency-Key required.

### DateMoveResponse

Fields:

- session_id: UUID
- status: DateSessionStatus
- step: DateStepView | None
- partial_feedback: dict[str, Any] | None

### DateFinishResponse

Fields:

- session_id: UUID
- result: DateResult
- score: int
- airi_reaction: str
- relationship_event: RelationshipFeedbackView
- reward: RewardEventView | None
- memory_job_id: UUID | None

## 10. Reward and media schemas

### RewardEventView

Fields:

- event_id: UUID
- status: RewardStatus
- type: Literal["image", "note", "voice", "story_card", "credit"]
- title: str | None
- preview: dict[str, Any] | None

### RewardListResponse

Fields:

- items: list[RewardEventView]

### CreateMediaJobRequest

Fields:

- character_id: str
- source_type: Literal["reward_event", "date_event"]
- source_id: UUID
- media_type: Literal["image"]
- quality: Literal["basic", "premium"]

Headers:

- Idempotency-Key required.

### MediaJobResponse

Fields:

- job_id: UUID
- status: MediaStatus
- asset: MediaAssetView | None
- refund: RefundView | None

### MediaAssetView

Fields:

- id: UUID
- url: str
- expires_at: datetime | None

### RefundView

Fields:

- status: Literal["none", "pending", "completed"]
- ledger_id: UUID | None

## 11. Credit and plan schemas

### CreditBalanceView

Fields:

- currency_type: Literal["credit"]
- bucket: Literal["free_daily", "ad_reward", "subscription_allowance", "purchased", "promo"]
- amount: int
- expires_at: datetime | None

### CreditBalanceResponse

Fields:

- balances: list[CreditBalanceView]

### CreditLedgerRowView

Fields:

- id: UUID
- amount: int
- bucket: str
- reason: str
- source_type: str
- source_id: str
- created_at: datetime

### PlanAllowanceView

Fields:

- feature: str
- period_type: str
- limit_amount: int
- used_amount: int | None

### PlanView

Fields:

- plan: PlanCode
- display_name: str
- price_label: str | None
- allowances: list[PlanAllowanceView]
- credit_grant: int | None

## 12. Report schemas

### CreateReportRequest

Fields:

- target_type: Literal["message", "media_asset", "character"]
- target_id: UUID | str
- reason: Literal["unsafe", "sexual", "minor", "harassment", "privacy", "other"]
- note: str | None

Headers:

- Idempotency-Key required.

### CreateReportResponse

Fields:

- report_id: UUID
- status: Literal["open"]

## 13. OpenAPI generation rules

FastAPI docs:

- `/openapi.json` enabled in non-production.
- production can expose only internal docs or disabled docs.
- schema titles must be stable.
- response_model must be declared for every route.
- error responses must include documented ApiErrorResponse.

Versioning:

- mobile API path version: `/api/mobile/v1`.
- breaking schema changes require v2 or backward-compatible fields.
- additive optional fields allowed.

Naming:

- Pydantic classes use PascalCase.
- JSON fields use snake_case end-to-end for first release.

Reason:

- Flutter can map snake_case reliably.
- Keeping backend and API JSON in snake_case reduces early mapping bugs.

## 14. Validation and tests

Schema tests:

- every request example validates.
- every response example validates.
- enum invalid values fail.
- idempotency-required endpoints reject missing header.
- OpenAPI generation succeeds.

Contract tests:

- `/app/bootstrap` response can render Chat first screen.
- `POST /chat/turn` response includes reply and optional feedback.
- date start/move/finish response matches rule engine result.
- quota exceeded returns ApiErrorResponse with QUOTA_EXCEEDED.
- provider degraded returns either fallback reply or PROVIDER_DEGRADED error.

## 15. Acceptance criteria

이 문서 기준 개발 착수 전 다음이 가능해야 한다.

- route별 request/response Pydantic class names are known.
- shared enums are known.
- OpenAPI generation policy is known.
- idempotency-required endpoints are explicit.
- mobile and admin schema boundaries are separated.
- schema tests can be written before service implementation.
