# QA, test, and release verification plan

작성일: 2026-06-04

이 문서는 AI Companion 첫 상용 release의 테스트 전략과 release gate에서 요구되는 증거를 정의한다. 목표는 "기능이 된다"가 아니라 결제, credit, memory, generated media, provider cost, safety, deletion 같은 상용 리스크가 검증됐음을 증명하는 것이다.

## 1. Test layers

| Layer | Purpose | Required before |
|---|---|---|
| Unit tests | rule/ledger/schema/service 로직 검증 | closed beta |
| Contract tests | OpenAPI/Pydantic/mobile API 호환성 | closed beta |
| Integration tests | DB, Redis, queue, provider mock, billing webhook | closed beta |
| E2E smoke tests | 핵심 사용자 loop 검증 | public beta |
| Load tests | SLO/capacity/cost protection 검증 | commercial launch |
| Safety tests | policy, report, moderation, crisis route 검증 | public beta |
| Store/legal checks | AI disclosure, delete, privacy, IAP copy 검증 | commercial launch |
| Ops drills | incident, backup/restore, kill switch 검증 | commercial launch |

## 2. Required test data

Test data must be synthetic.

Fixtures:

- guest user.
- linked account user.
- Free user.
- Plus user.
- Premium user.
- credit pack purchaser.
- Airi default profile.
- relationship levels 1, 3, 5, 8, 12.
- memory samples by type.
- three official date event templates from `19`.
- reward media statuses: locked, pending, moderation_pending, unlocked, rejected, failed.
- provider responses: success, timeout, rate_limited, unsafe, partial_failure.
- billing webhooks: purchase, renewal, cancellation, refund, duplicate, delayed.
- deletion requests: pending, processing, completed, failed.

## 3. Unit test requirements

Backend unit tests:

- credit ledger append-only behavior.
- idempotency key duplicate handling.
- credit spend priority.
- provider failure refund rule.
- quota reset and hard cap.
- relationship delta calculation.
- memory extraction candidate filtering.
- memory delete state transition.
- date event scoring.
- reward unlock rule.
- safety classification routing.
- admin RBAC permission check.

Rule engine unit tests:

- each date event normal success.
- neutral result.
- low score result.
- duplicate move.
- duplicate finish.
- expired session.
- invalid choice.
- reward already unlocked.
- relationship level boundary.

Schema tests:

- Pydantic request/response validates examples.
- enum values match API contract.
- OpenAPI generation is stable.
- mobile-required fields are not optional by accident.
- internal fields are not leaked to mobile.

## 4. Integration test requirements

Core integration flows:

1. Guest starts app -> chat turn -> memory candidate -> relationship event.
2. User links account -> guest memory/credit migration behavior.
3. Chat turn uses provider mock -> provider usage event saved -> cost attributed.
4. Date event start/move/finish -> relationship/reward/ledger events committed.
5. TTS job queued -> provider mock success -> media/audio status ready.
6. Image reward queued -> moderation pending -> unlocked or rejected.
7. Quota exceeded -> API returns upgrade/ad/shop details.
8. Billing webhook duplicate -> no duplicate credit/subscription grant.
9. Refund webhook -> compensating ledger entry.
10. Report submitted -> moderation queue -> admin action audit.
11. Memory delete -> retrieval excludes deleted memory.
12. Account deletion request -> job status -> privacy state updated.

Infrastructure integration:

- migration apply.
- migration rollback where supported.
- Redis rate limit shared across app instances.
- queue retry.
- dead letter queue.
- object storage signed URL.
- webhook signature verification.
- admin audit log write.

## 5. Mobile QA matrix

Devices:

- iOS current major version.
- iOS previous major version if supported.
- Android current major version.
- Android lower-end device profile.
- tablet layout only if supported.

Network:

- normal.
- slow.
- offline.
- provider timeout.
- retry after reconnect.

Mobile scenarios:

- onboarding/age gate/consent.
- first chat.
- voice permission denied.
- STT failure fallback.
- TTS pending/failed.
- quota exceeded.
- date event completed.
- reward pending/rejected/unlocked.
- shop purchase sandbox.
- restore purchase.
- memory delete.
- report content.
- account deletion request.

Acceptance:

- no blocking crash in critical loop.
- no invisible paid/credit failure.
- no generated media visible before moderation pass.
- no missing report/delete path.

## 6. Billing and credit verification

Sandbox tests:

- subscription purchase.
- subscription renewal.
- subscription cancellation.
- subscription expiration.
- credit pack purchase.
- duplicate webhook.
- delayed webhook.
- refund.
- chargeback if platform supports sandbox simulation.

Ledger assertions:

- every paid grant has source reference.
- every spend has feature_route.
- failed provider call either does not charge or creates refund event.
- admin adjustment has reason and audit.
- balance snapshot equals ledger replay.

Release blocker:

- paid launch is blocked if duplicate webhook can double grant credits.
- paid launch is blocked if provider failure can charge without refund path.
- paid launch is blocked if restore purchase is missing on iOS.

## 7. Safety and moderation verification

Safety tests:

- explicit sexual request blocked.
- minor-like sexualization blocked.
- self-harm/crisis route safe response.
- harassment/hate blocked or redirected.
- illegal instruction blocked.
- real-person sexualized image request blocked.
- unsafe image generation rejected.
- user report creates moderation item.
- block/report path works from chat/media/settings.

Moderation tests:

- generated media starts hidden.
- moderation pass unlocks media.
- moderation reject keeps media hidden.
- admin decision writes audit.
- user sees clear rejected/failed state.

Release blocker:

- public beta is blocked if report path does not create an actionable moderation record.
- image reward launch is blocked if unsafe media can be shown before moderation.

## 8. Provider and cost verification

Required before public beta:

- provider mock test passes.
- provider timeout test passes.
- provider fallback test passes.
- provider usage event saved for every provider call.
- route-level cost attribution exists.

Required before commercial launch:

- provider benchmark from `29` completed.
- provider daily cap configured.
- cost dashboard visible.
- top 1% user cost scenario simulated.
- kill switch tested.
- text-only fallback tested.
- image queue pause tested.

Release blocker:

- commercial launch is blocked if provider spend cannot be attributed by feature route.
- commercial launch is blocked if high-cost feature has no cap/kill switch.

## 9. Load and SLO verification

Use `27` as the source of load scenarios.

Minimum proof before commercial launch:

- API p50/p90 measured.
- chat p50/p90 measured.
- queue backlog behavior measured.
- DB write/read pressure measured.
- provider fallback behavior under failure measured.
- Redis rate limit works across instances.
- admin/analytics read path does not overload production DB.

Scale claim rule:

- "100k+ ready" can only mean architecture-aware and testable until real load/beta evidence exists.
- production marketing or investor claim must not imply proven 100k traffic unless load test and provider quota evidence exist.

## 10. Release evidence checklist

Closed beta evidence:

- test report.
- migration result.
- API contract test result.
- unit test summary.
- smoke test summary.
- known issues list.

Public beta evidence:

- mobile QA matrix result.
- safety test result.
- billing sandbox result.
- report/delete flow result.
- provider fallback result.
- basic dashboard screenshots or links.

Commercial launch evidence:

- provider benchmark result.
- load test result or explicit risk acceptance.
- backup/restore drill result.
- incident drill result.
- store/legal checklist result.
- final price/IAP product id sign-off.
- privacy/terms/support URL sign-off.

## 11. Release blocker list

Do not release if any item is true:

- credit ledger replay mismatch.
- billing duplicate grants credits.
- provider usage missing cost attribution.
- generated media can bypass moderation.
- report/delete path unavailable.
- account deletion job cannot be tracked.
- admin sensitive action lacks audit.
- API contract differs from mobile implementation.
- app crash blocks first chat.
- paid plan copy differs from backend allowance.
- privacy/terms/delete copy differs from actual behavior.

## 12. QA ownership

Minimum ownership:

- backend engineer owns unit/integration/provider/ledger tests.
- mobile engineer owns mobile matrix and store screenshot sanity.
- PM owns copy, pricing, plan, user journey acceptance.
- ops/backend owns load, observability, incident, backup drills.
- safety reviewer owns moderation and policy test set.

If team is small, the same person can hold multiple roles, but the checklist cannot disappear.

