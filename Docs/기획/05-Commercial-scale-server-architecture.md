# Commercial Scale Server Architecture

## 목적

AI companion + 데이트형 미니게임 + 음성/이미지/영상 보상 서비스를 상용 수준으로 운영한다고 가정하고, 10만 동시 사용자까지 확장 가능한 서버 아키텍처를 설계한다.

## 전제

10만 동시 사용자라는 말은 10만 명이 동시에 LLM을 호출한다는 뜻이 아니다. 실제 서비스에서는 다음을 분리해서 봐야 한다.

```text
Concurrent connected users:
  앱에 접속 중인 사용자 수

Active chat turns:
  실제로 메시지를 보내고 AI 응답을 기다리는 사용자 수

Realtime voice sessions:
  WebSocket/STT/TTS가 열려 있는 음성 세션 수

Media generation jobs:
  이미지/영상/긴 음성 생성 queue에 들어간 작업 수
```

10만 connected users를 처리하려면 연결 유지 계층과 AI 호출 계층을 분리해야 한다. 10만 명이 동시에 LLM을 호출하게 만들면 provider quota와 비용 때문에 바로 터진다.

## 핵심 원칙

1. 일반 API 서버와 WebSocket/voice gateway를 분리한다.
2. LLM/STT/TTS/image/video 호출은 provider router와 quota manager를 거친다.
3. 고비용 작업은 request-response로 기다리지 않고 queue/job 구조로 처리한다.
4. 사용자 plan, credit, quota는 서버 중앙에서 강제한다.
5. 관계 상태, 메모리, 결제, 미디어, 게임 상태를 같은 테이블에 섞지 않는다.
6. 대화 전체를 LLM에 넣지 않고 summary + memory top-k + current state만 넣는다.
7. 무료 유저와 유료 유저의 priority를 분리한다.
8. provider 장애를 전제로 fallback과 degraded mode를 둔다.

## 전체 아키텍처

```text
Client App
  |
  v
CDN / WAF / API Gateway
  |
  +--> Auth Service
  +--> Plan / Quota Service
  +--> Chat API
  +--> Game / Date API
  +--> Reward / Credit API
  +--> Gallery / Media API
  |
  +--> Realtime Gateway
        |
        +--> WebSocket Session Manager
        +--> Streaming STT Gateway
        +--> Voice Turn Controller

Core Services
  |
  +--> Chat Orchestrator
  +--> Character Dialogue Service
  +--> Relationship State Service
  +--> Memory Service
  +--> Game Rule Engine
  +--> Reward Unlock Service
  +--> Billing / Credit Ledger
  +--> Safety Service

Async Layer
  |
  +--> Message Queue / Event Stream
  +--> TTS Worker
  +--> Image Worker
  +--> Video Worker
  +--> Memory Extraction Worker
  +--> Notification Worker
  +--> Analytics Worker

Provider Layer
  |
  +--> LLM Provider Router
  +--> STT Provider Router
  +--> TTS Provider Router
  +--> Image Provider Router
  +--> Video Provider Router

Data Layer
  |
  +--> PostgreSQL / MySQL cluster
  +--> Redis cluster
  +--> Vector DB / pgvector
  +--> Object Storage
  +--> Analytics Warehouse
  +--> Log / Trace / Metrics
```

## 서비스 분리

### API Gateway

역할:

- 인증 토큰 확인
- request size 제한
- IP/user rate limit
- routing
- WAF 연동
- abuse traffic 차단

주의:

- business logic을 넣지 않는다.
- provider API key를 절대 client에 노출하지 않는다.
- 무료/유료 quota는 gateway에서 1차 체크하고, core service에서 다시 확인한다.

### Auth Service

역할:

- social login
- anonymous trial user
- account linking
- token refresh
- device/user 식별
- 탈퇴/데이터 삭제 요청

초기에는 Firebase/Auth0/Supabase/Auth.js 같은 managed auth를 검토할 수 있다. 직접 auth를 만들면 보안/운영 부담이 커진다.

### Plan / Quota Service

역할:

- Free/Plus/Premium plan 확인
- daily text turn limit
- voice seconds limit
- image/video quota
- credit balance
- priority tier
- abuse flag

이 서비스는 모든 고비용 기능 앞에서 호출된다.

```text
User request
-> Plan / Quota check
-> allow / reject / degrade / queue
```

### Chat Orchestrator

역할:

- 사용자 메시지 수신
- context 구성
- LLM route 선택
- memory lookup
- relationship state lookup
- safety check
- LLM response 요청
- response를 text / emotion / action / memory candidate로 분리

Chat Orchestrator는 단순히 LLM을 호출하는 함수가 아니다. 사용자 상태와 비용, latency, plan을 같이 보고 routing해야 한다.

### Character Dialogue Service

역할:

- character profile
- tone/persona rules
- forbidden style
- few-shot examples
- output schema
- emotion/intent/action generation

PromptMotionLab의 `RuntimeCharacterService`와 `CharacterProfileStore`가 이 영역의 prototype이다.

### Relationship State Service

역할:

- affinity
- trust
- mood
- energy
- familiarity
- jealousy-lite
- last interaction time
- recent event summary

중요:

LLM이 숫자를 직접 결정하면 안 된다. LLM은 이벤트 해석을 돕고, 최종 state update는 rule engine이 한다.

```text
event: movie_date_completed
rule: affinity +3, mood = warm
LLM: reaction text only
```

### Memory Service

역할:

- short-term conversation
- long-term memory
- user preference
- previous date/game result
- important promise
- relationship milestone

구성:

```text
Recent messages:
  Redis / DB

Long-term memory:
  PostgreSQL + vector index

Memory extraction:
  async worker
```

실시간 응답 중에는 memory extraction을 기다리지 않는다. 응답 후 background worker가 중요한 내용을 추출한다.

### Game Rule Engine

역할:

- mini-game state
- valid move check
- win/lose/draw
- score
- reward condition
- relationship event 생성

중요:

LLM에게 승패 판정을 맡기면 안 된다. 보상과 관계도 변경은 deterministic rule engine이 해야 한다.

```text
User action
-> GameRuleEngine validates
-> result event
-> RelationshipStateService updates
-> CharacterDialogueService generates reaction
```

### Reward Unlock Service

역할:

- image reward
- voice reward
- story card
- diary
- event ticket
- relationship level unlock

고비용 reward는 즉시 생성하지 않고 job으로 넣는다.

```text
Reward unlocked
-> Media job queued
-> user sees pending state
-> worker generates media
-> gallery updated
```

### Billing / Credit Ledger

역할:

- subscription status
- paid credit
- free credit
- monthly allowance
- event ticket
- refund/cancel status
- transaction history

원칙:

- paid credit과 free credit을 분리한다.
- credit 차감은 ledger 방식으로 기록한다.
- client에서 credit balance를 신뢰하지 않는다.
- 모든 고비용 작업은 사전 authorization 후 실행한다.

### Safety Service

역할:

- adult/minor policy
- sexual content policy
- self-harm/mental health escalation
- harassment/abuse
- user report
- generated media safety
- prompt injection 방어

AI companion 앱은 정책 리스크가 높다. 안전 정책은 후순위가 아니라 상용 기본 요건이다.

## Realtime Architecture

### Realtime Gateway

역할:

- WebSocket 연결 유지
- heartbeat
- reconnect
- session auth
- per-user connection limit
- voice session limit

일반 API 서버와 분리해야 하는 이유:

- WebSocket은 connection-heavy
- Chat API는 request/CPU/provider-heavy
- 둘을 같은 서버에 두면 스케일링 기준이 꼬인다.

### Voice Turn Controller

역할:

- streaming STT
- partial transcript
- final transcript
- turn start/end
- barge-in
- silence timeout
- TTS playback event

초기에는 PTT로 시작해도 되지만, 상용 companion 앱은 VAD/turn-taking이 필요하다.

### Voice Flow

```text
Client microphone
-> Realtime Gateway
-> STT Provider
-> partial transcript
-> final transcript
-> Chat Orchestrator
-> LLM
-> first sentence
-> TTS job
-> audio stream / segment
-> client playback
```

목표는 "전체 답변 완료 후 재생"이 아니라 "첫 문장부터 재생"이다.

## Async / Queue Architecture

### Queue가 필요한 작업

| 작업 | 이유 |
|---|---|
| TTS | provider 지연/재시도 필요 |
| image generation | 고비용/느림/실패 가능 |
| video generation | 매우 느림/고비용 |
| memory extraction | 실시간 응답을 막으면 안 됨 |
| diary/story generation | 긴 생성 |
| notification | background 처리 |
| analytics | 실시간 응답과 분리 |

### Queue 구조

```text
API request
-> validate quota
-> create job
-> enqueue
-> return job_id
-> worker processes
-> result stored
-> client notified by WebSocket/polling/push
```

### Priority Queue

우선순위가 필요하다.

```text
Premium live voice > Plus chat > Free chat > Free image reward > batch analytics
```

무료 유저의 image/video job이 premium voice response를 막으면 안 된다.

## Provider Router

### 역할

- 모델 선택
- provider 선택
- timeout
- retry
- fallback
- quota 관리
- cost 기록

### LLM Routing

```text
short_social:
  gpt-4.1-nano or low-cost Gemini

default_chat:
  gpt-4.1-mini or Gemini Flash

story:
  mini / Claude / Gemini higher quality

safety:
  rule + safety model

fallback:
  cheaper provider or canned response
```

### Provider Quota Manager

10만 동시 사용자에서는 provider quota가 병목이 된다.

필수 기능:

- provider별 QPS 제한
- model별 TPM/RPM 제한
- user별 daily budget
- plan별 priority
- provider 장애 시 degraded response
- monthly cost cap

## Data Architecture

### 주요 DB

| 영역 | 저장소 | 이유 |
|---|---|---|
| user/account | PostgreSQL/MySQL | 정합성 중요 |
| subscription/credit | PostgreSQL/MySQL | ledger, transaction 필요 |
| relationship state | PostgreSQL/MySQL | 사용자별 상태 |
| conversations | PostgreSQL + partitioning | 대량 write |
| recent session | Redis | 빠른 접근 |
| memory vector | pgvector / vector DB | semantic retrieval |
| game sessions | Redis + DB | 진행 중은 Redis, 완료 후 DB |
| media assets | Object Storage | 이미지/영상/음성 |
| analytics | BigQuery/Snowflake/ClickHouse류 | 집계/분석 |
| logs/traces | observability stack | 장애 추적 |

### 테이블 예시

```text
users
characters
user_character_state
conversations
messages
memories
game_sessions
game_events
reward_definitions
user_rewards
media_assets
credit_ledger
subscriptions
provider_usage
safety_events
```

### 데이터 분리 원칙

- 결제/credit ledger는 절대 대화 테이블과 섞지 않는다.
- 메시지는 partitioning을 전제로 둔다.
- media는 DB에 바이너리로 저장하지 않는다.
- memory는 원문과 embedding을 분리 관리한다.
- 삭제 요청을 고려해 user_id 기반 cascade/soft-delete 정책을 정한다.

## Scaling Strategy

### 1단계: MVP / Closed Beta

```text
1 API server
1 PostgreSQL
1 Redis
Object Storage
OpenAI/ElevenLabs provider
Basic monitoring
```

목표:

- 100~1,000 DAU
- 기능 검증
- cost_per_user 측정
- retention 확인

### 2단계: Public Beta

```text
API server autoscale
Realtime gateway 분리
Queue/worker 도입
PostgreSQL managed
Redis managed
Object storage + CDN
provider usage logging
payment/credit ledger
```

목표:

- 1,000~10,000 DAU
- 무료/유료 플랜 검증
- provider cost cap
- failure recovery

### 3단계: Scale

```text
Multi-region edge
API gateway
Realtime gateway cluster
Queue cluster
Worker autoscaling
DB read replica / partitioning
Redis cluster
Vector DB scale
Analytics warehouse
Observability/SRE
```

목표:

- 10,000~100,000 DAU
- 수십만 connected sessions
- provider routing/fallback
- cost-based throttling

### 4단계: 100K Concurrent

100K concurrent는 다음 전제가 필요하다.

```text
Realtime connection layer:
  horizontally scalable WebSocket gateway

Active turn throttling:
  plan별 동시 처리 제한

Queue:
  high-cost jobs isolated

Provider router:
  provider quota aware

DB:
  partitioned conversations
  separate billing ledger
  Redis cluster

Observability:
  per-service p50/p90/p99 latency
  cost per route
  provider errors
  queue lag
```

## Capacity Thinking

예시 가정:

```text
100,000 connected users
10% active in last minute = 10,000 active users
2% sending turn at the same moment = 2,000 active turns
voice session 1% = 1,000 concurrent voice sessions
image jobs 0.1% = 100 concurrent media jobs
```

이 숫자에서 중요한 것은 "100,000 connected"가 아니라 active turn과 voice/media job이다.

### 병목 후보

| 병목 | 대응 |
|---|---|
| Provider QPS/TPM | routing, queue, priority, fallback |
| WebSocket connection | realtime gateway 분리 |
| DB write | partitioning, batch write, async analytics |
| Redis memory | TTL, cluster, eviction policy |
| Image/video job | separate queue, paid priority |
| TTS latency | segment TTS, provider fallback |
| 비용 폭주 | user quota, monthly cap, anomaly detection |

## Reliability / Failure Mode

### Degraded Mode

provider 장애 시 전체 앱이 멈추면 안 된다.

| 장애 | fallback |
|---|---|
| LLM 장애 | canned response, cheaper provider, retry queue |
| STT 장애 | text input 안내, 다른 STT provider |
| TTS 장애 | text-only response, delayed voice |
| Image 장애 | reward pending, retry later |
| Video 장애 | credit refund/retry |
| Memory 장애 | recent context only |
| Payment 장애 | 기존 entitlement 유지, 신규 결제 제한 |

### Timeout Rule

```text
Chat response:
  p90 2~4s 목표
  timeout 시 짧은 fallback

TTS first audio:
  p90 1~2s 목표
  실패 시 text first

Image:
  async job
  user에게 pending 상태 표시

Video:
  async job
  notification when ready
```

## Cost Control Architecture

### Cost Event

모든 provider 호출은 cost event를 남겨야 한다.

```json
{
  "userId": "u_123",
  "plan": "plus",
  "provider": "openai",
  "model": "gpt-4.1-mini",
  "route": "default_chat",
  "inputTokens": 1200,
  "outputTokens": 160,
  "estimatedCostUsd": 0.000736,
  "requestId": "req_abc"
}
```

### 필요한 지표

- user별 daily cost
- plan별 average cost
- provider별 monthly spend
- route별 token 사용량
- image/video job cost
- free user total cost
- paid user margin
- heavy user top 1% cost

## Security

필수:

- API key server-side only
- user auth
- device/session binding
- request signing optional
- rate limit
- credit ledger integrity
- payment webhook verification
- media access signed URL
- data deletion/export
- prompt injection 방어
- moderation/safety logging

## 현재 PromptMotionLab에서 가져올 것

| 현재 자산 | 상용 구조 적용 |
|---|---|
| `RuntimeCharacterService` | Character Dialogue Service prototype |
| `CharacterProfileStore` | Character profile/versioning |
| `RoutingOpenAiRuntimeBehaviorProvider` | LLM Provider Router prototype |
| `RuntimeTurnAsyncJobService` | Async turn/job design |
| `TtsAsyncJobService` | TTS job pattern |
| `Streaming STT providers` | Realtime voice gateway provider layer |
| `runtime_character_matrix_test.py` | Character response QA |
| `latency_metrics_logger.py` | Cost/latency observability prototype |
| `rate_limiter.py` | 초기 rate limit prototype |

가져오지 말아야 할 것:

- UE5 face morph/lip-sync runtime은 이 서비스의 핵심이 아니다.
- 앱이 이미지/영상 기반이면 게임엔진 구조를 가져오지 않는다.
- in-memory rate limit/session은 상용 구조에 그대로 쓰면 안 된다.

## 기술 선택 제안

### 초기

```text
Backend:
  FastAPI or Node/NestJS

DB:
  PostgreSQL

Cache:
  Redis

Queue:
  Redis Queue / Celery / BullMQ / Cloud Queue

Object Storage:
  S3 / Azure Blob / GCS

Vector:
  pgvector first, dedicated vector DB later

Monitoring:
  OpenTelemetry + Grafana/Datadog/Sentry
```

### Scale

```text
API Gateway:
  Cloudflare / AWS API Gateway / Azure Front Door / NGINX/Kong

Realtime:
  dedicated WebSocket gateway

Queue:
  Kafka / PubSub / SQS / RabbitMQ depending scale

DB:
  partitioned PostgreSQL + read replicas

Redis:
  cluster

Analytics:
  BigQuery / ClickHouse / Snowflake
```

## Final Architecture Judgment

10만 동시 사용자를 목표로 할 때 가장 위험한 착각은 "서버를 크게 하면 된다"는 생각이다.

실제로는 다음을 분리해야 한다.

```text
connection scale
turn processing scale
provider quota scale
media job scale
database write scale
cost control scale
```

그리고 AI companion 앱의 핵심 병목은 CPU보다 provider quota와 비용이다. 따라서 아키텍처는 처음부터 "AI 호출을 줄이고, 라우팅하고, queue에 넣고, 유료 우선순위를 부여하고, 비용을 측정하는 구조"여야 한다.

MVP는 작게 시작하되, 다음 4개는 처음부터 production-shaped로 둬야 한다.

```text
1. user/plan/quota
2. async job queue
3. provider router
4. cost/latency logging
```

이 4개가 없으면 사용자가 늘 때 기능이 아니라 비용과 장애가 먼저 터진다.
