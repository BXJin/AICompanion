# Commercial v1 decision register

작성일: 2026-06-04

이 문서는 AI Companion 첫 상용 release 개발을 막는 PM/engineering 결정을 한 곳에서 관리한다. 목적은 모든 결정을 지금 확정하는 것이 아니라, 개발용 기본값과 상용 출시 전 최종 sign-off 항목을 분리하는 것이다.

원칙:

- 개발 기본값은 코드/DB/API를 만들 수 있게 해준다.
- 상용 출시 확정값은 provider 실측, 스토어 정책, 법무/세무, PM pricing 판단 이후에 닫는다.
- launch blocker와 non-blocker를 구분한다.
- 결정 변경이 DB migration, API contract, billing product, mobile UI copy에 미치는 영향을 기록한다.

## 1. Decision status

| Status | Meaning |
|---|---|
| decided | v1 개발/출시에 사용 |
| dev_default | 개발은 진행하되 출시 전 재확정 필요 |
| blocked | 결정 없이는 해당 구현/출시 불가 |
| measure_first | 실측/테스트 후 결정 |
| legal_review | 법무/스토어/세무 검토 후 결정 |

## 2. Product decisions

| ID | Decision | Status | Development default | Launch requirement | Owner |
|---|---|---|---|---|---|
| P-001 | First release character count | decided | Airi 1명 | same | PM |
| P-002 | Explicit adult content | decided | not supported | same | PM/Safety |
| P-003 | Date event count | decided | 3 official events | same or PM-approved additions | PM |
| P-004 | First screen | decided | Chat home | same | PM |
| P-005 | Shop placement | decided | no bottom tab, contextual entry | same unless conversion test changes | PM |
| P-006 | Live voice call | decided | excluded | separate roadmap decision | PM/Engineering |
| P-007 | Multi-character/UGC marketplace | decided | excluded | separate roadmap decision | PM |

## 3. Account and age decisions

| ID | Decision | Status | Development default | Launch requirement | Owner |
|---|---|---|---|---|---|
| A-001 | Guest start | dev_default | allowed with server guest user | confirm fraud/privacy handling | PM/Engineering |
| A-002 | Guest account migration | dev_default | migrate memory summary and eligible credits on account link | final abuse/fraud policy | PM/Engineering |
| A-003 | Guest deletion | dev_default | immediate deletion if no payment ledger; otherwise deletion request flow | legal/accounting retention review | PM/Legal |
| A-004 | Age gate | legal_review | block underage from romantic/suggestive mode | launch country policy | PM/Legal/Safety |
| A-005 | Adult-coded Airi | decided | profile states adult character | store screenshot/copy review | PM/Safety |

## 4. Data and DB decisions

| ID | Decision | Status | Development default | Launch requirement | Owner |
|---|---|---|---|---|---|
| D-001 | Primary key format | dev_default | UUID v7 or ULID-compatible string id | choose one before first migration merge | Backend |
| D-002 | PostgreSQL enum vs varchar/check | dev_default | varchar + application enum + check for fast-changing policy fields | keep migration compatibility | Backend |
| D-003 | Message partitioning | measure_first | no partition in v1 migration, design indexes so partitioning can be added | decide after beta volume/load test | Backend/Ops |
| D-004 | Ledger model | decided | append-only ledger with compensating events | same | Backend/Finance |
| D-005 | Ledger balance snapshot | dev_default | derived snapshot with replay verification job | verify in QA before paid beta | Backend |
| D-006 | Raw message retention | legal_review | retain only as needed for product/safety; summarize memory separately | privacy policy and deletion policy | PM/Legal/Backend |
| D-007 | Memory deletion | decided | soft delete/exclude from retrieval, job/audit trail | same | Backend/Safety |
| D-008 | Admin audit retention | legal_review | immutable audit with minimized personal data | legal retention period | Ops/Legal |

Recommendation:

- Use UUID v7 if stack/tooling supports it cleanly. If not, use UUID4 for first migration and avoid leaking ordering assumptions into product logic.
- Avoid DB enums for plan/status/safety values that may change under store policy pressure.

## 5. API and runtime decisions

| ID | Decision | Status | Development default | Launch requirement | Owner |
|---|---|---|---|---|---|
| API-001 | Auth token refresh | dev_default | short-lived access token + refresh token/session endpoint | security review before public beta | Backend |
| API-002 | Streaming transport | dev_default | start with HTTP response or SSE; WebSocket only if voice/live requires it | mobile latency test | Backend/Mobile |
| API-003 | Idempotency | decided | required for chat write, date finish, reward, billing/credit actions | same | Backend |
| API-004 | Outbox/retry pattern | dev_default | outbox for reward/media/billing side effects | integration test before public beta | Backend |
| API-005 | Provider fallback | decided | route-level fallback and text-only fallback | real provider test before public beta | Backend |
| API-006 | Queue technology | dev_default | Redis queue/Celery/RQ equivalent for v1 | revisit if backlog/throughput exceeds threshold | Backend/Ops |

## 6. Monetization decisions

| ID | Decision | Status | Development default | Launch requirement | Owner |
|---|---|---|---|---|---|
| M-001 | Free plan exists | decided | yes | same | PM |
| M-002 | Plus/Premium exists | dev_default | yes, placeholder products disabled in production | final price and copy sign-off | PM/Finance |
| M-003 | Credit pack exists | dev_default | yes, sandbox product ids only | final price, expiration, refund policy | PM/Finance/Legal |
| M-004 | Purchased credit expiration | legal_review | no forced expiration in development | launch country legal/tax review | PM/Legal/Finance |
| M-005 | Provider failure refund | decided | no charge before success when possible; compensating refund if charged | QA proof from `32` | Backend/Finance |
| M-006 | Rewarded ads | dev_default | interface and ledger source supported; launch can disable | ad network policy and fraud review | PM/Engineering |
| M-007 | Store fee assumption | measure_first | model 15% and 30% scenarios | final store/account condition | Finance |

Development product ids:

```text
plus_monthly_dev
premium_monthly_dev
credits_small_dev
credits_medium_dev
credits_large_dev
```

Production product ids must not be created until final price/copy is approved.

## 7. Provider decisions

| ID | Decision | Status | Development default | Launch requirement | Owner |
|---|---|---|---|---|---|
| PR-001 | LLM default provider | measure_first | provider interface + mock + configurable route | benchmark from `29` | Backend/PM |
| PR-002 | STT provider | measure_first | text fallback always available | Korean WER/latency test | Backend/Mobile |
| PR-003 | TTS provider | measure_first | provider interface + cached phrase support | voice quality/cost test | PM/Backend |
| PR-004 | Image provider | measure_first | async queue + moderation + kill switch | accepted image cost and safety test | PM/Backend/Safety |
| PR-005 | Provider data terms | legal_review | no production launch until reviewed | commercial/data policy sign-off | Legal/Backend |

## 8. Admin and ops decisions

| ID | Decision | Status | Development default | Launch requirement | Owner |
|---|---|---|---|---|---|
| O-001 | Admin frontend stack | dev_default | React+Vite or simple internal web matching backend auth | choose before admin UI implementation | Engineering |
| O-002 | Admin deployment | dev_default | private access/cloud auth, no public unauthenticated route | final SSO/VPN/private app decision | Ops |
| O-003 | Manual credit adjustment | decided | reason + audit + approval for high-risk adjustment | same | PM/Ops |
| O-004 | Moderation SLA | dev_default | SLA draft from `31` | staffing and escalation owner | PM/Ops/Safety |
| O-005 | Incident owner | dev_default | backend/ops owner during beta | on-call assignment before public beta | Engineering/Ops |
| O-006 | Backup/restore | decided | backup enabled, restore rehearsal before launch | evidence from `30`/`32` | Ops |

## 9. UI/content decisions

| ID | Decision | Status | Development default | Launch requirement | Owner |
|---|---|---|---|---|---|
| UI-001 | Mobile IA | decided | Chat/Date/Rewards/Profile | same | PM/Design |
| UI-002 | Design system | dev_default | baseline tokens/components from `31` | final visual QA before store screenshots | Design/PM |
| UI-003 | Store screenshots | legal_review | safe screenshots from `31` | final store/legal review | PM/Design/Legal |
| UI-004 | AI disclosure copy | legal_review | copy from `28`/`31` | store/legal sign-off | PM/Legal |
| UI-005 | Date event content copy | dev_default | content variations during implementation | QA from `32` | PM/Content |

## 10. Decisions that block development

The following must be decided before implementation starts:

- backend stack: FastAPI/Python.
- DB: PostgreSQL.
- first character: Airi.
- first release scope: chat, memory, relationship, 3 date events, reward, credit, admin minimum.
- no explicit adult content.
- ledger append-only.
- provider adapter abstraction.

Current status:

```text
No development blocker remains at planning level.
```

## 11. Decisions that block public beta

Public beta blockers:

- auth/session security review not completed.
- report/delete path unavailable.
- billing sandbox idempotency not tested if paid flow is enabled.
- provider fallback not tested.
- admin audit missing.
- moderation queue missing.
- privacy/terms draft missing.
- mobile QA matrix from `32` not passed.

## 12. Decisions that block commercial launch

Commercial launch blockers:

- final Plus/Premium/credit prices not signed off.
- production IAP product ids not created/reviewed.
- provider benchmark from `29` incomplete.
- store/legal/privacy checklist from `28` incomplete.
- production ops checklist from `30` incomplete.
- QA/release evidence from `32` incomplete.
- load/SLO proof from `27` missing without explicit risk acceptance.
- account deletion/privacy behavior differs from published policy.

## 13. Change control

Any change to these decisions must update affected documents:

- Product scope: `15`, `16`, `24`.
- API: `17`, `25`, `26`.
- DB/ledger: `18`, `20`.
- Date/rule: `19`.
- Admin: `21`, `31`.
- Store/legal: `28`.
- Provider/cost: `29`.
- Ops/security/analytics: `30`.
- QA/release: `32`.

