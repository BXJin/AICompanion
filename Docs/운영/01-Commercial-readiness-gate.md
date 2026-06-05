# Commercial readiness gate

작성일: 2026-06-05

이 문서는 AICompanion을 closed beta, public beta, commercial launch로 올릴 수 있는지 판단하는 운영 게이트다.

핵심 판단:

```text
사용자가 돈을 낼 만큼 계속 돌아오는가?
AI 비용이 매출보다 빨리 커지지 않는가?
안전/삭제/신고/환불 문제가 운영자가 처리 가능한 형태로 들어오는가?
캐릭터 품질이 반복 사용 중 무너지지 않는가?
```

## 1. Stage 정의

| Stage | 목적 | 허용 범위 | 금지 |
|---|---|---|---|
| Internal alpha | 핵심 루프 검증 | mock/제한 provider, 테스트 계정 | 유료 결제, 외부 유저 모집 |
| Closed beta | 실제 사용성/비용 관찰 | 제한된 초대 유저, sandbox 또는 제한 결제 | 대규모 광고, scale claim |
| Public beta | store-safe 운영 검증 | 공개 유입, 제한 유료화 | 검증 안 된 이미지/음성 기능 확대 |
| Commercial launch | 반복 매출 운영 | 유료 플랜, CS/모니터링/정책 대응 | 미측정 비용 기능, 수동 DB 운영 |

## 2. Closed beta 진입 조건

필수:

- 첫 실행 -> 첫 채팅 -> memory/relationship 피드백이 동작한다.
- 최소 1개 date event가 시작/완료/결과/보상 상태까지 이어진다.
- report/delete/memory delete 진입점이 있다.
- provider usage event가 모든 AI 호출에 기록된다.
- credit ledger가 append-only이고 중복 차감/중복 지급을 막는다.
- admin이 user, credit, provider usage, report를 최소 조회할 수 있다.
- generated media는 moderation 전 사용자에게 공개되지 않는다.
- 기본 dashboard에서 API error, provider error, cost/day, queue backlog를 볼 수 있다.

권장 기준:

| 지표 | Closed beta 권장 기준 |
|---|---|
| app crash-free sessions | 98% 이상 |
| first chat success rate | 95% 이상 |
| chat response p95 | 5초 이하, 음성 제외 |
| TTS first audio p95 | 2.5초 이하 또는 pending UI 제공 |
| image reward completion p95 | 120초 이하 또는 async/pending UX 제공 |
| provider usage attribution | 99% 이상 |
| duplicate ledger anomaly | 0건 |

보류 조건:

- 비용 산출이 안 되는 provider 호출이 있다.
- report/delete 경로가 실제 레코드를 만들지 않는다.
- unsafe media가 moderation 없이 노출될 수 있다.
- 앱 첫 채팅이 불안정하다.

## 3. Public beta 진입 조건

필수:

- 모바일 QA matrix 통과.
- privacy/terms/support/account deletion 문구와 실제 동작이 일치한다.
- 앱스토어 AI disclosure, generated media disclosure, report path가 준비된다.
- provider timeout/rate limit/fallback/degraded 상태가 모바일에 표현된다.
- queue retry/dead letter 또는 실패 상태 처리가 있다.
- billing sandbox를 켠다면 duplicate webhook/idempotency/refund 테스트가 끝난다.
- safety test set이 통과한다.

권장 기준:

| 지표 | Public beta 권장 기준 |
|---|---|
| D1 retention | 25% 이상이면 계속 검증, 15% 미만이면 core loop 재검토 |
| D7 retention | 8% 이상이면 계속 검증, 4% 미만이면 출시 보류 |
| first chat -> second chat | 55% 이상 |
| first date event completion | 35% 이상 |
| quota exceeded -> paywall/shop view | 20% 이상 |
| report handling SLA | 24시간 이내 90% |
| deletion request tracking | 100% 추적 가능 |

보류 조건:

- paid plan copy와 backend allowance가 다르다.
- provider cost/user/day가 가격 정책으로 설명되지 않는다.
- safety incident를 admin에서 추적할 수 없다.
- Airi가 성인 캐릭터 정책과 충돌하는 이미지/말투로 노출된다.

## 4. Commercial launch 진입 조건

필수:

- final pricing, credit pack, subscription product id가 확정되어 문서/앱/스토어와 일치한다.
- provider benchmark와 cost simulation이 완료된다.
- load/SLO test 또는 명시적 risk acceptance가 있다.
- backup/restore rehearsal이 완료된다.
- incident runbook rehearsal이 완료된다.
- production admin RBAC와 audit log가 동작한다.
- media moderation kill switch, provider kill switch, high-cost feature cap이 있다.
- deletion/export workflow가 실제로 검증된다.
- store/legal checklist가 제출 국가 기준으로 재검토된다.

상용 출시 보류 조건:

- 비용 dashboard가 없다.
- credit/billing ledger replay가 맞지 않는다.
- duplicate webhook이 credit을 중복 지급할 수 있다.
- unsafe generated media가 공개될 수 있다.
- admin 민감 조회가 audit 없이 가능하다.
- 개인정보 삭제 요청을 추적하거나 완료 증명할 수 없다.
- 캐릭터 이미지/음성/말투 품질 기준이 없다.

## 5. Go / No-Go 회의 템플릿

```text
Release candidate:
Stage:
Decision: Go / No-Go / Go with risk acceptance

Product:
- D1/D7:
- first chat success:
- date event completion:
- paid intent / purchase:

Cost:
- cost/user/day:
- top 1% user cost:
- provider daily cap:
- high-cost feature kill switch:

Quality:
- chat p95:
- TTS first audio p95:
- image reward completion p95:
- crash-free sessions:

Safety/Ops:
- report backlog:
- moderation backlog:
- deletion request status:
- incident drill:
- backup/restore drill:

Known risks:
-

Owner sign-off:
- PM:
- Backend/Ops:
- Mobile:
- Safety/CS:
```

## 6. Risk acceptance 규칙

다음 리스크는 문서화된 risk acceptance 없이는 넘기지 않는다.

- SLO를 만족하지 못하지만 UX fallback으로 감수하는 경우.
- load test를 일부 생략하는 경우.
- 특정 국가의 법무 검토를 뒤로 미루는 경우.
- provider fallback 없이 단일 provider로 시작하는 경우.
- 이미지 생성 품질/일관성 기준이 목표보다 낮은 경우.
- paid flow 없이 public beta를 먼저 여는 경우.

risk acceptance에는 owner, 만료일, 보완 작업, rollback 기준을 적는다.
