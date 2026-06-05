# Shared Activity v1.1 product package plan

작성일: 2026-06-05

이 문서는 `35-Shared-activity-system-spec.md`를 실제 제품 패키지로 내릴 때, v1.1에서 무엇을 넣고 무엇을 미룰지 결정하기 위한 PM 기획안이다.

관점:

- AI companion 앱.
- 연애 시뮬레이션/관계 progression 게임.
- 모바일 상용 서비스.
- Airi 1명으로 시작.
- 사용자는 실제로 Airi를 만날 수 없으므로, 앱 안의 작은 공동 경험이 관계의 증거가 되어야 한다.

기준 문서:

- `06-Commercial-product-PRD-and-core-loop.md`
- `15-First-release-scope-decisions.md`
- `19-Date-event-rule-spec.md`
- `23-Relationship-memory-rule-table.md`
- `34-Companion-mini-game-content-candidate-research.md`
- `35-Shared-activity-system-spec.md`

## 1. PM 결론

v1.1에는 Shared Activity를 두 축으로 넣는다.

1. 감상 공유 1개
   - 추천: `Movie/Music Reflection`.
   - 목적: Airi가 사용자의 취향을 이해하고 다음 대화에서 기억하는 느낌.

2. 간단한 게임 1개
   - 추천: `Quick Connect`.
   - 목적: 매일 짧게 같이 할 수 있는 playful activity.

Ending은 v1.1에 전면 구현하지 않는다.

대신:

- v1.1에서는 `season_progress`와 `shared_moment`만 쌓는다.
- v1.2에서 `Season Recap`으로 노출한다.
- 내부 상태는 `happy/warm/playful/quiet_trust/neutral/bittersweet/unresolved`를 쓸 수 있다.
- 사용자에게 `Bad Ending`이라는 표현은 쓰지 않는다.

## 2. Why this package

감상 공유와 간단한 게임은 역할이 다르다.

| 축 | 사용자 욕구 | 제품 효과 | 위험 |
|---|---|---|---|
| 감상 공유 | 내 취향을 알아주는 AI | memory 품질, 다음 대화 continuity | 너무 문답형이면 지루함 |
| 간단한 게임 | 같이 노는 느낌 | daily return, playful rivalry | 게임만 따로 놀면 관계 루프가 약함 |
| Season Recap | 우리가 쌓은 기록 확인 | 장기 retention, 보상/스토리 카드 | 너무 일찍 넣으면 무거움 |

20년차 PM 관점에서 중요한 것은 "기능 수"가 아니다.

첫 상용 companion에서 필요한 것은:

- 첫날: Airi가 나를 기억한다.
- 3일차: Airi와 같이 한 일이 쌓인다.
- 7일차: 관계가 달라진 느낌이 있다.
- 14일차: 내가 이 앱에서 만든 기록이 보인다.

v1.1은 3일차와 7일차를 보강하는 release다.

## 3. v1.1 user promise

사용자에게 줄 약속:

> Airi와 대화만 하는 것이 아니라, 짧은 감상과 한 판의 게임을 함께 하며 서로의 취향과 장난스러운 순간을 쌓는다.

내부 제품 문장:

```text
Shared Activity v1.1 lets Airi learn what the user likes and how the user plays.
```

사용자 화면 문구 방향:

- "Airi Moment".
- "오늘 같이 할 것".
- "짧게 한 번".
- "우리의 기록".

피해야 할 문구:

- "연애 성공/실패".
- "Bad Ending".
- "관계 회복 필요".
- "호감도 하락".
- "Airi가 실망했다".

## 4. v1.1 activity 1: Movie/Music Reflection

### Goal

사용자의 취향을 memory로 만들고, 다음 대화에서 Airi가 자연스럽게 회상할 수 있는 shared moment를 만든다.

### Why first

- 기존 Movie talk date와 자연스럽게 이어진다.
- LLM 비용이 낮다.
- 게임 엔진/라이선스 리스크가 없다.
- 사용자가 텍스트로 쉽게 참여한다.
- Airi의 companion 감정이 잘 살아난다.

### Format

3분 이하.

```text
Step 1. 오늘 떠오르는 콘텐츠 선택
  movie / music / drama / book / game / not sure

Step 2. 감상 mood 선택
  cozy / exciting / sad / funny / thoughtful

Step 3. 한 줄 감상 입력
  optional free text

Step 4. Airi response
  Airi mirrors the user's taste and asks one light follow-up

Finish.
  shared memory card + relationship delta + optional reward progress
```

### Result model

| result | condition | relationship | memory | reward |
|---|---|---|---|---|
| completed_low | 선택지만 완료 | familiarity +1 | weak preference candidate | note progress +0 |
| completed_mid | 선택지 + 짧은 감상 | familiarity +2, affinity +1 | preference candidate | note progress +1 |
| completed_high | 구체 감상 + Airi follow-up 응답 | familiarity +3, trust +1 | active candidate eligible | shared memory card progress |
| blocked | unsafe/copyright/personal data issue | no gain | none or safety event | none |

### Memory candidates

Allowed:

- preferred genre.
- preferred mood.
- favorite content category.
- disliked mood/category.
- reflection style: deep, casual, emotional, playful.

Disallowed:

- pirated content sharing.
- copyrighted text/lyrics excerpt storage.
- sensitive personal data.
- explicit sexual content.
- third-party private information.

### Airi reaction tone

Early relationship:

```text
그 분위기 좋아하는구나. 오늘은 조용한 쪽으로 기억해둘게.
```

Warm relationship:

```text
전에 말한 취향이랑 이어지는 느낌이 있어. 너는 너무 무겁지 않은 감정선을 좋아하는 쪽 같아.
```

Playful relationship:

```text
이건 좀 네 취향이다. 다음엔 내가 하나 골라와도 돼?
```

Safety:

- Airi must not claim to store memory until memory state is active or eligible.
- Use "기억해둘 수 있어" or "다음에 참고할게" only when backend can create candidate.

## 5. v1.1 activity 2: Quick Connect

### Goal

사용자가 Airi와 "짧게 한 판" 한 느낌을 만들고, 승패보다 playful/shared moment를 relationship에 반영한다.

### Why Quick Connect

- 3~5분.
- 규칙 설명이 쉽다.
- 모바일 UI가 간단하다.
- AI 난이도 조절이 쉽다.
- 도박/현금성 오해가 낮다.
- Connect Four 변형으로 직접 구현 가능하다.

### Format

```text
Board: 6 rows x 7 columns
Goal: connect 4
Mode: user vs Airi
Difficulty: easy / normal
Turn time: soft limit
Result: user_win / airi_win / draw / abandoned
```

v1.1에서는 multiplayer가 아니다. Airi AI와 하는 single-player activity다.

### Result model

| result | relationship | reward | Airi reaction |
|---|---|---|---|
| user_win | affinity +2, familiarity +1 | game note progress +1 | 축하, 장난스러운 인정 |
| airi_win | affinity +1, trust +1 | retry hint | 약한 장난, 사용자를 낮추지 않음 |
| draw | trust +1, familiarity +1 | shared moment progress +1 | 같이 비긴 경험 강조 |
| abandoned | no gain | none | 부담 없는 재개 제안 |
| repeated_loss | trust +1 max/day | coaching hint | 난이도 낮추기 제안 |

### Difficulty rule

| relationship/mood | difficulty suggestion |
|---|---|
| early | easy |
| playful + user_win_streak | normal |
| repeated_loss | easy |
| distant/tired | easy or no game suggestion |
| user explicitly asks challenge | normal |

### Anti-frustration rule

- Airi should not win too aggressively in early relationship.
- On first game, target outcome should be forgiving, but not fake if the user makes legal losing moves.
- If user loses 2 times in a row, offer "easy rematch" or "coaching mode".
- Do not attach premium reward only to winning.

### Anti-farming rule

- relationship gain cap applies.
- reward-bearing finish once per day.
- casual replay can exist with no reward.
- duplicate finish is idempotent.
- abandoned sessions do not grant reward.

## 6. Relationship branches for v1.1

v1.1 should not try to implement a full dating sim branch tree. It should introduce 4 readable branches.

| branch | signal | Airi behavior | unlock hint |
|---|---|---|---|
| warm_growth | reflection + date completion | remembers taste, suggests soft activities | Airi note |
| playful_rivalry | Quick Connect participation | light rivalry, rematch, teasing within limit | game badge |
| quiet_trust | comfort/date/reflection with emotional mood | gentle tone, fewer jokes | comfort note |
| distant_return | absence/abandoned activities | low-pressure return | comeback moment |

Do not expose branch names directly to the user.

User-facing expression:

- "Airi가 네 취향을 조금 더 알게 됐어."
- "오늘은 장난스러운 분위기가 잘 맞았어."
- "무리하지 않는 쪽이 지금은 더 좋아 보여."
- "오랜만이니까 짧게만 해도 괜찮아."

## 7. Season Recap instead of Ending

Ending이 필요한가?

PM 판단:

- v1.1에는 필요 없다.
- v1.2에는 필요하다.
- 단, 이름은 Ending이 아니라 Season Recap이어야 한다.

이유:

- 연애 시뮬레이션 문법상 엔딩은 강한 몰입 장치다.
- 하지만 AI companion 앱에서 직접적인 bad ending은 감정 조작, CS, 환불, 이탈 리스크가 있다.
- 사용자가 원하는 것은 "끝"보다 "우리가 쌓은 기록"이다.

### v1.1 state only

v1.1에서는 아래만 저장한다.

```text
season_progress
activity_counts
shared_moments
dominant_branch
unresolved_signals
last_recap_candidate
```

### v1.2 visible recap

14일 또는 28일 단위로 보여준다.

User-facing examples:

- "이번 시즌의 Airi Moment".
- "우리가 같이 쌓은 기록".
- "Airi가 기억한 너의 취향".
- "다음에 이어갈 순간".

Internal outcome:

| internal | visible title | meaning |
|---|---|---|
| happy | 따뜻하게 가까워진 시간 | balanced growth |
| playful | 장난스럽게 가까워진 시간 | game/rivalry high |
| quiet_trust | 편안하게 쌓인 시간 | trust/comfort high |
| neutral | 가볍게 이어진 시간 | low activity, no issue |
| bittersweet | 잠깐 쉬어간 시간 | absence/unfinished |
| unresolved | 다시 맞춰볼 시간 | repair needed |

Important:

- `unresolved` is not displayed as failure.
- paid reward is not revoked.
- repair activity is suggested gently.

## 8. v1.1 UX placement

Do not create a fifth bottom tab.

Use existing IA:

- Chat: primary recommendation and activity entry.
- Date: activity list and ongoing session.
- Rewards: shared memory card, game badge, note progress.
- Profile: relationship/memory/activity history.

Chat entry examples:

```text
오늘은 짧게 음악 얘기해볼래?
```

```text
한 판만 할래? 오래 안 걸려.
```

Date tab naming:

- If UI needs a broader label, consider `Moments` instead of `Date`.
- Do not use `Games` as top-level label because it narrows the product.

## 9. Reward economy

v1.1 reward should be mostly low-cost.

Default:

- Airi note.
- shared memory card progress.
- game badge.
- relationship feedback.
- basic image reward progress only on milestone.

Avoid:

- image reward per activity.
- voice reward per win.
- credit payout per game.
- random chance reward.

Recommended caps:

| reward | cap |
|---|---|
| relationship gain | existing daily cap |
| reward-bearing Quick Connect | 1/day |
| reflection memory candidate | 2/day |
| shared memory card progress | 3/week |
| basic image reward progress | weekly cap |

## 10. Content roadmap

| release | content | purpose |
|---|---|---|
| v1 | 3 date events | proof of memory/relationship/reward loop |
| v1.1 | Movie/Music Reflection + Quick Connect | taste memory + daily playful activity |
| v1.2 | Season Recap + repair activity | long-term progression |
| v1.3 | Gomoku or Reversi + co-planning follow-up | content variety |
| v1.4 | special event/anniversary activity | monetizable seasonal content |

## 11. PM decisions now

Recommended decisions:

1. UX naming:
   - Use `Airi Moment` in copy.
   - Keep bottom tab as `Date` for v1 if already designed.
   - Consider renaming Date tab to `Moments` only when v1.1 activity count grows.

2. First v1.1 reflection:
   - Start with `Movie/Music Reflection`, not a generic review system.
   - Do not require content upload.

3. First v1.1 game:
   - Start with `Quick Connect`.
   - Implement AI directly.
   - No poker/casino/random payout.

4. Ending:
   - Do not expose Ending in v1.1.
   - Store season progress.
   - Launch visible `Season Recap` in v1.2.

5. Reward:
   - Notes/cards/badges first.
   - Image/voice as milestone.

6. Relationship:
   - No level down.
   - Negative outcomes affect mood/distance/repair only.

## 12. What still needs PM co-design

다음은 사용자와 함께 구상해야 한다.

1. Airi Moment의 실제 화면 이름:
   - "Airi Moment"
   - "오늘의 순간"
   - "같이 하기"
   - "Moments"

2. 감상 공유의 첫 카테고리:
   - 영화 중심.
   - 음악 중심.
   - 영화/음악 통합.

3. Quick Connect의 Airi 말투:
   - 장난을 얼마나 허용할지.
   - 승리했을 때 놀림 강도.
   - 연패 시 코칭 톤.

4. Season Recap의 주기:
   - 14일.
   - 28일.
   - 첫 recap만 7일.

5. 보상 카드의 시각 톤:
   - 감성 diary.
   - 게임 badge.
   - 사진 album.
   - Airi handwritten note.

6. relationship 수치 노출:
   - affinity/trust/familiarity를 숫자로 보여줄지.
   - mood와 level만 보여줄지.
   - 사용자에게 수치를 숨기고 event log만 보여줄지.

## 13. Development implication

v1.1 구현 전에 backend는 다음을 준비해야 한다.

- generic activity template/session/result model 설계.
- current date_event result를 activity history로 mirror하는 adapter.
- ActivityRuleEngine interface.
- ReflectionRuleEngine.
- QuickConnectRuleEngine.
- ActivityRecommendationService.
- season progress accumulator.
- reward cap integration.
- memory candidate integration.

하지만 지금 immediate backend 순서는 바꾸지 않는다.

현재 진행 중인 v1 backend core:

```text
memory activation/delete
reward/media async job
billing webhook
admin minimum API
QA/integration/load smoke
```

이후 v1.1 planning에서 shared activity DB/API를 반영한다.

## 14. PM final judgment

감상 공유와 간단한 게임은 둘 다 넣는 것이 맞다.

단, 둘을 같은 무게로 크게 만들면 안 된다. v1.1은 다음 정도가 적절하다.

- 감상 공유: memory를 만드는 얕고 자주 쓰는 activity.
- Quick Connect: 하루 한 번 짧게 노는 activity.
- Season Recap: 구현하지 않고 데이터만 쌓기.

이렇게 가면 AI companion의 본질을 해치지 않고, 연애 시뮬레이션의 progression 감각을 작게 붙일 수 있다.
