# AI Companion Server

FastAPI backend skeleton for the AI Companion commercial v1.

Reference docs:

- `Docs/기획/26-Backend-skeleton-service-boundary-plan.md`
- `Docs/기획/25-OpenAPI-Pydantic-schema-plan.md`
- `Docs/개발/01-Development-plan-and-tech-stack.md`

## Local run

```powershell
cd Server
pip install -e .[dev]
uvicorn app.main:create_app --factory --reload
```

Health checks:

- `GET /health`
- `GET /ready`

## Current scope

This is Phase 0 skeleton only:

- FastAPI app factory.
- settings/config.
- request id middleware.
- structured JSON access logging.
- versioned mobile/admin/webhook API boundaries.
- guest auth/session persistence for local development.
- admin auth dependency skeleton.
- webhook signature dependency skeleton.
- SQLAlchemy session setup.
- Alembic migration for `users` and `user_sessions`.
- Alembic migration for v1 domain baseline tables.
- idempotent Airi seed and authenticated bootstrap aggregation.
- authenticated `POST /api/mobile/v1/chat/turn` with conversation/message persistence and mock LLM replies.
- common API schemas.
- route/module boundaries.
- mock LLM provider interface.

Real auth providers, provider usage logging, ledger services, relationship/memory services, and real admin workflows are intentionally next steps.

Known current chat limits:

- `Idempotency-Key` is required, but duplicate replay needs a later message/idempotency storage migration.
- provider usage events are intentionally deferred to the provider usage logging session.
