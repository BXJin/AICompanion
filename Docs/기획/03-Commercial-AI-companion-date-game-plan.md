# Commercial Plan - AI Companion Date Game

## 결론

이 프로젝트는 게임엔진이 필수인 프로젝트가 아니다.

상용 레벨로 가려면 핵심은 3D 렌더링이 아니라 다음이다.

```text
AI companion
+ relationship state
+ date/game event loop
+ reward unlock
+ image/video/voice content
+ subscription/credit monetization
+ safety/policy
+ cost control
```

따라서 기술 선택은 다음처럼 잡는 게 현실적이다.

| 영역 | 추천 | 이유 |
|---|---|---|
| 클라이언트 | 모바일 앱 또는 PWA | Zeta/Nika/Vela류는 대화/콘텐츠/결제 UX가 핵심 |
| 렌더링 | 정적 이미지, 짧은 영상, 애니메이션 카드 | 게임엔진보다 비용/개발 속도/배포가 유리 |
| 게임 | 서버 룰 엔진 | 승패/보상은 deterministic하게 판정해야 함 |
| AI | LLM + memory + media generation | 캐릭터성/대화/콘텐츠 생성 담당 |
| 과금 | 구독 + 크레딧 혼합 | 대화는 구독, 이미지/영상/voice call은 크레딧이 적합 |

## 참고 시장

### Character.AI / Zeta 계열

Character.AI는 c.ai+에서 better memory, ad-free chats, 최신 모델 접근, no slow mode, unlimited voice calls, swipes/customization 등을 구독 가치로 제시한다. 월 $9.99, 연 $94.99 가격이 표시되어 있다.

Zeta는 Google Play 기준 "무제한 채팅", 캐릭터 생성, story/roleplay, memory, 대화 기반 이미지 생성을 강조한다. Google Play 페이지에는 광고와 인앱 결제가 표시되어 있다.

### Vela 계열

Vela는 voice, memory, consistent face/photo를 핵심으로 잡는다. 무료 플랜은 30 messages/day, 5 voice messages/day, 5 selfies/day, short-term memory를 제공하고, Plus/Premium에서 long-term memory, 더 많은 메시지/voice/selfie, custom companion, premium voice, priority speed를 제공한다.

### Nika / Aurora 계열

Nika는 AI girlfriend/boyfriend companion과 Aurora City dating simulator RPG를 함께 운영한다. 30-level Bond System, images/video, ElevenLabs voice, live calls, diary, story generator, UGC scenario marketplace를 강조한다. Aurora City는 RPG stats, jobs, seasonal events, relationship levels로 dates/sleepovers/marriage를 해금하는 구조다.

### Questie / WhisperGames 계열

Questie는 게임 화면을 보고 real-time voice chat으로 반응하는 AI gaming companion이다. 요금은 credit 기반 시간제로 설명한다.

WhisperGames는 AI Game Master가 party games, quizzes, riddles, mystery stories, solo adventures, couples games를 진행한다. 이는 companion보다는 "AI 진행자"에 가깝다.

## 제품 포지셔닝

### 한 줄 포지션

```text
대화로 관계를 쌓고, 데이트형 미니게임을 함께 하며, 결과가 기억/보상/스토리 콘텐츠에 반영되는 AI companion 서비스.
```

### 기존 서비스와의 차이

| 비교군 | 기존 강점 | 빈틈 | 우리 방향 |
|---|---|---|---|
| Character.AI/Zeta | 캐릭터챗, 롤플레잉, 스토리 | 명확한 게임 결과/보상 루프 약함 | 관계 기반 데이트 게임 루프 |
| Nika/Aurora | 관계 레벨, 이미지/영상, dating sim | 게임 판정/데이트형 미니게임을 더 명확히 만들 여지 | companion + date mini-game + reward |
| Love and Deepspace류 | 이벤트/미니게임/보상/연출 강함 | LLM 기반 자유 대화 companion는 아님 | LLM companion에 보상/데이트 루프 결합 |
| Questie | 실시간 게임 companion | 외부 게임 보조 중심 | 앱 내부에서 캐릭터와 직접 플레이 |
| WhisperGames | AI game master | 관계형 companion 아님 | 캐릭터 관계/감정/해금 중심 |

## 상용 레벨 MVP

처음부터 모든 기능을 만들면 망한다. 상용 앱처럼 보이려면 MVP도 "작지만 반복 가능한 루프"가 있어야 한다.

### MVP 목표

```text
대화 5분
-> 캐릭터가 데이트/게임 제안
-> 사용자가 1~3분짜리 미니게임 진행
-> 결과 저장
-> 캐릭터 반응
-> 관계도 변화
-> 작은 보상 해금
-> 다음 대화에서 기억
```

### MVP 기능 범위

| 기능 | MVP 포함 | 설명 |
|---|---|---|
| Text chat | 포함 | 가장 기본 |
| Voice input/output | 선택 | 비용 때문에 초기에는 제한 |
| 캐릭터 profile | 포함 | 말투/성격/금지 표현 |
| Relationship state | 포함 | 친밀도, 신뢰도, 기분 |
| Mini-game 1개 | 포함 | 카드 선택/주사위/간단한 보드게임 |
| Reward unlock | 포함 | 사진 1장, 음성 메시지, 짧은 스토리 |
| Long-term memory | 최소 포함 | 이름, 취향, 최근 이벤트, 게임 결과 |
| Image generation | 제한 포함 | 무료는 적게, 유료/크레딧 중심 |
| Video generation | MVP 제외 | 비용이 큼. 유료 보상으로 후순위 |
| Live call | MVP 제외 | 비용/latency/품질 리스크 큼 |
| UGC scenario marketplace | MVP 제외 | 운영/검수 난이도 큼 |

## 콘텐츠 기획

### 콘텐츠 축

| 축 | 내용 | 과금 적합도 |
|---|---|---|
| Chat | 일상 대화, 고민 상담, 장난, 연애/친구 관계 | 구독 |
| Date event | 카페, 산책, 영화, 집, 여행, 밤 산책 | 구독 + 해금 |
| Mini-game | 카드 선택, 심리게임, 틱택토, 주사위, 기억력 게임 | 무료/구독 |
| Story | 관계 레벨별 짧은 스토리 | 구독/해금 |
| Photo | 데이트 사진, 셀피, 기념 사진 | 크레딧 |
| Voice | 음성 메시지, 축하, 위로, ASMR류 | 크레딧/프리미엄 |
| Video | 짧은 5~8초 영상 | 고가 크레딧 |
| Diary | 캐릭터가 쓴 하루 기록/관계 기록 | 구독 |

### 데이트 이벤트 예시

| 이벤트 | 입력 | 게임/선택 | 결과 |
|---|---|---|---|
| 영화 감상 | 사용자가 본 영화/장르 입력 | 감상 포인트 선택 | 감상 카드 + 대화 기억 |
| 카페 데이트 | 메뉴/분위기 선택 | 캐릭터 취향 맞추기 | 친밀도 변화 + 사진 해금 |
| 산책 | 장소/시간 선택 | 대화 선택지 | mood 변화 |
| 보드게임 | 카드/주사위/간단한 전략 | 승패 판정 | 보상/장난 대사 |
| 고민 상담 | 고민 주제 입력 | 캐릭터 반응 선택 | trust 증가 |

### 보상 콘텐츠

| 보상 | 예시 | 조건 |
|---|---|---|
| 사진 | "오늘 카페에서 찍은 사진" | 데이트 성공, 친밀도 증가 |
| 음성 메시지 | "오늘 고생했어" | 피곤/위로 대화 후 |
| 스토리 카드 | "첫 영화 데이트 기록" | 이벤트 완료 |
| 프로필 변화 | 말투가 조금 편해짐 | 관계 레벨 상승 |
| 특별 대화 주제 | 비밀 이야기, 과거 이야기 | 신뢰도 조건 |
| 짧은 영상 | 웃는 장면, 손 흔드는 장면 | 유료/고레벨 보상 |

## 관계 시스템

### 상태값

| 상태 | 설명 | 사용처 |
|---|---|---|
| affinity | 호감도/친밀도 | 대화 톤, 해금 조건 |
| trust | 신뢰도 | 깊은 고민/비밀 주제 |
| mood | 현재 기분 | 반응 감정 |
| energy | 캐릭터 에너지 | 대화 길이/장난 정도 |
| jealousy | 질투/서운함 | 과몰입 리스크 때문에 약하게만 |
| familiarity | 익숙함 | 반말/장난/짧은 반응 |
| memory_score | 사용자를 얼마나 알고 있는지 | 개인화 반응 |

### 업데이트 원칙

LLM이 직접 숫자를 임의로 바꾸면 안 된다.

```text
User event
-> Rule-based state update
-> LLM에게 현재 state 요약 전달
-> LLM은 대사/감정만 생성
```

예시:

```text
영화 데이트 완료: affinity +3
사용자가 고민 공유: trust +2
게임에서 캐릭터가 패배: mood playful, affinity +1
무례한 발화: mood distant, affinity -1
```

## 게임 설계

### 게임엔진이 필요 없는 이유

이 프로젝트의 게임은 물리/3D/실시간 렌더링이 핵심이 아니다. 핵심은 "캐릭터와 함께 하는 선택/판정/보상 루프"다.

따라서 다음 구조면 충분하다.

```text
GameSession
GameState
GameRuleEngine
RewardEngine
RelationshipState
DialogueReaction
```

### 추천 미니게임

| 게임 | 구현 난이도 | 캐릭터성과의 연결 |
|---|---:|---|
| 카드 선택 심리게임 | 낮음 | 캐릭터 취향/사용자 성향 반영 |
| 틱택토 | 낮음 | 승패/장난 반응 |
| 기억력 게임 | 중간 | "지난번 기억"과 연결 |
| 주사위 데이트 | 낮음 | 랜덤 이벤트/보상 |
| 영화 감상 퀴즈 | 중간 | 사용자가 본 영화 맥락 |
| 보드게임형 경로 선택 | 중간 | 데이트 진행/스토리 |
| 협동 선택 게임 | 중간 | 관계도/신뢰도 반영 |

### 게임 판정 원칙

```text
GameRuleEngine
- 유효한 행동인지 검증
- 승패 판정
- 점수 계산
- 보상 조건 판정
- state update event 생성

LLM
- 캐릭터 반응
- 칭찬/장난/서운함/응원
- 스토리 문장
- 다음 제안
```

## 과금 구조

### 추천 모델

상용 레벨에서는 무료 + 구독 + 크레딧 혼합이 가장 현실적이다.

```text
Free
-> 하루 제한으로 맛보기

Plus
-> 대화/메모리/기본 데이트 루프 확장

Premium
-> 고급 음성, 우선 응답, 더 많은 콘텐츠 생성

Credit
-> 이미지/영상/특별 음성/고비용 생성
```

### 플랜 예시

| 플랜 | 가격 예시 | 제공 |
|---|---:|---|
| Free | 0원 | 하루 메시지 제한, 기본 캐릭터 1~3명, 짧은 메모리, 기본 미니게임 |
| Plus | 월 9,900~14,900원 | 메시지 확대, 장기 메모리, 데이트 이벤트, 기본 사진 보상, 커스텀 캐릭터 1명 |
| Premium | 월 19,900~29,900원 | 우선 응답, 고급 voice, 더 많은 사진/음성, 고급 이벤트, 커스텀 슬롯 |
| Credit pack | 3,000~49,000원 | 이미지/영상/특별 음성 생성 |
| Lifetime/Founder | 99,000~299,000원 | 초기 유저 확보용. 장기 비용 리스크 주의 |

### 기능별 과금 적합도

| 기능 | 무료 | 구독 | 크레딧 |
|---|---:|---:|---:|
| 기본 텍스트 대화 | O | O | X |
| 장기 메모리 | 제한 | O | X |
| 미니게임 | 제한 | O | X |
| 데이트 이벤트 | 일부 | O | 일부 |
| 일반 사진 | 제한 | O | O |
| 고품질 사진 | X | 일부 | O |
| 음성 메시지 | 제한 | O | O |
| live voice call | X | 제한 | O |
| 짧은 영상 | X | 제한 | O |
| 커스텀 캐릭터 | X | O | O |

### 왜 크레딧이 필요한가

텍스트 대화는 모델 라우팅과 캐싱으로 비용을 낮출 수 있다. 하지만 이미지/영상/고급 음성은 호출 단가가 높고 남용 가능성이 크다.

따라서 다음은 크레딧으로 묶는 게 맞다.

- 고해상도 이미지
- 영상 생성
- 긴 음성 메시지
- voice call
- 고급 모델 기반 스토리 생성
- 특별 이벤트 재생성

## 콘텐츠 운영 구조

### 운영 단위

| 단위 | 설명 |
|---|---|
| Character Pack | 캐릭터 외형/성격/voice/persona |
| Date Scenario | 영화, 카페, 산책, 여행, 밤 통화 등 |
| Mini-game Template | 카드, 주사위, 심리게임, 퀴즈 |
| Reward Pack | 사진, 음성, 영상, 스토리 카드 |
| Season Event | 발렌타인, 생일, 여름휴가, 크리스마스 |
| Memory Event | 이전 대화/게임 결과 기반 특수 대사 |

### 시즌 운영 예시

| 시즌 | 콘텐츠 |
|---|---|
| 1주차 | 첫 만남, 카페 데이트, 기본 카드게임 |
| 2주차 | 영화 감상 이벤트, 감상 카드 보상 |
| 3주차 | 산책 데이트, 사진 보상 |
| 4주차 | 관계 레벨 5 해금 스토리 |
| 월간 | 한정 의상/사진/음성 메시지 |

## 기술 아키텍처

### 기본 구조

```text
Client App
-> Chat UI
-> Date/Game UI
-> Gallery
-> Reward/Shop

Server
-> AuthService
-> CharacterDialogueService
-> RelationshipStateService
-> MemoryService
-> GameRuleEngine
-> RewardUnlockService
-> MediaGenerationService
-> BillingService
-> SafetyService
-> ProviderLayer
   -> LLM
   -> STT
   -> TTS
   -> Image
   -> Video
```

### 주요 테이블

| 테이블 | 역할 |
|---|---|
| users | 계정 |
| characters | 캐릭터 정의 |
| user_character_state | 사용자별 캐릭터 관계 상태 |
| conversations | 대화 세션 |
| messages | 메시지 |
| memories | 장기 기억 |
| game_sessions | 미니게임 진행 상태 |
| game_events | 게임 행동/결과 |
| rewards | 보상 정의 |
| user_rewards | 사용자별 해금 보상 |
| media_assets | 생성 이미지/영상/음성 |
| purchases | 결제/크레딧 내역 |
| safety_events | 정책/신고/차단 로그 |

## MVP 개발 순서

### Phase 0 - 검증

- 텍스트 대화
- 캐릭터 1명
- 관계 상태 3개: affinity/trust/mood
- 미니게임 1개
- 보상 1개
- 로컬/서버 DB 저장

### Phase 1 - 앱다운 루프

- 데이트 이벤트 3개
- 보상 갤러리
- 장기 메모리
- 무료 제한
- 크레딧 mock
- basic safety

### Phase 2 - 상용 베타

- 실제 결제
- 이미지 생성
- 음성 메시지
- 구독/크레딧
- 사용자 인증
- 삭제/내보내기
- 모니터링/비용 알림

### Phase 3 - 성장

- 시즌 이벤트
- 커스텀 캐릭터
- UGC 시나리오
- 영상 생성
- live call
- 추천/랭킹/커뮤니티

## 안전/정책

상용 AI companion은 정책 리스크가 크다. 특히 연애형/사진형 서비스면 더 크다.

필수 정책:

- 성인 캐릭터만 사용
- 미성년자처럼 보이는 캐릭터 금지
- 선정성/노골적 성적 콘텐츠 제한
- 의료/심리 위기 상황 안내
- 과몰입 방지 문구
- 대화 삭제/데이터 내보내기
- 신고/차단
- 광고/결제 고지
- 생성 이미지/영상 워터마크 또는 AI 생성 표시 검토

## 비용 관리

AI provider 선택, 유저당 AI 비용, DAU별 서버/AI 비용 추정은 별도 문서에 정리한다.

- `Docs/미래프로젝트/04-AI-provider-cost-and-scaling.md`

### 비용이 큰 기능

| 기능 | 비용 리스크 |
|---|---|
| LLM long context | 대화가 길어질수록 증가 |
| Voice call | 실시간 STT/LLM/TTS 모두 소모 |
| Image generation | 유저가 반복 생성하면 급증 |
| Video generation | 가장 비쌈 |
| Memory/RAG | embedding/query 비용과 DB 비용 |

### 비용 보호

- 무료 메시지 일일 제한
- 이미지/영상은 크레딧
- 모델 라우팅
- context 압축
- memory top-k 제한
- 캐릭터별 system prompt 캐싱
- 생성 결과 재사용
- 월별 비용 cap
- 사용자별 rate limit
- 이상 사용 감지

## PromptMotionLab 재활용 전략

직접 재사용보다 "서버 구조와 평가 방식"을 재활용하는 게 맞다.

| PromptMotionLab 자산 | 새 프로젝트 적용 |
|---|---|
| LLM provider routing | 비용/latency 모델 라우팅 |
| CharacterProfileStore | companion profile |
| RuntimeCharacterService | CharacterDialogueService |
| RuntimeTurnAsyncJobService | async chat/media response |
| STT/TTS provider | voice chat/voice message |
| Matrix test | 캐릭터 말투 회귀 테스트 |
| Rate limit/security | 공개 베타 비용 보호 |
| latency metrics | 상용 UX 측정 |

UE5 관련 face morph/lip-sync는 직접 재사용 가치가 낮다. 새 프로젝트가 이미지/영상 기반이면, 이 부분은 기술 포트폴리오로 남기고 서비스 구현에는 가져오지 않는 편이 낫다.

## 성공 지표

| 지표 | 목표 |
|---|---|
| D1 retention | 첫날 재방문 |
| D7 retention | 관계/보상 루프 효과 |
| 평균 대화 턴 | 캐릭터 몰입도 |
| 미니게임 진입률 | 제안 UX 효과 |
| 미니게임 완료율 | 게임 길이/난이도 적절성 |
| 보상 해금률 | 콘텐츠 동기 |
| 이미지/음성 구매율 | 크레딧 과금 가능성 |
| 비용/활성유저 | 사업 지속성 |
| fallback/timeout rate | 서비스 안정성 |

## 냉정한 판단

이 아이디어는 기술적으로 가능하고, 시장 요소도 이미 검증되어 있다. 하지만 "캐릭터챗 + 게임 + 보상 + 이미지/영상 + 관계 상태"를 한 번에 만들면 범위가 너무 커진다.

상용 레벨을 목표로 하더라도 첫 버전은 다음 하나만 증명해야 한다.

```text
사용자가 AI 캐릭터와 대화한다.
캐릭터가 짧은 데이트형 게임을 제안한다.
사용자가 게임을 끝낸다.
결과가 관계/기억/보상에 남는다.
다음 대화에서 캐릭터가 그 결과를 기억한다.
```

이 루프가 재미있으면 확장할 가치가 있다. 이 루프가 재미없으면 이미지/영상/과금/UGC를 붙여도 서비스가 약하다.

## Sources

- Character.AI c.ai+ pricing/features: https://character.ai/subscribe
- Zeta Google Play listing: https://play.google.com/store/apps/details?hl=en-US&id=com.scatterlab.messenger
- Vela pricing/features: https://meetvela.app/
- Nika / Aurora product description: https://nika.team/en/
- Questie gaming companion/pricing: https://www.questie.ai/
- WhisperGames feature description: https://whispergames.ai/
