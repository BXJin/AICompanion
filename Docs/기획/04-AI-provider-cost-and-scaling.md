# AI Provider / License / Cost / Scaling Plan

첫 release의 plan별 allowance, credit 단위, rewarded ad, 실패/환불 정책은 `20-Credit-plan-allowance-policy.md`를 기준으로 한다.

## 목적

AI companion + 데이트형 미니게임 + 이미지/음성/영상 보상 서비스를 실제 상용 서비스로 운영한다고 가정하고, 어떤 AI provider를 쓸지, 개인 라이선스와 상업 라이선스 차이는 무엇인지, 사용자 수가 늘 때 비용이 어떻게 증가하는지, 과금 구조를 얼마로 잡아야 안전한지 정리한다.

## 핵심 결론

이 서비스의 비용은 서버비보다 AI 사용량이 먼저 터진다.

```text
낮은 비용:
- 텍스트 LLM 대화
- 짧은 memory lookup
- 단순 게임 판정

중간 비용:
- STT
- TTS
- 장기 메모리/RAG

높은 비용:
- 고품질 voice call
- 이미지 생성
- 영상 생성
- 긴 스토리/다중 캐릭터 생성
```

따라서 상용 가격 구조는 다음이 맞다.

```text
Free:
텍스트 중심 + 제한된 음성/이미지 맛보기

Plus:
장기 메모리 + 더 많은 대화 + 데이트 이벤트 + 제한된 음성/이미지

Premium:
우선 응답 + 고급 음성 + 더 많은 이미지/음성 + 커스텀 캐릭터

Credit:
고품질 이미지, 영상, 긴 음성, live call, 특별 이벤트
```

구독 하나로 모든 고비용 기능을 무제한 제공하면 사용자가 늘수록 손실이 커진다.

## 개인 구독과 상용 API의 차이

| 항목 | 개인/무료 사용 | 상용 서비스 기준 | 판단 |
|---|---|---|---|
| ChatGPT Plus/Pro | 사용자가 ChatGPT 앱에서 쓰는 개인 구독 | 내 앱의 백엔드 API 비용을 대체하지 않음 | 서비스에는 OpenAI API 과금 필요 |
| OpenAI API | 사용량 기반 | 입력/출력 token, audio/image token 기준 과금 | 백엔드 서비스에 적합 |
| OpenAI output | 약관상 사용자가 input 권리를 보유하고 output 소유가 원칙 | 정책/법률 준수 필요 | 이미지/스토리/대화 상용 활용 가능성 있음 |
| ElevenLabs Free | 개인/비상업 사용 | 상업 서비스에 부적합 | 출시/수익화에는 사용 금지 |
| ElevenLabs Starter 이상 | commercial license 포함 | TTS/voice clone 상용 사용 가능 | 최소 유료 플랜 필요 |
| Voice clone | 본인 또는 권리 보유 음성만 안전 | 성우/제3자 음성은 명시 동의/계약 필요 | 캐릭터 voice 권리 관리 필수 |
| Google Play Billing | 앱 내 디지털 상품 결제 | 서비스 수수료 15% 또는 조건별 30% | 매출에서 먼저 차감 |

상용 기준으로는 "내가 개인 계정으로 구독해서 앱 사용자들에게 돌린다"는 구조가 아니다. 사용자 요청은 서비스 백엔드에서 API로 처리하고, 비용/권리/정책을 서비스 운영자가 책임지는 구조다.

## 공개 가격 기준

2026-06-02 확인 기준. 가격은 바뀔 수 있으므로 출시 전 재확인이 필요하다.

| Provider | 항목 | 공개 가격 |
|---|---|---:|
| OpenAI `gpt-4.1-nano` | Text input | `$0.10 / 1M tokens` |
| OpenAI `gpt-4.1-nano` | Text output | `$0.40 / 1M tokens` |
| OpenAI `gpt-4.1-mini` | Text input | `$0.40 / 1M tokens` |
| OpenAI `gpt-4.1-mini` | Text output | `$1.60 / 1M tokens` |
| OpenAI GPT-Realtime-Whisper | Streaming STT | `$0.017 / minute` |
| OpenAI GPT-Realtime-2 | Realtime audio input/output | audio input `$32 / 1M tokens`, audio output `$64 / 1M tokens` |
| OpenAI GPT-Image-2 | Image generation | image input `$8 / 1M tokens`, image output `$30 / 1M tokens` |
| ElevenLabs Flash/Turbo | TTS | 약 `$0.05 / 1K characters` |
| ElevenLabs Multilingual | TTS | 약 `$0.10 / 1K characters` |
| ElevenLabs Scribe Realtime | STT | 약 `$0.39 / hour` |
| ElevenLabs Agent Speech Engine | Voice agent | 약 `$0.08 / minute` |
| Azure App Service Linux B1 | API server | 약 `$13.14 / month` |
| Google Play | Subscription / IAP fee | 일반적으로 15%, 조건별 30% |

## 추천 AI 구성

### MVP / 베타

| 기능 | 추천 | 이유 |
|---|---|---|
| 짧은 대화 | OpenAI `gpt-4.1-nano` | 인사, 감사, 짧은 감정 반응은 저비용 모델로 충분 |
| 일반 대화/고민 | OpenAI `gpt-4.1-mini` | 품질과 비용 균형 |
| STT | OpenAI Realtime Whisper 또는 ElevenLabs Scribe 비교 | 한국어 인식 품질과 latency를 실제 테스트해야 함 |
| TTS | ElevenLabs Flash/Turbo | 캐릭터 앱에서 음성 품질은 핵심 UX |
| 이미지 | OpenAI image 또는 별도 image provider | 셀피/데이트 사진/보상 콘텐츠 |
| 영상 | MVP 제외 | 원가와 실패/재생성 리스크 큼 |
| 메모리 | PostgreSQL + pgvector | 사용자별 관계/취향/이벤트 저장 |
| 캐시/제한 | Redis | rate limit, session, job queue |

## Provider 후보 확장

현재 PromptMotionLab 경험상 OpenAI + ElevenLabs 조합이 가장 빠르게 MVP를 만들기 좋다. 하지만 상용 서비스 기준으로는 특정 provider에 종속되면 가격 인상, 장애, 품질 문제에 취약하다.

### LLM 후보

| Provider | 후보 모델 | 장점 | 단점 | 추천 용도 |
|---|---|---|---|---|
| OpenAI | `gpt-4.1-nano`, `gpt-4.1-mini` | 현재 프로젝트에서 이미 구조 검증. 가격/품질 균형 좋음 | 이미지/음성까지 같이 쓰면 vendor lock-in 가능 | 기본 LLM routing |
| Google Gemini | Gemini Flash / Flash-Lite 계열 | 가격 경쟁력, 긴 context, Google 생태계 | 모델/가격/쿼터 변동이 잦을 수 있음 | 저비용 대량 대화 후보 |
| Anthropic Claude | Haiku/Sonnet 계열 | 긴 글, 안전한 톤, 추론 품질 | OpenAI/Gemini 저가 모델 대비 비쌀 수 있음 | 스토리/감정/긴 대화 후보 |
| DeepSeek/Qwen 등 | 저비용 API 또는 self-host 후보 | 비용 절감 가능 | 품질/안전/정책/운영 안정성 검증 필요 | 내부 실험/비용 절감 후보 |
| OpenRouter/aggregator | 여러 모델 라우팅 | provider 비교가 쉬움 | 상용 안정성/데이터 정책/장애 책임 검토 필요 | 실험용, 최종 상용은 신중 |

상용 기준 추천은 다음이다.

```text
Primary: OpenAI 또는 Gemini
Secondary fallback: 다른 LLM provider
Special route: Claude 계열은 긴 스토리/감정 서사 품질 비교용
Low-cost route: Gemini Flash-Lite/저가 모델을 무료 유저용으로 실험
```

### STT 후보

| Provider | 장점 | 단점 | 판단 |
|---|---|---|---|
| OpenAI Realtime/Transcribe | 한국어 품질 기대, LLM 생태계 연동 | 비용/latency 실제 측정 필요 | 품질 후보 |
| ElevenLabs Scribe | STT 단가가 낮은 편, voice 제품군과 결합 | 한국어 품질 직접 검증 필요 | 비용 후보 |
| Azure Speech | PromptMotionLab에서 이미 사용 | 일부 단어 오인식 경험 있음 | 안정성 후보 |
| Google Speech-to-Text | 한국어/클라우드 안정성 | 가격/구현 복잡도 검토 필요 | 대안 후보 |
| Deepgram | real-time STT 특화 | 한국어 품질/상용 조건 검증 필요 | 실시간 후보 |

STT는 가격표보다 실제 한국어 인식률이 중요하다. "음성"을 "삼성"으로 듣는 문제가 반복되면, 몇 센트 싼 provider보다 품질 좋은 provider가 낫다.

### TTS 후보

| Provider | 장점 | 단점 | 판단 |
|---|---|---|---|
| ElevenLabs | 캐릭터 음성 품질, voice clone, companion 앱에 적합 | 비용이 Azure/Google보다 커질 수 있음 | 1순위 후보 |
| Azure TTS | 안정적, 현재 프로젝트 경험 있음 | 감정/캐릭터성은 약할 수 있음 | 저비용/기본 후보 |
| Google Cloud TTS | Chirp/Neural 계열, 클라우드 안정성 | voice character fit 검증 필요 | 대안 후보 |
| Cartesia/PlayHT 등 | 실시간 voice 제품군 | 상용 권리/가격 검토 필요 | 실험 후보 |

AI companion 앱은 TTS가 캐릭터성을 크게 좌우한다. 텍스트는 좋아도 음성이 기계적이면 서비스 인상이 약해진다.

### 이미지 생성 후보

이미지 생성은 일반 LLM이 아니라 image generation model/API를 사용한다. 일부 모델은 multimodal LLM처럼 prompt를 이해하지만, 비용과 과금 단위는 텍스트 LLM과 다르다.

| Provider | 모델/방식 | 장점 | 단점 | 추천 용도 |
|---|---|---|---|---|
| OpenAI Image | GPT Image 계열 | prompt 이해, 품질, API 안정성 | token 기반이라 1장 원가 실측 필요 | 고품질 보상 이미지 |
| Replicate | FLUX, Ideogram, Recraft 등 | 모델 선택 폭 넓음, pay-per-use | 모델별 가격/권리/품질 편차 | 실험/프로토타입 |
| fal.ai | FLUX, GPT Image, video 모델 등 | 이미지/영상 모델 폭 넓음, 빠른 serverless | 모델별 가격이 다르고 변동 가능 | 이미지/영상 provider 비교 |
| Stability AI | Stable Diffusion 계열 | SD 생태계, 커스터마이징 | 라이선스/저작권/품질 검토 필요 | 커스텀 스타일/비용 절감 |
| Runware | 다양한 image/video model API | 저렴한 모델 선택 가능, includeCost 지원 | 품질/정책/권리 검증 필요 | 비용 최적화 실험 |
| Self-host SD/Flux | 직접 GPU 운영 | 장기 대량 생성 시 원가 절감 가능 | GPU 운영/튜닝/안전필터 부담 | 규모가 커진 뒤 검토 |

상용 초기에는 OpenAI/Replicate/fal/Runware 중 2개 이상을 테스트해서 `1장 평균 원가`, `실패율`, `재생성률`, `정책 리스크`, `캐릭터 일관성`을 비교해야 한다.

## 이미지 생성은 어떤 AI를 쓰는가

이미지 보상은 다음 두 단계로 나누는 게 좋다.

```text
1. LLM
   - 캐릭터 상태, 데이트 이벤트, 보상 조건을 보고 이미지 prompt 작성
   - 예: "카페 데이트 후 Airi가 남긴 폴라로이드 사진"

2. Image generation model
   - prompt를 받아 실제 이미지 생성
   - OpenAI Image, FLUX, Stable Diffusion, Ideogram, Recraft 등
```

즉, "대화 LLM"과 "이미지 생성 AI"는 분리된다.

### 이미지 prompt 생성 예시

```text
User completed cafe date event.
Relationship affinity +3.
Reward: cafe selfie.

LLM output:
{
  "mediaType": "image",
  "prompt": "A soft, cozy cafe selfie of an adult AI companion character...",
  "safetyTags": ["adult_character", "non_explicit"],
  "style": "polaroid",
  "costTier": "standard"
}

ImageProvider:
-> generate image
-> store asset
-> unlock reward
```

### 이미지 비용 운영 원칙

- 대화 LLM이 이미지를 직접 만들지 않는다.
- 이미지 생성은 별도 `MediaGenerationService`가 담당한다.
- 생성 전 safety/policy check를 한다.
- 이미지 1장당 실제 provider cost를 저장한다.
- 무료 이미지는 주간/월간 cap을 둔다.
- 재생성은 반드시 credit을 소모한다.
- 영상은 MVP에서 제외하거나 고가 credit으로 제한한다.

### 모델 라우팅

```text
short_social:
  인사, 감사, 짧은 안부, 가벼운 질문
  -> gpt-4.1-nano

default:
  일반 대화, 감정, 관계, 데이트 이벤트
  -> gpt-4.1-mini

story/event:
  스토리 카드, 보상 문구, 긴 대화
  -> gpt-4.1-mini

safety:
  rule 기반 1차 감지 + 필요 시 LLM

media prompt:
  이미지/영상 prompt 생성
  -> mini
```

## 대화 LLM 비용

### 1턴 비용 가정

| 대화 유형 | 입력/출력 가정 | 모델 | 1턴 비용 대략 |
|---|---:|---|---:|
| 짧은 인사/감사 | 300 input / 50 output | nano | `$0.00005` |
| 일반 대화 | 700 input / 80 output | nano 80% + mini 20% | `$0.00016` |
| 고민/관계/스토리 | 1,500 input / 180 output | mini | `$0.00089` |
| 긴 메모리 포함 | 3,000 input / 250 output | mini | `$0.00160` |

텍스트 대화만 보면 비용은 낮다.

```text
20 turns/day -> 약 $0.10/month/user
50 turns/day -> 약 $0.25/month/user
100 turns/day -> 약 $0.49/month/user
```

하지만 context를 길게 계속 넣으면 비용이 늘어난다. 그래서 장기 대화는 전체 history를 그대로 넣지 말고 summary + memory top-k로 줄여야 한다.

## STT 비용

음성 입력은 사용량에 비례한다.

| 사용량 | OpenAI Realtime Whisper 기준 | ElevenLabs Scribe 기준 |
|---|---:|---:|
| 1분/day | 약 `$0.51/month` | 약 `$0.20/month` |
| 5분/day | 약 `$2.55/month` | 약 `$0.98/month` |
| 10분/day | 약 `$5.10/month` | 약 `$1.95/month` |

다만 STT는 가격만 보고 결정하면 안 된다. 한국어 인식률, latency, partial/final 품질, WebSocket 안정성이 더 중요하다. 무료 유저에게 음성 입력을 무제한으로 열면 손실 가능성이 커진다.

## TTS 비용

TTS는 캐릭터 서비스에서 체감 품질을 크게 좌우하지만, 무료로 많이 열면 비용이 빠르게 오른다.

ElevenLabs Flash/Turbo `$0.05 / 1K chars` 가정:

| TTS 사용량 | 월 비용/유저 |
|---|---:|
| 100 chars/day | `$0.15` |
| 500 chars/day | `$0.75` |
| 1,000 chars/day | `$1.50` |
| 2,000 chars/day | `$3.00` |
| 5,000 chars/day | `$7.50` |

무료 유저가 하루 500자 TTS만 써도 1,000명 기준 월 `$750`가 된다. 따라서 무료 플랜은 TTS 답변 수를 강하게 제한해야 한다.

## 이미지 생성 비용

이미지는 "사용자에게 돈을 내게 만드는 기능"이지만, 원가와 정책 리스크가 있다.

OpenAI GPT Image 계열은 이미지가 token으로 환산되어 과금된다. 해상도/품질/입력 이미지 수/출력 이미지 수에 따라 비용이 달라지므로, 출시 전 provider별 실제 1장 평균 원가를 측정해야 한다.

운영 정책:

| 이미지 기능 | 과금 방식 | 이유 |
|---|---|---|
| 기본 셀피 | Plus/Premium에 소량 포함 | retention 보상 |
| 데이트 보상 사진 | 구독 + 제한 | 관계 루프 강화 |
| 고품질 이미지 | credit | 반복 생성 비용 방어 |
| 재생성 | credit | 무한 reroll 방지 |
| 사용자 prompt 자유 입력 | credit + safety | 정책/비용 리스크 큼 |

초기에는 실제 AI 이미지 생성보다 "보상 슬롯/갤러리 UX"를 먼저 만들고, 생성은 제한적으로 붙이는 게 안전하다.

## 영상 생성 비용

영상은 MVP 무료 기능으로 넣으면 안 된다.

이유:

- 원가가 높음
- 생성 실패/품질 불만/재생성 요구가 많음
- 저장소/CDN 비용 증가
- 정책 검수 부담 증가

추천:

```text
MVP:
사전 제작 영상 카드 또는 mock reward

베타:
짧은 영상 1개 = credit 사용

상용:
월간 video cap + queue + 재생성 정책 + 고가 credit
```

## 메모리 / RAG 비용

메모리는 AI companion의 핵심 가치지만 개인정보와 비용이 생긴다.

| 기능 | 비용 | 과금 위치 |
|---|---|---|
| 최근 대화 20~40턴 | 낮음 | 무료 가능 |
| 장기 기억 추출 | LLM/embedding 비용 | Plus 이상 |
| vector search | DB/embedding 비용 | Plus 이상 |
| 캐릭터별 일기/요약 | LLM 비용 | Premium/credit |
| 데이터 삭제/내보내기 | 운영 비용 | 필수 기능 |

무료 유저에게 장기 메모리를 무제한 제공하면 DB/embedding/요약 비용과 개인정보 책임이 커진다.

## 서버 비용

서버는 사용자 수와 완전히 1:1로 증가하지 않는다. 대부분의 AI 연산은 외부 provider가 수행하고, 서버는 orchestration, 상태 저장, 제한, 결제, 이벤트 판정 역할을 한다.

| 단계 | 구성 | 월 고정비 대략 |
|---|---|---:|
| Prototype | App Service B1 + 간단 DB | `$13~50` |
| Closed beta | App Service 1~2개 + PostgreSQL + storage + logs | `$80~300` |
| Public beta | App Service/Premium or container + PostgreSQL + Redis + monitoring | `$300~1,500` |
| Scale | multi-instance + queue + Redis + DB replica + CDN + observability | `$1,500+` |

서버비가 늘어나는 경우:

- 동시 접속 WebSocket 증가
- voice call 실시간 세션 증가
- 이미지/영상 저장량 증가
- RAG query 증가
- 로그/모니터링 증가
- 결제/보상/이벤트 트래픽 증가

## 사용자 유형별 월 원가

| 유형 | 사용량 | LLM | STT | TTS | 이미지/영상 | 월 AI 원가/유저 |
|---|---|---:|---:|---:|---:|---:|
| Text-only free | 20 text turns/day | `$0.10` | `$0` | `$0` | `$0` | `$0.10` |
| Light voice | 20 turns/day, STT 1min/day, TTS 500 chars/day | `$0.10` | `$0.20~0.51` | `$0.75` | `$0` | `$1.05~1.36` |
| Voice-heavy | 50 turns/day, STT 5min/day, TTS 2,000 chars/day | `$0.25` | `$0.98~2.55` | `$3.00` | `$0` | `$4.23~5.80` |
| Image-light | 20 turns/day, 10 images/month | `$0.10` | 선택 | 선택 | provider별 측정 필요 | 변동 큼 |
| Video-user | 영상 생성 포함 | 텍스트 비용은 작음 | 선택 | 선택 | 가장 큼 | credit 필수 |
| Live call user | 30min/month voice agent | 별도 | 별도 | 별도 | `$0` | ElevenLabs Agent 기준 `$2.40+` |

## DAU별 비용 예시

### Text 중심

| DAU | AI 비용/월 | 서버/DB/Redis/Storage | 합계 대략 |
|---:|---:|---:|---:|
| 100 | `$10` | `$30~100` | `$40~110` |
| 1,000 | `$100` | `$150~500` | `$250~600` |
| 10,000 | `$1,000` | `$1,000~5,000` | `$2,000~6,000` |

### Light voice 중심

| DAU | AI 비용/월 | 서버/DB/Redis/Storage | 합계 대략 |
|---:|---:|---:|---:|
| 100 | `$105~136` | `$30~100` | `$135~236` |
| 1,000 | `$1,050~1,360` | `$150~500` | `$1,200~1,860` |
| 10,000 | `$10,500~13,600` | `$1,000~5,000` | `$11,500~18,600` |

### Voice-heavy 중심

| DAU | AI 비용/월 | 서버/DB/Redis/Storage | 합계 대략 |
|---:|---:|---:|---:|
| 100 | `$423~580` | `$50~150` | `$473~730` |
| 1,000 | `$4,230~5,800` | `$300~800` | `$4,530~6,600` |
| 10,000 | `$42,300~58,000` | `$2,000~8,000` | `$44,300~66,000` |

## 실제 매출에서 차감되는 비용

앱 가격을 정할 때 AI 원가만 보면 안 된다.

| 항목 | 영향 |
|---|---|
| Google Play / App Store 수수료 | 일반적으로 15%, 조건별 30% |
| VAT/부가세 | 국가별로 다름 |
| PG/환불/차지백 | 웹 결제 시 별도 |
| 서버/DB/로그/스토리지 | 고정비 + 사용량 |
| AI provider | 변동비 |
| 고객지원/신고처리 | companion 서비스에서 중요 |
| 콘텐츠 검수 | 이미지/영상/UGC가 있으면 필수 |

## 안전한 가격 설계

### 추천 소비자가

| 플랜 | 가격 | 포함 기능 | 목표 원가 |
|---|---:|---|---:|
| Free | 0원 | 텍스트 20~30턴/day, 음성 맛보기, 이미지 거의 없음 | `$0.10~0.50/user/month` |
| Plus | 12,900원 | 더 많은 대화, 장기 메모리, 데이트 이벤트, 제한된 음성/이미지 | `$1~3/user/month` |
| Premium | 24,900원 | 우선 응답, 고급 voice, 더 많은 이미지/음성, 커스텀 캐릭터 | `$3~7/user/month` |
| Credit small | 3,300원 | 소량 이미지/특별 음성 | 고비용 기능 분리 |
| Credit medium | 11,000원 | 이미지/이벤트 보상 번들 | ARPU 보강 |
| Credit large | 33,000원 | 영상/고급 이미지 중심 | heavy user 원가 방어 |

## 무료 크레딧 / 보상 크레딧 설계

상용 companion 앱은 무료 크레딧을 줄 수 있다. 다만 무료 크레딧은 "마케팅 비용"이고, AI 원가가 실제로 발생한다.

### 무료 크레딧 종류

| 크레딧 | 지급 조건 | 목적 | 주의점 |
|---|---|---|---|
| 가입 보너스 | 최초 가입 | 핵심 기능 체험 | 너무 많이 주면 가입 어뷰징 |
| 일일 출석 | 하루 1회 | 재방문 유도 | 이미지/영상까지 주면 원가 증가 |
| 광고 보상 | rewarded ad 시청 | 광고 수익으로 일부 보전 | 광고 수익보다 보상 원가가 낮아야 함 |
| 이벤트 보상 | 시즌/데이트 완료 | 몰입도 증가 | 이벤트별 cost cap 필요 |
| 관계 레벨 보상 | 친밀도 상승 | 장기 이용 유도 | high-cost reward는 제한 |

### 크레딧 단위 제안

크레딧은 실제 원가보다 높게 책정해야 한다. 원가와 판매가가 너무 가까우면 플랫폼 수수료/환불/실패 재생성에서 손실이 난다.

| 사용처 | 내부 원가 가정 | 권장 소비 크레딧 |
|---|---:|---:|
| 짧은 음성 메시지 | 낮음~중간 | 1~2 credits |
| 기본 이미지 1장 | provider별 실측 필요 | 5~10 credits |
| 고품질 이미지 1장 | 중간 | 10~25 credits |
| 이미지 재생성 | 동일 원가 발생 | 동일 credit |
| 짧은 영상 | 높음 | 50~200 credits |
| live voice 1분 | 중간~높음 | 10~30 credits |

### 무료 크레딧 원칙

```text
무료 크레딧은 텍스트/낮은 원가 기능 위주.
이미지/영상은 무료 지급량을 아주 작게.
광고 보상 크레딧은 광고 예상 수익보다 낮은 원가의 보상만 지급.
```

예를 들어 rewarded ad 1회로 기본 이미지 1장을 무료 제공하는 것은 위험하다. eCPM이 낮은 국가/기간에는 광고 수익보다 이미지 생성 원가가 더 클 수 있다.

## 광고 수익 계산

AdMob은 banner, interstitial, rewarded, app open, native 같은 형식을 제공한다. AI companion 앱에서는 강제 광고보다 rewarded ad가 가장 자연스럽다.

### 광고 형식 판단

| 광고 형식 | 추천도 | 이유 |
|---|---:|---|
| Rewarded ad | 높음 | 사용자가 보상을 원할 때 자발적으로 시청 |
| Native ad | 중간 | 피드/갤러리 사이에 자연스럽게 배치 가능 |
| Interstitial | 낮음~중간 | 대화 흐름을 끊기 쉬움 |
| Banner | 낮음 | 수익 낮고 companion 몰입감 저해 |
| App open | 낮음 | 첫 인상 나빠질 수 있음 |

### 광고 수익 공식

AdMob의 eCPM은 1,000회 노출당 예상 수익이다.

```text
ad_revenue = impressions / 1000 * eCPM * fill_rate
```

예시:

```text
rewarded ad 1,000회 노출
eCPM $5
fill rate 80%

수익 = 1000 / 1000 * 5 * 0.8
     = $4

광고 1회당 수익 = $0.004
```

즉 광고 1회로 보전 가능한 원가는 매우 작을 수 있다.

### 광고 기반 보상 계산

| 가정 | 광고 1회당 수익 | 지급해도 되는 보상 |
|---|---:|---|
| eCPM $1, fill 70% | `$0.0007` | 텍스트/낮은 원가 보상 |
| eCPM $5, fill 80% | `$0.004` | 소량 credit, 짧은 TTS 일부 |
| eCPM $10, fill 80% | `$0.008` | 저가 이미지 일부 보조 가능 |
| eCPM $20, fill 90% | `$0.018` | 기본 이미지 1장 일부 보조 가능 |

이미지 1장 원가가 `$0.02~0.08`이면 광고 1회로 완전히 커버하기 어렵다. 따라서 광고 보상은 다음처럼 설계하는 게 안전하다.

```text
광고 1회:
- 1~3 credits
- 또는 텍스트 대화 추가
- 또는 짧은 음성 1회

이미지 1장:
- 광고 여러 회 누적
- 또는 Plus/Premium
- 또는 paid credit
```

### 광고 + 크레딧 혼합 모델

```text
Free user:
  하루 텍스트 제한 도달
  -> 광고 시청
  -> +5 text turns 또는 +1~3 credits

Image reward:
  기본 필요 credit: 10
  광고 1회 보상: 2 credits
  -> 광고 5회 또는 paid credit 필요
```

이렇게 해야 광고 수익과 생성 원가의 괴리가 줄어든다.

## 다른 게임/앱의 무료 크레딧 방식 반영

모바일 게임/AI 앱은 보통 무료 재화와 유료 재화를 분리한다.

| 재화 | 설명 | 예시 |
|---|---|---|
| Free credits | 출석/광고/이벤트로 지급 | 낮은 원가 기능에 사용 |
| Paid credits | 결제 구매 | 이미지/영상/voice call에 사용 |
| Subscription allowance | 월 구독 포함 사용량 | 매월 이미지 N장, 음성 N분 |
| Event tickets | 특정 데이트/게임 입장권 | 시즌 이벤트 제어 |
| Premium currency | 고급 콘텐츠 전용 | 영상, 고품질 이미지 |

추천 구조:

```text
Free Gems:
  광고/출석으로 지급
  텍스트 추가, 기본 미니게임, 낮은 원가 보상

Paid Gems:
  결제로 구매
  이미지/영상/voice call

Monthly Allowance:
  Plus/Premium 구독 포함 사용량
  매월 리셋
```

무료 재화와 유료 재화를 완전히 동일하게 만들면, 광고/어뷰징으로 고비용 기능을 소모할 수 있다. 고비용 기능은 paid credit 또는 subscription allowance를 우선 사용하게 해야 한다.

### Plus 손익 가정

```text
소비자가: 12,900원
Google Play 15% 후: 10,965원
대략 USD: 약 $7.9
목표 gross margin 60% 이상
허용 원가: 약 $3.1 이하
```

Plus는 light voice 수준까지는 안전하지만, voice-heavy 유저가 많아지면 제한이 필요하다.

### Premium 손익 가정

```text
소비자가: 24,900원
Google Play 15% 후: 21,165원
대략 USD: 약 $15.3
목표 gross margin 60% 이상
허용 원가: 약 $6.1 이하
```

Premium은 voice-heavy 일부를 감당할 수 있지만, 영상 생성까지 무제한으로 넣으면 위험하다.

## 플랜별 권장 제한

### Free

```text
Text: 20~30 turns/day
Voice input: 1 min/day
TTS: 3~5 replies/day
Image: 0~1/week
Video: 없음
Memory: short-term only
Custom character: 없음
```

### Plus

```text
Text: 150~300 turns/day
Voice input: 10~20 min/month
TTS: 500~1,000 chars/day
Image: 10~30/month
Video: 없음 또는 credit only
Memory: long-term enabled
```

### Premium

```text
Text: 넉넉하게
Voice input: 60~120 min/month
TTS: 2,000~3,000 chars/day
Image: 50~100/month
Video: credit discount
Memory: long-term + richer personalization
Priority: yes
```

## 비용 관리 운영 룰

### 반드시 필요한 cap

| Cap | 이유 |
|---|---|
| user daily LLM turns | 무료 남용 방지 |
| user daily voice seconds | STT/TTS 비용 방어 |
| user monthly image count | 이미지 비용 방어 |
| user monthly video count | 영상 비용 방어 |
| provider monthly budget | 사고 방지 |
| event campaign budget | 시즌 이벤트 폭주 방지 |
| free user total monthly cap | 무료 유저 손실 제한 |

### 대시보드 필수 지표

```text
cost_per_user_day
cost_per_paid_user_month
free_user_cost_month
paid_user_ai_cost_month
llm_tokens_by_route
stt_minutes
tts_characters
image_generation_count
video_generation_count
gross_margin_by_plan
heavy_user_top_1_percent_cost
```

## 출시 전 비용 검증 실험

실제 가격을 정하기 전 다음 실험이 필요하다.

1. 100명 closed beta
2. 2주 동안 실제 사용량 수집
3. 유저당 평균 turn, voice seconds, image count 측정
4. free/paid 가정별 원가 계산
5. Plus/Premium 제한 조정
6. credit 가격 조정

AI companion 앱은 일부 heavy user가 비용의 대부분을 만들 수 있다. 평균만 보면 위험하고, 상위 1% 유저의 비용을 반드시 따로 봐야 한다.

## 냉정한 판단

텍스트 대화만 제공하면 비용은 낮지만 차별점이 약하다. 음성/이미지/영상/데이트 보상을 많이 열면 차별점은 커지지만 비용이 빠르게 오른다.

초기 상용 설계는 다음이 맞다.

```text
무료:
텍스트 중심 + 제한된 voice/image 맛보기

구독:
long-term memory + 더 많은 대화 + 데이트 이벤트 + 기본 voice/image

크레딧:
고품질 이미지, 영상, 긴 음성, 특별 이벤트
```

즉, AI 비용이 많이 드는 기능일수록 credit으로 분리해야 한다. 구독 하나로 모든 고비용 기능을 무제한 제공하면 사용자가 늘수록 손실이 커진다.

## 20-year PM revenue model correction

### Problem

If the plan is designed only around cost protection, Free becomes too weak. In an AI companion product, this is dangerous.

Users may churn immediately if Free feels like this:

```text
I watched ads, but the character still remembers nothing.
It is an AI companion, but there is almost no voice.
It is a character app, but there is no photo/reward.
The conversation stops before I feel attached.
```

Free is not just a trial. Free must create the first emotional loop: the user should feel that the character remembers a little, talks a little, and gives at least a small reward.

### Revised product philosophy

```text
Free:
  Show the core fun.
  Give short memory, limited voice, and a tiny image/reward taste.
  Control cost with ads and hard caps.

Plus:
  The main subscription.
  Remove ads.
  Unlock long-term memory, date events, mini-games, and more voice/image allowance.

Premium:
  For immersive and heavy users.
  Add premium voice, more images, priority response, and custom companion slots.

Credits:
  Protect high-cost generation.
  Use for image regeneration, video, long voice, live call, and special events.

Season/Event Pack:
  Content revenue.
  Sell limited date events, anniversary events, story packs, and special rewards.
```

### Revised pricing proposal

| Product | Price | Role | PM judgment |
|---|---:|---|---|
| Free | 0 KRW | Acquisition / ads / conversion | Must show core fun |
| Plus | 14,900 KRW | Main subscription | Ad-free + memory + date loop |
| Premium | 29,900 KRW | Heavy user defense | Premium voice/image/priority |
| Credit small | 3,300 KRW | Small purchase | Small image/voice usage |
| Credit medium | 11,000 KRW | Main credit pack | Image/special event bundle |
| Credit large | 33,000 KRW | Heavy user | Video/high-quality image/long voice |
| Season Pack | 9,900~19,900 KRW | Content revenue | Seasonal date/story/reward |

Plus at 9,900 KRW is easier to buy, but margins become weak once voice and image usage are included. For this type of AI content app, 14,900 KRW is safer as the main subscription price.

### Free allowance recommendation

Free should feel slightly limited, not empty.

```text
Text:
  30~50 turns/day

Memory:
  short-term conversation
  very small long-term summary, about 3~5 memories
  examples: name, preferences, recent date/game result

Voice:
  voice input 1 min/day
  TTS 3~5 short replies/day

Image:
  basic selfie/reward 1 image/week
  or 1~2 signup bonus images

Game/Date:
  1~2 basic mini-games
  some basic date events

Ads:
  enabled
  rewarded ads give text turns, small credits, or extra basic voice

Video:
  not included
```

This is enough for users to feel that the character is alive. But high-quality images, long voice, and video should not be open in Free.

### Plus allowance recommendation

Plus should be ad-free. If ads remain after payment, companion immersion is damaged.

```text
Text:
  150~300 turns/day

Memory:
  long-term memory
  date/game result memory
  preference memory

Voice:
  voice input 30~60 min/month
  TTS 1,000~2,000 chars/day

Image:
  20~40 standard images/month
  regeneration uses credits

Game/Date:
  basic date events
  basic mini-games
  relationship-level rewards

Ads:
  removed

Video:
  credit only
```

The value of Plus is not just more messages. It is "the character remembers me better, the relationship deepens, and I can enjoy the loop without ads."

### Premium allowance recommendation

```text
Text:
  generous, but still with abuse caps

Memory:
  richer personalization
  diary/story memory

Voice:
  120~240 min/month voice input
  TTS 3,000~5,000 chars/day
  premium voice

Image:
  80~150 images/month
  some high-quality allowance

Game/Date:
  premium date events
  special rewards
  early access

Custom:
  custom companion slots

Video:
  credit discount
  very small monthly allowance only if margins are proven
```

Premium is not unlimited. It is a generous high-end experience with caps. Video should still not be unlimited.

### Ad reward design

Ads are support revenue, not the core business. A single rewarded ad may only cover a very small cost.

Safe rewarded ad options:

```text
1 rewarded ad:
  +5 text turns
  or +1~3 free credits
  or 1 short voice reply

Multiple ads accumulated:
  1 basic image

Do not give directly from 1 ad:
  high-quality image
  video
  long voice call
```

Giving one image for one ad can lose money depending on country, eCPM, fill rate, and image generation cost. It is safer to give small credits and let users accumulate them.

### Separate free credits and paid credits

Game and AI apps should separate free currency and paid currency.

| Currency | Source | Use |
|---|---|---|
| Free Credits | attendance, ads, events | text extension, basic voice, some basic images |
| Paid Credits | purchase | regeneration, high-quality image, video, live call |
| Monthly Allowance | Plus/Premium | monthly voice/image allowance |
| Event Tickets | event/purchase | seasonal dates, special mini-games |

High-cost features should consume Paid Credits or Monthly Allowance first. Free Credits should not be enough to consume unlimited video/high-quality image generation.

### Final revenue structure

```text
1. Free + Ads
   - acquisition
   - core fun preview
   - partial cost recovery

2. Plus
   - main MRR
   - ad-free
   - long-term memory
   - date/mini-game loop
   - basic voice/image

3. Premium
   - heavy user defense
   - premium voice/image
   - priority response
   - custom companion

4. Credits
   - high-cost generation defense
   - image regeneration
   - video
   - long voice
   - live call

5. Season/Event Pack
   - content revenue
   - Valentine's Day, birthday, Christmas, trip, movie date, etc.
```

### PM judgment

The most important revenue product is Plus. Free keeps users from deleting the app. Premium protects against heavy users. Credits prevent high-cost media generation from destroying margins.

The dangerous structure is:

```text
Free is too empty, so users churn.
Plus is cheap but opens too much, so costs explode.
Premium is not meaningfully different from Plus.
Images/videos are given through ads and lose money.
```

The safer final direction is:

```text
Free shows the fun.
Plus deepens the relationship without ads.
Premium provides immersive high-end experience.
Credits sell expensive generation.
Season Packs create content revenue.
```

This mixed subscription + credit + event pack model is safer than subscription-only or ad-only monetization for an AI companion app.

## Sources

- OpenAI API pricing: https://openai.com/api/pricing/
- OpenAI GPT-4.1 pricing: https://openai.com/index/gpt-4-1/
- OpenAI Terms of Use: https://openai.com/policies/terms-of-use/
- ElevenLabs API pricing: https://elevenlabs.io/pricing/api
- ElevenLabs commercial use help: https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform
- Google Play service fees: https://support.google.com/googleplay/android-developer/answer/112622
- Azure App Service Linux pricing: https://azure.microsoft.com/en-us/pricing/details/app-service/linux/
