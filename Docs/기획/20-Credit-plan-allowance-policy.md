# Credit, plan allowance, and billing policy

작성일: 2026-06-04

이 문서는 첫 상용 모바일 release의 Free/Plus/Premium/Credit/Ads 정책을 개발 가능한 수준으로 정의한다.

기준 문서:

- `04-AI-provider-cost-and-scaling.md`
- `15-First-release-scope-decisions.md`
- `17-Mobile-API-contract.md`
- `18-DB-schema-and-ledger-migration-plan.md`

## 결론

첫 release에서 "무제한" 표현은 금지한다.

상용 AI companion의 과금 정책은 다음 균형을 맞춰야 한다.

1. Free 사용자가 핵심 재미를 느낀다.
2. 고비용 voice/TTS/image는 hard cap으로 보호한다.
3. Plus는 광고 제거 이상의 명확한 가치가 있다.
4. Premium은 heavy user와 priority/media 기능을 보호한다.
5. Credit은 image, regeneration, premium voice, premium event에 쓴다.
6. 결제/광고/provider 실패는 ledger로 복구 가능해야 한다.

## 1. Plan structure

### Free

목표:

- 삭제 방지.
- 핵심 루프 체험.
- rewarded ad와 Plus 전환 유도.

제공:

| feature | allowance |
|---|---:|
| text chat | 50 turns/day |
| voice input | 60 seconds/day |
| TTS | 5 short replies/day |
| active memories | 5 total |
| date event | 3 official events, cooldown 적용 |
| basic image reward | 1/week |
| rewarded ad | credit 지급 |

제한:

- premium voice 없음.
- image regeneration은 credit 필요.
- long memory 확장 없음.
- priority queue 없음.

### Plus

목표:

- 일반 유료 사용자.
- 광고 제거 + memory/voice/TTS/image credit 확장.

제공:

| feature | allowance |
|---|---:|
| text chat | 300 turns/day |
| voice input | 600 seconds/day |
| TTS | 50 short replies/day |
| active memories | 50 total |
| monthly image credit | 30 credits |
| ads | removed |
| queue | normal |

### Premium

목표:

- heavy user와 고비용 기능 보호.
- priority/media/voice 중심.

제공:

| feature | allowance |
|---|---:|
| text chat | 1000 turns/day |
| voice input | 1800 seconds/day |
| TTS | 150 replies/day |
| active memories | 200 total |
| monthly image credit | 100 credits |
| premium voice | enabled within cap |
| queue | priority |
| premium reward preview | enabled |

주의:

- Premium도 무제한이 아니다.
- Premium 사용자의 top 1% 비용은 별도 dashboard에서 추적한다.

## 2. Credit unit policy

Credit은 고비용 기능 보호용이다.

Credit spend:

| item | credit |
|---|---:|
| basic image generation | 10 |
| image regeneration | 8 |
| premium image generation | 20 |
| short premium voice reward | 5 |
| premium date event entry | 10 |
| failed provider retry by user request | 0 or original cost policy |

Credit buckets:

1. free_daily
2. ad_reward
3. subscription_allowance
4. purchased
5. promo

Spend priority:

```text
free_daily
-> ad_reward
-> subscription_allowance
-> promo
-> purchased
```

주의:

- purchased credit을 먼저 쓰면 CS/환불 리스크가 커진다.
- purchased credit은 만료 정책을 국가/스토어/법무 검토 전까지 보수적으로 둔다.

## 3. Rewarded ad policy

목표:

- Free 사용자에게 즉시 체감 가능한 보상 제공.
- 광고 수익보다 AI 원가가 커지는 구조 방지.

권장:

| ad action | reward |
|---|---:|
| rewarded ad 1회 | 2 credits |
| daily ad reward cap | 10 credits |
| image 1장 필요 credit | 10 credits |

의미:

- 광고 5회로 basic image 1장 수준.
- 광고 1회로 image 1장을 바로 주지 않는다.

주의:

- 국가별 eCPM 차이가 커서 광고 1회 = 이미지 1장은 위험하다.
- rewarded ad 중복 지급은 idempotency key로 막는다.
- 광고 완료 callback과 credit 지급은 ledger로 연결한다.

## 4. Credit ledger reasons

Ledger reason enum:

지급:

- daily_free_grant
- rewarded_ad_grant
- subscription_monthly_grant
- purchase_grant
- promo_grant
- provider_refund
- moderation_refund
- admin_adjustment_grant

차감:

- image_generation_spend
- image_regeneration_spend
- premium_voice_spend
- premium_event_entry_spend
- admin_adjustment_revoke

정정:

- reversal

필수:

- 모든 ledger row는 source_type/source_id/idempotency_key를 가진다.
- admin adjustment는 admin_audit_log_id와 reason이 필요하다.

## 5. Failure and refund rules

### Provider call before execution

상황:

- quota/credit check 통과 전 실패.
- provider 호출 전 validation 실패.

정책:

- credit 차감하지 않는다.

### Provider timeout after spend

상황:

- credit 차감 후 provider timeout.

정책:

- job status failed.
- retry 가능하면 user에게 retry 제공.
- retry 불가면 provider_refund ledger row 추가.

### Moderation rejected

상황:

- image 생성은 됐지만 output moderation rejected.

정책:

- 사용자 귀책이 아닌 template/provider 문제면 moderation_refund.
- 사용자 prompt가 정책 위반이면 refund 없음 또는 partial refund. 첫 release는 사용자 자유 prompt를 제한해 이 케이스를 줄인다.

### Duplicate webhook

정책:

- platform_transaction_id와 idempotency_key로 중복 지급 방지.
- 같은 transaction은 같은 ledger 결과를 반환한다.

### Chargeback/refund

정책:

- purchased credit 미사용분 회수.
- 이미 사용한 credit은 negative adjustment 또는 account flag.
- 상세 처리는 launch country/payment policy 확정 후 보강.

## 6. Quota service rules

Quota check order:

```text
auth
-> age policy
-> plan status
-> feature allowance
-> credit requirement
-> provider budget/kill switch
-> create request/job
```

Hard cap features:

- voice_second.
- tts_reply.
- image_generation.
- premium_voice.
- media_regeneration.

Soft cap features:

- text_turn for paid users can show slow-mode or upgrade guidance before hard block.

Kill switch:

- free_image_generation_pause.
- tts_text_only_fallback.
- premium_voice_pause.
- image_provider_pause.
- ad_reward_credit_adjustment.
- expensive_model_route_downgrade.

## 7. Pricing placeholders

출시 전 공식 가격/실측 원가로 재검증해야 한다.

Placeholder:

| item | price |
|---|---:|
| Plus monthly | 9,900 KRW or local equivalent |
| Premium monthly | 19,900 KRW or local equivalent |
| Credit pack small | 30 credits |
| Credit pack medium | 100 credits |
| Credit pack large | 300 credits |

주의:

- 실제 가격은 provider 원가, store 수수료, VAT, 국가별 구매력으로 다시 계산한다.
- Lifetime/Founder plan은 AI 원가 누적 리스크가 커서 첫 release에서 권장하지 않는다.

## 8. Product copy rules

금지:

- "unlimited chat"
- "unlimited voice"
- "guaranteed image"
- "adult content available"
- "AI therapist"

권장:

- "More daily voice and TTS"
- "Monthly image credits"
- "Priority response queue"
- "Memory expansion"
- "Generated media is reviewed for safety"

## 9. Acceptance criteria

개발 착수 전 다음이 가능해야 한다.

- quota exceeded error가 shop/ad/upgrade UI로 연결된다.
- credit balance는 ledger replay로 재계산 가능하다.
- rewarded ad 중복 callback이 credit을 중복 지급하지 않는다.
- subscription webhook 중복/지연이 credit을 중복 지급하지 않는다.
- provider 실패/ moderation rejected 시 refund policy가 ledger에 남는다.
- plan 화면에 allowance, renewal/cancel, credit 사용처가 표시된다.
- admin이 credit ledger와 provider cost를 확인할 수 있다.

## 10. Open decisions

PM/engineering decision required:

1. Plus/Premium 실제 가격.
2. Credit pack 가격.
3. purchased credit 만료 정책.
4. refund/chargeback 세부 정책.
5. Free voice cap을 seconds 기준으로 고정할지 count 기준으로 바꿀지.
6. ad reward credit을 국가별 eCPM에 따라 동적으로 조정할지.
