# AI companion commercial app master index

이 폴더는 PromptMotionLab을 기반으로 한 **차기 상용 AI companion/date mini-game 앱**의 기획, 비용, 서버 구조, 운영 정책을 정리한다.

중요한 전제:

- 현재 PromptMotionLab은 실시간 3D AI character pipeline 포트폴리오 프로젝트다.
- 차기 상용앱은 반드시 UE/3D일 필요가 없다.
- 상용 목표는 "AI와 대화한다"가 아니라 **AI companion과 관계를 쌓고, 데이트형 콘텐츠/미니게임/보상/기억이 연결되는 반복 서비스**다.
- 100k 사용자를 목표로 할 경우, 기능보다 먼저 비용 제어, LLM 동시성, 운영툴, 안전정책이 설계되어야 한다.

## 문서 읽는 순서

아래 목록을 최신 기준으로 본다. 같은 번호대의 짧은 초안 문서가 남아 있을 수 있지만, 상용 설계 기준 문서는 이 index에 적힌 파일을 우선한다.

1. `01-AI-companion-date-game-market.md`
   - 시장 포지션과 기존 서비스 대비 차별점.

2. `02-PromptMotionLab-reuse-map.md`
   - 현재 PromptMotionLab에서 재활용 가능한 코드/설계.

3. `03-Commercial-AI-companion-date-game-plan.md`
   - 제품 컨셉, 콘텐츠 루프, 과금 방향.

4. `04-AI-provider-cost-and-scaling.md`
   - AI provider 비용, 광고/구독/credit 수익 구조.

5. `05-Commercial-scale-server-architecture.md`
   - 100k connected 기준 서버 아키텍처 초안.

6. `06-Commercial-product-PRD-and-core-loop.md`
   - 상용 제품 PRD, 핵심 루프, 유저 경험 기준.

7. `07-Data-model-state-and-ledger-design.md`
   - 사용자, 캐릭터, 기억, 관계, 보상, 결제 ledger 데이터 모델.

8. `08-LLM-runtime-concurrency-and-provider-quota.md`
   - LLM 동시 호출, provider quota, queue, fallback 설계.

9. `09-Admin-ops-tooling-and-backoffice.md`
   - 운영툴, CS, moderation, 비용/장애 모니터링.

10. `10-Safety-policy-and-launch-operations.md`
    - 안전정책, 개인정보, 신고/차단, 런칭 운영 정책.

11. `11-Commercial-roadmap-team-and-release-gates.md`
    - 상용 런칭 로드맵, 팀 구성, release gate.

12. `12-Commercial-detailed-design-backlog.md`
    - 다음 단계에서 세부 설계해야 할 API, DB, admin, queue, payment, safety 작업 목록.

13. `13-Mobile-first-commercial-detail-plan.md`
    - 첫 상용 버전을 모바일 앱으로 잡았을 때의 화면, API, 과금, 리스크 설계.

14. `14-Zeta-Nika-benchmark-commercial-design.md`
    - Zeta/Nika/Aurora류 상용 서비스 벤치마킹과 우리 제품 설계 반영안.

15. `15-First-release-scope-decisions.md`
    - 첫 상용 모바일 release의 date mini-game, free allowance, 캐릭터 수, 수위, 첫 화면 핵심 경험 권장안.

16. `16-Mobile-user-journey-and-screen-IA.md`
    - 첫 상용 모바일 release의 사용자 여정, 하단 탭 IA, 핵심 화면, 상태/예외 흐름, UX acceptance criteria.

17. `17-Mobile-API-contract.md`
    - 첫 상용 모바일 release의 API 계약, 공통 error/idempotency 규칙, chat/date/reward/credit/report endpoint 기준.

18. `18-DB-schema-and-ledger-migration-plan.md`
    - PostgreSQL migration 수준의 테이블, 제약, 인덱스, transaction, ledger 설계 기준.

19. `19-Date-event-rule-spec.md`
    - 첫 release 3개 official date event의 deterministic rule, score, reward, relationship, QA 기준.

20. `20-Credit-plan-allowance-policy.md`
    - Free/Plus/Premium/Credit/Ads 제공량, credit 단위, 실패/환불, quota/kill switch 정책.

21. `21-Admin-minimum-screen-spec.md`
    - 첫 release 필수 admin 6개 화면, RBAC, audit, moderation, queue/cost 운영 기준.

22. `22-Airi-character-profile-v1.md`
    - 첫 release 단일 캐릭터 Airi의 personality, tone, safety, voice, visual, QA 기준.

23. `23-Relationship-memory-rule-table.md`
    - relationship level/update, memory extraction/retrieval/delete, service contract 기준.

24. `24-Commercial-development-readiness-audit.md`
    - 현재 문서 세트가 개발 착수/상용 출시/100k 확장 기준에서 어디까지 충분한지 점검한 audit.

25. `25-OpenAPI-Pydantic-schema-plan.md`
    - FastAPI/Pydantic schema naming, shared enum, DTO, OpenAPI generation, contract test 기준.

26. `26-Backend-skeleton-service-boundary-plan.md`
    - backend skeleton layout, service/repository/provider boundary, transaction, test, done criteria 기준.

27. `27-Scale-load-test-SLO-capacity-plan.md`
    - 100k+ 확장을 고려한 traffic model, load test, SLO, autoscaling, DB/provider capacity 기준.

28. `28-Store-legal-privacy-launch-checklist.md`
    - Store policy, legal/privacy, AI disclosure, deletion, subscription/credit launch checklist.

29. `29-Provider-evaluation-cost-simulation-plan.md`
    - LLM/STT/TTS/image provider benchmark, cost/user/day, plan margin simulation 기준.

30. `30-Production-ops-security-observability-analytics-plan.md`
    - Production ops, security, observability, analytics, deployment, incident/backup 기준.

31. `31-Mobile-admin-wireframe-design-system-spec.md`
    - Mobile/admin wireframe, component baseline, design token, permission copy, store screenshot 기준.

32. `32-QA-test-release-verification-plan.md`
    - Unit/integration/mobile/billing/safety/provider/load QA, release evidence, blocker 기준.

33. `33-Commercial-v1-decision-register.md`
    - PM/engineering decision register, development defaults, beta/commercial launch blockers.

## Archive

중복되던 짧은 초안 문서는 `_archive/commercial-drafts-20260602/`로 이동했다. 최신 상용 설계 기준은 이 index에 적힌 문서만 따른다.

## PM 판단 기준

상용앱으로 갈 때 "가능한 기능"보다 중요한 것은 다음 순서다.

1. 사용자가 매일 다시 들어올 이유가 있는가?
2. 무료 사용자가 바로 이탈하지 않을 만큼 핵심 경험을 제공하는가?
3. 유료 전환 이유가 비용 높은 기능과 자연스럽게 연결되는가?
4. AI 비용이 매출보다 빠르게 증가하지 않도록 제한되어 있는가?
5. 운영자가 문제 사용, 비용 폭주, 모델 장애, 부적절 콘텐츠를 볼 수 있는가?
6. 개인정보 삭제, 신고, 환불, 미성년/성인 콘텐츠 정책이 준비되어 있는가?
7. 사용자가 첫날 Airi의 memory/relationship/reward 연결을 실제로 체감하는가?

## 개발 판단 기준

상용 구조에서는 다음을 금지한다.

- LLM 호출을 무제한 동시 실행
- 사용자 상태를 서버 메모리에만 저장
- credit 차감을 단순 balance update로 처리
- admin access audit 없이 대화/이미지를 열람
- provider 장애 시 전체 서비스 중단
- 무료 사용자의 고비용 기능 무제한 허용
- safety/moderation을 출시 후에 붙이는 방식
- 화면에서 queue, quota, provider degraded 상태를 숨기고 사용자를 방치하는 방식
