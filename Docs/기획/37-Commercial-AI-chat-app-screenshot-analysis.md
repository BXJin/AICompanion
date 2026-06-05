# Commercial AI chat app screenshot analysis

작성일: 2026-06-05

분석 대상:

- `Docs/상용앱/zeta`
- `Docs/상용앱/대파`
- `Docs/상용앱/크랙`

목적:

상용 AI chat 앱 스크린샷에서 반복되는 제품 구조를 추출하고, AICompanion 기획에 반영할 항목과 제외할 항목을 판단한다.

## 결론

상용 AI chat 앱은 대부분 단순 채팅이 아니라 **roleplaying discovery + scenario loop + generated media reward** 구조를 갖고 있다.

즉, 사용자가 계속 들어오게 만드는 장치는 다음이다.

1. 수많은 캐릭터 또는 상황을 고르는 discovery.
2. 사용자가 대화할 명분을 주는 roleplay/scenario.
3. 캐릭터가 먼저 보내는 메시지.
4. 대화 중 이미지, voice, storyshot 같은 즉시 보상.
5. 대화 후 요약, 리포트, memory.
6. 추천 답변, 선택지, 한 줄 입력으로 진입 장벽을 낮추는 UX.

AICompanion의 기존 방향인 **Chat -> memory -> relationship -> date/shared activity -> reward -> next recall**은 상용앱 패턴과 맞다.

다만 그대로 따라가면 안 되는 지점도 있다.

- 수백만 캐릭터 marketplace는 v1에 맞지 않는다.
- "무제한 대화" 카피는 AI 비용 구조와 충돌한다.
- 선정적/자극적 roleplay는 store policy, safety, 캐릭터 신뢰를 무너뜨릴 수 있다.
- creator monetization은 retention 검증 전에는 운영 복잡도가 크다.

따라서 우리 기획에 넣을 핵심은 **roleplay 자체**가 아니라 **Airi와 함께할 대화 명분을 만드는 scenario/activity packaging**이다.

## 1. Zeta 분석

스크린샷 근거:

- 추천, 랭킹, 퀴즈, 트렌드, 베스트, 신작 탭.
- 일상/로맨스, 집착/피폐, BL, 학원물 등 장르 태그.
- "400만 개의 캐릭터"를 전면 카피로 사용.
- "밤새도록 멈출 수 없는 채팅".
- "15초 만에 우리 대화가 눈앞에"라는 대화 기반 일러스트 생성.
- "눈 뜨면 와 있는 선톡".
- "내 생일까지 기억하는 캐릭터".
- "AI 답변 추천으로 끊김 없는 채팅".

### 제품 구조

Zeta는 캐릭터 marketplace와 roleplay feed가 중심이다.

| 요소 | 관찰 |
|---|---|
| Discovery | 추천/랭킹/퀴즈/트렌드/장르 탭 |
| 캐릭터 수 | 400만 캐릭터 강조 |
| Hook | 소꿉친구, 재벌 3세, BL 등 강한 취향 태그 |
| Proactive message | 캐릭터 선톡 |
| Memory | 생일/추억 기억 강조 |
| Generated media | 대화가 일러스트가 되는 순간 |
| Input support | AI 답변 추천 |

### 우리 기획에 반영할 점

1. **Airi 선톡 / daily greeting 강화**
   - 이미 `bootstrap.daily.greeting`과 daily return journey가 있다.
   - 더 구체적으로 "어제 대화/오늘 date hint/기억 1개 기반 선톡"을 설계할 가치가 있다.

2. **추천 답변 또는 선택지**
   - date event에서 선택지 중심 구조는 이미 있다.
   - Chat에서도 첫날/막힘 상태에 한해 `reply_suggestions`를 제공하면 진입 장벽을 낮출 수 있다.
   - 단, 사용자가 대화한다는 느낌을 해치지 않도록 항상 노출하지 않는다.

3. **대화 기반 이미지 보상**
   - `reward_events`와 media async job 방향과 맞다.
   - Zeta처럼 "15초"를 약속하지 말고, 우리 기획 기준인 async/pending/p95 120초 정책을 유지한다.

4. **장르/상황 태그를 캐릭터가 아니라 activity에 적용**
   - v1은 Airi 단일 캐릭터라 marketplace discovery를 복제하면 안 된다.
   - 대신 Airi Moment / Date / Shared Activity에 mood tag를 붙인다.
   - 예: comfort, playful, movie, weekend, quiet, challenge.

### 제외할 점

- 400만 캐릭터 규모 경쟁.
- BL/집착/피폐 중심 자극 태그를 Airi v1에 전면 도입.
- "멈출 수 없는", "무제한"류 카피.
- birthday/memory를 과도하게 감정 의존으로 포장하는 방식.

### Bloomy-style daily persona note

블루미류 앱은 "사람처럼 기억하고 공감하는 AI 친구", "셀카 보내주는 AI", "친구/연인/멘토" 감성을 강하게 사용한다.

이 방향은 우리 제품에도 일부 필요하다.

다만 AICompanion은 다음처럼 정리한다.

```text
Airi는 일상형 AI companion이다.
기본 채팅에서도 카페, 회사, 친구, 산책, 점심 같은 작은 일상 연출을 자연스럽게 말할 수 있다.
단, 실제 식별 가능한 회사명/실명/장소/연락처/사용자 개인정보/실제 촬영물/AI 정체성 부정은 금지한다.
```

허용 예:

```text
오늘 카페 갔다가 네 생각났어.
오늘 회사에서 팀장이 나한테 진짜 심하게 뭐라고 했어.
친구한테 네 얘기했더니 귀엽대.
```

경계 질문을 받으면:

```text
그건 비밀이야.
장소까지는 안 알려줄래.
실제 사진은 아니고, 오늘 분위기로 만든 Airi 셀카야.
```

단, 자해/불법/의료/법률/금융/개인정보 유출 같은 안전 이슈는 playful deflection이 아니라 safety route로 처리한다.

## 2. 대파 분석

스크린샷 근거:

- "실전 같은 연애 리허설, 상황별 대화 미션".
- "소개팅부터 썸, 고백까지".
- "페르소나 트레이닝".
- StoryShot으로 대화 순간을 이미지로 보관.
- 캐릭터 목소리 설정.
- 대화 리포트와 추천.
- 놀이터: 운세, 한소절송, 쓱싹그림, 칭찬받기, 편들어줘.

### 제품 구조

대파는 캐릭터 소비보다 **훈련/리허설/피드백**이 강하다.

| 요소 | 관찰 |
|---|---|
| Positioning | AI 연애 리허설 |
| Scenario | 소개팅, 썸, 고백, 갈등 조율 |
| Mission | 상황별 대화 미션 |
| Feedback | 실시간 코칭, 대화 리포트 |
| Media | StoryShot |
| Voice | 캐릭터 목소리 설정 |
| Utility mini features | 운세, 노래, 그림, 칭찬, 편들기 |

### 우리 기획에 반영할 점

1. **Date result report**
   - 대파의 대화 리포트는 우리 date event result screen에 잘 맞는다.
   - 단순히 "success/neutral"을 보여주는 대신, 왜 관계가 올랐고 어떤 memory 후보가 생겼는지 요약한다.

   예:

   ```text
   Result: warm success
   Relationship: trust +2, familiarity +1
   Airi noticed: quiet movie preference
   Next: movie reflection activity unlocked
   ```

2. **Mission-based activity copy**
   - "연애 리허설"은 우리 제품 톤과 다르다.
   - 하지만 "오늘의 Airi Moment", "짧은 대화 미션", "함께 정하기" 같은 구조는 쓸 수 있다.

3. **StoryShot을 Reward/Memory card로 흡수**
   - 대화 순간 이미지 저장은 우리 `reward gallery`와 `shared memory card` 방향에 맞다.
   - 다만 generated media moderation과 credit/ledger 정책을 반드시 연결한다.

4. **대화 후 추천**
   - "다음 상대 추천" 대신 "다음 activity 추천"이 맞다.
   - Airi 단일 캐릭터를 유지하면서 콘텐츠 반복성을 만들 수 있다.

5. **놀이터형 low-cost 기능**
   - 칭찬받기, 편들어줘 같은 기능은 비용이 낮고 재방문 hook이 될 수 있다.
   - 하지만 무분별하게 넣으면 앱 정체성이 흐려진다.
   - v1.1 Shared Activity에서 low-cost daily activity로 검토한다.

### 제외할 점

- 연애 코칭/훈련을 제품의 중심 정체성으로 두는 것.
- "센스 평가"가 사용자를 과하게 평가/판정하는 느낌.
- 운세 등 AI Companion core loop와 약한 기능을 v1에 추가.
- 캐릭터 voice 선택을 너무 넓게 열어 Airi 일관성을 깨는 것.

## 3. 크랙 분석

스크린샷 근거:

- "이 세계를 찢는 단 한 줄, 즉흥 서사 플레이".
- 시뮬레이션, 로맨스, 1:1 롤플레잉, SF/판타지 등 장르 태그.
- "최애랑 친구처럼 무제한 대화".
- "5분이면 끝, 누구나 AI 콘텐츠 작가".
- 캐릭터 만들기: 프로필, 캐릭터 설정, 서사 설정.
- 크랙 오리지널 혜택, 콘텐츠 구매금, 크리에이터 정산 비율.
- 요약 메모리.
- AI 파티챗.

### 제품 구조

크랙은 companion보다는 **roleplay story platform + creator economy**에 가깝다.

| 요소 | 관찰 |
|---|---|
| Hook | 즉흥 서사 플레이 |
| Discovery | 장르/인기/로맨스/SF/판타지 |
| Creation | 누구나 AI 콘텐츠 작가 |
| Economy | 콘텐츠 구매금, 크리에이터 정산 |
| Memory | 요약 메모리 |
| Social | AI 파티챗 |

### 우리 기획에 반영할 점

1. **Scenario template authoring 개념**
   - v1에서는 운영자가 date/shared activity template을 관리한다.
   - v1.2 이후 admin template editor 또는 content ops flow로 확장 가능하다.
   - 사용자 UGC는 retention, safety, moderation 데이터가 쌓인 뒤 검토한다.

2. **요약 메모리**
   - 우리 memory summary 정책과 맞다.
   - 원문 전체를 넣는 대신 summary와 source metadata를 분리하는 기존 방향을 유지한다.

3. **Party chat은 장기 후보**
   - 여러 AI/친구와 함께하는 파티챗은 콘텐츠적으로 강하다.
   - 하지만 realtime, moderation, multi-agent orchestration, 비용이 커서 v1/v1.1에는 맞지 않는다.
   - v2+ 후보로만 둔다.

4. **한 줄 입력으로 장면 전개**
   - date/shared activity에서 사용자의 짧은 자유 입력을 받아 Airi reaction과 memory candidate로 쓰는 방향과 맞다.
   - 단, result는 rule engine이 결정해야 한다.

### 제외할 점

- creator economy를 v1에 포함.
- 사용자 제작 캐릭터 marketplace.
- "무제한 대화" 카피.
- 강한 남성/여성 인기, 로맨스 자극 태그를 전면에 내세우는 discovery.
- 콘텐츠 구매금/정산 구조를 core loop 검증 전에 도입.

## 4. 세 앱 공통 패턴

| 패턴 | 상용앱에서의 역할 | AICompanion 적용 판단 |
|---|---|---|
| 장르/상황 태그 | 캐릭터 discovery 강화 | 캐릭터가 아니라 activity tag로 적용 |
| 선톡 | 재방문 hook | daily greeting/proactive Airi message로 적용 |
| 추천 답변 | 대화 지속성 강화 | onboarding/막힘 상태에 제한 적용 |
| 대화 기반 이미지 | 보상/몰입 | reward/media async job으로 적용 |
| 요약 memory | 장기 맥락 | candidate/active/delete lifecycle 유지 |
| 대화 리포트 | 학습/성취감 | date/shared activity result report로 적용 |
| 미션/리허설 | 행동 명분 제공 | Airi Moment/activity mission으로 적용 |
| 캐릭터 marketplace | 콘텐츠 양 확장 | v1 제외 |
| UGC/creator economy | 공급 확장/수익화 | v2+ 후보 |
| 파티챗 | social novelty | v2+ 후보 |
| 무제한 대화 | 마케팅 hook | 제외 |

## 5. 우리 기획에 추가할 구체 항목

### 5.1 Airi proactive message policy

목적:

- 매일 다시 들어올 이유를 만든다.
- 단순 push spam이 아니라 memory/relationship/activity 기반 메시지로 만든다.

초안:

| Trigger | Example | Cap |
|---|---|---:|
| first day after onboarding | 첫 대화 이어가기 | 1/day |
| yesterday memory exists | 어제 말한 취향 회상 | 1/day |
| date event available | 오늘 가능한 Airi Moment 제안 | 1/day |
| reward pending/unlocked | 보상 확인 안내 | event-based |
| absence 3+ days | 부담 없는 복귀 인사 | 1/3 days |

주의:

- 죄책감 유발 copy 금지.
- 미성년/restricted mode에서는 romantic/suggestive 선톡 제한.
- push notification과 in-app greeting을 분리한다.

### 5.2 Reply suggestion policy

목적:

- 첫날 사용자가 대화를 시작하지 못하는 문제를 줄인다.
- roleplay/date activity에서 선택지를 제공해 QA와 safety를 높인다.

적용:

- onboarding 첫 대화.
- date event step.
- provider degraded 후 fallback.
- 사용자가 30초 이상 입력하지 않는 경우.

제외:

- 모든 turn에 자동 추천 답변을 상시 노출.
- 사용자가 말할 내용을 AI가 과하게 대신 작성.

### 5.3 Date/activity result report

목적:

- 대화가 relationship/memory/reward로 이어졌다는 증거를 보여준다.
- 대파의 대화 리포트 장점을 companion core loop에 맞게 흡수한다.

필드:

```text
result_band
airi_reaction
relationship_delta
memory_candidate_summary
reward_progress
next_recommended_activity
```

UI:

- Date result 화면에서 1차 노출.
- Profile > Relationship recent events에서 축약 노출.
- 너무 평가받는 느낌을 줄 수 있으므로 "점수표"보다 "Airi가 기억한 순간" 중심으로 표현한다.

### 5.4 StoryShot -> Shared Memory Card

목적:

- 대화/활동 결과를 보상 갤러리와 memory에 연결한다.

정책:

- generated image는 moderation pass 전까지 공개하지 않는다.
- Free는 weekly/basic cap을 따른다.
- 실패/거절/환불은 ledger와 job status로 추적한다.
- card는 원문 대화 전체가 아니라 summary 기반으로 생성한다.

### 5.5 Activity tagging

v1의 Date와 v1.1 Shared Activity에 다음 tag를 붙인다.

| Tag | 사용처 |
|---|---|
| cozy | Movie talk, comfort |
| playful | Quick Connect |
| reflection | Movie/Music Reflection |
| planning | Weekend plan |
| repair | unresolved/absence recovery |
| reward | reward progress activity |
| low_cost | text-only daily activity |

효과:

- Zeta/Crack식 장르 discovery의 장점만 가져온다.
- Airi 단일 캐릭터 구조를 유지한다.
- 추천/분석/retention 실험 단위가 생긴다.

## 6. 기존 문서에 반영할 위치

| 반영 항목 | 기존 문서 |
|---|---|
| proactive message policy | `16-Mobile-user-journey-and-screen-IA.md`, `17-Mobile-API-contract.md` |
| reply suggestions | `16`, `17`, `25-OpenAPI-Pydantic-schema-plan.md` |
| date/activity result report | `19-Date-event-rule-spec.md`, `31-Mobile-admin-wireframe-design-system-spec.md` |
| StoryShot -> Shared Memory Card | `23-Relationship-memory-rule-table.md`, `35-Shared-activity-system-spec.md`, `36-Shared-activity-v1-1-product-package-plan.md` |
| activity tags | `35`, `36` |
| admin content template editor later | `21-Admin-minimum-screen-spec.md`, `35` |

## 7. PM 판단

우리 앱에 필요한 것은 롤플레잉 앱을 그대로 따라가는 것이 아니다.

상용 앱들이 roleplaying에 치우친 이유는 다음이다.

- 캐릭터/상황이 많을수록 첫 클릭률이 올라간다.
- 강한 설정은 사용자가 첫 문장을 쓰기 쉽게 만든다.
- 대화가 곧 이미지/보상으로 이어지면 재방문 이유가 생긴다.
- memory와 선톡은 "나를 기억한다"는 착각이 아니라 체감 경험을 만든다.

하지만 AICompanion은 Airi 단일 캐릭터와 관계 누적이 핵심이다.

따라서 반영 방향은 다음이다.

```text
캐릭터 marketplace가 아니라 Airi activity packaging.
무제한 대화가 아니라 quota와 cost가 보이는 지속 가능한 대화.
자극적 roleplay가 아니라 store-safe daily persona와 shared activity.
UGC creator economy가 아니라 운영자가 검증한 template.
일회성 이미지가 아니라 relationship/memory/reward에 연결된 shared memory card.
```

## 8. Next planning task

다음에 기존 기획에 실제로 반영한다면 우선순위는 다음이다.

1. `16`에 proactive Airi message와 reply suggestion 상태 추가.
2. `19`에 date result report 필드 추가.
3. `35/36`에 activity tag와 Shared Memory Card 개념 추가.
4. `17/25`에 `replySuggestions`, `resultReport`, `activityTags` response schema 추가.
5. `21/31`에 admin/content ops에서 template과 prompt version을 보는 optional flow 추가.

v1 backend 구현 순서를 흔들 정도의 변경은 아니다. 지금은 core loop 구현을 계속하고, 위 항목은 v1.1 planning 보강으로 넣는 것이 맞다.
