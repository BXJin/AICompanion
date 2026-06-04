# Scale, load test, SLO, and capacity plan

작성일: 2026-06-04

이 문서는 AI Companion 앱을 100k+ 사용자 확장 가능성을 유지하며 개발하기 위한 load test, SLO, capacity, autoscaling 기준을 정의한다.

기준 문서:

- `05-Commercial-scale-server-architecture.md`
- `08-LLM-runtime-concurrency-and-provider-quota.md`
- `18-DB-schema-and-ledger-migration-plan.md`
- `21-Admin-minimum-screen-spec.md`
- `24-Commercial-development-readiness-audit.md`
- `26-Backend-skeleton-service-boundary-plan.md`

## 결론

첫 release에서 실제 100k 동시 접속을 바로 처리하겠다고 설계하면 비용과 복잡도가 과하다.

하지만 첫 구조는 100k로 가는 길을 막으면 안 된다.

따라서 개발 초기부터 다음을 지킨다.

1. API server는 stateless.
2. user/session/job state는 DB/Redis/queue에 저장.
3. provider 호출은 concurrency pool과 quota를 통과.
4. TTS/image/memory/moderation은 queue 기반.
5. cost/user/day와 provider usage는 DB/metric으로 집계.
6. SLO는 endpoint/feature별로 분리한다.

## 1. Traffic model

100k users는 같은 의미가 아니다.

구분:

| 용어 | 의미 |
|---|---|
| registered users | 가입자 수 |
| MAU | 월간 활성 사용자 |
| DAU | 일간 활성 사용자 |
| concurrent app users | 동시에 앱을 켠 사용자 |
| active chat users | 동시에 chat turn을 보내는 사용자 |
| active provider jobs | 동시에 LLM/TTS/STT/image provider를 호출하는 작업 |

첫 scale target:

| stage | registered | DAU | concurrent app | active chat turns/min |
|---|---:|---:|---:|---:|
| closed beta | 1k | 200 | 30 | 10 |
| public beta | 20k | 3k | 500 | 150 |
| early commercial | 100k | 15k | 2k | 600 |
| scale target | 500k+ | 100k | 10k+ | 3000+ |

주의:

- 100k registered와 100k concurrent는 전혀 다르다.
- 100k concurrent를 목표로 하는 인프라는 제품/수익 검증 후 별도 단계다.

## 2. Feature load classes

### Class A: cheap synchronous

- app bootstrap.
- character state.
- reward list.
- memory list.
- credit balance.

Target:

- p50 < 200ms.
- p90 < 500ms.
- p99 < 1000ms.

### Class B: chat turn

- `POST /chat/turn`.

Target:

- first visible local reaction: 0.2-0.5s.
- text response first render: 1-2s.
- full response: 2-4s.
- timeout fallback: 8-12s.

### Class C: voice/STT

- `POST /voice/stt`.

Target:

- transcript p50 < 1s for short clips.
- p90 < 2.5s.
- hard duration cap by plan.

### Class D: async TTS/image/memory/moderation

- TTS job.
- image generation.
- memory extraction.
- moderation.

Target:

| job | expected | timeout |
|---|---:|---:|
| TTS short | 2-5s | 20s |
| memory extraction | 10-60s | 5m |
| image generation | 30-180s | 10m |
| moderation | 5-60s | 5m |

## 3. SLO draft

First public beta SLO:

| feature | availability | latency |
|---|---:|---|
| app bootstrap | 99.5% | p90 < 500ms |
| chat turn accepted | 99.0% | p90 < 2s to first render |
| chat full response | 98.5% | p90 < 5s |
| TTS job completion | 97.0% | p90 < 10s |
| image job completion | 95.0% | p90 < 5m |
| credit ledger write | 99.9% | p90 < 300ms |
| report submission | 99.5% | p90 < 500ms |

Commercial SLO는 beta 측정 후 조정한다.

주의:

- provider 장애는 전체 앱 장애로 전파하지 않는다.
- degraded mode를 SLO에 포함한다.

## 4. Load test scenarios

### Scenario 1: app open burst

목표:

- 아침/저녁 push 후 bootstrap burst를 견딘다.

Pattern:

- 10k users open app over 5 minutes.
- 70% bootstrap only.
- 20% chat within 1 minute.
- 10% date/reward/profile navigation.

Metrics:

- bootstrap p50/p90/p99.
- DB connection pool.
- Redis hit rate.
- error rate.

### Scenario 2: chat burst

Pattern:

- 1000 active chat users.
- each sends 1 turn every 60-120s.
- mock provider first, real provider shadow test later.

Metrics:

- route latency.
- provider concurrency pool saturation.
- queue wait.
- fallback rate.
- cost/min.

### Scenario 3: TTS spike

Pattern:

- 20% of chat turns request TTS.
- Free cap enforced.
- paid users priority.

Metrics:

- TTS queue age.
- provider timeout.
- first audio latency.
- text-only fallback rate.

### Scenario 4: image reward spike

Pattern:

- date event campaign.
- 5k users complete event in 1 hour.
- 10% request image generation.

Metrics:

- image queue backlog.
- moderation queue backlog.
- credit spend/refund.
- provider failure.

### Scenario 5: billing/ad idempotency

Pattern:

- duplicate rewarded ad callbacks.
- duplicate subscription webhooks.
- delayed webhook arrival.

Metrics:

- duplicate credit grant count should be 0.
- ledger replay matches snapshot.

## 5. Autoscaling policy

API server scale signals:

- CPU.
- p90 latency.
- request queue length.
- DB connection saturation.

Worker scale signals:

- queue backlog count.
- oldest job age.
- running job count.
- provider concurrency pool usage.

Do not autoscale blindly on:

- provider timeout spike.
- image queue spike caused by abuse.

Instead:

- apply kill switch.
- tighten quota.
- downgrade route.
- pause free image generation.

## 6. DB capacity plan

Tables that grow fastest:

- messages.
- provider_usage_events.
- async_jobs.
- credit_ledger.
- media_assets.
- admin_audit_logs.

Closed beta:

- single PostgreSQL instance.
- no partitioning unless needed.
- indexes from `18`.

Public beta:

- monitor table size and index bloat.
- consider monthly partitioning for provider_usage_events.
- messages partitioning decision before heavy growth.

Commercial:

- read replica for admin/analytics if needed.
- data warehouse export for long-term analytics.
- ledger remains primary source for credit.

## 7. Provider quota plan

Provider quota is usually the real bottleneck.

Per provider track:

- RPM.
- TPM.
- concurrent requests.
- audio seconds/min.
- image jobs/min.
- spend/day.
- failure rate.

Required controls:

- route concurrency pool.
- plan priority queue.
- provider daily spend cap.
- fallback provider.
- degraded mode.

## 8. Cost load simulation

Before public beta, run simulations:

| simulation | target |
|---|---|
| free light user | cost/user/day |
| plus normal user | margin after store fee |
| premium heavy user | top 1% cost |
| image-heavy user | credit burn and provider spend |
| voice-heavy user | TTS/STT cost |

Output:

- cost/user/day by plan.
- gross margin by plan.
- provider spend by route.
- kill switch threshold.

## 9. Observability

Required metrics:

- request_count by endpoint/status.
- p50/p90/p99 latency by endpoint.
- provider_usage cost by route/provider/model.
- queue backlog by job_type.
- oldest job age.
- credit ledger writes.
- quota exceeded count.
- fallback rate.
- safety block rate.
- report count.
- moderation SLA.

Required logs:

- request_id.
- user_id where safe.
- route.
- provider/model.
- idempotency_key hash.
- error_code.

## 10. Acceptance criteria

Before public beta:

- load test can run with mock provider.
- bootstrap p90 target is measured.
- chat p90 target is measured with mock provider.
- provider usage dashboard shows cost by route.
- queue monitor shows backlog and oldest job age.
- duplicate webhook/ad callbacks do not duplicate credit.
- kill switch can pause free image generation.
- degraded mode can return text-only fallback.

Before commercial launch:

- real provider latency/cost measured.
- plan gross margin simulation complete.
- public beta traffic replay or synthetic load test complete.
- DB growth estimate for 6 months complete.
- provider quota agreement or fallback plan exists.
