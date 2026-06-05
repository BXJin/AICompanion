# AICompanion operations master index

작성일: 2026-06-05

이 폴더는 AI Companion / 연애 시뮬레이션형 서비스의 상용 운영 판단 기준을 모은다.

`Docs/기획`은 무엇을 만들지와 왜 만드는지를 정리한다. `Docs/운영`은 출시해도 되는지, 운영 중 어떤 수치를 보고 멈출지, CS/안전/비용/품질 문제를 어떻게 처리할지를 정리한다.

## 읽는 순서

1. `01-Commercial-readiness-gate.md`
   - closed beta, public beta, commercial launch로 넘어가기 위한 운영 게이트.

2. `02-Live-ops-playbook.md`
   - 운영자가 매일/매주 확인해야 할 대시보드, CS, moderation, 비용, 장애 대응.

3. `03-Beta-metrics-cost-and-quality-validation.md`
   - 베타에서 상용 가능성을 판단하기 위한 retention, latency, cost, conversion, safety 지표.

4. `04-Character-consistency-and-content-quality-ops.md`
   - Airi 캐릭터 일관성, 이미지/음성/말투 품질 검수, 프롬프트/모델 변경 운영.

## 운영 문서의 원칙

- 감으로 출시하지 않는다. 다음 단계로 넘어가는 기준은 수치와 증거로 남긴다.
- 비용이 통제되지 않는 기능은 기본 제공하지 않는다.
- 안전/신고/삭제/환불/차단 경로가 없는 기능은 public beta에 올리지 않는다.
- 캐릭터 일관성이 깨지는 변경은 기능 회귀로 본다.
- prompt, provider, 가격, credit 정책 변경은 운영 이벤트로 기록한다.
- 장애 대응보다 중요한 것은 장애가 난 기능을 빨리 제한할 수 있는 kill switch다.

## 관련 기획/개발 문서

- `Docs/기획/10-Safety-policy-and-launch-operations.md`
- `Docs/기획/20-Credit-plan-allowance-policy.md`
- `Docs/기획/24-Commercial-development-readiness-audit.md`
- `Docs/기획/27-Scale-load-test-SLO-capacity-plan.md`
- `Docs/기획/28-Store-legal-privacy-launch-checklist.md`
- `Docs/기획/29-Provider-evaluation-cost-simulation-plan.md`
- `Docs/기획/30-Production-ops-security-observability-analytics-plan.md`
- `Docs/기획/32-QA-test-release-verification-plan.md`
- `Docs/기획/33-Commercial-v1-decision-register.md`
- `Docs/개발/03-Modular-monolith-and-service-boundary.md`

## 세션 간 사용 규칙

- 서버 세션은 운영 지표를 만들거나 바꾸면 이 폴더의 게이트/플레이북과 맞는지 확인한다.
- 모바일 세션은 사용자에게 노출되는 장애, quota, pending, rejected, report/delete 상태가 운영 문서와 맞는지 확인한다.
- PM/기획 세션은 가격, 정책, 캐릭터, 안전 기준을 바꾸면 운영 게이트와 QA 문서를 같이 갱신한다.
- 상용 출시 가능성 판단은 `Docs/운영/01`과 `Docs/운영/03`의 증거가 없으면 보류로 본다.
