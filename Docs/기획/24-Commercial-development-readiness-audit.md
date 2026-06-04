# Commercial development readiness audit

작성일: 2026-06-04

이 문서는 `Docs/기획`과 `Docs/개발`이 실제 상용 AI Companion 앱 개발 착수에 충분한지 점검하는 audit 문서다.

목표 기준:

- 첫 release는 모바일 앱.
- Airi 1명.
- 100k+ 사용자 확장 가능성을 고려.
- Chat -> memory/relationship -> date event -> reward -> next session continuity 루프 구현.
- 비용, 안전, 운영, 결제, provider 장애를 출시 후가 아니라 초기 구조에 반영.

## 결론

현재 문서 세트는 **backend skeleton, DB migration, 모바일 API schema, rule engine, quota/ledger service 개발 착수 기준까지는 도달했다.**

다만 **상용 출시 완료 기준은 아직 아니다.**

출시 전까지 반드시 남은 것은 다음이다.

1. `29` 기준 provider별 실제 원가/latency 실측.
2. Plus/Premium/credit pack 실제 가격 확정.
3. `28` 기준 launch country별 privacy/terms/refund/legal 문구 확정.
4. `28` 기준 App Store/Google Play 최신 정책 재확인.
5. Pydantic schema와 Alembic migration 실제 코드 작성.
6. admin/auth/RBAC 구현.
7. beta QA와 `29` 기준 cost simulation.

## 1. Document coverage audit

| 영역 | 기준 문서 | 상태 | 판단 |
|---|---|---|---|
| 제품 정의 | `06` | covered | 핵심 루프와 지표 있음 |
| 시장/벤치마킹 | `01`, `14` | covered | Zeta/Nika류 대비 차별점 있음 |
| 첫 release scope | `15` | covered | Airi 1명, date 3개, store-safe 수위 |
| 모바일 UX/IA | `16` | covered | Chat/Date/Rewards/Profile, 상태/예외 포함 |
| 모바일 API | `17` | covered | endpoint, error, idempotency 기준 있음 |
| DB/ledger | `07`, `18` | covered | migration 수준 table/constraint/transaction 있음 |
| date event rule | `19` | covered | 3개 event deterministic rule 있음 |
| plan/credit | `20` | covered with placeholders | allowance/credit/refund 기준 있음, 가격은 placeholder |
| admin minimum | `21` | covered | 6개 필수 화면/RBAC/audit 있음 |
| Airi profile | `22` | covered | tone/safety/voice/visual 기준 있음 |
| relationship/memory | `23` | covered | level/update/memory lifecycle 있음 |
| provider quota/runtime | `08` | covered | concurrency/backpressure/fallback 기준 있음 |
| server architecture | `05` | covered | 100k 기준 아키텍처 방향 있음 |
| safety/launch ops | `10` | partial | 정책 방향 있음, 최신 store/legal 검증 필요 |
| development plan | `Docs/개발/01`, `02` | covered | stack/reuse/bottleneck 기준 있음 |
| OpenAPI/Pydantic | `25` | covered | schema naming/enums/DTO/contract test 기준 있음 |
| backend skeleton | `26` | covered | service/repository/provider boundary와 done criteria 있음 |
| load/SLO/capacity | `27` | covered | traffic model, load test, SLO, capacity 기준 있음 |
| store/legal/privacy | `28` | covered | AI disclosure, deletion, privacy, subscription/credit launch checklist 기준 있음 |
| provider/cost simulation | `29` | covered | provider benchmark, cost/user/day, plan margin simulation 기준 있음 |
| production ops/security/analytics | `30` | covered | deployment, CI/CD, secrets, observability, analytics, incident, backup 기준 있음 |
| mobile/admin wireframe/design | `31` | covered | mobile/admin wireframe, component baseline, design token, permission/store screenshot 기준 있음 |
| QA/test/release verification | `32` | covered | unit/integration/mobile/billing/safety/provider/load test와 release evidence 기준 있음 |
| decision register | `33` | covered | 개발 기본값, PM/engineering 결정, beta/commercial blocker 기준 있음 |

## 2. Development start readiness

### Backend skeleton

Ready enough:

- FastAPI 선택.
- service/repository/provider/worker 구조.
- mobile/admin API boundary.
- provider adapter 방향.
- request_id/idempotency/usage logging 기준.

Next implementation artifacts:

- project skeleton.
- settings/env structure.
- SQLAlchemy models.
- Alembic migration.
- Pydantic schemas from `25`.
- auth/session skeleton.

### DB migration

Ready enough:

- users/devices/characters/messages/memories/relationship/events/rewards/media/credit/provider/admin tables defined.
- key constraints and indexes defined.
- ledger/replay/snapshot policy defined.
- transaction rules for chat/date/credit defined.

Implementation/sign-off still needs:

- UUID/ULID decision managed in `33`.
- PostgreSQL enum/check decision managed in `33`.
- actual Alembic SQL.
- partitioning timing decision managed in `33`.

### Mobile client

Ready enough:

- Flutter primary recommendation.
- first-run journey.
- 4-tab IA.
- key screen states.
- quota/provider degraded/pending/error flows.

Implementation/sign-off still needs:

- Flutter screens implemented from `31`.
- design system/component baseline applied from `31`.
- OS permission copy applied from `31`.
- store screenshot/copy finalized from `31` and `28`.

### Rule engine

Ready enough:

- 3 date events specified.
- score/result bands.
- relationship/reward/memory outputs.
- idempotency and QA matrix.

Implementation/sign-off still needs:

- concrete JSON templates during implementation.
- unit/release tests from `32`.
- content copy variations during implementation.

### Monetization

Ready enough:

- Free/Plus/Premium structure.
- credit buckets/spend priority.
- rewarded ad reward ratio.
- refund/failure policy.

Implementation/sign-off still needs:

- final prices.
- IAP product ids.
- launch country tax/store/legal review.
- provider cost simulation.
- decision ownership and launch blockers managed in `33`.

### Admin/ops

Ready enough:

- minimum 6 screens.
- role definitions.
- audit requirement.
- kill switch/cost/queue/moderation flows.

Implementation/sign-off still needs:

- admin UI implemented from `31`.
- admin auth provider decision managed in `33`.
- internal deployment model from `30`.
- moderation SLA draft from `31`; final SLA after staffing decision.

## 3. 100k+ user readiness audit

Covered:

- stateless API direction.
- Redis rate limit/cache direction.
- queue/provider concurrency direction.
- provider usage event.
- cost dashboard.
- queue monitor.
- DB partitioning consideration.
- media storage/CDN direction.
- admin audit.

Not yet enough for actual 100k launch:

- no actual load test result yet.
- no production autoscaling verification.
- no measured DB capacity sizing.
- no provider quota contract.
- data warehouse/event analytics spec exists in `30`, but no real beta data yet.
- SLO/SLA numbers are draft, not validated by beta traffic.

Judgment:

- The documents are enough to build a commercial-shaped MVP that will not block future 100k scaling.
- They are not enough to promise 100k production traffic on day 1.
- This is the correct tradeoff. Designing full 100k infra before proving retention and unit economics would be wasteful.

## 4. Critical open decisions

PM/engineering must decide before beta:

1. Guest start account migration:
   - guest memory/credit transfer on login.
   - guest deletion behavior.

2. Age gate policy:
   - restricted mode vs block.
   - country-specific handling.

3. Pricing:
   - Plus/Premium monthly price.
   - credit pack price.
   - purchased credit expiration.

4. Provider selection:
   - LLM default/low-cost route.
   - STT provider.
   - TTS provider.
   - image provider.

5. Store/legal:
   - privacy policy.
   - terms.
   - subscription terms.
   - AI generated content disclosure.
   - refund policy.

6. Admin deployment:
   - internal VPN/private app/cloud auth.
   - manual credit adjustment approval.

## 5. Build sequence from current docs

Recommended next engineering sequence:

1. Backend skeleton from `26`: done in `Server/`.
2. Settings/env/request_id/logging: done in `Server/`.
3. Mobile/admin/webhook route boundary: done in `Server/`.
4. Guest auth/session persistence: done in `Server/`.
5. `users` and `user_sessions` SQLAlchemy models/Alembic migration: done in `Server/`.
6. v1 domain baseline SQLAlchemy models/Alembic migration from `18`: done in `Server/`.
7. Seed Airi character and expand authenticated bootstrap: done in `Server/`.
8. Implement Pydantic schemas from `25`.
9. Implement `POST /chat/turn` with mock provider.
10. Implement provider usage events and cost dashboard data path.
11. Implement character/relationship/memory base services.
12. Implement credit ledger and quota service.
13. Implement date event rule engine from `19`.
14. Implement reward/media async job skeleton.
15. Implement minimum admin API.
16. Add mobile Flutter skeleton around `16` IA.
17. Run mock-provider load tests from `27`.
18. Run provider benchmark/cost simulation from `29`.
19. Apply store/legal/privacy launch checklist from `28`.
20. Add production ops/security/observability/analytics baseline from `30`.
21. Build mobile/admin UI baseline from `31`.
22. Implement QA/release verification baseline from `32`.
23. Track PM/engineering decisions from `33`.

## 6. Release gate checklist

Closed beta gate:

- auth/guest session works.
- Airi chat works with mock or low-cost provider.
- relationship event/snapshot works.
- memory candidate/delete works.
- date event 3개 start/move/finish works.
- credit ledger replay works.
- provider usage event recorded.
- admin user lookup/credit/cost/moderation works.
- report/delete path works.
- QA blocker list from `32` has no blocking issue.

Public beta gate:

- real billing sandbox.
- rewarded ad sandbox.
- real provider latency/cost dashboard.
- queue retry/dead letter.
- media moderation.
- app crash/error monitoring.
- privacy/terms draft.
- mobile QA matrix from `32` passes.
- billing sandbox checks from `32` pass.

Commercial launch gate:

- final pricing.
- final legal/store copy.
- production admin RBAC.
- incident runbook rehearsal.
- observability/analytics dashboards ready.
- backup/restore rehearsal completed.
- provider benchmark/cost simulation completed.
- provider fallback tested.
- cost cap/kill switch tested.
- deletion/export tested.
- App Store/Google Play review package.
- release evidence checklist from `32` complete.
- commercial launch blockers from `33` resolved.

## 7. Final judgment

Current state:

```text
Planning completeness for development start: sufficient.
Planning completeness for commercial launch planning: sufficient.
Planning completeness for 100k scale planning: sufficient for architecture-aware MVP.
Planning completeness for 100k production proof: not achieved until load tests/provider quota/beta data exist.
```

Recommended stance:

- Start backend/mobile skeleton using these documents.
- Do not claim launch readiness yet.
- Do not expand scope to second character, video, live call, UGC, or marketplace before the Airi core loop is implemented and measured.
