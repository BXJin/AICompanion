# Admin minimum screen spec

작성일: 2026-06-04

이 문서는 첫 상용 모바일 release 전에 반드시 필요한 admin/backoffice 최소 화면을 정의한다.

기준 문서:

- `09-Admin-ops-tooling-and-backoffice.md`
- `10-Safety-policy-and-launch-operations.md`
- `18-DB-schema-and-ledger-migration-plan.md`
- `20-Credit-plan-allowance-policy.md`

## 결론

첫 release admin은 예쁘게 만드는 것이 목표가 아니다.

목표는 다음 사고를 막는 것이다.

1. 결제했는데 credit이 안 들어온다.
2. provider 비용이 폭주한다.
3. 부적절한 이미지/대화가 신고된다.
4. queue가 쌓여 사용자가 pending 상태에 갇힌다.
5. 운영자가 대화/이미지를 열람했는데 audit이 없다.

따라서 첫 release 최소 admin은 아래 6개 화면이다.

1. User lookup
2. Credit ledger viewer
3. Provider cost dashboard
4. Queue monitor
5. Moderation review
6. Admin audit log viewer

## 1. Admin access rules

필수:

- admin 전용 auth.
- RBAC.
- 모든 write action audit log.
- 대화 원문/이미지 열람 reason 필수.
- production admin 계정은 개인 계정과 분리.

Roles:

| role | allowed |
|---|---|
| super_admin | all |
| cs_operator | user lookup, credit ledger read, report status read |
| moderator | moderation review, content disable |
| content_ops | date event/reward template read/update draft |
| developer_ops | provider/queue/cost dashboard |
| finance_ops | billing/credit ledger read, refund workflow |

## 2. User lookup

목적:

- CS/운영자가 사용자 상태를 빠르게 확인한다.

Search keys:

- user id.
- email hash.
- device id hash.
- platform transaction id.
- report id.

Displayed:

- user status.
- plan.
- age_gate_status.
- created_at.
- last_login_at.
- linked devices.
- quota summary.
- recent safety/report flags.
- deletion request status.

Actions:

- view credit ledger.
- view reports.
- view memories metadata.
- request account deletion handling.
- suspend user. super_admin only.

Audit:

- user detail view는 audit log 대상.
- 대화 원문 보기와 credit adjustment는 별도 reason required.

## 3. Credit ledger viewer

목적:

- 결제/광고/환불/credit 지급 사고를 추적한다.

Displayed:

- current balance by bucket.
- ledger rows.
- source_type/source_id.
- idempotency_key.
- amount.
- reason.
- created_at.
- related webhook/job/report.

Filters:

- user_id.
- bucket.
- reason.
- date range.
- source_type.

Actions:

- manual adjustment request.
- export user ledger for CS.
- replay balance check.

Write action:

- 수동 조정은 super_admin 또는 finance_ops approval 필요.
- 조정은 ledger reversal/grant row로만 처리한다.
- 기존 ledger row 수정/삭제 금지.

## 4. Provider cost dashboard

목적:

- AI 비용 폭주를 조기에 발견한다.

Displayed:

- cost by day.
- cost by provider/model/route.
- cost by feature.
- cost by plan.
- p50/p90 latency.
- failure/fallback rate.
- top costly users.
- top costly features.

Alerts:

- daily budget threshold.
- provider failure spike.
- image generation spike.
- TTS cost spike.
- free user cost per day threshold.

Actions:

- enable slow-mode.
- downgrade route.
- pause free image generation.
- pause provider.
- adjust rewarded ad credit. super_admin/developer_ops.

Audit:

- kill switch 변경은 audit log 필수.

## 5. Queue monitor

목적:

- TTS/image/memory/moderation pending 상태를 운영자가 확인한다.

Displayed:

- queue by job_type.
- queued/running/succeeded/failed/dead_letter counts.
- oldest job age.
- average wait time.
- retry count.
- provider error_code.

Actions:

- retry failed job.
- cancel job.
- move to dead_letter.
- pause queue.
- resume queue.

Rules:

- user-facing job status와 queue backend 상태가 맞아야 한다.
- queue pause는 provider cost dashboard kill switch와 연결된다.

## 6. Moderation review

목적:

- 신고/이미지/안전 이벤트를 검토한다.

Queues:

- user reports.
- generated media pending review.
- rejected media.
- safety events high severity.

Displayed:

- target type.
- target preview with redaction.
- reporter.
- reason.
- safety result.
- related user/character.
- created_at.

Actions:

- approve.
- reject.
- disable asset.
- refund credit.
- warn user.
- suspend user.
- escalate.

Rules:

- media preview는 signed admin URL.
- explicit content는 redaction/blur default.
- 원문 대화 열람은 reason required.
- 모든 decision은 moderation_result와 admin_audit_logs에 기록.

## 7. Admin audit log viewer

목적:

- 운영자 접근과 조작을 추적한다.

Displayed:

- admin user.
- action.
- target_type.
- target_id.
- reason.
- request_id.
- ip_hash.
- created_at.

Filters:

- admin_user_id.
- target_type.
- target_id.
- action.
- date range.

Rules:

- audit log는 수정/삭제하지 않는다.
- 개인정보 최소화를 위해 before/after full payload 저장은 피한다.

## 8. Optional first release admin screens

있으면 좋지만 필수 6개보다 후순위:

- Conversation inspector.
- Memory manager.
- Prompt/version manager.
- Content/date event manager.
- Payment/refund console.

단, 다음 경우에는 optional이 아니라 필수가 된다.

- prompt를 운영 중 hot rollout한다면 Prompt/version manager 필요.
- memory 삭제 CS가 많다면 Memory manager 필요.
- 결제/환불을 내부에서 처리한다면 Payment/refund console 필요.

## 9. Admin API boundary

Admin API는 mobile API와 분리한다.

Base path:

```text
/api/admin/v1
```

필수 endpoint group:

- `/admin/users`
- `/admin/credits`
- `/admin/provider-usage`
- `/admin/jobs`
- `/admin/moderation`
- `/admin/audit-logs`

Security:

- separate admin auth.
- RBAC middleware.
- request_id.
- admin_audit middleware.
- IP allowlist optional for production.

## 10. Acceptance criteria

첫 release admin은 다음을 만족해야 한다.

- CS가 user id로 plan/quota/credit 상태를 확인할 수 있다.
- 결제/광고 credit 지급 내역을 ledger로 추적할 수 있다.
- provider cost를 day/provider/model/route별로 볼 수 있다.
- TTS/image/memory/moderation queue backlog를 볼 수 있다.
- 신고된 media/message를 moderation review에서 처리할 수 있다.
- admin이 대화/이미지를 열람하면 reason과 audit log가 남는다.
- kill switch 변경이 audit log에 남는다.

## 11. Open decisions

PM/engineering decision required:

1. admin 첫 버전 기술 스택: React+Vite 또는 Next.js.
2. admin 배포 위치: 내부 VPN, private app, 또는 cloud auth.
3. manual credit adjustment approval flow.
4. moderation SLA.
5. admin user onboarding/offboarding process.
