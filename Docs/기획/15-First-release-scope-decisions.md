# First release scope decisions

작성일: 2026-06-03

이 문서는 첫 상용 모바일 release에서 PM이 결정해야 하는 5개 항목에 대한 권장안을 정리한다.

화면 IA와 사용자 여정은 `16-Mobile-user-journey-and-screen-IA.md`를 기준으로 한다.

## 결론 요약

| 항목 | 권장 결정 | 이유 |
|---|---|---|
| Date mini-game | 넣는다. 단, 3개 official event만 | 단순 채팅앱과 차별화되는 핵심 루프 |
| Free TTS/image | 조금 준다 | 너무 막으면 바로 삭제될 가능성 높음 |
| 캐릭터 수 | Airi 1명으로 시작 | 깊이/품질/비용/운영을 먼저 잡아야 함 |
| 수위 | store-safe 최대치: romantic/suggestive까지 | explicit 성인물은 스토어/광고/결제 리스크 큼 |
| 첫 화면 핵심 | Chat 중심 + voice button + reward hint | 진입은 대화, 유지력은 보상/관계로 만든다 |

## 1. Date mini-game을 반드시 넣을지

### 권장

넣는다. 하지만 첫 release에서는 3개 정도의 official date event만 넣는다.

### 이유

단순 AI chat만으로는 Zeta/Character.AI/Nika류와 정면 경쟁이 된다. 우리 차별점은 "AI와 대화한다"가 아니라 **AI와 함께 짧은 데이트형 콘텐츠를 하고, 결과가 관계/보상/기억에 반영된다**는 점이다.

### 첫 release 범위

추천 event:

1. Movie talk date
   - 영화 취향 대화.
   - 영화관/장면/취향 reward.

2. Comfort date
   - 우울함, 피곤함, 커리어 고민.
   - Airi note / voice 응원 reward.

3. Weekend plan date
   - 주말 계획, 산책, 카페, 게임, 영화.
   - daily relationship bonus.

### 구현 원칙

- LLM은 대사/감정/힌트만 담당.
- 결과/점수/보상은 rule engine이 판단.
- reward unlock은 credit/relationship ledger에 기록.

## 2. 무료 사용자에게 TTS/image를 어느 정도 줄지

### 권장

무료에도 반드시 일부 제공한다.

### Free 권장 제공량

| 기능 | Free 권장 |
|---|---|
| Text chat | 30~50 turns/day |
| Voice input | 1 min/day 또는 3~5회/day |
| TTS | 3~5 short replies/day |
| Image reward | 1 basic reward/week |
| Long memory | 3~5개 summary |
| Rewarded ad | voice/image credit 지급 |

### 이유

사용자 입장에서는 "광고도 보는데 음성도 못 듣고, 이미지도 못 보고, 기억도 못 한다"면 바로 삭제할 가능성이 높다.

다만 비용 보호는 필요하다.

- TTS는 짧은 응답만 무료.
- image는 weekly reward 또는 ad credit으로 제한.
- video는 Free에서 제외.
- regeneration은 credit 차감.

## 3. 캐릭터를 Airi 1명으로 시작할지, 2명 이상으로 시작할지

### 권장

Airi 1명으로 시작한다.

### 이유

상용 AI companion은 캐릭터 수보다 캐릭터 깊이가 중요하다.

캐릭터가 늘어나면 함께 늘어나는 것:

- personality prompt
- fewshot
- voice profile
- image style
- memory policy
- relationship script
- date event variation
- safety policy
- QA matrix

첫 release에서 2명 이상으로 시작하면 품질이 얕아질 가능성이 높다.

### 예외

2명으로 시작하려면 다음 조건이 필요하다.

- Airi: warm companion.
- second character: 완전히 다른 market positioning.
- 두 캐릭터 모두 voice/image/personality QA 완료.

그 전에는 Airi 1명 + event 다양화가 낫다.

## 4. 성인/연애 표현 수위를 어디까지 허용할지

### 사용자 의도

가능한 최대 범위까지 허용하고 싶다.

### 냉정한 판단

모바일 스토어에 배포할 앱이면 `최대 수위`는 explicit adult가 아니라 **store-safe romantic/suggestive maximum**으로 잡아야 한다.

권장 수위:

- 허용: 연애 감정, 플러팅, 데이트 분위기, 설렘, 질투, 가벼운 스킨십 암시, 감정적 친밀감.
- 제한: 노골적인 성행위 묘사, 신체 부위 중심 묘사, 누드/반누드 이미지, 성적 행위를 목적으로 한 이미지/영상 생성.
- 금지: 미성년 또는 미성년처럼 보이는 캐릭터의 성적/연애 고수위 표현, non-consensual sexual content, deepfake sexual content.

### 이유

Google Play의 AI-generated content 정책은 AI 생성 앱이 제한 콘텐츠 생성을 방지해야 하며, offensive content 신고 기능을 앱 안에 제공해야 한다고 요구한다. Apple도 objectionable content와 UGC moderation/report/block 체계를 중요하게 본다.

즉, "18+라고 표시하면 다 된다"가 아니다. 특히 AI companion + generated image 조합은 심사 리스크가 크다.

### 제품 정책 제안

#### Store version

- romantic/suggestive.
- no explicit sexual acts.
- no nudity.
- no minor-like character.
- media generation은 moderation.
- report/block/delete 제공.

#### Future adult route

정말 explicit adult를 하고 싶다면 별도 전략이 필요하다.

- 앱스토어 외부 웹 서비스.
- 성인 인증.
- 별도 결제사.
- 광고 수익 포기 가능성.
- 더 강한 moderation/legal 검토.

첫 상용 모바일 release에는 추천하지 않는다.

## 5. 첫 화면 핵심 경험을 chat, voice, image reward 중 무엇으로 둘지

### 권장

첫 화면은 chat 중심으로 간다.

구성:

```text
main chat
-> Airi greeting with memory
-> prominent voice button
-> small relationship status
-> reward/event hint
```

### 이유

- Chat이 가장 비용 예측이 쉽다.
- Voice는 매력적이지만 비용과 latency가 크다.
- Image reward는 retention 장치이지 첫 입력 경험이 아니다.

첫 화면에서 보여줘야 할 것:

- Airi가 기억하고 있다는 느낌.
- 바로 말 걸 수 있는 채팅창.
- 음성 버튼.
- 오늘 할 수 있는 date/reward hint.
- 관계 레벨 변화.

## 최종 권장 scope

첫 상용 모바일 release:

- Airi 1명.
- Chat-first UX.
- 짧은 voice input.
- 제한적 TTS.
- 3 official date events.
- 8~12 relationship levels.
- weekly/basic image reward.
- Airi diary/note.
- Free/Plus/Premium/Credit.
- Rewarded ad.
- Store-safe romantic/suggestive max.
- Explicit adult content는 제외.

## PM decision status

| 질문 | 상태 |
|---|---|
| 첫 release에 date mini-game을 넣을지 | 권장: 넣는다 |
| 무료 TTS/image 제공량 | 권장: 제한적으로 제공 |
| 캐릭터 수 | 권장: Airi 1명 |
| 수위 | 권장: store-safe 최대치 |
| 첫 화면 핵심 | 권장: chat 중심 |

## Development handoff

이 문서의 결정은 다음 개발 기준으로 넘긴다.

- Navigation: Chat, Date, Rewards, Profile 4개 하단 탭.
- First screen: Chat.
- First-run: age gate, login/guest start, AI/privacy disclosure, Airi intro, first chat.
- Core proof: 첫 세션 안에 memory/relationship/reward 중 최소 1개 이상 피드백.
- Date events: Movie talk date, Comfort date, Weekend plan date.
- Rule ownership: date result, reward unlock, relationship delta는 rule engine/ledger가 담당.
- AI ownership: Airi reply, emotion, hint, diary, memory summary.
- Safety: explicit adult, minor-like romance, nude/sexual image generation 금지.
- Cost: voice/TTS/image는 quota, queue, credit, provider usage logging을 통과해야 한다.

Date event의 구체 rule/score/reward 기준은 `19-Date-event-rule-spec.md`를 따른다.
Airi 캐릭터 기준은 `22-Airi-character-profile-v1.md`, relationship/memory 기준은 `23-Relationship-memory-rule-table.md`를 따른다.

## Sources

- Google Play AI-Generated Content policy: https://support.google.com/googleplay/android-developer/answer/13985936
- Google Play AI-generated content overview: https://support.google.com/googleplay/android-developer/answer/14094294
- Apple App Store Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
