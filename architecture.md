# AICompanion architecture

Last updated: 2026-06-05

## 1. Product architecture

AICompanion is a mobile-first AI companion service.

Core loop:

```text
mobile app
-> chat/date/shared activity action
-> backend service/rule engine
-> provider adapter if needed
-> DB event/ledger write
-> Airi response/reward/memory feedback
-> next session continuity
```

The product must preserve these separations:

- LLM writes copy, not state.
- Rule engines decide results.
- Ledger records credit changes.
- Relationship state is event-sourced into snapshots.
- Memory can be created, activated, retrieved, deleted, and exported.
- Admin access is separated and audited.

## 2. Repository architecture

Current top-level layout:

```text
Docs/
  기획/
  개발/
Server/
  app/
  alembic/
  tests/
handoff.md
todo.md
architecture.md
```

Expected future layout:

```text
Mobile/ or Client/
Admin/ or WebAdmin/
```

Do not create future client/admin directories until a session actually starts that implementation.

## 3. Backend architecture

Current backend:

- Python.
- FastAPI.
- SQLAlchemy.
- Alembic.
- pytest.
- Modular monolith.

Backend route boundaries:

```text
/api/mobile/v1
/api/admin/v1
/api/webhooks/v1
```

Layering:

```text
api route
-> schema/auth/dependency
-> service
-> repository
-> model/database
```

Provider integration:

```text
service
-> provider adapter interface
-> concrete provider
-> provider usage event
```

Current implemented backend domains:

- health.
- guest auth/session.
- app bootstrap.
- Airi character seed.
- conversations/messages.
- mock chat.
- provider usage events.
- relationship snapshots/events.
- memory candidates.
- credit ledger/quota.
- date event templates/sessions/moves.
- reward events from date finish.
- admin boundary skeleton.
- billing webhook boundary skeleton.

## 4. Data architecture

Important current table groups:

- users/user_sessions.
- characters.
- conversations/messages.
- character_relationship_snapshots.
- relationship_events.
- memories.
- provider_usage_events.
- credit_ledger_entries.
- credit_balance_snapshots.
- quota_counters.
- plan_allowances.
- date_event_templates.
- date_game_sessions.
- date_game_moves.
- reward_events.
- admin_audit_logs.

State rules:

- relationship snapshot must be reproducible from events.
- credit changes must be append-only ledger entries.
- reward unlock/progress must be server decided.
- memory raw source and summary must stay separable.
- admin audit logs are append-only in normal operation.

## 5. Client architecture

Mobile is expected to be Flutter-first based on current docs.

Mobile responsibilities:

- render chat/date/reward/profile flows.
- collect user input.
- handle local pending/loading/error states.
- play TTS/audio when available.
- display server-owned relationship/reward/memory feedback.

Mobile must not:

- compute final date/game results.
- grant rewards.
- change credit balances.
- mutate relationship state directly.
- call admin/webhook endpoints.

Important mobile states:

- guest session missing/expired.
- chat sending/thinking/provider degraded/quota exceeded/safety blocked.
- date event active/completed/expired/duplicate finish.
- reward locked/progress/pending/unlocked/rejected.
- memory candidate/active/delete pending.
- payment pending/webhook delayed.

## 6. Admin architecture

Admin is a separate surface, not a mobile mode.

Admin API:

```text
/api/admin/v1
```

Minimum admin capabilities:

- user lookup.
- credit ledger viewer.
- provider cost/usage dashboard.
- queue/job monitor.
- moderation review.
- admin audit log viewer.

Admin rules:

- separate auth/RBAC.
- every sensitive read/action requires audit.
- manual credit adjustment uses ledger events.
- media/conversation access requires reason.

## 7. Shared Activity architecture

Current v1 implementation uses date event tables and services.

v1.1 planning introduces generic Shared Activity:

```text
activity_templates
activity_sessions
activity_steps
activity_moves
activity_results
activity_recommendations
season_arcs
season_moments
```

Do not migrate v1 date event tables prematurely.

Recommended path:

1. Finish v1 backend core.
2. Add shared activity tables/services in v1.1.
3. Mirror existing date event outputs into activity history.
4. Add Movie/Music Reflection.
5. Add Quick Connect.
6. Accumulate season progress.
7. Add visible Season Recap later in v1.2.

## 8. Service split readiness

Start as modular monolith, but keep future split boundaries clean:

- billing/ledger.
- provider routing.
- realtime gateway.
- admin/ops.
- analytics.
- shared activity/game engine.

Split trigger examples:

- provider traffic/concurrency dominates API.
- billing audit requirements grow.
- admin permission model becomes complex.
- realtime voice/websocket scale requires separate gateway.
- shared activity/game engine becomes high throughput or independently deployed.

## 9. Engineering invariants

- Routes do not contain business rules.
- Services own business rules.
- Repositories own DB queries.
- Providers are replaceable adapters.
- Idempotency is required for write APIs that can be retried.
- All cost-bearing provider calls create usage events.
- Credit/reward/payment changes are auditable.
- Mobile/admin/webhook boundaries remain separate.
- Docs must be updated when behavior changes.
