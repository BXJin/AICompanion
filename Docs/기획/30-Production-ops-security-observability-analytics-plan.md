# Production ops, security, observability, and analytics plan

작성일: 2026-06-04

이 문서는 AI Companion을 실제 상용 서비스로 운영하기 위해 필요한 production operations, security, observability, analytics, deployment 기준을 정의한다.

`05`, `10`, `21`, `24`, `26`, `27`, `28`, `29`에 흩어진 운영 요구사항을 개발 착수 가능한 체크리스트로 묶는다. 이 문서는 기능 추가 기획이 아니라 상용 운영에서 서비스가 깨지지 않도록 하는 최소 운영 기준이다.

## 1. Scope

포함:

- environment strategy.
- CI/CD and release gates.
- secrets and configuration.
- authentication/security controls.
- observability events, logs, metrics, traces.
- product analytics event taxonomy.
- incident response.
- backup, restore, and disaster recovery.
- data retention and privacy operations.
- production readiness checklist.

제외:

- full enterprise SOC2/ISO certification.
- multi-region active-active architecture.
- self-hosted model operations.
- advanced fraud scoring model.

## 2. Environments

최소 환경:

| Environment | Purpose | Data | External providers |
|---|---|---|---|
| local | developer loop | fake/minimal seed | mock by default |
| dev | shared development | synthetic only | sandbox or mock |
| staging | release verification | synthetic + approved test accounts | sandbox or limited production keys |
| production | real users | real data | production keys |

원칙:

- production data를 local/dev로 복사하지 않는다.
- staging은 production과 같은 migration, queue, cache, object storage 구조를 사용한다.
- provider key는 environment별로 분리한다.
- billing, subscription, rewarded ads는 sandbox와 production product id를 분리한다.
- admin은 production과 staging login boundary를 분리한다.

## 3. Deployment model

첫 상용 release 권장:

```text
Mobile app
-> CDN/WAF/API gateway
-> FastAPI application
-> PostgreSQL
-> Redis
-> Worker queue
-> Object storage/CDN
-> Observability stack
```

Backend deployment:

- stateless API containers or app service instances.
- separate worker process for TTS, image, memory extraction, moderation.
- separate scheduler for reconciliation and cleanup jobs.
- migration step before app rollout.
- health check endpoint.
- readiness check endpoint.
- graceful shutdown for in-flight requests.

Admin deployment:

- separate admin frontend or protected admin route.
- production admin behind SSO, VPN, private access, or cloud identity-aware proxy.
- admin API requires RBAC and audit log.
- no direct database editing for normal operations.

## 4. CI/CD gates

Pull request gate:

- lint.
- unit tests.
- schema validation.
- migration generation check.
- OpenAPI generation check.
- contract tests for public API.
- security/static dependency check where available.

Staging gate:

- migration apply/rollback test.
- smoke test for auth, chat, credit ledger, date event, report/delete.
- provider mock test.
- billing sandbox webhook idempotency test.
- admin audit action test.
- queue retry/dead letter test.

Production gate:

- feature flag defaults reviewed.
- kill switches reviewed.
- migration backup point confirmed.
- rollback plan documented.
- dashboard and alert links ready.
- on-call owner assigned.

## 5. Secrets and configuration

Secrets:

- provider API keys.
- database credentials.
- Redis credentials.
- JWT/session signing keys.
- Apple/Google billing secrets.
- object storage signing keys.
- admin SSO credentials.
- webhook signing secrets.

Rules:

- secrets are never stored in repo.
- secrets are injected through environment/secret manager.
- production secrets are readable only by deployment runtime and minimal operators.
- key rotation must be possible without code change.
- provider keys can be disabled per route.

Configuration categories:

| Category | Examples | Change process |
|---|---|---|
| static config | database URL, storage bucket | deployment |
| runtime config | route timeout, token cap, kill switch | admin/config store |
| product policy | allowance, credit price, safety threshold | versioned config |
| experiment | copy, prompt version, model route | feature flag |

## 6. Security controls

API security:

- request size limit.
- rate limit by IP, user, device, route.
- auth token expiration and refresh.
- idempotency key for write/charge/reward endpoints.
- signed webhook verification.
- upload content type and size validation.
- CORS allowlist.
- abuse blocklist.

Data security:

- passwordless/social login or secure credential storage.
- conversation and memory access scoped by user_id.
- admin data access requires role and reason.
- raw conversation export limited to approved roles.
- payment/ledger records are immutable except compensating entries.
- generated media uses signed URLs or access-controlled delivery.

Operational security:

- production DB access is audited.
- admin actions write `admin_audit_logs`.
- provider dashboard keys are restricted.
- break-glass access has a time limit and postmortem requirement.
- suspicious usage can trigger user/feature/provider throttle.

## 7. Observability

Every request should carry:

- request_id.
- user_id when authenticated.
- device_id when available.
- session_id.
- route.
- feature_route.
- provider_route when used.
- app_version.
- platform.
- country when available.

Required logs:

| Log/event | Purpose |
|---|---|
| api_request_log | latency, status, route health |
| provider_usage_event | cost, token, latency, provider attribution |
| credit_ledger_event | charge/refund/replay |
| relationship_event | relationship progression audit |
| memory_event | extraction/delete/retrieval audit |
| safety_event | moderation and blocked response trace |
| queue_job_event | retry/dead letter/backlog |
| billing_webhook_event | duplicate/delayed payment handling |
| admin_audit_log | operator accountability |
| deletion_request_event | privacy operation trace |

Required metrics:

- API request count/error rate.
- p50/p90/p99 latency by route.
- chat first-token latency.
- provider latency and failure rate.
- provider fallback rate.
- cost per user/day.
- queue backlog and oldest job age.
- credit ledger mismatch count.
- billing webhook failure count.
- report/moderation backlog.
- memory delete completion time.
- crash-free sessions.

Alert examples:

| Alert | Initial threshold |
|---|---|
| API 5xx rate | 5m above 2% |
| chat p90 latency | 10m above SLO |
| provider failure rate | 5m above 5% |
| provider daily spend | 80% of daily cap |
| queue oldest job age | above route limit |
| billing webhook failures | any sustained failure |
| ledger replay mismatch | any confirmed mismatch |
| deletion job stalled | over policy SLA |
| moderation backlog | over SLA |

## 8. Analytics event taxonomy

Analytics는 product decision과 cost control을 위해 필요하다. 개인정보 위험을 줄이기 위해 raw message content를 analytics event에 넣지 않는다.

Core product events:

| Event | Required properties |
|---|---|
| app_opened | user_id, session_id, app_version, platform |
| onboarding_started | source, platform |
| age_gate_completed | result, country |
| chat_turn_sent | route, plan, input_mode, character_id |
| chat_turn_completed | route, latency_ms, provider_route, cost_bucket |
| voice_input_started | plan, remaining_allowance |
| tts_played | voice_id, cached, latency_ms |
| memory_saved | memory_type, confidence_bucket |
| memory_deleted | memory_type, source |
| relationship_level_changed | from_level, to_level, reason |
| date_event_started | template_id, relationship_level |
| date_event_completed | template_id, result_band, reward_status |
| reward_unlocked | reward_type, source, moderation_status |
| quota_exceeded | feature_route, plan |
| credit_spent | source, amount, feature_route |
| credit_refunded | reason, amount |
| subscription_screen_viewed | entry_point, plan |
| subscription_purchased | plan, store, price_bucket |
| report_submitted | target_type, category |
| account_deletion_requested | user_type, reason_bucket |

Funnel metrics:

- onboarding start -> first chat.
- first chat -> second chat.
- first chat -> first memory saved.
- first date event prompt -> date event completed.
- date event completed -> reward viewed.
- quota exceeded -> subscription screen viewed.
- subscription screen viewed -> purchase.

Retention metrics:

- D1 retention.
- D7 retention.
- D30 retention.
- chat days per week.
- date event completion per week.
- reward unlock per week.
- memory interaction per week.

Cost analytics:

- cost/user/day by plan.
- cost/feature_route.
- top 1% user cost.
- provider cost by route.
- failed provider cost.
- refunded credit cost.

## 9. Incident response

Incident severity:

| Severity | Examples | Response target |
|---|---|---|
| SEV0 | data leak, payment corruption, unsafe content mass exposure | immediate |
| SEV1 | chat unavailable, billing broken, provider cost runaway | under 15m triage |
| SEV2 | major feature degraded, queue backlog, admin unavailable | under 1h triage |
| SEV3 | minor degradation, isolated provider issue | next business day |

Runbook template:

1. Declare incident and owner.
2. Identify impacted users/features.
3. Check dashboards and recent deploys.
4. Apply kill switch or rollback if needed.
5. Preserve logs and audit evidence.
6. Communicate status internally.
7. Resolve or mitigate.
8. Write postmortem with action items.

High-risk runbooks required before public beta:

- provider outage.
- provider cost spike.
- billing webhook failure.
- credit ledger mismatch.
- unsafe generated media exposure.
- account deletion job failure.
- data export/delete request escalation.
- admin account compromise.
- queue backlog saturation.

## 10. Backup and recovery

Minimum backup policy:

- PostgreSQL automated daily backups.
- point-in-time recovery if supported by hosting tier.
- object storage versioning or deletion protection for generated media where practical.
- config backup for runtime policy.
- migration rollback plan.

Restore test:

- staging restore test before public beta.
- production restore rehearsal before commercial launch.
- ledger replay check after restore.
- sample user account recovery check.
- media URL/access check.

Data that must not be casually restored:

- deleted memories.
- account deletion requests.
- moderation removals.
- legal retention exceptions.

Restore processes must respect deletion and privacy state.

## 11. Privacy operations

Required operational jobs:

- account deletion workflow.
- memory deletion workflow.
- media deletion or access revocation.
- stale guest cleanup.
- old raw message retention cleanup.
- provider usage log retention cleanup.
- privacy export job if supported.

Required admin capabilities:

- view deletion request status.
- retry failed deletion job.
- confirm legal/accounting retention exception.
- audit who accessed user content.
- export minimal evidence for dispute handling.

## 12. Release readiness checklist

Backend skeleton phase:

- request_id middleware.
- structured logger.
- health/readiness endpoints.
- config/secrets pattern.
- provider usage event schema.
- admin audit log schema.
- security limit middleware.

Closed beta:

- staging environment.
- migration apply/rollback verified.
- smoke test script.
- basic dashboards.
- provider daily cap alert.
- report/delete admin path.
- backup enabled.

Public beta:

- production deployment pipeline.
- Sentry or equivalent crash/error monitoring.
- provider fallback alert.
- billing webhook alert.
- queue backlog alert.
- deletion workflow tested.
- privacy/terms/support URLs ready.

Commercial launch:

- restore rehearsal completed.
- incident runbooks rehearsed.
- admin RBAC reviewed.
- cost dashboard reviewed.
- analytics funnel reviewed.
- store/legal checklist from `28` complete.
- provider/cost simulation from `29` complete.
- load/SLO test from `27` complete or explicitly deferred with risk acceptance.

## 13. Non-negotiables

- No production launch without provider cost dashboard.
- No paid launch without credit ledger idempotency and billing webhook audit.
- No generated media launch without moderation and kill switch.
- No admin launch without RBAC and audit logs.
- No public beta without report/delete path.
- No scale claim without load test evidence.
- No privacy claim without deletion workflow evidence.

