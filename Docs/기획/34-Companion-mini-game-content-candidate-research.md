# Companion mini-game content candidate research

작성일: 2026-06-04

이 문서는 `35-Shared-activity-system-spec.md`의 하위 연구 문서로, AI Companion의 date event 이후 확장할 2인 보드게임/미니게임 콘텐츠, 보상/패널티, 관계 분기, 엔딩 구조를 정리한다.

기준 문서:

- `06-Commercial-product-PRD-and-core-loop.md`
- `15-First-release-scope-decisions.md`
- `16-Mobile-user-journey-and-screen-IA.md`
- `19-Date-event-rule-spec.md`
- `23-Relationship-memory-rule-table.md`
- `35-Shared-activity-system-spec.md`

## 1. 결론

현재 기획은 첫 release의 3개 official date event, deterministic result, relationship delta, reward event까지는 잘 잡혀 있다.

하지만 사용자가 말한 체스, 오목, 루미큐브류, 포커류 같은 "실제 보드게임 콘텐츠"와 승패별 반응, 장기 relationship branch, happy/bad ending은 아직 상세 기획으로 충분히 표현되어 있지 않다.

따라서 상용 v1/v1.1의 판단은 다음이 맞다.

1. 첫 release에는 기존 3개 date event를 유지한다.
2. 보드게임은 v1.1 이후 Shared Activity의 "Companion mini-game pack"으로 분리한다.
3. 포커/카지노형 게임은 store policy와 gambling 오해 리스크 때문에 제외한다.
4. 패널티는 paid credit 차감이나 관계 레벨 하락이 아니라 mood, cooldown, missed bonus, repair event 중심으로 설계한다.
5. ending은 영구 실패가 아니라 season arc outcome으로 만든다. 사용자가 언제든 repair path로 회복할 수 있어야 한다.

## 2. 현재 문서의 부족한 점

Covered:

- 3개 date event: Movie talk, Comfort, Weekend plan.
- result band: failed, neutral, success.
- reward type: note, image, voice, relationship bonus.
- relationship state: affinity, trust, familiarity, mood, distance.
- rule engine이 결과/보상/관계 변경을 결정한다는 원칙.

Missing:

- 실제 2인 보드게임 후보와 우선순위.
- 게임별 AI 난이도, 라이선스, 모바일 UX, store policy risk.
- 승/패/무/기권/재도전별 Airi 반응.
- 관계 상태에 따른 게임 open condition.
- bad ending, happy ending, neutral ending, repair ending 같은 장기 콘텐츠 구조.
- 반복 플레이 abuse 방지와 reward farming 방지.
- 게임 결과가 memory, diary, reward gallery, relationship event에 어떻게 누적되는지의 상세 규칙.

## 3. 콘텐츠 축

상용 앱의 메인 콘텐츠는 "AI chat"만이 아니다.

```text
daily chat
-> date event or mini-game invitation
-> deterministic result
-> Airi reaction
-> relationship/memory/reward update
-> next session continuity
```

콘텐츠 축은 3개로 나눈다.

| 축 | 목적 | release |
|---|---|---|
| Emotional date event | 첫날 memory/relationship/reward 체감 | v1 |
| Deterministic mini-game | 매일 다시 들어올 이유와 가벼운 승패 경험 | v1.1 |
| Relationship season arc | 장기 retention, ending, repair, story card | v1.2+ |

## 4. 보드게임 후보 평가

평가 기준:

- 2명이 짧게 할 수 있는가.
- AI 상대 구현이 현실적인가.
- 오픈소스 엔진/프레임워크를 상용 앱에서 쓸 수 있는가.
- 모바일 UX가 복잡하지 않은가.
- 도박/현금성 보상으로 오해될 가능성이 낮은가.
- Airi 반응과 relationship rule에 연결하기 쉬운가.

| 후보 | 적합도 | AI/구현 판단 | 라이선스/정책 판단 | 우선순위 |
|---|---:|---|---|---:|
| Connect Four | 높음 | minimax/alpha-beta로 충분. 짧고 결과가 명확함 | MIT 구현 사례 있음. boardgame.io도 MIT | 1 |
| Gomoku/오목 | 높음 | 자체 minimax/MCTS 구현 가능. 난이도 조절 쉬움 | 강한 공개 엔진은 라이선스 확인 필요. 자체 구현 권장 | 1 |
| Reversi/Othello | 높음 | 규칙 단순, 전략성 충분, 모바일 UX 좋음 | MIT Reversi engine 사례 있음. 자체 구현도 가능 | 1 |
| Checkers/Draughts | 중간 | 검증된 엔진/룰 구현 가능. 난이도는 오목보다 높음 | MIT TypeScript engine 사례 있음 | 2 |
| Chess | 중간 | AI는 매우 성숙. 하지만 캐주얼 companion에는 무거움 | Stockfish는 GPLv3. 상용 앱 결합 방식 주의 | 2 |
| Backgammon | 중간 | 주사위와 확률이 있어 반응은 좋음 | gambling 오해 가능. 현금성 보상 금지 필요 | 3 |
| Tile rummy/Rummikub-like | 중간 | 재미는 좋지만 룰/AI/UX가 복잡함 | Rummikub 상표/IP 주의. generic tile-rummy로만 검토 | 3 |
| Poker | 낮음 | AI/룰은 가능 | App Store/Google Play gambling review 리스크 큼 | 제외 |
| Rock-paper-scissors/card high-low | 낮음 | 구현 쉬움 | 반복성 약하고 운 의존이 커서 reward farming 방지 필요 | 보조 |

## 5. 추천 MVP mini-game pack

v1.1에서 실제로 넣을 후보는 3개면 충분하다.

1. Quick Connect
   - Connect Four 변형.
   - 3~5분.
   - 초보자도 즉시 이해.
   - 승패가 명확해 Airi 반응 만들기 좋음.

2. Five-in-a-row date
   - 오목 변형.
   - 5~7분.
   - 난이도 조절 쉬움.
   - "한 수 더 둘래?" 같은 companion 대화와 잘 맞음.

3. Reversi cafe
   - Reversi/Othello 변형.
   - 5~8분.
   - 역전이 자주 나와 감정 반응이 좋음.
   - 차분한 관계/집중형 date에 적합.

Chess는 strong AI가 있어 매력적이지만 첫 mini-game pack에는 넣지 않는 편이 낫다.

이유:

- Stockfish 같은 강한 엔진은 GPLv3라 앱 결합/배포 방식에 법무 검토가 필요하다.
- 초보 사용자는 진입 장벽이 높다.
- companion 앱의 핵심은 실력 겨루기보다 감정 루프와 관계 변화다.

## 6. 게임 오픈 조건

게임은 아무 때나 전부 열면 콘텐츠 소모가 빠르다. 관계/상태/쿨다운과 연결한다.

| unlock | 조건 | 콘텐츠 | 목적 |
|---|---|---|---|
| level 1 | first chat 완료 | Movie talk, Weekend plan | 첫날 체감 |
| level 2 | relationship score 20+ | Quick Connect | 첫 캐주얼 승패 |
| level 3 | trust 15+ 또는 Comfort 완료 | Reversi cafe | 차분한 전략 date |
| level 4 | familiarity 25+ | Five-in-a-row date | 반복 플레이 |
| level 5 | 첫 image reward 해금 | Checkers beta | 중급 전략 |
| level 6+ | steady streak 5일+ | Special game variant | 장기 retention |

Mood 조건:

- mood=playful: Quick Connect, Gomoku 우선 제안.
- mood=warm: Reversi, Movie talk 우선 제안.
- mood=concerned: Comfort date 우선, 승패형 게임 제안 제한.
- mood=tired: 짧은 게임만 제안하고 guilt copy 금지.

쿨다운:

- 같은 게임 reward-bearing finish는 24시간 1회.
- reward 없는 casual replay는 허용 가능하지만 relationship gain은 cap 적용.
- 기권/중단은 30~60분 soft cooldown.

## 7. 승패별 보상/패널티

원칙:

- 패배를 강한 처벌로 만들지 않는다.
- paid credit을 패배로 잃게 하지 않는다.
- relationship level은 첫 release와 v1.1에서 내려가지 않는다.
- 부정적 결과는 mood, distance, missed bonus, repair prompt로 표현한다.

| 결과 | relationship | reward | Airi 반응 |
|---|---|---|---|
| user_win | affinity +2, familiarity +1 | note progress 또는 image progress | 장난스럽게 인정, 다음 도전 제안 |
| airi_win | affinity +1, trust +1 | retry hint, small note | 약하게 놀리되 사용자를 깎아내리지 않음 |
| draw | trust +1, familiarity +1 | shared memory card progress | "우리 비겼네" 공동 경험 강조 |
| user_forfeit | no gain, mood neutral/tired | no reward | 부담 주지 않고 나중에 이어하기 제안 |
| repeated_loss | trust +1 max/day | coaching hint | 실력 비하 금지, 난이도 낮추기 제안 |
| unsafe_input | no normal reward | safety route | normal game loop 중단 |
| exploit/replay | no gain | no reward | 서버에서는 조용히 idempotent 처리 |

Reward detail:

- First win of day: Airi note.
- First draw of week: story/memory card progress.
- Win streak 3: basic image reward progress. Free weekly cap 적용.
- Lose streak 3: comfort/coaching note. 보상은 작게 주되 승리 보상보다 낮게.
- Airi wins 3 times: "revenge match" event unlock. credit 차감 없음.

## 8. Relationship branch model

관계는 단일 호감도 숫자로 보면 안 된다.

필수 축:

- affinity: 즐거움, 친근함.
- trust: 안전감, 위로, 일관성.
- familiarity: 서로의 취향/습관을 아는 정도.
- mood: 단기 감정.
- distance: 장기 이탈/불편감.
- repair_score: 갈등 이후 회복 정도.

Branch는 다음처럼 잡는다.

| branch | 조건 | 콘텐츠 톤 | 보상 |
|---|---|---|---|
| warm_growth | affinity/trust/familiarity 균형 상승 | 편안한 date, 자연스러운 기억 회상 | happy note, image card |
| playful_rivalry | affinity 높고 game participation 높음 | 승부욕, 장난, 재도전 | game badge, playful voice |
| quiet_trust | trust 높고 comfort/date 중심 | 위로, 약속, 낮은 자극 | comfort note, soft voice |
| distant_return | 7일+ 부재 또는 forfeit 반복 | 부담 없는 복귀, 짧은 제안 | comeback note |
| unresolved_tension | harsh input, repeated unsafe soft block, broken promise 반복 | 거리감, repair 제안 | reward 제한, repair event |
| overfarmed | 반복 replay/exploit 신호 | 감정 반응 축소, reward cap | no reward |

## 9. Ending design

Ending은 "앱 종료"가 아니라 season arc 결과다. 2~4주 단위로 한 season을 닫고 다음 season으로 이어간다.

### Happy ending

조건 예시:

- relationship score threshold 달성.
- 최소 3종 콘텐츠 완료.
- safety/harsh event가 낮음.
- memory active 3개 이상.

결과:

- season story card.
- Airi note collection unlock.
- basic/premium image reward progress.
- 다음 season title unlock.

### Neutral ending

조건 예시:

- 일부 콘텐츠만 완료.
- 관계 수치가 낮지만 negative event도 낮음.

결과:

- recap note.
- missed memory/reward preview.
- 다음 season에서 쉬운 재진입.

### Bittersweet ending

조건 예시:

- long absence, unfinished promise, repeated forfeit.

결과:

- Airi가 사용자를 탓하지 않는 회고.
- comeback event 제안.
- distance는 유지되지만 level 하락 없음.

### Bad ending

상용 companion에서 bad ending은 조심해야 한다.

허용되는 bad ending:

- season arc가 "unresolved"로 끝남.
- reward 일부가 잠금 해제되지 않음.
- repair event가 열린다.
- Airi 톤이 잠시 조심스러워진다.

금지되는 bad ending:

- "너 때문에 상처받았다"식 guilt copy.
- paid user의 보상 박탈.
- 사용자의 실제 인간 관계를 방해하는 표현.
- Airi가 사용자를 처벌하거나 버리는 표현.

Bad ending 조건 예시:

- repeated harsh input.
- safety soft block이 일정 횟수 이상.
- promise event를 여러 번 완료하지 않음.
- exploit/reward farming 시도.

회복 조건:

- repair date 1회 완료.
- safety-safe apology/clarification 선택지.
- 2~3일 정상 대화.
- comfort 또는 low-pressure game 완료.

## 10. Airi 반응 규칙

| 관계 상태 | user win | Airi win | user loss streak | comeback |
|---|---|---|---|---|
| early | 정중한 칭찬 | 가벼운 장난 | 난이도 낮추기 제안 | 다시 와줘서 반갑다는 중립 톤 |
| warm | 친근한 축하 | 장난스럽게 재도전 제안 | 같이 연습하자 | 기억 1개만 자연스럽게 회상 |
| playful | 라이벌처럼 반응 | 더 강한 장난 가능 | revenge match 제안 | "오늘은 짧게 한 판?" |
| trusted | 결과보다 과정 칭찬 | 사용자의 기분 배려 | 위로/코칭 | 부재를 탓하지 않음 |
| distant | 과한 애정 금지 | 담백한 반응 | 관계 보상 최소화 | repair event 제안 |

절대 규칙:

- LLM은 승패, 점수, reward unlock을 바꾸지 못한다.
- Airi는 실제 저장되지 않은 memory를 기억한다고 말하지 않는다.
- 패배/부재/기권을 정서적으로 압박하지 않는다.

## 11. 구현 모델 초안

기존 date event 모델을 확장한다.

```text
game_templates
game_sessions
game_moves
game_results
relationship_events
reward_events
memory_candidates
season_arcs
season_endings
```

Service boundary:

- GameRuleEngine: legal move, score, result, anti-cheat.
- GameAiAdapter: game-specific AI move. 자체 구현 또는 외부 엔진 wrapper.
- RelationshipStateService: result를 relationship_event로 반영.
- RewardUnlockService: reward cap, progress, unlock.
- MemoryService: memorable result만 candidate 생성.
- AiriReactionService: deterministic result를 받아 LLM copy 생성.

주의:

- chess engine처럼 GPL 계열 엔진을 직접 앱에 포함할 경우 법무 검토 전까지 production 포함 금지.
- external engine process나 separate service로 분리해도 라이선스 의무가 사라진다고 가정하면 안 된다.
- store-safe 앱에서는 현금성/현물성 reward와 chance-based gambling 표현을 피한다.

## 12. QA acceptance criteria

보드게임/ending 기획이 개발 가능하려면 다음을 만족해야 한다.

- 동일한 game state와 move는 동일한 result를 만든다.
- reward-bearing finish 중복 호출은 보상을 중복 지급하지 않는다.
- 승/패/무/기권/중단/만료/unsafe input이 모두 테스트된다.
- relationship daily cap이 적용된다.
- reward weekly/monthly cap이 적용된다.
- Airi reaction이 score/result를 조작하지 않는다.
- bad ending이 guilt/manipulation copy를 사용하지 않는다.
- underage/restricted mode에서는 romantic reward가 제한된다.
- poker/casino/real-money-like content는 launch scope에 없다.

## 13. PM 판단

현재 기획은 "AI companion + date event + reward/memory loop"의 뼈대는 좋다.

다만 콘텐츠적 깊이를 상용 retention으로 가져가려면 다음이 추가되어야 한다.

1. v1.1 mini-game pack 3개 확정.
2. game result -> relationship/reward/memory mapping table.
3. season ending/repair event rule table.
4. Airi reaction copy matrix.
5. game reward farming 방지 정책.
6. game engine license/legal review.

개발 순서상 지금 당장 보드게임을 구현하면 backend core loop 구현이 느려진다. 따라서 v1 backend에서는 기존 date event rule engine과 reward/media/memory loop를 먼저 끝내고, v1.1에서 mini-game framework와 첫 게임 1개를 넣는 것이 현실적이다.

## Sources

- Stockfish official site, GPLv3 notice: https://stockfishchess.org/
- chess.js npm package, BSD-2-Clause: https://www.npmjs.com/package/chess.js
- boardgame.io npm package, MIT and turn-based framework features: https://www.npmjs.com/package/boardgame.io/v/0.43.0
- Google Play Real-Money Gambling, Games, and Contests policy: https://support.google.com/googleplay/android-developer/answer/9877032/
- Apple App Review Guidelines, 5.3 Gaming, Gambling, and Lotteries: https://developer.apple.com/app-store/review/guidelines/
- rust-reversi PyPI, MIT Reversi engine example: https://pypi.org/project/rust-reversi/1.4.3/
- rapid-draughts package listing, MIT checkers/draughts engine example: https://www.jsdelivr.com/package/npm/rapid-draughts
- Connect Four JS, MIT minimax/alpha-beta example: https://www.gimu.org/connect-four-js/
- rummikub-solver PyPI, MIT solver example: https://pypi.org/project/rummikub-solver/
- Rummikub official newsroom, IP ownership context: https://rummikub.com/newsroom/
