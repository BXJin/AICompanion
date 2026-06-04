# Provider evaluation and cost simulation plan

작성일: 2026-06-04

이 문서는 AI Companion 첫 상용 release에서 LLM, STT, TTS, image provider를 선택하기 위한 실측 기준과 cost simulation 방식을 정의한다.

현재 문서 세트는 provider adapter, usage logging, quota, ledger 구조를 정의했다. 하지만 실제 provider 선택은 문서 추정이 아니라 한국어 품질, latency, failure rate, unit cost를 측정한 뒤 결정해야 한다.

## 1. Decision principles

Provider 선택 기준:

1. Korean conversation quality.
2. Emotional companion tone stability.
3. p50/p90 latency.
4. failure and fallback behavior.
5. cost per successful feature route.
6. quota and concurrency headroom.
7. safety and policy compatibility.
8. commercial terms and data handling.
9. SDK/API operational maturity.
10. observability and usage attribution.

금지:

- 단일 provider 가격표만 보고 결정.
- 품질 테스트 없이 가장 싼 provider 선택.
- image/TTS처럼 원가 변동이 큰 기능을 unlimited처럼 판매.
- provider별 데이터 처리 조건을 확인하지 않고 상용 출시.

## 2. Provider routes

LLM routes:

| Route | Purpose | Quality requirement | Cost posture |
|---|---|---|---|
| short_social | 짧은 일상 답변 | medium | lowest stable |
| default_chat | 일반 Airi 대화 | high | balanced |
| date_event_reaction | date event 반응 | high | balanced |
| memory_extraction | memory 후보 추출 | medium-high | low cost |
| media_prompt | reward image prompt 생성 | high | balanced |
| safety | safety classification/rewriting | high precision | low latency |
| fallback | degraded response | medium | cheap/reliable |

Non-LLM routes:

| Route | Purpose | Key metric |
|---|---|---|
| STT | voice input transcription | Korean WER, latency |
| TTS | Airi voice playback | naturalness, latency, cost/min |
| Image | reward image generation | identity consistency, moderation pass rate, cost/image |

## 3. Benchmark dataset

최소 benchmark set:

| Dataset | Count | Notes |
|---|---:|---|
| Korean daily chat | 100 | casual, affectionate, short/long mixed |
| Korean emotional support | 50 | non-medical, non-crisis |
| Boundary/safety prompts | 80 | sexual, minor-like, self-harm, harassment, illegal |
| Memory extraction cases | 80 | preference, schedule, relationship facts, sensitive info |
| Date event reactions | 60 | 3 official events x result bands |
| Voice STT samples | 50 | noisy/quiet, short/long |
| TTS lines | 80 | greeting, teasing, apology, diary, reward |
| Image prompts | 40 | Airi safe reward images |

데이터셋 원칙:

- 실제 사용자 개인정보를 사용하지 않는다.
- 테스트 프롬프트와 기대 결과를 versioned fixture로 관리한다.
- safety dataset은 통과/차단 기대값을 명시한다.
- Airi tone은 `22-Airi-character-profile-v1.md`를 기준으로 평가한다.

## 4. LLM evaluation metrics

정량 지표:

- success rate.
- p50 latency.
- p90 latency.
- p99 latency for public beta only.
- average input tokens.
- average output tokens.
- cost per route.
- fallback rate.
- safety false allow rate.
- safety false block rate.
- memory extraction precision/recall.

정성 지표:

- Airi tone consistency.
- Korean naturalness.
- over-apology rate.
- hallucinated memory rate.
- boundary handling.
- emotional overdependence risk.
- date event immersion.

Scoring:

```text
score = quality * 0.35
      + latency * 0.20
      + reliability * 0.15
      + cost * 0.15
      + safety * 0.10
      + operations * 0.05
```

첫 release에서는 quality와 safety를 cost보다 높게 둔다. 다만 image/TTS는 cost variance가 크므로 hard cap 없이는 출시하지 않는다.

## 5. STT evaluation metrics

필수 지표:

- Korean word error rate.
- short utterance accuracy.
- noisy environment accuracy.
- p50/p90 latency.
- timeout rate.
- cost per minute.
- streaming support.
- mobile upload bandwidth impact.

합격 기준:

- 조용한 환경의 짧은 한국어 발화에서 사용자가 다시 말해야 하는 비율이 낮아야 한다.
- 실패 시 text input fallback이 즉시 가능해야 한다.
- voice input은 Free plan에서 hard cap이 있어야 한다.

## 6. TTS evaluation metrics

필수 지표:

- voice naturalness.
- Airi tone fit.
- p50/p90 generation latency.
- cache hit potential.
- cost per 1,000 characters or minute.
- failure rate.
- commercial voice usage terms.

운영 원칙:

- 자주 쓰는 greeting, apology, reward line은 cache할 수 있어야 한다.
- TTS 실패는 chat 실패로 처리하지 않는다.
- provider 장애 시 text-only fallback이 가능해야 한다.

## 7. Image evaluation metrics

필수 지표:

- cost per accepted image.
- generation latency.
- moderation rejection rate.
- Airi identity consistency.
- prompt adherence.
- unsafe output rate.
- storage/CDN cost impact.

원가 계산은 generated image가 아니라 accepted image 기준으로 한다.

```text
accepted_image_cost =
  (generation_cost_total + moderation_cost_total + retry_cost_total)
  / accepted_image_count
```

이미지 기능은 출시 초기에 가장 위험한 원가 항목이다. Plus/Premium 포함량은 실측 전 placeholder로만 두고, 무제한 표현은 금지한다.

## 8. Cost simulation formula

기본 단위:

```text
llm_cost_per_turn =
  input_tokens * input_token_price
  + output_tokens * output_token_price

tts_cost_per_play =
  characters_or_seconds * tts_unit_price

stt_cost_per_voice =
  audio_seconds * stt_unit_price

image_cost_per_reward =
  generation_cost + moderation_cost + retry_expected_cost

cost_per_user_day =
  llm_turns * llm_cost_per_turn
  + voice_uses * stt_cost_per_voice
  + tts_plays * tts_cost_per_play
  + image_rewards * image_cost_per_reward
  + storage_cdn_cost
  + observability_cost

gross_margin =
  revenue_after_store_fee
  - provider_cost
  - infra_cost
  - support_and_moderation_cost
```

Plan별 simulation:

| Segment | Required scenario |
|---|---|
| Free light | 5 chat/day, no image |
| Free engaged | daily cap 근접, limited voice/TTS |
| Plus average | daily chat, weekly image, moderate TTS |
| Premium average | higher TTS/image usage |
| Heavy top 1% | cap까지 사용 |
| Abuser | quota/rate-limit hit |

## 9. Required experiments

### Experiment A: Chat route benchmark

목표:

- short_social/default_chat/date_event_reaction provider 후보 비교.

측정:

- quality score.
- p50/p90 latency.
- cost per successful route.
- fallback rate.
- safety failure.

결과물:

- route별 default provider.
- route별 fallback provider.
- route별 max token budget.
- route별 timeout.

### Experiment B: Memory extraction

목표:

- memory candidate 추출이 과잉 저장/누락 없이 동작하는지 확인.

측정:

- precision.
- recall.
- sensitive info false save.
- cost per extraction.
- latency.

결과물:

- extraction provider.
- confidence threshold.
- sensitive category blocklist.
- manual QA cases.

### Experiment C: TTS provider

목표:

- Airi voice 품질과 원가 균형 확인.

측정:

- tone fit.
- p50/p90 latency.
- failure rate.
- cache effectiveness.
- cost per 1,000 plays.

결과물:

- default TTS provider.
- cached phrase policy.
- fallback text-only policy.

### Experiment D: Image provider

목표:

- safe reward image를 원가 통제 가능한 범위에서 생성할 수 있는지 확인.

측정:

- accepted image cost.
- rejection rate.
- identity consistency.
- unsafe output rate.
- latency.

결과물:

- first release image allowance.
- credit price for extra image.
- moderation threshold.
- kill switch threshold.

### Experiment E: Plan margin simulation

목표:

- Free/Plus/Premium/Credit 구조가 store fee와 provider cost 이후에도 손실을 통제하는지 확인.

측정:

- cost/user/day.
- gross margin per plan.
- top 1% user cost.
- provider daily cap trigger rate.
- free user monthly burn.

결과물:

- final allowance table.
- final credit price table.
- heavy user cap.
- plan upgrade trigger.

## 10. Provider decision table

최종 선택 시 작성할 표:

| Feature | Default provider | Fallback | Timeout | Cost cap | Reason |
|---|---|---|---:|---:|---|
| short_social | TBD | TBD | TBD | TBD | benchmark 후 확정 |
| default_chat | TBD | TBD | TBD | TBD | benchmark 후 확정 |
| date_event_reaction | TBD | TBD | TBD | TBD | benchmark 후 확정 |
| memory_extraction | TBD | TBD | TBD | TBD | benchmark 후 확정 |
| safety | TBD | TBD | TBD | TBD | benchmark 후 확정 |
| STT | TBD | text input | TBD | TBD | benchmark 후 확정 |
| TTS | TBD | text-only | TBD | TBD | benchmark 후 확정 |
| Image | TBD | queue pause | TBD | TBD | benchmark 후 확정 |

## 11. Data handling checklist

Provider 계약/정책에서 확인해야 할 항목:

- submitted prompts retained or not.
- training use opt-out availability.
- data residency.
- enterprise/commercial terms.
- logging retention.
- deletion support.
- rate limit and quota.
- billing granularity.
- content policy compatibility.
- incident support channel.

출시 전까지 확인되지 않으면 해당 provider는 fallback 또는 beta-only로 제한한다.

## 12. Acceptance criteria

Backend skeleton 착수 전:

- provider adapter interface exists in design.
- usage logging schema exists.
- route names and cost attribution keys exist.

Public beta 전:

- at least 2 LLM candidates measured.
- at least 2 TTS candidates measured or TTS scope reduced.
- image cost per accepted reward measured.
- cost/user/day simulation complete.
- provider fallback path tested.
- provider daily cap and kill switch configured.

Commercial launch 전:

- final provider route table approved.
- Plus/Premium/Credit allowance updated with measured cost.
- store/legal copy uses actual capability and limits.
- provider commercial/data terms reviewed.
- p50/p90 latency dashboard live.
- provider failure runbook rehearsed.
