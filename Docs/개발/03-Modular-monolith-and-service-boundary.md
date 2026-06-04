# Modular monolith and service boundary

작성일: 2026-06-04

이 문서는 AI Companion backend를 Python/FastAPI modular monolith로 시작하되, 향후 realtime, billing/ledger, provider routing, admin/ops, analytics를 별도 서비스로 분리할 수 있게 만드는 개발 규칙을 정의한다.

목표는 지금부터 microservice로 쪼개는 것이 아니다. 첫 release는 하나의 deployable backend로 가되, 내부 경계가 무너지지 않게 만든다.

## 1. Current decision

첫 release backend:

```text
FastAPI modular monolith
PostgreSQL
Redis
Queue/worker
Object storage
API Gateway/WAF in front
```

이 결정은 다음 이유로 유지한다.

- AI provider 연동과 실험 속도가 중요하다.
- Python SDK와 Pydantic 기반 API contract가 빠르다.
- 첫 release에서 팀과 운영 복잡도를 키우지 않는다.
- module boundary를 지키면 나중에 일부 서비스를 분리할 수 있다.

## 2. Hard boundaries

반드시 지킬 경계:

| Layer | Allowed responsibility | Must not do |
|---|---|---|
| API route | auth, request validation, response mapping, rate-limit hook | business logic, DB transaction, provider decision |
| Service | business rule, transaction boundary, orchestration | raw HTTP response shaping |
| Repository | DB read/write only | provider call, external API call, business policy decision |
| Provider adapter | external provider call, usage unit return | DB write, ledger update, user state mutation |
| Worker | async job execution and retry | hidden user-facing state change without event/ledger |
| Schema | API request/response contract | internal domain mutation logic |

Rules:

- Route calls service.
- Service calls repository and provider adapter.
- Repository never calls provider.
- Provider adapter never writes DB.
- Billing/credit/date/reward state changes go through service transaction boundary.
- All cost-impacting calls produce provider usage or ledger events.

## 3. API boundary

Public prefixes:

```text
/api/mobile/v1/*
/api/admin/v1/*
/api/webhooks/v1/*
/health
/ready
```

Rules:

- Mobile API and admin API are separated.
- Billing/webhook API is separated from mobile API.
- Admin API always requires admin auth/RBAC dependency.
- Mobile write APIs require user/device/session context.
- Webhooks require signature verification before business logic.
- Versioned prefixes are mandatory.

## 4. Auth/session boundary

Development default:

- guest session is allowed.
- access token and refresh token are skeleton tokens until a real auth provider is chosen.
- token parsing is isolated behind `security.auth`.

Rules:

- API routes depend on `CurrentUserContext`, not raw token strings.
- Admin routes depend on `AdminUserContext`.
- Guest users cannot perform payment export/account deletion without account link policy.
- Auth provider can be replaced without changing services.

Future split:

- Managed auth or dedicated auth service can replace local token logic.
- API services should only trust verified user/admin context.

## 5. Billing and credit ledger boundary

Billing/ledger is a likely future split candidate.

Rules:

- Credit ledger is append-only.
- Duplicate webhook/idempotency cannot double grant credits.
- Payment webhook route does not directly mutate arbitrary user state.
- Ledger service owns credit spend/grant/refund.
- Ledger replay must be possible.
- Billing provider/store payload is stored as an auditable event.

Future split trigger:

- paid traffic grows.
- finance/audit requirements increase.
- ledger throughput or compliance needs exceed main API ownership.

## 6. Provider routing boundary

Provider routing is a likely future split candidate.

Rules:

- Provider selection is made through route names such as `short_social`, `default_chat`, `memory_extraction`, `media_prompt`.
- Provider API keys stay server-side.
- Provider adapter returns usage units.
- Provider usage event records route, provider, model, latency, token/seconds/image units, estimated cost.
- Fallback/downgrade is configured by route.

Future split trigger:

- multiple providers are actively routed.
- route-level cost cap needs independent deployment.
- provider quota/backpressure becomes complex.

## 7. Realtime boundary

Realtime voice/WebSocket is excluded from first release. If added later, it should be split before 100k connected user claims.

Rules now:

- Do not build live call assumptions into core chat service.
- Voice input remains request/response or async job until realtime scope is approved.
- STT/TTS provider interfaces stay separate from chat orchestration.

Future split:

```text
Mobile
-> Realtime Gateway
-> STT/TTS providers
-> Core API for session/user/credit state
```

## 8. Admin/ops boundary

Rules:

- Admin API is not mobile API with a different flag.
- Admin user context is separate from app user context.
- Every sensitive admin action writes audit log.
- Admin read models can be optimized separately from mobile responses.
- Manual credit adjustment uses ledger service.

Future split trigger:

- CS/moderation workflows grow.
- admin traffic or permission model becomes complex.
- internal deployment/security requires separate service.

## 9. Analytics/event boundary

Rules:

- Analytics events do not include raw message content.
- Product analytics is append-only event stream or table.
- Provider usage/cost events are separate from general product analytics.
- API request logging is not a replacement for product analytics.

Future split trigger:

- event volume affects API DB.
- long-term analytics needs warehouse/export pipeline.
- experimentation requires independent event processing.

## 10. Code review checklist

Reject the change if:

- route contains business logic beyond request/response/auth.
- repository calls provider or external HTTP API.
- provider adapter writes DB or ledger.
- mobile/admin/webhook prefixes are mixed.
- paid/credit state is changed without idempotency.
- admin action lacks audit plan.
- cost-impacting provider call lacks usage event plan.
- queue job payload has no typed schema.
- service returns raw FastAPI `Response` instead of domain result/API schema.
- new module makes future split harder without justification.

