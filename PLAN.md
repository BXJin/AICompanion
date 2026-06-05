# AICompanion plan

Last updated: 2026-06-05

This file is the cross-session execution plan. It is intentionally shorter than the planning docs under `Docs/`.

Read order for every session:

```text
handoff.md
-> architecture.md
-> PLAN.md
-> todo.md
-> relevant Docs/기획, Docs/개발, or Docs/운영 file
```

## Phase 0: Repository and backend foundation

Status: mostly implemented.

Goal:

- Make the repository runnable and keep backend boundaries clean.

Done/expected:

- FastAPI modular monolith under `Server/`.
- SQLAlchemy/Alembic baseline.
- Mobile/admin/webhook route prefixes.
- Guest auth/session.
- Airi seed/bootstrap.
- Mock chat.
- Relationship/memory candidate base.
- Credit ledger/quota.
- Date event rule engine.

Exit criteria:

- Relevant backend tests pass.
- `handoff.md` accurately reflects backend state.
- Mobile-facing API changes are reflected in `Docs/기획/17-Mobile-API-contract.md`.

## Phase 1: v1 backend core loop

Status: active.

Goal:

- Complete server-owned Airi relationship loop before mobile starts depending on unstable APIs.

Work:

- Memory activation/delete API.
- Async memory extraction skeleton.
- Reward/media async job skeleton.
- Reward gallery/read API.
- Billing webhook to ledger integration.
- Minimum admin API.
- Provider cost dashboard data path.
- Persistent idempotency replay.
- QA/integration/load smoke.

Exit criteria:

- Chat/date/reward/memory/credit loop works with mock providers.
- Server owns result/reward/relationship/credit decisions.
- Admin can inspect enough state for closed beta support.
- Mobile can build against stable bootstrap/chat/date/reward/memory contracts.

## Phase 2: Flutter mobile v1

Status: not started.

Goal:

- Build the mobile app around the stable v1 backend loop.

Default stack:

- Flutter.

Workspace:

- To be decided: `Mobile/` or `Client/`.

Work:

- Flutter project skeleton.
- Age gate / consent.
- Guest start.
- App bootstrap.
- Chat home.
- Relationship/memory/reward hint components.
- Date event list/play/result.
- Reward gallery.
- Profile/settings/privacy/report entry.
- Quota/provider degraded/pending/error states.

Exit criteria:

- Mobile can complete first-run journey.
- Mobile can complete one date event and show relationship/reward feedback.
- Mobile does not compute server-owned state locally.
- API mismatches are recorded in `handoff.md`, not hidden in UI workarounds.

## Phase 3: Admin and ops v1

Status: skeleton only.

Goal:

- Make closed beta operable without direct DB edits.

Work:

- Admin auth/RBAC.
- User lookup.
- Credit ledger viewer.
- Provider usage/cost dashboard.
- Queue/job monitor.
- Moderation review.
- Admin audit log viewer.

Exit criteria:

- Sensitive reads/actions are audited.
- Manual credit adjustment uses ledger events.
- Provider/cost and moderation issues can be inspected from admin tools.

## Phase 4: Closed beta readiness

Status: not ready.

Goal:

- Prove the v1 loop with real usage, safe operations, and measured cost.

Required:

- Memory candidate/delete path works.
- Reward/media pending/unlocked/rejected path works.
- Report/delete path exists.
- Billing sandbox idempotency works if paid flow is enabled.
- Admin can inspect user/credit/provider/report with audit.
- Provider benchmark and cost simulation are run.
- Mobile QA matrix passes.
- Operations readiness gate from `Docs/운영/01-Commercial-readiness-gate.md` is reviewed.
- Beta metrics plan from `Docs/운영/03-Beta-metrics-cost-and-quality-validation.md` is ready.

Exit criteria:

- No blocker from `Docs/기획/32-QA-test-release-verification-plan.md`.
- Cost/user/day can be measured.
- Provider failure/degraded states are visible to mobile.
- Daily ops dashboard fields from `Docs/운영/02-Live-ops-playbook.md` have owners or explicit deferrals.

## Phase 5: v1.1 Shared Activity

Status: planning only.

Goal:

- Expand beyond 3 date events only after v1 loop is proven.

Default package:

- Movie/Music Reflection.
- Quick Connect.
- Season progress data only.
- Visible Season Recap deferred to v1.2.

Do not start before:

- v1 backend core loop is complete, or PM explicitly changes priority.

## Phase 6: Public beta and commercial launch

Status: not ready.

Public beta blockers:

- Real provider latency/cost dashboard.
- Queue retry/dead letter.
- Media moderation.
- App crash/error monitoring.
- Privacy/terms draft.
- Billing/ad sandbox where enabled.
- Character consistency QA from `Docs/운영/04-Character-consistency-and-content-quality-ops.md`.

Commercial launch blockers:

- Final pricing.
- Final legal/store copy.
- Production admin RBAC.
- Incident runbook rehearsal.
- Backup/restore rehearsal.
- Provider fallback tested.
- Deletion/export tested.
- Release evidence checklist complete.
- Go/No-Go evidence from `Docs/운영/01-Commercial-readiness-gate.md`.

## Current priority statement

Finish Phase 1 before building Phase 5.

Mobile work can start once the Phase 1 bootstrap/chat/date/reward contracts are stable enough, but any mismatch must be handled through `handoff.md` and `Docs/기획/17-Mobile-API-contract.md`.
