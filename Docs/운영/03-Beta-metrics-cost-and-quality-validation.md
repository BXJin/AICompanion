# Beta metrics, cost, and quality validation

작성일: 2026-06-05

이 문서는 closed/public beta에서 상용 출시 가능성을 판단하기 위한 지표와 측정 방법을 정의한다.

## 1. 베타의 목적

베타는 기능 목록을 보여주는 행사가 아니다.

검증해야 하는 것:

- 사용자가 Airi와 다시 대화하러 오는가.
- memory/relationship/reward가 재방문 이유가 되는가.
- latency가 관계 몰입을 깨지 않는가.
- AI 비용이 유료화로 설명 가능한가.
- safety/CS/report/delete를 운영자가 처리할 수 있는가.
- 캐릭터 이미지/음성/말투가 반복 사용 중 유지되는가.

## 2. 사용자 지표

| Metric | 의미 | 위험 신호 |
|---|---|---|
| D1 retention | 첫날 경험이 다시 올 이유를 줬는지 | 15% 미만 |
| D7 retention | 관계/기억 루프가 살아있는지 | 4% 미만 |
| first chat success | 온보딩/서버/LLM 첫 경험 안정성 | 90% 미만 |
| first -> second chat | Airi 반응이 계속 말하고 싶게 하는지 | 40% 미만 |
| chat days/week | 습관성 | 2일 미만 |
| first date completion | date event 진입/완료 UX | 25% 미만 |
| reward viewed | 보상이 동기부여가 되는지 | unlock 대비 60% 미만 |
| memory interaction | 기억 저장/삭제/회상 체감 | 거의 발생하지 않음 |

PM 판단:

- D1이 낮으면 첫인상/온보딩/첫 응답 문제다.
- D1은 괜찮고 D7이 낮으면 관계 progression이나 반복 콘텐츠 문제다.
- chat은 많은데 date event가 낮으면 event UX 또는 reward 기대치 문제다.
- date event는 높은데 결제 의향이 낮으면 monetization 연결이 약하다.

## 3. 지연률 지표

| Route | 측정 | 목표/판단 |
|---|---|---|
| text chat | send -> first token/response | p95 4~5초 이내 |
| voice input | speech end -> transcript final | p95 1.5초 목표 |
| TTS | response ready -> first audio | p95 2.5초 이내 또는 chunked/pending |
| voice turn | user speech end -> Airi audio start | p95 3초대 목표 |
| image reward | request -> approved/unlocked | async 허용, p95 120초 이내 |
| date event finish | finish -> result/reward | p95 2초 이내 |

운영 판단:

- 평균 latency는 출시 판단 근거로 부족하다. p95/p99를 본다.
- 음성 통화는 "완료 시간"보다 "첫 오디오 시작"이 중요하다.
- 이미지 생성은 즉시 완료보다 pending/retry/refund UX가 중요하다.
- provider 장애 시 모바일에 degraded/pending 상태가 보여야 한다.

## 4. 비용 지표

상용 판단을 위해 반드시 산출:

- cost/user/day by plan.
- cost/chat turn.
- cost/voice minute.
- cost/image reward.
- cost/date event.
- cost/memory extraction.
- failed provider cost.
- refunded credit cost.
- top 1% user cost.
- free user monthly expected cost.
- paid user monthly expected cost.

가격 판단:

```text
monthly gross margin =
monthly revenue after store fee
- AI provider cost
- storage/CDN cost
- payment/refund/CS reserve
```

보류 기준:

- free user가 광고/전환 없이 월 비용을 과도하게 만든다.
- paid user heavy segment가 플랜 가격을 초과한다.
- voice/image 기능이 cap 없이 열려 있다.
- 실패 provider 호출이 비용으로 남는데 사용자 보정 정책이 없다.
- provider별 비용 attribution이 없다.

## 5. 결제/전환 지표

| Metric | 의미 |
|---|---|
| quota exceeded count | 무료 제한이 실제로 도달되는지 |
| quota exceeded -> shop/paywall | 유료 전환 동선이 자연스러운지 |
| shop/paywall -> purchase | 가격/가치 제안이 맞는지 |
| purchase -> repeated use | 결제 후 만족도 |
| refund/chargeback | 기대치 불일치 |
| credit pack repurchase | 소모형 상품의 반복성 |

주의:

- 초반 결제율만 보고 출시 판단하지 않는다.
- refund/CS/비용을 같이 봐야 한다.
- 결제 전환보다 retention이 먼저다. 관계형 앱은 재방문이 없으면 장기 매출이 약하다.

## 6. 안전/CS 지표

필수:

- report count by category.
- report rate per 1k sessions.
- moderation backlog.
- moderation SLA.
- unsafe block rate.
- false positive complaint.
- account deletion request.
- memory deletion request.
- refund request.
- safety incident count.

판단:

- 신고가 적다는 것만으로 안전하다고 보지 않는다.
- report 진입점이 눈에 안 띄면 신고가 적게 나온다.
- romantic companion은 사용자의 정서 의존/위기 발화가 발생할 수 있다.
- self-harm/crisis route는 Airi 캐릭터 말투보다 안전 template이 우선이다.

## 7. 캐릭터 품질 지표

측정:

- Airi tone complaint per 1k chats.
- hallucinated memory complaint.
- relationship mismatch complaint.
- image consistency pass rate.
- TTS voice mismatch/failure.
- generated reward rejection rate.
- prompt/provider version별 품질 차이.

판단:

- 캐릭터 일관성 이슈는 "이미지 생성 실패"가 아니라 product trust 이슈다.
- memory 오류는 기능 오류보다 감정적 불만으로 커질 수 있다.
- prompt 변경은 A/B 테스트처럼 다루고 rollback 기준을 둔다.

## 8. 베타 리포트 템플릿

```text
Beta period:
User count:
Build/version:
Provider/model/prompt versions:

Product:
- DAU:
- D1/D7:
- first chat success:
- first -> second chat:
- date event completion:
- reward viewed:

Quality:
- chat p95:
- TTS first audio p95:
- image reward p95:
- crash-free sessions:
- Airi quality complaints:

Cost:
- cost/user/day:
- cost/chat:
- cost/voice minute:
- cost/image:
- top 1% user cost:
- failed provider cost:

Safety/Ops:
- reports:
- moderation backlog:
- deletion requests:
- refund requests:
- incidents:

Decision:
- Continue beta / Expand / Hold / Rollback

Top fixes before next stage:
-
```

## 9. 표본 크기 기준

초기 권장:

- Internal alpha: 5~10명.
- Closed beta 1: 30~50명.
- Closed beta 2: 100~300명.
- Public beta: 1,000명 이상에서 비용/retention 재측정.

주의:

- 30명 베타로 결제율을 확정하지 않는다.
- 100명 미만에서 safety incident가 0건이어도 안전하다는 뜻은 아니다.
- provider latency는 지역/시간대/요금제별로 다르게 측정한다.
