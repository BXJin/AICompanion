# Commercial roadmap, team, and release gates

이 문서는 "데모"가 아니라 실제 상용앱 출시를 목표로 한 개발 로드맵이다. MVP라는 말로 품질 기준을 낮추면 안 된다. 대신 **단계별 출시 범위를 줄이되, 구조는 상용형으로 유지**한다.

## 제품 단계

### Phase 0: Commercial architecture prototype

목표:

- 상용 구조의 뼈대를 검증한다.

필수:

- auth.
- user/character state DB.
- credit ledger.
- provider usage logging.
- model routing.
- basic admin dashboard.
- queue 기반 async job.

출시 대상:

- 내부 테스트.

성공 기준:

- 한 사용자의 대화/기억/credit/보상 흐름이 DB로 남는다.
- provider 비용이 feature/user 단위로 추적된다.
- LLM/TTS/image job이 queue로 제어된다.

### Phase 1: Closed beta

목표:

- 핵심 재미와 비용 구조를 검증한다.

범위:

- 1~2명 캐릭터.
- text chat.
- limited voice/TTS.
- 3~5개 date event.
- memory summary.
- reward image unlock.
- manual moderation.

성공 기준:

- D1 retention 의미 있는 수준.
- user당 AI cost 예측 가능.
- safety incident 대응 가능.
- CS 처리 가능.

### Phase 2: Public beta

목표:

- 유료 전환과 광고/credit 루프 검증.

범위:

- Plus subscription.
- rewarded ads.
- credit purchase.
- image generation credit.
- admin ops 강화.
- provider fallback.
- queue/backpressure.

성공 기준:

- paid conversion 측정.
- free user cost cap 유지.
- provider 장애 시 서비스 유지.
- moderation SLA 운영.

### Phase 3: Commercial launch

목표:

- 실제 매출과 운영 지속성.

범위:

- Plus/Premium.
- credit packs.
- seasonal event.
- content ops.
- prompt rollout.
- full audit log.
- privacy/delete/export.

성공 기준:

- gross margin이 양수.
- CS/운영 프로세스가 버틴다.
- crash/latency/provider failure가 허용 범위.
- 주요 safety policy 통과.

### Phase 4: Scale to 100k connected users

목표:

- 대규모 연결 사용자와 고비용 AI 작업을 분리해 안정 운영.

필수:

- Redis/queue cluster.
- multi-region or region-aware routing.
- autoscaling.
- provider quota manager.
- dedicated media generation workers.
- data warehouse.
- fraud/abuse detection.
- SLA/SLO.

## 팀 구성

최소 상용팀:

- Product Manager.
- Backend Lead.
- AI Application Engineer.
- Mobile/Web Client Engineer.
- Content Designer.
- UI/UX Designer.
- DevOps/SRE.
- QA.
- CS/Moderator.

성장 시 필요:

- Data Analyst.
- Trust & Safety Lead.
- Billing/Payment Engineer.
- ML/Prompt Engineer.
- Creator/Content Ops.

## 개발 원칙

1. Feature보다 ledger와 usage logging을 먼저 만든다.
2. Provider는 바뀔 수 있으므로 adapter/provider 구조로 둔다.
3. LLM은 게임 판정을 맡지 않고 대사/감정/힌트만 맡는다.
4. Credit 차감은 idempotency key가 있어야 한다.
5. 모든 admin access는 audit log를 남긴다.
6. Free plan에는 핵심 경험을 조금 주되, 고비용 기능은 credit으로 보호한다.
7. Prompt 변경도 배포로 취급한다.

## Release gates

### Product gate

- 사용자가 하루 뒤 다시 들어올 이유가 있는가?
- Free에서도 서비스 가치를 체감하는가?
- 유료 전환 이유가 명확한가?
- 광고가 경험을 파괴하지 않는가?
- reward가 단순 보상이 아니라 관계/스토리와 연결되는가?

### Engineering gate

- p50/p90 latency 측정 가능.
- provider failure fallback.
- queue backlog dashboard.
- credit ledger 검증.
- admin audit log.
- smoke/regression test.
- rollback 가능.

### Cost gate

- cost/user/day 측정.
- plan별 gross margin 계산.
- image/video credit 원가 추적.
- daily cost cap.
- provider별 kill switch.

### Safety gate

- user report.
- moderation review.
- memory delete.
- account delete.
- age/character policy.
- crisis response.
- media moderation.

### Store gate

- privacy policy.
- AI generated content disclosure.
- subscription terms.
- refund policy.
- ad disclosure.
- user data deletion path.

## 100k 기준 준비 체크

100k connected 전까지 반드시 필요한 것:

- stateless API server.
- Redis rate limit.
- distributed queue.
- provider quota manager.
- DB read/write scaling.
- media storage/CDN.
- admin dashboard.
- data warehouse.
- alerting.
- incident runbook.

필요하지만 나중에 해도 되는 것:

- self-hosted LLM.
- custom fine-tuned foundation model.
- multi-character marketplace.
- full video call.
- realtime multiplayer.

## PromptMotionLab 이후 실제 개발 순서

1. Product PRD 확정.
2. DB schema와 ledger 먼저 설계.
3. auth/payment/credit skeleton.
4. text chat + memory + relationship state.
5. date mini-game rule engine.
6. reward/media unlock.
7. provider cost dashboard.
8. admin moderation.
9. ads/subscription/credit pack.
10. public beta.

