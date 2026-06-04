# Backend skeleton and service boundary plan

작성일: 2026-06-04

이 문서는 AI Companion backend를 실제로 생성할 때의 skeleton, module boundary, service 책임, 초기 구현 순서를 정의한다.

기준 문서:

- `17-Mobile-API-contract.md`
- `18-DB-schema-and-ledger-migration-plan.md`
- `19-Date-event-rule-spec.md`
- `20-Credit-plan-allowance-policy.md`
- `21-Admin-minimum-screen-spec.md`
- `25-OpenAPI-Pydantic-schema-plan.md`
- `Docs/개발/01-Development-plan-and-tech-stack.md`

## 결론

첫 backend skeleton의 목표는 기능을 많이 붙이는 것이 아니다.

목표는 다음 구조를 처음부터 깨지 않게 만드는 것이다.

1. API route는 auth/request/response만 담당한다.
2. business logic은 service layer에 둔다.
3. DB 접근은 repository로 분리한다.
4. provider 호출은 adapter로 숨긴다.
5. credit/relationship/reward 변경은 transaction boundary를 가진다.
6. provider usage, request_id, audit log는 초기부터 기록 가능해야 한다.

## 1. Project layout

권장:

```text
Server/
  app/
    main.py
    config.py
    logging.py
    dependencies.py
    api/
      mobile/
        v1/
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
      admin/
        v1/
          users.py
          credits.py
          provider_usage.py
          jobs.py
          moderation.py
          audit_logs.py
    schemas/
    models/
    repositories/
    services/
    providers/
      llm/
      stt/
      tts/
      image/
    workers/
    security/
    telemetry/
    tests/
  alembic/
```

주의:

- 기존 `Server-Python`이 있더라도 상용앱 backend는 새 namespace로 분리한다.
- PromptMotionLab 재사용은 provider/service 패턴 중심으로 하고, in-memory session/job 구조는 가져오지 않는다.

## 2. Core dependencies

첫 skeleton dependency:

- FastAPI.
- Pydantic.
- SQLAlchemy.
- Alembic.
- asyncpg 또는 psycopg.
- Redis client.
- Celery/RQ 중 하나.
- pytest.
- httpx test client.

Optional:

- OpenTelemetry.
- Sentry.
- structlog 또는 standard logging JSON formatter.

## 3. Config structure

Settings:

- ENV.
- DATABASE_URL.
- REDIS_URL.
- JWT_SECRET or auth provider config.
- OPENAI_API_KEY.
- STT_PROVIDER.
- TTS_PROVIDER.
- IMAGE_PROVIDER.
- STORAGE_PROVIDER.
- ADMIN_AUTH_MODE.
- COST_DAILY_LIMIT_USD.
- FREE_IMAGE_GENERATION_ENABLED.
- TTS_ENABLED.

Rules:

- provider API key는 client에 노출하지 않는다.
- kill switch는 config/DB/admin setting 중 하나로 관리한다.
- production secret은 env 또는 secret manager.

## 4. Middleware

Required:

- request_id middleware.
- structured logging middleware.
- error mapping middleware.
- auth dependency.
- idempotency dependency for write routes.
- rate limit dependency.

Admin-only:

- admin auth.
- RBAC dependency.
- admin audit dependency.

## 5. Service boundaries

### AuthSessionService

Responsibilities:

- guest session create.
- provider login verify.
- refresh token.
- user/device registration.

### AgeGateService

Responsibilities:

- age gate status.
- romance_allowed decision.
- restricted mode/block decision.

### AppBootstrapService

Responsibilities:

- first screen aggregate.
- user plan/quota.
- Airi character summary.
- relationship snapshot.
- daily greeting/date/reward hint.

Rules:

- should not call expensive provider on every app open.

### ChatOrchestrator

Responsibilities:

- quota check.
- safety precheck.
- memory retrieval.
- LLM provider call via CharacterDialogueService.
- message persistence.
- relationship feedback.
- memory extraction job enqueue.
- optional TTS job enqueue.
- provider usage event.

### CharacterDialogueService

Responsibilities:

- Airi profile context.
- prompt construction.
- model route selection.
- provider fallback response.
- response validation against Airi contract.

### RelationshipStateService

Responsibilities:

- apply relationship event.
- enforce daily cap.
- update snapshot.
- recalculate snapshot.

### MemoryService

Responsibilities:

- create candidate.
- safety filter.
- activate candidate.
- retrieve context.
- delete/export memory.

### DateEventService

Responsibilities:

- start/move/finish orchestration.
- session state.
- rule engine integration.
- reward/relationship/memory job output.

### DateEventRuleEngine

Responsibilities:

- deterministic scoring.
- result band.
- relationship delta.
- reward decision.
- idempotency-safe rule output.

### RewardUnlockService

Responsibilities:

- write reward_events.
- enforce duplicate reward constraint.
- connect reward to media job or note.

### CreditLedgerService

Responsibilities:

- grant/spend/refund/reversal.
- bucket spend priority.
- snapshot update.
- ledger replay verification.
- idempotency.

### QuotaService

Responsibilities:

- plan allowance lookup.
- quota counter increment.
- hard/soft cap decision.
- kill switch decision.

### MediaGenerationService

Responsibilities:

- credit/quota check.
- media job create.
- prompt template.
- provider call via image provider.
- moderation status.
- refund policy.

### ProviderUsageService

Responsibilities:

- record provider_usage_events.
- estimate cost.
- aggregate for admin dashboard.

### SafetyService

Responsibilities:

- input/output safety classification.
- crisis route.
- media prompt safety.
- safety event write.

### AdminAuditService

Responsibilities:

- admin action audit log.
- reason enforcement.
- target/action metadata.

## 6. Repository boundaries

Repositories:

- UserRepository.
- CharacterRepository.
- ConversationRepository.
- MessageRepository.
- RelationshipRepository.
- MemoryRepository.
- DateEventRepository.
- RewardRepository.
- CreditLedgerRepository.
- QuotaRepository.
- ProviderUsageRepository.
- AsyncJobRepository.
- SafetyRepository.
- ReportRepository.
- AdminAuditRepository.

Rules:

- repositories do not call providers.
- repositories do not implement business rules.
- services own transaction boundaries.

## 7. Provider adapter interfaces

### LlmProvider

Methods:

```text
generate_chat_response(prompt, route, request_context) -> LlmResult
```

Result:

- text.
- model.
- input_tokens.
- output_tokens.
- latency_ms.
- safety_metadata.

### SttProvider

Methods:

```text
transcribe(audio, language, request_context) -> SttResult
```

### TtsProvider

Methods:

```text
synthesize(text, voice_profile, style, request_context) -> TtsResult
```

### ImageProvider

Methods:

```text
generate_image(prompt, visual_profile, quality, request_context) -> ImageResult
```

Rules:

- provider adapters return usage units.
- provider adapters do not write DB directly.
- provider adapters raise typed provider errors.

## 8. Transaction strategy

Use service-level transaction boundary.

Chat:

- provider call outside DB transaction.
- DB writes in short transaction.
- idempotency check before write.

Date finish:

- lock session row.
- deterministic rule calculation.
- write relationship/reward/session status in transaction.

Credit spend:

- lock balance snapshots.
- insert ledger rows.
- update snapshots.
- create job.

Admin action:

- perform action.
- write audit in same transaction where possible.

## 9. Test strategy

Unit tests:

- DateEventRuleEngine.
- CreditLedgerService.
- RelationshipStateService.
- MemoryService safety filter.
- QuotaService.

Integration tests:

- auth/session create.
- chat turn with mock LLM.
- duplicate chat idempotency.
- date start/move/finish.
- duplicate date finish.
- media job refund path.
- report create -> moderation queue.
- admin action -> audit log.

Contract tests:

- OpenAPI generation.
- Pydantic examples validate.
- error response shape stable.

Load/cost tests later:

- chat p50/p90.
- provider usage aggregation.
- queue backlog simulation.
- top 1% heavy user cost simulation.

## 10. Initial implementation sequence

1. Create FastAPI app skeleton.
2. Add settings, request_id, structured logging.
3. Add SQLAlchemy base and Alembic.
4. Implement models from `18`.
5. Implement schemas from `25`.
6. Implement auth/session guest flow.
7. Implement credit ledger and quota service.
8. Implement character seed and bootstrap endpoint. Done in `Server/`.
9. Implement chat turn with mock LLM provider. Done in `Server/`.
10. Implement chat provider usage event logging. Done in `Server/`.
11. Implement chat relationship/memory base services. Done in `Server/`.
12. Implement credit ledger and quota service.
13. Implement date event rule engine and endpoints.
14. Implement async job skeleton for TTS/image/memory.
15. Implement admin minimum API.
16. Add provider usage dashboard data endpoints.

## 11. Done criteria for backend skeleton

Backend skeleton is done when:

- local server boots.
- `/health` returns ok.
- `/openapi.json` generates.
- Alembic migration applies and rolls back locally.
- guest session can be created.
- bootstrap endpoint returns Airi state.
- chat turn works with mock provider.
- date event can start/move/finish.
- credit ledger replay test passes.
- duplicate idempotency tests pass.
- admin audit log is written for admin test action.

## 12. Open decisions

Engineering decision required:

1. SQLAlchemy sync vs async.
2. Celery vs RQ for first release.
3. UUID vs ULID.
4. snake_case vs camelCase API JSON. Recommendation: snake_case.
5. admin auth provider.
6. local development DB/container strategy.
