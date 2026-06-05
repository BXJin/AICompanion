# AICompanion handoff

Last updated: 2026-06-05

Purpose:

- Keep separate Codex/PM/dev sessions aligned.
- Prevent backend, mobile, admin, and planning work from drifting into different product assumptions.
- Make the next session start from current project state instead of rediscovering context.

## 1. Current product direction

AICompanion is not just an AI chat app.

Core product loop:

```text
chat with Airi
-> shared activity/date event
-> deterministic result
-> Airi reaction
-> relationship/memory/reward update
-> next session recalls the shared moment
```

Current v1 focus:

- Airi single character.
- Mobile-first chat.
- Guest auth/session.
- Memory/relationship/reward loop.
- 3 official date events.
- Credit/quota/ledger foundation.
- Admin/ops minimum.

v1.1 planning direction:

- Shared Activity framework.
- Movie/Music Reflection.
- Quick Connect.
- Season Recap data only in v1.1; visible Season Recap deferred to v1.2.

Authoritative planning docs:

- `Docs/기획/00-Commercial-app-master-index.md`
- `Docs/기획/15-First-release-scope-decisions.md`
- `Docs/기획/24-Commercial-development-readiness-audit.md`
- `Docs/기획/35-Shared-activity-system-spec.md`
- `Docs/기획/36-Shared-activity-v1-1-product-package-plan.md`
- `Docs/개발/01-Development-plan-and-tech-stack.md`
- `Docs/개발/03-Modular-monolith-and-service-boundary.md`
- `Docs/운영/00-Operations-master-index.md`
- `Docs/운영/01-Commercial-readiness-gate.md`
- `Docs/운영/02-Live-ops-playbook.md`
- `Docs/운영/03-Beta-metrics-cost-and-quality-validation.md`
- `Docs/운영/04-Character-consistency-and-content-quality-ops.md`

## 2. Session ownership map

### Backend session

Current active implementation area.

Workspace:

- `Server/`
- `Docs/개발/`
- backend-related planning docs under `Docs/기획/17`, `18`, `20`, `21`, `23`, `24`, `25`, `26`, `32`

Must preserve:

- FastAPI modular monolith.
- route -> schema/auth/response only.
- service layer for business rules.
- repository layer for DB access.
- provider calls behind adapters.
- mobile/admin/webhook route prefixes must stay separated.
- billing/credit/reward/relationship changes must be idempotent/auditable.

Current backend state:

- Guest auth/session persistence implemented.
- DB model/Alembic baseline implemented.
- Airi seed and authenticated bootstrap implemented.
- Mock chat turn implemented.
- Provider usage event logging implemented.
- Relationship/memory candidate base implemented.
- Credit ledger/quota implemented.
- Date event rule engine implemented.
- Tests were passing after the last backend implementation sequence.

Next backend sessions:

1. Memory activation/delete API and async extraction job skeleton.
2. Reward/media async job skeleton.
3. Billing webhook -> credit ledger integration.
4. Minimum admin API.
5. QA/integration/load smoke.

### Mobile client session

Not implemented yet.

Expected workspace:

- likely future `Client/` or `Mobile/` directory.
- use `Docs/기획/16-Mobile-user-journey-and-screen-IA.md`
- use `Docs/기획/17-Mobile-API-contract.md`
- use `Docs/기획/31-Mobile-admin-wireframe-design-system-spec.md`
- use `Docs/개발/02-Bottleneck-reuse-and-mobile-stack.md`

Default stack decision:

- Flutter first, unless PM explicitly changes stack.

Mobile first scope:

- age gate / consent.
- guest start.
- chat home.
- app bootstrap.
- relationship/memory/reward hints.
- date event list/play/result.
- reward gallery.
- profile/settings/privacy/report entry.

Mobile must not:

- call webhook APIs.
- rely on client-side result/reward decisions.
- compute credit, reward, relationship, or date result locally except for display previews.

### Admin/backoffice session

Not fully implemented yet.

Expected references:

- `Docs/기획/21-Admin-minimum-screen-spec.md`
- `Docs/기획/31-Mobile-admin-wireframe-design-system-spec.md`
- `Docs/기획/30-Production-ops-security-observability-analytics-plan.md`

Current backend has:

- admin route boundary skeleton.
- local admin token dependency.
- admin user summary endpoint.
- admin audit log model exists, but real workflows are not implemented yet.

Admin first scope:

- user lookup.
- credit ledger viewer.
- provider cost/usage dashboard.
- queue/job monitor.
- moderation review.
- admin audit log viewer.

Admin must not:

- reuse mobile auth.
- expose sensitive user content without reason/audit.
- bypass ledger for manual credit changes.

### Planning/content session

Current planning state is extensive. New planning work should update existing docs unless a new artifact is clearly needed.

Recently added:

- `Docs/기획/34-Companion-mini-game-content-candidate-research.md`
- `Docs/기획/35-Shared-activity-system-spec.md`
- `Docs/기획/36-Shared-activity-v1-1-product-package-plan.md`

Planning rule:

- v1 scope stays focused on backend/mobile proof of Airi relationship loop.
- v1.1 Shared Activity planning can continue, but should not derail current v1 backend sequence.
- Commercial readiness claims must use `Docs/운영/01` and `Docs/운영/03` evidence, not planning intent.

### Operations session

Expected references:

- `Docs/운영/00-Operations-master-index.md`
- `Docs/운영/01-Commercial-readiness-gate.md`
- `Docs/운영/02-Live-ops-playbook.md`
- `Docs/운영/03-Beta-metrics-cost-and-quality-validation.md`
- `Docs/운영/04-Character-consistency-and-content-quality-ops.md`
- `Docs/기획/30-Production-ops-security-observability-analytics-plan.md`
- `Docs/기획/32-QA-test-release-verification-plan.md`

Operations first scope:

- define dashboard ownership.
- prepare beta report process.
- define prompt/model/provider change log.
- define kill switch owners.
- validate character consistency before image reward launch.
- run Go/No-Go readiness review before public beta or commercial launch.

Operations must not:

- approve launch based only on feature completion.
- manually edit credit, reward, subscription, memory, or moderation state outside service/admin APIs.
- accept image/voice/provider changes without cost, latency, safety, and character regression checks.

## 3. Cross-session contracts

### API boundary

Backend exposes:

- `/api/mobile/v1/*` for mobile.
- `/api/admin/v1/*` for admin.
- `/api/webhooks/v1/*` for external webhooks.

Do not mix these prefixes.

### Result ownership

Server owns:

- date event result.
- game/activity result.
- credit ledger.
- reward unlock/progress.
- relationship delta.
- memory candidate/activation.
- provider usage event.

Client owns:

- rendering.
- local optimistic UI states.
- input collection.
- playback.
- navigation.

LLM owns:

- Airi wording.
- emotional reaction.
- hints.
- summaries, only when service rules allow.

LLM must not own:

- scores.
- rewards.
- credit changes.
- relationship deltas.
- safety policy decisions.

### Contract change protocol

This is the most important rule for parallel backend/mobile sessions.

When the backend session changes any mobile-facing API, it must update all of these before finishing:

- `Docs/기획/17-Mobile-API-contract.md`
- affected Pydantic schemas under `Server/app/schemas/`
- affected route behavior under `Server/app/api/mobile/v1/`
- relevant tests under `Server/tests/`
- this `handoff.md` if the mobile implementation needs to react differently

When the mobile session finds an API mismatch, it must not silently work around it in UI state. It should update the handoff with:

- endpoint
- expected shape from docs
- actual shape from server
- blocking UI flow
- proposed contract change

Use this format in the session handoff section:

```text
API contract note:
- Endpoint:
- Change/mismatch:
- Mobile impact:
- Backend action:
- Docs updated:
```

### Cross-session status board

Backend status:

- Current owner area: `Server/`
- Current priority: finish v1 backend core loop before v1.1 shared activity implementation.
- Must notify mobile session when: bootstrap, chat, date event, reward, memory, quota, auth, or error shape changes.

Mobile status:

- Current owner area: future `Mobile/` or `Client/`
- Stack default: Flutter.
- Must notify backend session when: UI requires a new field, new error state, pagination behavior, media playback ticket, or changed auth/session behavior.

Admin status:

- Current owner area: future `Admin/` or `WebAdmin/`
- Must notify backend session when: admin read/write workflows require new audit fields, RBAC scopes, or manual ledger operations.

Path note:

- Some PowerShell output may show Korean folder names as mojibake.
- If a path is hard to type, locate it by filename:

```powershell
rg --files Docs | rg "17-Mobile-API-contract"
rg --files Docs | rg "31-Mobile-admin"
rg --files Docs | rg "Operations-master-index"
```

## 4. Current implementation risks

- Chat idempotency is required by API shape, but full persistent replay is still a future item.
- Memory candidates exist, but activation/delete APIs and async extraction are not implemented yet.
- Reward events exist, but reward/media async job fulfillment is not implemented yet.
- Billing webhook routes are skeletal; ledger integration is still pending.
- Admin route boundary exists, but real admin workflows/RBAC/audit behavior are not complete.
- Shared Activity v1.1 is planning only; do not implement it before v1 backend loop is complete unless PM explicitly changes priority.
- No generated OpenAPI artifact is committed yet. Until it exists, `Docs/기획/17-Mobile-API-contract.md` and `Server/app/schemas/` must be manually kept in sync.
- Mobile work has not started yet, so backend API changes are still cheaper now than after Flutter screens bind to them.

## 5. Handoff checklist for every session

Before starting:

- Read `handoff.md`, `todo.md`, and `architecture.md`.
- Check `git status --short`.
- Check the relevant docs for the area being touched.
- Keep existing user changes; do not revert unrelated work.
- Check whether the work changes a cross-session contract.

Before finishing:

- Run relevant tests or explain why not.
- Update docs if behavior, settings, or limitations changed.
- Summarize changed files.
- Commit and push if this session produced repo changes.
- If any mobile-facing API changed, add an API contract note above.
