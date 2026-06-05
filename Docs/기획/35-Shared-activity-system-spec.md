# Shared activity system spec

작성일: 2026-06-04

이 문서는 AI Companion에서 Airi와 사용자가 "실제로 만날 수 없는 한계"를 앱 안의 공동 경험으로 보완하기 위한 Shared Activity 기획 기준이다.

기준 문서:

- `06-Commercial-product-PRD-and-core-loop.md`
- `15-First-release-scope-decisions.md`
- `16-Mobile-user-journey-and-screen-IA.md`
- `19-Date-event-rule-spec.md`
- `23-Relationship-memory-rule-table.md`
- `34-Companion-mini-game-content-candidate-research.md`

## 1. 결론

제품의 장기 확장 방향은 "AI chat + mini-game"이 아니라 **AI와 함께한 온라인 공동 경험이 관계, 기억, 보상, 엔딩으로 누적되는 앱**이어야 한다.

Shared Activity는 다음을 모두 포함하는 상위 개념이다.

- date event.
- mini-game.
- movie/music/book impression sharing.
- preference quiz.
- co-planning.
- comfort routine.
- daily challenge.
- story/season event.

첫 release에서는 기존 3개 date event가 Shared Activity의 v1 proof가 된다.

v1.1 이후에는 보드게임 1개를 바로 추가하기보다 Shared Activity framework를 먼저 잡고, 그 위에 mini-game, 감상 공유, 계획 세우기, season arc를 순차 확장한다.

## 2. Product principle

나쁜 방향:

```text
AI chat app
-> separate mini-game menu
-> user wins/loses
-> small reward
```

이 구조는 흔한 채팅앱에 게임을 붙인 형태가 된다.

좋은 방향:

```text
AI chat
-> Airi suggests an activity based on relationship/memory/mood
-> user and Airi complete a shared activity
-> deterministic result is recorded
-> Airi reacts emotionally within policy
-> relationship/memory/reward/season state changes
-> next chat recalls the shared moment
```

핵심은 게임 자체가 아니라 **같이 한 경험의 연속성**이다.

## 3. Activity taxonomy

| type | example | primary value | rule owner |
|---|---|---|---|
| emotional_date | Movie talk, Comfort, Weekend plan | 첫날 관계/기억 체감 | DateEventRuleEngine |
| board_game | Quick Connect, Gomoku, Reversi | 반복 접속, 승패 반응, playful branch | GameRuleEngine |
| media_reflection | movie/music/book impression | 취향 memory, 다음 추천, diary | ReflectionRuleEngine |
| co_planning | weekend plan, tiny goal, study/work session | 약속 memory, continuity | PlanningRuleEngine |
| comfort_routine | mood check, short breathing, encouragement | trust, safety-safe care | ComfortRuleEngine |
| preference_quiz | this-or-that, taste test | familiarity, personalization | QuizRuleEngine |
| season_story | anniversary, first month recap | ending, reward collection | SeasonArcRuleEngine |

v1 scope:

- emotional_date 3개만 구현.

v1.1 scope candidate:

- board_game 1개.
- media_reflection 1개.
- shared activity API/model framework.

v1.2+ scope candidate:

- season_story.
- repair activity.
- special variants.

## 4. Shared activity core loop

```text
eligibility check
-> recommendation
-> start
-> guided steps or moves
-> deterministic finish
-> relationship event
-> reward event/progress
-> memory candidate
-> Airi reaction
-> next-session recall
```

Each activity must produce at least two of:

- relationship delta.
- memory candidate.
- reward progress/unlock.
- diary/note.
- season progress.

If an activity only produces "fun" but leaves no memory/reward/relationship trail, it should not be prioritized.

## 5. Entry and recommendation rules

Airi should not randomly throw activities at the user. The recommendation should use current context.

Inputs:

- relationship level.
- affinity/trust/familiarity.
- mood.
- recent memory.
- last activity type.
- cooldown/quota.
- plan/free/premium eligibility.
- safety/restricted mode.

Recommendation examples:

| condition | recommended activity | reason |
|---|---|---|
| first day, no memory | Movie talk | safe preference memory 생성 |
| user sounds tired | Comfort routine | 승패형 게임보다 trust 루프 우선 |
| mood=playful, affinity high | Quick Connect/Gomoku | playful rivalry branch 강화 |
| last movie preference exists | Media reflection | memory continuity 강화 |
| weekend plan memory exists | Co-planning follow-up | 약속 회수 |
| distance high | Low-pressure comeback activity | guilt 없이 복귀 |
| repeated loss | coaching/revenge match | 관계 손상 없이 재도전 |

## 6. Relationship integration

Shared Activity는 호감도를 단순히 올리는 장치가 아니다. 어떤 활동을 어떻게 했는지에 따라 축이 다르게 오른다.

| behavior | affinity | trust | familiarity | mood | memory |
|---|---:|---:|---:|---|---|
| finishes playful game | +2 | 0 | +1 | playful | game moment |
| accepts Airi comfort | +1 | +3 | 0 | concerned->warm | comfort style |
| shares movie/music taste | +1 | 0 | +3 | warm | preference |
| keeps small promise | +1 | +2 | +2 | warm | promise completed |
| forfeits without issue | 0 | 0 | 0 | neutral | none |
| returns after absence | +1 | +1 | 0 | warm | comeback moment |
| harsh/unsafe input | 0 | 0 | 0 | concerned | safety event only |

Rules:

- first release and v1.1 do not decrease relationship_level.
- negative experiences affect mood/distance/repair need, not paid entitlement.
- relationship gain cap still applies.
- LLM reaction cannot modify relationship delta.

## 7. Reward and penalty design

Reward should represent "we did something together", not "you farmed a prize".

Reward types:

- Airi note.
- story card.
- shared memory card.
- basic image progress.
- short voice message.
- game badge.
- season progress.
- premium preview.

Penalty types allowed:

- missed bonus.
- cooldown.
- no relationship gain.
- lower reward progress.
- mood becomes neutral/tired/concerned.
- repair activity opens.

Penalty types not allowed:

- paid credit loss from losing.
- purchased reward removal.
- relationship level downgrade in v1/v1.1.
- guilt/manipulation copy.
- blocking core chat because of game loss.

## 8. Activity result bands

Common result bands:

| result | meaning | output |
|---|---|---|
| completed_low | finished with low score/loss | small note or retry hint |
| completed_mid | normal finish/draw | relationship + memory/progress |
| completed_high | strong finish/win/good sharing | relationship + reward progress |
| abandoned | user quit or expired | no reward, gentle resume |
| blocked | safety/policy issue | safety route, no normal reward |
| duplicate | repeated idempotency call | replay previous result |

Important:

- "bad result" and "bad ending" are not the same.
- One lost game should never become bad ending.
- Bad ending is a season-level outcome after repeated unresolved signals.

## 9. Season and ending model

Shared Activities should roll up into season arcs.

Season length:

- beta: 14 days.
- commercial default: 28 days.

Season state:

```text
season_id
user_id
character_id
started_at
ends_at
activity_counts_by_type
relationship_score_start
relationship_score_current
positive_moments
unresolved_moments
repair_score
ending_status
```

Ending types:

| ending | condition | user experience |
|---|---|---|
| happy | balanced relationship growth, 3+ activity types, low unresolved events | story card, note, image/voice progress |
| warm | steady chat/activity but low variety | recap note, next activity suggestion |
| playful | game participation high, affinity high | rivalry badge, playful voice |
| quiet_trust | comfort/planning high, trust high | soft note, promise card |
| neutral | low activity but no negative signal | simple recap, easy next step |
| bittersweet | absence or unfinished promises | comeback note, no guilt |
| unresolved | repeated harsh/safety/broken promise/exploit signals | repair activity, reward limit |

Bad ending in this product should be named internally as `unresolved`, not marketed as "bad ending".

Reason:

- companion 앱에서 노골적인 bad ending은 감정 조작처럼 보일 수 있다.
- 사용자는 언제든 회복 경로가 있어야 한다.
- 상용 결제/보상과 bad ending을 연결하면 CS와 환불 리스크가 커진다.

## 10. Repair activity

Repair is required if the product has bad/unresolved endings.

Repair activity examples:

- "짧게 다시 맞춰보기": Airi가 사용자의 선호를 다시 묻는다.
- "부담 없는 한 판": reward 없는 easy game.
- "약속 다시 정하기": missed promise를 작은 계획으로 재설정.
- "톤 다시 고르기": 사용자가 원하는 Airi 톤을 재선택.

Repair output:

- distance -1 to -3.
- mood neutral->warm.
- small note.
- no premium reward.
- no guilt copy.

## 11. Implementation direction

Do not create a separate system for each content type.

Recommended model:

```text
activity_templates
activity_sessions
activity_steps
activity_moves
activity_results
activity_recommendations
season_arcs
season_moments
```

Existing date event tables can remain for v1. In v1.1, either:

1. keep date event tables and add shared activity tables, then migrate future activities only.
2. generalize date event tables into activity tables with compatibility views/adapters.

Recommendation:

- v1: keep current date event implementation.
- v1.1: add shared activity tables/services and wrap existing date event outputs into activity history.
- avoid risky migration until mobile/retention data proves the content loop.

Service boundary:

- ActivityRecommendationService.
- ActivityEligibilityService.
- ActivityRuleEngine interface.
- ActivitySessionService.
- ActivityResultService.
- ActivityRewardService.
- ActivityMemoryService.
- SeasonArcService.
- AiriActivityReactionService.

Route rule:

- mobile routes expose shared activity UX.
- internal/admin routes manage templates and analytics.
- provider routes do not own game/result logic.

## 12. Analytics

Shared Activity must be measured as product core, not as optional entertainment.

Events:

- activity_recommended.
- activity_card_viewed.
- activity_started.
- activity_step_completed.
- activity_finished.
- activity_abandoned.
- activity_reward_viewed.
- activity_memory_created.
- next_chat_recalled_activity.
- season_ending_unlocked.
- repair_activity_started/completed.

Key metrics:

- activity start rate from chat hint.
- completion rate by type.
- next-day return after activity.
- reward view rate.
- memory recall satisfaction signal.
- D7 retention by first activity type.
- paid conversion after reward cap/premium preview.
- unresolved ending rate.
- repair completion rate.

## 13. Safety and policy

Shared Activity must keep the same safety boundary as chat.

Rules:

- gambling-like content is excluded from launch scope.
- no real-money prize, cashable item, or chance-based reward.
- underage/restricted mode blocks romantic/suggestive rewards.
- comfort activity must not become therapy/medical advice.
- media reflection must not require copyrighted media upload.
- Airi should not pressure users for absence, loss, or unfinished promises.

## 14. PM decisions needed

`36-Shared-activity-v1-1-product-package-plan.md`에서 v1.1 권장 패키지를 다음으로 정리했다.

- Movie/Music Reflection 1개.
- Quick Connect 1개.
- Season Recap은 v1.2 visible feature로 지연하고 v1.1에서는 progress만 저장.
- 사용자에게 `Bad Ending`은 노출하지 않고 내부 `unresolved`와 repair activity로 처리.

To continue planning with PM, the next decisions are:

1. Shared Activity brand name:
   - "Date", "Activity", "Moment", "Airi Moment", "Together" 중 어떤 UX naming을 쓸지.

2. First v1.1 activity:
   - Quick Connect.
   - Gomoku.
   - Reversi.
   - Movie/music reflection.

3. Relationship tone:
   - playful rivalry를 얼마나 강하게 둘지.
   - comfort/trust 루프를 더 앞에 둘지.

4. Ending visibility:
   - season ending을 사용자가 명시적으로 보는지.
   - 내부 상태로만 쓰고 reward card로 우회할지.

5. Repair visibility:
   - unresolved 상태를 직접 보여줄지.
   - "다시 맞춰보기" 같은 부드러운 활동으로만 노출할지.

6. Reward economy:
   - activity 보상이 image/voice 중심인지.
   - note/story card 중심인지.
   - game badge를 쓸지.

7. Content ops:
   - 운영자가 activity template을 추가/수정할 수 있어야 하는지.
   - v1.1에서 admin template editor까지 필요한지.

## 15. Development implication

현재 backend 구현 순서는 유지한다.

Immediate:

- memory activation/delete.
- reward/media async job.
- billing/admin/QA.

Then:

- shared activity framework planning to API/DB.
- activity recommendation service.
- first v1.1 activity rule engine.
- season arc service.

PM 판단:

Shared Activity는 제품 방향으로 맞다. 다만 v1 개발 중에 보드게임 구현까지 당기면 core loop가 늦어진다. 지금은 문서와 데이터 모델 방향을 잡고, v1의 date event가 shared activity proof로 작동하는지 먼저 측정하는 게 맞다.
