# AICompanion TODO

Last updated: 2026-06-05

This file tracks cross-session work. It is intentionally higher level than issue-level task tracking.

## Current priority

Keep finishing the v1 backend core loop before starting v1.1 Shared Activity implementation.

## Backend v1

Completed:

- [x] Guest auth/session persistence.
- [x] DB model/Alembic v1 baseline.
- [x] Airi character seed and authenticated bootstrap.
- [x] Authenticated mock chat turn persistence.
- [x] Provider usage event logging for mock chat.
- [x] Chat relationship event/snapshot update and preference memory candidates.
- [x] Credit ledger and quota service.
- [x] 3 official date event rule engine and APIs.

Next:

- [ ] Memory activation/delete API.
- [ ] Async memory extraction job skeleton.
- [ ] Reward/media async job skeleton.
- [ ] Reward gallery/read API.
- [ ] Billing webhook -> credit ledger integration.
- [ ] Admin minimum API beyond `/admin/users/me`.
- [ ] Provider cost dashboard data path.
- [ ] Persistent idempotency replay for chat/write APIs.
- [ ] QA/integration/load smoke pass.

## Mobile client v1

Not started.

- [ ] Decide/create mobile app workspace.
- [ ] Confirm Flutter as implementation stack or document PM-approved change.
- [ ] Build age gate / consent / guest start flow.
- [ ] Build chat home from app bootstrap + chat turn API.
- [ ] Build relationship/memory/reward hint components.
- [ ] Build date event list/play/result flow.
- [ ] Build reward gallery shell.
- [ ] Build profile/settings/privacy/report entry.
- [ ] Add provider degraded/quota/pending/error states.

## Admin/backoffice v1

Skeleton only.

- [ ] Decide admin frontend stack.
- [ ] Implement admin auth/RBAC beyond local token.
- [ ] Implement user lookup.
- [ ] Implement credit ledger viewer.
- [ ] Implement provider usage/cost dashboard.
- [ ] Implement queue/job monitor.
- [ ] Implement moderation review queue.
- [ ] Implement admin audit log viewer.
- [ ] Ensure sensitive reads require reason and audit.

## Billing/monetization

Planning exists; implementation pending.

- [ ] Define sandbox product IDs and environment config.
- [ ] Implement Google Play webhook ledger integration.
- [ ] Implement Apple webhook ledger integration.
- [ ] Add idempotency tests for duplicate webhooks.
- [ ] Add refund/compensating ledger events.
- [ ] Add rewarded ad credit grant path.
- [ ] Finalize Plus/Premium/credit pack prices before public beta.

## Shared Activity v1.1

Planning only. Do not start until PM explicitly prioritizes v1.1 or v1 backend core is complete.

- [ ] Design shared activity DB/API based on `Docs/기획/35` and `36`.
- [ ] Mirror existing date event results into activity history.
- [ ] Implement Movie/Music Reflection.
- [ ] Implement Quick Connect.
- [ ] Add season progress accumulator.
- [ ] Defer visible Season Recap to v1.2.
- [ ] Decide UX naming: `Airi Moment`, `Moments`, or keep `Date`.
- [ ] Decide relationship number visibility in mobile UI.

## Product/planning decisions

- [ ] Final launch country.
- [ ] Final age gate policy.
- [ ] Final privacy/terms/refund text.
- [ ] Provider benchmark and cost simulation.
- [ ] Image/TTS provider choice.
- [ ] Admin deployment model.
- [ ] Store screenshot/copy review.

## QA/release gates

Closed beta blockers:

- [ ] memory candidate/delete path works.
- [ ] reward/media pending/unlocked/rejected path works.
- [ ] billing sandbox idempotency works if paid flow enabled.
- [ ] admin can inspect user/credit/provider/report with audit.
- [ ] report/delete path exists.
- [ ] QA matrix from `Docs/기획/32-QA-test-release-verification-plan.md` passes.

Public beta blockers:

- [ ] real provider latency/cost dashboard.
- [ ] queue retry/dead letter.
- [ ] media moderation.
- [ ] app crash/error monitoring.
- [ ] privacy/terms draft.
- [ ] mobile QA matrix.

Commercial launch blockers:

- [ ] final pricing.
- [ ] final legal/store copy.
- [ ] production admin RBAC.
- [ ] incident runbook rehearsal.
- [ ] backup/restore rehearsal.
- [ ] provider fallback tested.
- [ ] deletion/export tested.
- [ ] release evidence checklist complete.
