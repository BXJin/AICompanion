# LLM runtime concurrency and provider quota design

상용 AI companion 앱에서 가장 위험한 비용 항목은 LLM, TTS, image/video generation이다. 특히 LLM은 "동시에 많이 호출하면 더 빠르다"가 아니라 **비용 폭주와 provider quota 초과를 부르는 병목**이다.

## 핵심 결론

100k connected users를 목표로 하면 LLM 호출은 무제한 병렬 처리하면 안 된다.

필요한 것은:

- plan별 priority queue
- provider별 concurrency semaphore
- token budget
- user/device별 rate limit
- feature별 cost cap
- fallback model
- backpressure UX

## 동시성 해석

100k connected users는 다음과 다르다.

- 100k connected
- 10k active in last minute
- 2k currently typing/speaking
- 500 active LLM turns
- 100 active TTS jobs
- 20 active image jobs

상용 설계는 connected 수보다 **active expensive job 수**를 기준으로 잡아야 한다.

## 예시 capacity model

가정:

- 100k connected.
- 10%가 최근 1분 내 active = 10k.
- active 중 10%가 turn 생성 중 = 1k.
- 평균 LLM 처리 2초.

필요 LLM throughput:

```text
1,000 concurrent turns / 2 sec = 500 LLM requests/sec
```

이 수치는 단일 provider에서 안정적으로 처리하기 어렵고 비용도 크다. 따라서 실제로는 다음이 필요하다.

- Free plan queue.
- Plus/Premium priority.
- short reply model routing.
- cached/common response.
- context compression.
- slow-mode.
- feature credit limit.

## 요청 우선순위

1. safety response
2. paid realtime voice turn
3. premium chat turn
4. plus chat turn
5. free chat turn
6. memory extraction
7. image prompt generation
8. background summary

background 작업은 user-facing 응답과 같은 queue를 쓰면 안 된다.

## Provider router

### Model routing 기준

short_social:

- 인사, 감사, 피곤, 외로움, 짧은 감정 응답.
- low-cost model.
- 짧은 context.

default_chat:

- 일반 대화, 관계 맥락, 가벼운 상담.
- balanced model.

complex_reasoning:

- 커리어, 긴 고민, 안전 관련 판단, 복잡한 게임/스토리 분기.
- stronger model.

media_prompt:

- image/video prompt 생성.
- safety tag와 style control 필요.

memory_extraction:

- low-cost model 또는 deterministic rule + LLM 보조.
- background queue.

## 동시성 제어 구조

```text
API Gateway
-> request validation
-> user plan/rate/credit check
-> Runtime Orchestrator
-> Priority Queue
-> Provider Router
-> Provider Concurrency Pool
-> Response Validator
-> Usage Ledger
```

## Provider concurrency pool

각 provider/model마다 별도 limit을 둔다.

예:

```text
openai:gpt-4.1-nano      max 300 concurrent
openai:gpt-4.1-mini      max 120 concurrent
gemini:flash             max 300 concurrent
anthropic:haiku          max 80 concurrent
image:fast-provider      max 20 concurrent
image:premium-provider   max 5 concurrent
tts:fast                 max 100 concurrent
tts:premium              max 30 concurrent
```

limit은 실제 quota와 latency 측정값을 보고 조정한다.

## Backpressure UX

Queue가 밀릴 때 사용자에게 보여줄 수 있는 graceful degradation:

- "잠깐 생각 중이야" local reaction.
- free plan slow-mode.
- text-only fallback.
- long answer를 short answer로 축소.
- image generation은 예약 처리.
- voice response 대신 text response.
- premium queue 우선 처리.

하면 안 되는 것:

- 요청을 계속 받아놓고 30초 이상 무응답.
- provider timeout 후 아무 설명 없이 실패.
- retry 폭주.

## Token budget

각 turn에는 budget이 있어야 한다.

- free short chat: 낮은 input/output token cap.
- paid chat: 더 긴 memory/context 허용.
- complex reasoning: higher cap but less frequent.
- image prompt: short but controlled.
- memory extraction: compressed input only.

## Context policy

LLM에 무조건 전체 대화 history를 넣으면 비용이 증가한다.

상용 구조:

```text
recent messages 6~12 turns
+ relationship snapshot
+ top-k memory summary
+ current event/game state
+ safety/style instructions
```

long-term memory는 원문이 아니라 summary 중심으로 넣는다.

## Cache policy

캐시 가능한 것:

- greeting variants.
- common fallback.
- short social response templates.
- character static profile.
- game rule explanations.
- reward description.

캐시하면 안 되는 것:

- 사용자 개인 고민 답변.
- safety-sensitive response.
- 결제/환불 안내 중 상태 의존 답변.
- 관계 상태가 강하게 반영되는 답변.

## Cost kill switch

상용 운영에는 다음 kill switch가 필요하다.

- provider별 daily cost cap.
- feature별 daily cost cap.
- free plan image generation 일시 중지.
- premium voice만 유지하고 free voice 중지.
- expensive model route 강제 downgrade.
- media generation queue pause.

## PromptMotionLab에서 재활용 가능한 부분

재활용:

- `RoutingOpenAiRuntimeBehaviorProvider`의 라우팅 개념.
- `RuntimeTurnAsyncJobService`의 async turn job 개념.
- latency logging.
- provider fallback 방향.

재설계:

- in-memory route decision.
- 단일 provider 중심 구조.
- 사용자 plan/credit/context budget 없는 호출.
- queue 없는 동시 처리.

