# 병목 지점, PromptMotionLab 재사용 판단, 모바일 스택 결정

작성일: 2026-06-04

## 결론

첫 릴리즈의 병목은 서버 CPU보다 다음 영역에서 먼저 생긴다.

1. 캐릭터 이미지 일관성
2. LLM 대화 지연률
3. TTS/voice 지연률과 비용
4. provider quota와 provider 장애
5. memory/RAG context 비용
6. image generation queue
7. credit/reward/relationship 정합성
8. admin/CS 처리량

`C:\Portfolio\PromptMotionLab`는 재사용 가치가 있다. 다만 그대로 가져오면 안 된다.

재사용 우선순위는 다음과 같다.

```text
직접 재사용 또는 얇게 수정:
  provider interface
  OpenAI runtime routing 개념
  Airi character profile/fewshot 방향
  timeout/fallback 패턴
  segmented TTS 패턴
  latency metrics 항목
  STT provider factory 방향

패턴만 재사용:
  FastAPI route 구성
  async turn job
  TTS audio handling
  rate limit/request size guard
  Unreal client state machine

재설계 필수:
  in-memory session store
  in-memory job queue
  local WAV file storage
  CSV latency metrics
  3D Behavior JSON schema
  UE5 face/lip-sync runtime
```

모바일 스택은 첫 릴리즈 기준으로 `Flutter`를 1순위로 둔다. 단, iOS 네이티브 품질이 중요한 결제/구독/알림/음성 권한/오디오 세션은 SwiftUI 또는 native plugin으로 보강할 수 있게 설계한다.

## 1. 병목 지도

### 1.1 캐릭터 외형 일관성

AI companion에서 이미지 보상은 단순 생성 이미지가 아니다. 사용자는 Airi를 같은 인물로 인식해야 한다.

병목:

- 이미지 생성 결과마다 얼굴, 헤어, 체형, 분위기가 달라짐
- prompt를 LLM이 자유 생성하면 일관성이 무너짐
- 재생성 요청이 늘면 비용이 빠르게 증가
- 부적절한 이미지가 생성되면 store/safety 리스크가 커짐

대응:

- `character_visual_profiles` 테이블 또는 config를 둔다.
- Airi의 visual identity를 고정한다.
- media prompt는 LLM 자유 문장이 아니라 template + controlled variables로 만든다.
- reference image, style guide, negative prompt, allowed outfit/theme를 관리한다.
- 생성 결과는 `pending -> approved/rejected` moderation status를 가진다.
- regeneration은 credit 차감 대상이다.

초기 구현:

```text
MediaPromptService
-> CharacterVisualProfile
-> DateEventRewardTemplate
-> SafetyPrecheck
-> ImageProvider
-> OutputModeration
-> MediaAsset
```

### 1.2 대화 지연률

chat-first 앱에서 첫 응답이 느리면 사용자는 바로 이탈한다.

병목:

- memory lookup
- safety check
- LLM provider latency
- 긴 context
- DB write
- TTS를 같은 request 안에서 기다리는 구조

대응:

- text response와 TTS job을 분리한다.
- recent messages 6~12턴 + relationship snapshot + memory top-k만 LLM에 넣는다.
- route를 나눈다.

```text
short_social -> 저비용/저지연 모델
default_chat -> 표준 모델
date_event_reaction -> 표준 모델
story/diary -> 비동기 또는 긴 timeout 허용
memory_extraction -> background worker
```

초기 latency 목표:

| 구간 | 목표 |
|---|---:|
| first visible reaction | 0.2~0.5s |
| text response first render | 1~2s |
| full chat response | 2~4s |
| first TTS audio | 2~3s |

### 1.3 TTS / voice 병목

실시간 통화는 STT, LLM, TTS가 연쇄로 붙기 때문에 가장 위험하다.

첫 릴리즈 판단:

- live call은 제외한다.
- PTT voice input + selected short TTS만 제공한다.
- TTS는 모든 답변이 아니라 짧은 답변/보상/감정 반응 중심으로 제한한다.

병목:

- TTS provider latency
- TTS provider 동시성 제한
- 긴 답변의 first audio delay
- voice 초당 비용
- 모바일 오디오 세션/권한/백그라운드 상태

대응:

- PromptMotionLab의 segmented TTS 패턴을 재사용한다.
- 첫 segment를 먼저 만들고 나머지는 뒤따라 생성한다.
- TTS queue를 chat queue와 분리한다.
- plan별 TTS char/day cap을 둔다.
- 실패 시 text-only fallback을 둔다.

### 1.4 provider quota / 장애

AI 서비스의 실제 병목은 서버보다 provider quota와 비용이다.

병목:

- LLM RPM/TPM
- STT streaming session limit
- TTS 동시성
- image generation queue
- provider 장애 또는 가격 변경

대응:

- provider별 concurrency pool
- route별 token budget
- user/plan quota
- provider_usage_events
- provider daily/monthly cost cap
- fallback route
- kill switch

필수 지표:

```text
provider
model
route
input_units
output_units
estimated_cost
latency_ms
fallback_used
request_id
user_id
plan
```

### 1.5 memory/RAG 병목

memory는 companion의 핵심이지만 비용과 개인정보 리스크가 크다.

병목:

- 전체 대화 history를 매번 넣으면 token 비용 증가
- memory extraction을 응답 전에 하면 latency 증가
- 민감정보가 memory에 저장될 위험
- memory 삭제/export 요구

대응:

- short-term context와 long-term memory를 분리한다.
- memory extraction은 async worker로 처리한다.
- memory summary, source message, embedding을 분리한다.
- memory safety filter를 둔다.
- 사용자가 memory를 삭제할 수 있어야 한다.

### 1.6 image/video queue 병목

image는 느리고 비싸다. video는 첫 릴리즈에서 넣으면 운영 리스크가 지나치게 크다.

대응:

- image는 async job만 허용한다.
- gallery에 pending 상태를 표시한다.
- Free는 weekly/basic image reward만 허용한다.
- regeneration은 credit 차감이다.
- video generation은 첫 릴리즈 제외다.

### 1.7 credit/reward/relationship 정합성

AI companion에서 사용자 신뢰를 깨는 가장 빠른 방법은 결제/보상/관계 수치가 꼬이는 것이다.

병목:

- 중복 webhook
- 중복 reward 지급
- provider 실패 후 credit 환불 누락
- LLM이 reward를 임의 지급
- relationship snapshot과 event log 불일치

대응:

- credit은 append-only ledger
- 모든 credit/reward 작업은 idempotency key 사용
- relationship은 event log + snapshot 구조
- reward unlock은 rule engine만 결정
- LLM은 감정 반응만 생성

### 1.8 admin/CS 병목

상용 출시 후에는 DB 직접 수정으로 운영할 수 없다.

최소 admin:

- user lookup
- conversation inspector
- credit ledger viewer
- provider cost dashboard
- queue monitor
- moderation review
- admin audit log viewer

## 2. PromptMotionLab 실제 코드 재사용 판단

확인 경로:

```text
C:\Portfolio\PromptMotionLab\Server-Python
C:\Portfolio\PromptMotionLab\Client-Unreal
```

### 2.1 높은 재사용 가치

#### RuntimeCharacterService

경로:

```text
Server-Python/app/services/runtime_character_service.py
```

재사용 가치:

- provider timeout/fallback 구조
- fast path response
- request_id/metadata 생성
- latency metric logging
- profile 기반 emotion intensity 조정
- emergency response

AICompanion 적용:

```text
RuntimeCharacterService
-> CharacterDialogueService
```

수정 필요:

- `RuntimeSessionStore`는 DB/Redis 기반 conversation/memory로 대체
- `BehaviorJson`은 3D gesture 중심에서 `CharacterReaction`으로 축소
- relationship snapshot, memory top-k, quota 정보를 prompt context에 추가
- provider_usage_events 저장 추가

#### CharacterProfileStore

경로:

```text
Server-Python/app/services/character_profile_store.py
```

재사용 가치:

- Airi profile 방향
- 말투 variation
- response examples
- character alias 개념

AICompanion 적용:

```text
CharacterProfileStore
-> CharacterProfileService
-> DB backed profile/versioning
```

수정 필요:

- 코드 하드코딩에서 DB/config versioning으로 전환
- store-safe romantic/suggestive policy 반영
- profile version, prompt version, rollout percentage 추가

#### RoutingOpenAiRuntimeBehaviorProvider

경로:

```text
Server-Python/app/providers/runtime/routing_openai_provider.py
```

재사용 가치:

- short_social vs default route 개념
- route_for 메타데이터
- 저비용 모델 라우팅

수정 필요:

- route 종류를 늘린다.

```text
short_social
default_chat
date_event_reaction
memory_extraction
media_prompt
safety
fallback
```

- token/cost budget을 route별로 연결한다.
- plan별 모델 제한을 둔다.

#### RuntimeTurnAsyncJobService

경로:

```text
Server-Python/app/services/runtime_turn_async_job_service.py
```

재사용 가치:

- async turn job 상태
- immediate reaction
- segmented TTS
- first segment ready logging
- timeout/failure 상태

수정 필요:

- 현재는 in-memory job dict와 asyncio task 기반이다.
- 상용 서비스에서는 Redis/Celery/RQ 또는 managed queue로 바꿔야 한다.
- job 상태는 DB/Redis에 저장해야 한다.
- TTS job은 chat turn job에서 분리해야 한다.

#### TtsService / TtsProvider

경로:

```text
Server-Python/app/services/tts_service.py
Server-Python/app/providers/tts/base.py
```

재사용 가치:

- TTS provider interface
- timeout/fallback
- concurrency semaphore
- audio metadata contract

수정 필요:

- local WAV 저장은 object storage로 대체
- audio URL은 signed URL 또는 media ticket으로 제공
- provider usage/cost logging 추가
- voice profile과 character profile 연결

#### Streaming STT provider factory

경로:

```text
Server-Python/app/providers/stt/streaming_factory.py
```

재사용 가치:

- Azure/OpenAI/Google STT provider 선택 구조
- env 기반 provider 교체

수정 필요:

- 첫 릴리즈는 streaming call보다 PTT voice input 중심으로 축소
- provider별 한국어 인식률/latency/cost 실측 후 선택
- voice session quota, abuse limit 추가

#### LatencyMetricsLogger

경로:

```text
Server-Python/app/services/latency_metrics_logger.py
```

재사용 가치:

- 측정해야 하는 latency 항목이 잘 잡혀 있음
- route, provider, model, fallback, first audio 지표 개념

수정 필요:

- CSV 파일 저장은 개발/벤치마크용으로만 사용
- 상용 서비스에서는 `provider_usage_events`, metrics backend, log pipeline으로 전환

### 2.2 중간 재사용 가치

#### FastAPI route/main/dependencies

경로:

```text
Server-Python/app/api/routes.py
Server-Python/app/main.py
Server-Python/app/dependencies.py
```

재사용:

- FastAPI app 구조
- dependency wiring
- API shape 참고

수정:

- AICompanion은 auth, plan/quota, billing, admin route가 필요하다.
- runtime/3D endpoint는 chat/date/reward/media 중심 API로 재설계한다.

#### Security guards

경로:

```text
Server-Python/app/security/rate_limit.py
Server-Python/app/security/body_size_limit.py
Server-Python/app/security/websocket_limits.py
```

재사용:

- 개발/베타용 guard 패턴

수정:

- in-memory limit이면 scale-out에서 깨진다.
- Redis 기반 user/device/IP rate limit으로 전환해야 한다.

### 2.3 낮은 재사용 가치

#### UE5 face/lip-sync/runtime

경로:

```text
Client-Unreal/PromptMotionClient
```

판단:

- 첫 릴리즈가 mobile chat/reward 중심이면 직접 재사용하지 않는다.
- voice input UX, async polling, playback state machine은 참고 가치가 있다.
- UE5 face morph/lip-sync는 현재 제품 핵심이 아니다.

#### Behavior JSON

경로:

```text
Server-Python/app/contracts/runtime_behavior.py
```

판단:

- 3D gesture/gaze/head motion 중심이라 그대로 쓰기 무겁다.
- AICompanion에서는 더 작은 schema가 맞다.

권장 schema:

```json
{
  "reply": "string",
  "emotion": "warm|playful|concerned|shy|neutral",
  "intent": "chat|date_invite|comfort|memory_recall|reward_hint|fallback",
  "ttsStyle": "warm|soft|playful|careful",
  "memoryCandidate": {},
  "dateEventSuggestion": {},
  "safetyFlags": []
}
```

## 3. 모바일 스택 판단

공식 문서 기준:

- Flutter는 하나의 코드베이스로 mobile, web, desktop 경험을 만들 수 있는 cross-platform UI framework다.
- React Native는 React paradigm을 사용해 Android/iOS native platform UI로 앱을 만든다.
- SwiftUI는 Apple platform용 declarative UI framework다.

출처:

- https://flutter.dev/
- https://reactnative.dev/
- https://developer.apple.com/documentation/swiftui

### 3.1 Flutter

장점:

- iOS/Android 동시 개발 속도가 빠르다.
- UI 일관성이 좋다.
- chat, gallery, shop, relationship status 같은 custom UI에 강하다.
- 애니메이션/카드형 reward UI를 만들기 쉽다.
- Android/Google Play/Firebase/Ads 쪽 통합 경험이 좋다.

단점:

- Dart 인력이 필요하다.
- iOS native feel을 아주 세밀하게 맞추려면 추가 작업이 필요하다.
- 음성, 결제, push, background audio는 native plugin 품질을 검증해야 한다.

적합한 경우:

- 소규모 팀
- iOS/Android 동시 출시
- custom UI가 많음
- 초기 속도가 중요함

### 3.2 React Native

장점:

- TypeScript/React 인력이 있으면 생산성이 높다.
- native module ecosystem이 넓다.
- web/admin과 일부 기술 맥락을 공유하기 쉽다.
- iOS/Android native UI 접근성이 좋다.

단점:

- dependency/native module 충돌 관리가 필요하다.
- RN bridge/new architecture 이해가 필요하다.
- 애니메이션/오디오/실시간 기능에서 native module 품질 편차가 있다.

적합한 경우:

- 팀이 React/TypeScript에 강함
- admin/web도 같은 인력이 맡음
- native module 관리 경험이 있음

### 3.3 Native iOS: SwiftUI

장점:

- iOS 품질, 성능, 접근성, 결제/구독, push, audio session 대응이 가장 좋다.
- App Store 정책 대응과 platform UX가 좋다.
- iOS 중심 premium 제품이면 장기적으로 강하다.

단점:

- Android를 따로 만들어야 한다.
- Kotlin/Android 팀이 추가로 필요하다.
- 첫 릴리즈 범위가 2배로 늘 수 있다.

적합한 경우:

- iOS-first premium 전략
- Android 출시를 늦춰도 됨
- native mobile 인력이 충분함

### 3.4 Native Android: Kotlin / Jetpack Compose

장점:

- Android/Google Play/AdMob/Billing 대응이 좋다.
- Android 음성 권한, background, notification 처리에 강하다.

단점:

- iOS를 별도로 만들어야 한다.
- 한국/글로벌 companion 앱에서 iOS 결제 유저를 놓칠 수 있다.

## 4. 스택 최종 권장

첫 릴리즈 기준 권장:

```text
Mobile:
  Flutter

Backend:
  FastAPI + Python

DB:
  PostgreSQL + pgvector

Cache/Queue:
  Redis + Celery/RQ

Object Storage:
  S3-compatible or Azure Blob

Admin:
  React + Vite or Next.js
```

단, 조건부로 바뀐다.

| 조건 | 추천 |
|---|---|
| 팀이 React/TypeScript에 매우 강함 | React Native |
| iOS premium만 먼저 출시 | SwiftUI |
| Android/AdMob 중심 검증 | Flutter 또는 Kotlin |
| 빠른 iOS/Android 동시 출시 | Flutter |
| native audio/call을 초기에 강하게 넣음 | SwiftUI/Kotlin 또는 RN/Flutter native module 검증 필수 |

현재 기획 기준 최종 판단:

```text
Flutter가 맞다.
하지만 live call을 첫 릴리즈에 넣지 않는다는 전제가 필요하다.
첫 릴리즈가 chat + PTT voice + limited TTS + reward gallery라면 Flutter가 가장 현실적이다.
```

live call을 초기에 넣겠다면 판단이 달라진다.

```text
live call first:
  Flutter 단독 결정 금지.
  iOS SwiftUI/AVAudioSession, Android Kotlin/AudioRecord/AudioTrack 검토 필요.

no live call first:
  Flutter 우선.
```

## 5. 개발 우선순위 조정

기존 `01-Development-plan-and-tech-stack.md`의 우선순위를 다음처럼 보강한다.

### 먼저 해야 하는 것

1. Provider adapter와 usage logging
2. Credit ledger와 quota
3. CharacterDialogueService
4. RelationshipStateService
5. MemoryService
6. DateEventRuleEngine
7. TTS async queue
8. MediaGenerationService
9. Admin 최소 화면

### 나중에 해야 하는 것

1. live call
2. video generation
3. UGC marketplace
4. multi-character world
5. self-hosted model

## 6. PM에게 필요한 결정

개발 착수 전 최종 결정이 필요한 항목:

1. 첫 릴리즈에서 live call을 완전히 제외할지
2. Flutter 기준으로 진행할지, React Native 경험자가 있다면 RN으로 바꿀지
3. iOS-first인지 iOS/Android 동시 출시인지
4. Airi image consistency를 provider 기능으로 해결할지, reference/style pipeline을 별도 구축할지
5. Free TTS cap을 `3~5 short replies/day`로 고정할지

개발자 판단:

```text
1. live call 제외
2. Flutter 우선
3. iOS/Android 동시 출시
4. visual profile + prompt template + output moderation 우선
5. Free TTS 3~5 short replies/day
```
