# Zeta / Nika benchmark for commercial design

작성일: 2026-06-03

이 문서는 Zeta, Nika/Aurora류 상용 AI companion 서비스를 벤치마킹해 차기 모바일 상용앱 설계에 반영할 항목을 정리한다.

주의:

- Zeta/Nika의 내부 구현은 공개되어 있지 않다.
- 아래 내용은 공식 앱 스토어/공식 사이트/공개 설명 기준의 제품 벤치마킹이다.
- Nika 비교 페이지는 자사 제품 홍보 성격이 있으므로 기능 방향 참고용으로만 본다.

## 0. 벤치마킹 방법

벤치마킹은 "저 앱에 기능이 있으니 우리도 넣자"가 아니다. 상용앱에서 이미 검증된 **사용자 루프, 과금 구조, 비용 통제, 운영 리스크**를 분해해서 우리 제품에 맞는 것만 가져오는 작업이다.

### 0.1 벤치마킹 대상

1. Zeta
   - AI character chat.
   - story/roleplay.
   - large character pool.
   - free + ads + in-app purchase.

2. Nika
   - AI girlfriend/boyfriend companion.
   - relationship/bond progression.
   - voice/image/video.
   - companion diary.

3. Aurora City
   - AI dating simulator RPG.
   - scenario/date/event progression.
   - stats/jobs/seasonal event.
   - multi-character world.

4. 참고군
   - Character.AI류: 대규모 캐릭터/UGC/chat retention.
   - Love and Deepspace류: 연애형 콘텐츠/보상/이벤트 progression.
   - Replika류: long-term companion/memory/voice.

### 0.2 비교 항목

각 서비스를 다음 기준으로 본다.

| 축 | 확인할 것 | 우리 설계 반영 |
|---|---|---|
| 첫 진입 | 앱 켜자마자 무엇을 하게 하는가 | 첫 화면 chat 중심인지, 캐릭터 선택 중심인지 |
| 핵심 루프 | 사용자가 매일 반복하는 행동 | chat -> date event -> reward -> memory |
| 관계 시스템 | 호감도/친밀도/레벨이 있는가 | relationship level/state 설계 |
| 기억 | 사용자를 얼마나 기억하는가 | memory summary/RAG/diary |
| 콘텐츠 | 채팅 외에 할 것이 있는가 | official date event, reward gallery |
| 보상 | 무엇을 unlock하는가 | image, voice, story, diary, event |
| 과금 | 구독/credit/광고 구조 | Free/Plus/Premium/Credit/Ads |
| 비용 통제 | 고비용 기능을 어떻게 제한하는가 | image/video/voice credit |
| 수위 정책 | romance/adult/UGC 리스크 | store-safe romantic/suggestive max |
| 운영 | 신고/차단/모더레이션이 필요한가 | admin ops/safety tooling |

### 0.3 가져올 것과 버릴 것

가져올 것:

- 무료 사용자도 핵심 경험을 맛보게 하는 구조.
- relationship level과 unlock.
- date/scenario event.
- diary/memory처럼 "관계가 쌓인다"는 증거.
- credit으로 image/video/voice 같은 고비용 기능 보호.

버릴 것:

- 첫 release부터 UGC marketplace.
- 캐릭터 수 대량 확장.
- explicit adult content를 모바일 스토어 앱에서 직접 제공.
- live call/video generation 선출시.
- LLM에게 게임 판정/보상 판정을 맡기는 구조.

### 0.4 산출물

벤치마킹 결과는 다음 문서에 반영한다.

- `15-First-release-scope-decisions.md`
  - 첫 release 범위.

- `13-Mobile-first-commercial-detail-plan.md`
  - 모바일 화면/API/과금 방향.

- `04-AI-provider-cost-and-scaling.md`
  - provider 비용과 credit 정책.

- `09-Admin-ops-tooling-and-backoffice.md`
  - 운영툴과 moderation.

즉, 벤치마킹 문서는 기능 목록이 아니라 **상용 설계 의사결정의 근거 문서**로 사용한다.

## 1. 벤치마킹 요약

### Zeta

공개 자료 기준 주요 포인트:

- 모바일 앱 중심.
- AI character chat / live stories.
- 광고와 인앱 구매가 같이 있음.
- 1M+ downloads, 수만 리뷰 규모로 노출됨.
- 캐릭터 생성과 스토리/롤플레이 경험을 강조.
- Google Play 설명 기준 2.5M+ characters created, 평균 사용 시간 2시간 이상을 강조.
- 무료 채팅과 이미지 생성 경험을 강하게 내세움.
- App Store 기준 in-app purchase에 `zeta pass`, `pieces`가 존재.
- App Store privacy 항목상 user content, identifiers, usage data, diagnostics, advertising data 등을 다룸.
- 연령 등급은 13+지만 mature/suggestive themes, sexual content, UGC, advertising 같은 store risk 요소가 존재.

### Nika / Aurora City

공개 자료 기준 주요 포인트:

- Telegram bot + PWA mobile app.
- Nika, Sebastian, Aurora City 3개 제품 라인.
- Nika/Sebastian: AI girlfriend/boyfriend companion.
- Aurora City: AI dating simulator RPG.
- 30-level Bond System.
- relationship level이 tone, behavior, unlock content에 영향.
- AI image/video generation.
- ElevenLabs voice, Whisper speech recognition, live voice calls.
- companion diary, story generator.
- UGC scenario marketplace.
- Aurora City는 7 characters, RPG stats, jobs, seasonal events, day/night/living world를 강조.
- free + paid plans + token packages 구조.

## 2. 제품 포지션 비교

| 항목 | Zeta | Nika / Aurora | 우리 차기앱 방향 |
|---|---|---|---|
| 핵심 정체성 | AI character chat + story creation | AI companion + dating sim/RPG | AI companion + date mini-game + reward/media + memory |
| 진입 방식 | 모바일 앱 | Telegram/PWA 중심 | 모바일 앱 우선 |
| 캐릭터 수 | 다수/UGC 성격 강함 | Nika/Sebastian + Aurora 7명 | 첫 release 1~2명 권장 |
| 관계 시스템 | memory/story immersion 강조 | 30-level Bond System 명시 | relationship level + affinity/trust/mood |
| 콘텐츠 루프 | chat/story/image | chat/scenario/date/RPG/reward | chat -> date event -> reward -> memory |
| 과금 | pass + pieces + ads | free + paid plans + token | free + plus + premium + credit + ads |
| 강점 | 대규모 캐릭터/스토리 풀 | 관계 progression과 멀티모달 깊이 | 관계/게임/보상을 하나의 모바일 루프로 연결 |
| 리스크 | UGC/광고/성인테마/스토리 품질 | 기능 범위 과대, Telegram 의존 | 초기 범위 과대, AI 비용 폭주 |

## 3. 우리가 반드시 벤치마킹할 것

### 3.1 Zeta에서 가져올 점

#### 1. Free-first 진입

Zeta는 공개 설명에서 무료 채팅/이미지 생성 경험을 강하게 밀고 있다. AI companion 앱은 무료 체험이 약하면 사용자가 바로 삭제한다.

우리 적용:

- Free도 text chat은 충분히 제공.
- Free도 짧은 voice/TTS 경험 제공.
- Free도 주간 reward/media unlock 제공.
- 단, 고비용 image/video는 credit/광고/구독으로 보호.

#### 2. Character/story discovery

Zeta는 수많은 캐릭터/스토리를 탐색하는 재미를 제공한다.

우리 적용:

- 첫 release는 캐릭터 1~2명으로 시작하되, 콘텐츠 discovery는 `date event`, `story episode`, `reward gallery`로 만든다.
- 캐릭터 수를 늘리기보다, 같은 캐릭터와 할 수 있는 이벤트를 늘리는 게 초기에는 안전하다.

#### 3. Pieces류 가상재화

Zeta의 `pieces`처럼 소비 단위가 있는 구조는 AI 비용 보호에 유리하다.

우리 적용:

- `credit`을 image/video/premium voice/regeneration/date premium event에 사용.
- text chat 자체는 너무 빡빡하게 credit화하지 않는다.
- credit ledger는 append-only로 만든다.

### 3.2 Nika/Aurora에서 가져올 점

#### 1. Bond level

Nika의 30-level Bond System은 companion 앱의 핵심 체류 장치다.

우리 적용:

- 처음부터 30단계까지 만들 필요는 없지만, 최소 10~15단계 relationship level은 필요하다.
- 각 level은 대사 tone만 바꾸는 게 아니라 unlock content와 연결되어야 한다.

예:

| Level | Unlock |
|---:|---|
| 1 | 기본 채팅 |
| 2 | 이름/취향 기억 |
| 3 | daily greeting 변화 |
| 4 | 첫 date event |
| 5 | reward image 1 |
| 6 | voice message style 추가 |
| 7 | companion diary |
| 8 | special scenario |
| 9 | premium date |
| 10 | story chapter unlock |

#### 2. Companion diary

Nika는 companion이 관계에 대해 diary를 작성하는 기능을 강조한다.

우리 적용:

- 매일 자동 diary가 아니라, 일정 turn/event 후 `Airi's note`처럼 짧은 기록을 생성.
- 사용자가 볼 수 있는 memory UI와 연결.
- diary는 장기 memory와 reward 사이의 감정적 접착제 역할.

#### 3. Scenario / date event

Nika의 official/community scenarios, Aurora의 dating sim/RPG 요소는 우리 아이디어와 가장 직접적으로 맞다.

우리 적용:

- 첫 release: UGC marketplace 금지.
- 운영자가 만든 official date event 3~5개만 제공.
- rule engine이 결과를 판정하고, LLM은 대사/감정/힌트만 담당.

#### 4. Multimodal

Nika는 text, image, video, voice, live calls를 묶는다.

우리 적용:

- 첫 상용 버전에서 video/live call은 제외.
- text + short voice + TTS + image reward까지가 현실적.
- video는 Premium credit-only async job으로 후순위.

## 4. 우리가 따라 하면 안 되는 것

### 4.1 초반부터 UGC marketplace

UGC scenario marketplace는 매력적이지만 운영 난이도가 높다.

위험:

- 부적절 콘텐츠.
- 저작권.
- 미성년/성인 캐릭터 정책.
- prompt injection.
- moderation 비용.

판단:

- commercial launch 이후 content ops와 moderation이 안정되기 전까지 보류.

### 4.2 캐릭터 수 과다

캐릭터가 많으면 좋아 보이지만, 각 캐릭터의 memory/personality/voice/media를 유지해야 한다.

초기에는 캐릭터 1~2명 + 깊은 관계/이벤트가 낫다.

### 4.3 실시간 video/call 선출시

실시간 call은 매력적이지만 비용/latency/안전 리스크가 크다.

첫 release는:

- text chat
- PTT voice input
- short TTS response
- async image reward

정도가 안전하다.

### 4.4 LLM에게 게임 판정 맡기기

데이트 미니게임의 승패/보상/관계 점수는 LLM이 아니라 rule engine이 판단해야 한다.

LLM 역할:

- 캐릭터 반응.
- 대사.
- 힌트.
- diary.
- memory summary.

Rule engine 역할:

- 성공/실패 판정.
- 점수.
- reward unlock.
- credit 차감/지급.
- cooldown.

## 5. 우리 앱의 벤치마킹 기반 핵심 설계

## 5.1 Core loop

```text
daily login
-> Airi greets user with remembered context
-> chat
-> Airi suggests date event
-> user plays short deterministic mini-game
-> result updates relationship
-> reward/media/diary unlock
-> memory extraction
-> next login reflects changed relationship
```

## 5.2 First commercial release recommendation

추천 범위:

- Mobile app.
- 1 core character: Airi.
- 8~12 relationship levels.
- Text chat.
- Short voice input.
- TTS for selected replies.
- 3 official date events.
- Basic reward gallery.
- Airi diary/note.
- Memory summary.
- Free/Plus/Premium/Credit.
- Rewarded ads.
- Admin ops.

제외:

- UGC marketplace.
- video generation.
- live voice call.
- multi-character world.
- custom character marketplace.

## 5.3 Date event 예시

### Movie talk date

목표:

- 사용자가 영화 취향을 말한다.
- Airi가 반응하고, 선택지 기반 짧은 대화 게임을 진행.

보상:

- 관계 점수.
- diary note.
- 영화관 분위기 reward image.

### Career comfort date

목표:

- 사용자가 커리어 고민을 털어놓는다.
- Airi가 성향별 질문을 던지고, 사용자의 결심을 정리.

보상:

- memory: user wants digital human / AI service career.
- diary note.
- 응원 voice message unlock.

### Weekend plan date

목표:

- 주말 계획을 함께 정한다.

보상:

- daily mission.
- small image reward.
- relationship familiarity 증가.

## 6. 수익구조 반영

벤치마킹 기반 판단:

- Free를 너무 막으면 Zeta류 무료 경험과 경쟁이 안 된다.
- Plus는 광고 제거 + memory + voice/TTS + image credit이 있어야 한다.
- Premium은 priority queue + premium media + larger memory가 있어야 한다.
- Credit은 image/video/regeneration/premium event에 써야 한다.

권장:

- Free: text 충분히, voice/TTS 조금, weekly reward.
- Plus: ad-free, daily voice/TTS 확장, monthly image credit.
- Premium: priority, premium voice/media, custom slot.
- Credit: 고비용 기능 보호.

## 7. 기술 아키텍처 반영

Zeta/Nika류를 따라가려면 PromptMotionLab의 단순 turn 구조만으로는 부족하다.

추가해야 하는 것:

- relationship state service.
- memory service.
- date event rule engine.
- reward unlock service.
- media generation queue.
- credit ledger.
- admin moderation.
- provider quota manager.
- prompt/version manager.

## 8. 출시 우선순위

### Phase 1

- Airi 1명.
- Chat + memory + relationship.
- 3 date events.
- reward gallery.
- Free/Plus/Credit.

### Phase 2

- voice/TTS 고도화.
- 더 많은 date events.
- diary.
- image reward quality 개선.
- admin ops 강화.

### Phase 3

- Premium.
- seasonal event.
- second character.
- creator scenario closed beta.

### Phase 4

- UGC marketplace.
- video.
- live voice call.
- multi-character world.

## 9. 결론

벤치마킹 결과, 우리 아이디어의 방향은 가능성이 있다. 다만 Zeta처럼 캐릭터/스토리 풀로 바로 경쟁하거나 Nika처럼 모든 멀티모달/RPG 기능을 첫 버전에 넣으면 실패 확률이 높다.

현실적인 상용 전략:

> Airi 1명으로 깊게 시작하고, 관계 progression + date event + reward/media + memory loop를 작게 완성한다.

초기 차별점:

- 단순 채팅이 아니라 함께 하는 date mini-game.
- 대화 결과가 관계/보상/기억에 반영.
- 무료에서도 핵심 경험 제공.
- 고비용 기능은 credit으로 보호.

## Sources

- Zeta Google Play listing: https://play.google.com/store/apps/details?id=com.scatterlab.messenger
- Zeta App Store listing: https://apps.apple.com/ca/app/zeta-create-your-own-story/id1619030760
- Nika official site: https://nika.team/en/
- Nika product page: https://nika.team/en/nika/
- Aurora comparison page: https://nika.team/en/compare/aurora-vs-replika/
