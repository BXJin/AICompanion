# PromptMotionLab Reuse Map for Future AI Companion Date Game

## 목적

추후 "AI companion + 데이트형 미니게임 + 사진/영상 보상" 프로젝트를 새 폴더에서 시작할 때, PromptMotionLab에서 재활용 가능한 코드/문서/설계 경험을 분류한다.

## 재활용 우선순위

| 우선순위 | 영역 | 재활용 가치 | 비고 |
|---|---|---|---|
| 높음 | Server-Python provider 구조 | STT/LLM/TTS 교체와 비용/latency 관리에 직접 사용 가능 | 3D와 무관하게 재사용 가능 |
| 높음 | Character profile / 말투 matrix | AI companion 품질 평가에 직접 사용 가능 | 새 캐릭터용 profile로 확장 |
| 높음 | Async turn / segmented TTS | 사용자가 기다리는 시간을 줄이는 핵심 구조 | 웹/앱에도 적용 가능 |
| 중간 | Behavior JSON | 3D 표정 대신 이미지/영상/이모션 UI로 변환 가능 | 스키마 재설계 필요 |
| 중간 | Streaming STT | 음성 대화형 앱에서 사용 가능 | VAD/turn-taking 추가 필요 |
| 낮음 | UE5 face morph/lip-sync | 새 프로젝트가 사진/영상 기반이면 직접 재사용 어려움 | 기술 포트폴리오로만 활용 |

## Server-Python 재활용 후보

### API / routing

| 경로 | 역할 | 재활용 방식 |
|---|---|---|
| `Server-Python/app/api/routes.py` | runtime respond, async turn, STT/TTS endpoint, WebSocket STT | 새 프로젝트의 chat/game API 라우팅 뼈대로 참고 |
| `Server-Python/app/main.py` | FastAPI app, rate limit, request size guard | 기본 보안/요청 제한 구조 재사용 |
| `Server-Python/app/dependencies.py` | provider/service dependency wiring | provider factory와 환경변수 기반 설정 참고 |

### LLM / character response

| 경로 | 역할 | 재활용 방식 |
|---|---|---|
| `Server-Python/app/services/runtime_character_service.py` | 사용자 메시지 -> reply + Behavior JSON 생성 | 새 프로젝트의 `CharacterDialogueService`로 발전 가능 |
| `Server-Python/app/services/character_profile_store.py` | Airi profile, 성격별 alias, 말투 규칙 | companion profile/profile versioning 설계에 재사용 |
| `Server-Python/app/providers/runtime/openai_provider.py` | OpenAI runtime behavior provider | LLM JSON contract 생성 방식 참고 |
| `Server-Python/app/providers/runtime/routing_openai_provider.py` | nano/mini 모델 라우팅 | 비용/latency 최적화용 model routing 재사용 |
| `Server-Python/app/contracts/runtime_behavior.py` | emotion/intent/gaze/gesture/ttsStyle schema | 새 프로젝트에서는 `CharacterReaction` schema로 축소/변환 |

### Async turn / latency

| 경로 | 역할 | 재활용 방식 |
|---|---|---|
| `Server-Python/app/services/runtime_turn_async_job_service.py` | LLM 응답과 TTS segment를 async job으로 처리 | 게임 결과 반응/음성 응답을 빠르게 시작하는 구조로 재사용 |
| `Server-Python/app/services/tts_async_job_service.py` | TTS job 저장/TTL/timeout | 보상 음성/캐릭터 음성 생성 job에 재사용 |
| `Server-Python/app/services/latency_metrics_logger.py` | 단계별 latency 기록 | 새 앱의 UX 지연 측정에 재사용 |
| `scripts/benchmark_runtime_turn_tts_latency.py` | TTS segmentation latency benchmark | TTS provider 변경 시 회귀 테스트로 사용 |

### STT / voice

| 경로 | 역할 | 재활용 방식 |
|---|---|---|
| `Server-Python/app/providers/stt/streaming_factory.py` | Azure/OpenAI/Google streaming STT provider 선택 | 새 프로젝트도 provider 교체 가능 구조로 시작 |
| `Server-Python/app/providers/stt/azure_streaming_provider.py` | Azure streaming STT | 기본 streaming STT provider |
| `Server-Python/app/providers/stt/openai_realtime_streaming_provider.py` | OpenAI realtime STT | STT 품질 비교 후보 |
| `Server-Python/app/services/stt_service.py` | batch STT service | fallback 또는 debug WAV용 |

### TTS

| 경로 | 역할 | 재활용 방식 |
|---|---|---|
| `Server-Python/app/providers/tts/base.py` | TTS provider interface | ElevenLabs/다른 TTS provider 추가 시 재사용 |
| `Server-Python/app/providers/tts/azure_provider.py` | Azure TTS + viseme | 새 프로젝트에서는 viseme보다 audio generation 중심으로 축소 |
| `Server-Python/app/services/tts_service.py` | TTS synthesis, audio file TTL cleanup | 음성 메시지 생성/보관 구조에 재사용 |
| `Server-Python/app/contracts/speech_timeline.py` | speech timeline contract | 영상/음성 응답 metadata contract로 변환 가능 |

### Security / limits / monitoring

| 경로 | 역할 | 재활용 방식 |
|---|---|---|
| `Server-Python/app/security/rate_limiter.py` | IP/request rate limit | 공개 베타 최소 보호 |
| `Server-Python/app/security/request_size_limit.py` | request body size guard | 이미지/음성 업로드 API에도 필요 |
| `Server-Python/app/security/websocket_connection_limiter.py` | WebSocket connection limit | voice/chat streaming 연결 제한 |
| `Server-Python/app/services/provider_failure_logger.py` | provider failure logging | 외부 API 장애 추적 |

## Client-Unreal 재활용 후보

새 프로젝트가 사진/영상 기반이면 UE5 코드는 직접 재사용 가치가 낮다. 다만 "실시간 캐릭터 반응 설계"를 참고하는 데는 가치가 있다.

| 경로 | 역할 | 재활용 방식 |
|---|---|---|
| `Client-Unreal/PromptMotionClient/Source/PromptMotionClient/Runtime/Core/PromptMotionRuntimeComponent.cpp` | runtime request, async turn polling, behavior apply | 웹/앱 client state machine 설계 참고 |
| `Client-Unreal/PromptMotionClient/Source/PromptMotionClient/Runtime/Core/PromptMotionTypes.h` | Behavior/Turn/TTS type 정의 | TypeScript/Kotlin DTO 설계 참고 |
| `Client-Unreal/PromptMotionClient/Source/PromptMotionClient/Runtime/Core/PromptMotionVoiceInputController.cpp` | PTT/VAD/streaming STT input flow | 모바일 voice input UX 참고 |
| `Client-Unreal/PromptMotionClient/Source/PromptMotionClient/Runtime/Core/PromptMotionStreamingSttClient.cpp` | STT WebSocket client | 앱 client WebSocket 구조 참고 |
| `Client-Unreal/PromptMotionClient/Source/PromptMotionClient/Runtime/Core/PromptMotionSpeechPlaybackController.cpp` | segment audio playback/gap logging | 음성 메시지 재생 queue/gap 로그 참고 |
| `Client-Unreal/PromptMotionClient/Source/PromptMotionClient/Runtime/Core/PromptMotionRuntimeEndpointConfig.cpp` | Local/Production endpoint profile | 앱 환경 설정 구조 참고 |

## Scripts / evaluation 재활용 후보

| 경로 | 역할 | 재활용 방식 |
|---|---|---|
| `scripts/runtime_character_matrix_test.py` | 캐릭터별 응답 matrix 평가 | 새 companion 말투/상황별 회귀 테스트로 재사용 |
| `scripts/runtime_voice_regression_wav_test.py` | TTS/STT voice regression | 음성 품질/latency 검증에 참고 |
| `scripts/smoke_openai_realtime_stt.py` | OpenAI realtime STT smoke | STT provider 교체 검증 |
| `scripts/production_smoke_test.py` | production endpoint smoke | 공개 배포 후 기본 응답 확인 |
| `Build/reports/runtime_character_matrix/` | matrix 실행 결과 | 말투 품질 변화 비교 자료 |

## Docs 재활용 후보

| 경로 | 내용 | 재활용 방식 |
|---|---|---|
| `Docs/현재/01-시스템-아키텍처.md` | 현재 STT/LLM/TTS/UE flow | 새 서비스 backend architecture 초안 |
| `Docs/현재/02-캐릭터-프로필-상태.md` | character profile / MBTI alias | companion profile 설계 참고 |
| `Docs/현재/03-LLM-라우팅.md` | nano/mini routing | 비용 최적화 설계 |
| `Docs/현재/05-STT-입력처리.md` | streaming STT / input 처리 | voice chat UX 설계 |
| `Docs/현재/06-테스트-검증.md` | matrix 테스트 방식 | 캐릭터 품질 평가 방식 |
| `Docs/미래/02-장기-메모리-RAG.md` | memory/RAG 확장 | 관계/데이트 기록 저장 구조 |
| `Docs/미래/03-캐릭터-상태-영속성.md` | closeness/trust state | 관계도/보상 시스템 기초 |
| `Docs/배포/01-Azure-서버-배포.md` | Azure App Service 배포 | 베타 서버 배포 참고 |

## 새 프로젝트에서 새로 만들어야 하는 영역

| 영역 | 필요한 이유 |
|---|---|
| `GameRuleEngine` | 승패/점수/턴/보상 판정은 LLM이 아니라 deterministic engine이 해야 함 |
| `RelationshipStateStore` | 친밀도, 신뢰도, 질투, 기분, 피로도 등 영속 저장 |
| `RewardUnlockService` | 사진/영상/스토리/음성 메시지 해금 조건 관리 |
| `MemoryStore` | 대화, 게임 결과, 데이트 기록 저장 |
| `MediaGenerationProvider` | 이미지/영상 생성 provider |
| `ContentSafetyPolicy` | 성인성, 캐릭터 나이, 과몰입, 개인정보 안전 정책 |
| `UserAuth` | 공개 서비스에서는 사용자별 제한/과금/저장소가 필요 |

## 추천 초기 아키텍처

```text
Client App
-> ChatController
-> GameController
-> MediaGallery

Server
-> CharacterDialogueService
-> GameRuleEngine
-> RelationshipStateService
-> MemoryService
-> RewardUnlockService
-> MediaGenerationService
-> Provider Layer
   -> LLM
   -> STT
   -> TTS
   -> Image/Video
```

## 재사용 시 주의점

- PromptMotionLab의 Behavior JSON은 3D 표정/립싱크 중심이다. 새 프로젝트에서는 `emotion`, `intent`, `rewardHint`, `memoryWrite`, `mediaSuggestion` 중심으로 다시 줄이는 편이 낫다.
- UE5 runtime 코드는 새 앱에 직접 가져가기보다, async request/state machine 설계를 참고하는 정도가 맞다.
- 현재 rate limiter는 인메모리 기반이다. 공개 베타 이상에서는 Redis 같은 shared limiter가 필요하다.
- 관계/메모리 저장은 서버 DB에 두는 것이 맞다. 앱 로컬 저장만으로는 여러 기기/계정/복구가 어렵다.
- 이미지/영상 보상은 비용이 크므로 daily limit, unlock condition, paid credit 구조를 처음부터 고려해야 한다.
