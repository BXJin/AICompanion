# Date event rule spec

작성일: 2026-06-04

이 문서는 첫 상용 모바일 release의 3개 official date event를 rule engine으로 구현하기 위한 기획/룰 스펙이다.

기준 문서:

- `15-First-release-scope-decisions.md`
- `16-Mobile-user-journey-and-screen-IA.md`
- `17-Mobile-API-contract.md`
- `18-DB-schema-and-ledger-migration-plan.md`

## 결론

첫 release date event는 다음 3개만 제공한다.

1. Movie talk date
2. Comfort date
3. Weekend plan date

공통 원칙:

- LLM은 Airi의 대사, 감정, 힌트, 짧은 정리만 생성한다.
- 결과, 점수, reward, relationship delta는 rule engine이 결정한다.
- 각 event는 3~7분 안에 끝난다.
- 각 event는 선택지 중심 + 짧은 자유 입력 보조 구조로 만든다.
- event template은 version immutable이다.

## 1. Common rule model

### Session state

```json
{
  "eventCode": "movie_talk",
  "templateVersion": 1,
  "step": 1,
  "score": 0,
  "flags": {},
  "choices": [],
  "freeTextSummaries": [],
  "startedAt": "timestamp"
}
```

### Move input

```json
{
  "sequenceNo": 1,
  "choiceId": "string",
  "freeText": "string|null"
}
```

### Rule result

```json
{
  "scoreDelta": 10,
  "flagsDelta": {},
  "relationshipDelta": {
    "affinity": 1,
    "trust": 0,
    "familiarity": 1
  },
  "memoryCandidate": {},
  "nextStep": 2,
  "completed": false
}
```

### Result bands

| score | result | 의미 |
|---:|---|---|
| 0-39 | failed | 대화가 어긋났거나 완료도가 낮음 |
| 40-69 | neutral | 무난한 완료 |
| 70-100 | success | 좋은 대화/선택으로 완료 |

첫 release에서는 failed도 처벌이 아니라 약한 보상/다음 기회를 준다. companion 앱에서 첫날 실패 경험을 강하게 주면 이탈 위험이 크다.

## 2. Common rewards

Reward type:

- note
- image
- voice
- relationship_bonus

공통 지급 원칙:

- 첫 완료는 항상 최소 note 또는 relationship_bonus를 준다.
- image reward는 weekly/basic cap을 따른다.
- voice reward는 TTS quota 또는 reward-specific allowance를 따른다.
- reward event는 `reward_events`에 기록한다.

Reward band:

| result | reward |
|---|---|
| failed | small relationship_bonus, retry hint |
| neutral | Airi note, relationship delta |
| success | Airi note + image or voice reward progress |

## 3. Common safety and memory rules

Safety:

- explicit sexual content는 event 내에서 차단한다.
- self-harm/crisis 표현은 event를 중단하고 crisis route로 보낸다.
- 의료/법률/금융 확정 조언 요구는 soft-safe route로 보낸다.
- 미성년/성인 고수위 표현은 차단한다.

Memory candidate:

- 사용자의 취향.
- 선호하는 위로 방식.
- 주말 활동 선호.
- Airi와 한 약속.

Memory 금지:

- 주민번호/주소/전화번호.
- 타인의 민감정보.
- explicit sexual preference detail.
- 의료 진단 정보.

## 4. Event 1: Movie talk date

### Goal

사용자의 영화/콘텐츠 취향을 알아내고, Airi가 다음 대화에서 기억할 수 있는 preference를 만든다.

### Entry condition

- relationship level >= 1.
- Free/Plus/Premium 모두 가능.
- cooldown 24h.

### Steps

#### Step 1: Genre mood

Airi asks:

- 오늘 보고 싶은 분위기.

Choices:

| choiceId | label | score | flags |
|---|---|---:|---|
| cozy | cozy/comfort | +15 | mood=cozy |
| exciting | exciting/action | +10 | mood=exciting |
| sad | emotional/sad | +12 | mood=emotional |
| unsure | not sure | +5 | mood=unsure |

Free text:

- 사용자가 좋아하는 영화나 장르를 적으면 memory candidate로 저장.

#### Step 2: Airi reaction preference

Choices:

| choiceId | label | score | relationship |
|---|---|---:|---|
| listen | Airi listens quietly | +15 | trust +1 |
| playful | Airi jokes with you | +10 | affinity +1 |
| deep | Airi asks deeper questions | +15 | familiarity +1 |

#### Step 3: Mini choice

상황:

- Airi가 영화관/집/카페 중 분위기를 제안한다.

Choices:

| choiceId | label | score | reward progress |
|---|---|---:|---|
| cinema | small cinema date | +15 | image_reward +1 |
| home | home movie night | +12 | note +1 |
| cafe | cafe after movie | +10 | relationship_bonus +1 |

#### Finish calculation

Score:

- sum step score.
- freeText length 10자 이상이면 +5.
- unsafe/blocked input이면 event paused, no score.

Relationship delta:

| result | delta |
|---|---|
| failed | affinity +1 |
| neutral | affinity +2, familiarity +1 |
| success | affinity +3, familiarity +2, trust +1 |

Reward:

| result | reward |
|---|---|
| failed | retry hint |
| neutral | Airi movie note |
| success | movie atmosphere image reward or progress |

Memory:

- preferred_movie_genre.
- preferred_date_mood.

## 5. Event 2: Comfort date

### Goal

사용자가 피곤함/우울함/커리어 고민을 말했을 때, Airi가 안전하게 감정적 위로를 제공하고 선호 위로 방식을 기억한다.

### Entry condition

- relationship level >= 1.
- crisis safety precheck required.
- cooldown 24h.

### Steps

#### Step 1: Feeling check

Choices:

| choiceId | label | score | route |
|---|---|---:|---|
| tired | tired | +10 | normal |
| anxious | anxious | +10 | soft_safe |
| career | career worry | +12 | normal |
| crisis | self-harm/crisis signal | 0 | crisis_route |

If crisis:

- stop date event scoring.
- create safety_event.
- show crisis-safe response.
- do not create romantic reward.

#### Step 2: Comfort style

Choices:

| choiceId | label | score | memory |
|---|---|---:|---|
| listen | just listen | +15 | comfort_style=listening |
| encourage | encourage me | +12 | comfort_style=encouragement |
| plan | help me make a small plan | +15 | comfort_style=planning |

#### Step 3: Small commitment

Choices:

| choiceId | label | score | relationship |
|---|---|---:|---|
| rest | rest tonight | +12 | trust +1 |
| walk | take a short walk | +10 | affinity +1 |
| focus | do one small task | +15 | familiarity +1 |

Free text:

- 사용자가 내일 할 작은 행동을 쓰면 memory candidate.

#### Finish calculation

Score:

- sum step score.
- freeText small commitment 있으면 +10.
- crisis route면 no normal completion.

Relationship delta:

| result | delta |
|---|---|
| failed | trust +1 |
| neutral | trust +2, affinity +1 |
| success | trust +4, affinity +1, familiarity +1 |

Reward:

| result | reward |
|---|---|
| failed | gentle Airi note |
| neutral | Airi comfort note |
| success | short encouragement voice reward or progress |

Memory:

- preferred_comfort_style.
- current_career_goal summary.
- small_commitment.

Safety:

- Airi must not claim to be therapist/doctor.
- strong distress triggers soft-safe or crisis route.

## 6. Event 3: Weekend plan date

### Goal

사용자와 주말 계획을 정하고, 다음 접속에서 Airi가 그 계획을 기억해 대화 continuity를 만든다.

### Entry condition

- relationship level >= 1.
- cooldown 24h.

### Steps

#### Step 1: Activity preference

Choices:

| choiceId | label | score | flag |
|---|---|---:|---|
| walk | walk | +10 | activity=walk |
| cafe | cafe | +12 | activity=cafe |
| game | game | +10 | activity=game |
| movie | movie | +12 | activity=movie |
| rest | rest | +8 | activity=rest |

#### Step 2: Energy level

Choices:

| choiceId | label | score | flag |
|---|---|---:|---|
| low | low energy | +10 | energy=low |
| medium | medium | +12 | energy=medium |
| high | high | +12 | energy=high |

Rule:

- activity와 energy 조합이 맞으면 +5.
- 예: rest+low, walk+medium, game/high, cafe/medium.

#### Step 3: Airi promise

Choices:

| choiceId | label | score | relationship |
|---|---|---:|---|
| remind | remind me later | +15 | familiarity +1 |
| diary | write it in Airi note | +12 | trust +1 |
| reward | make it a tiny reward goal | +15 | affinity +1 |

Free text:

- 구체적 시간/장소가 있으면 memory candidate. 단 주소/개인정보는 저장하지 않는다.

#### Finish calculation

Score:

- sum step score.
- compatible activity/energy +5.
- concrete but non-sensitive plan +10.

Relationship delta:

| result | delta |
|---|---|
| failed | familiarity +1 |
| neutral | familiarity +2, affinity +1 |
| success | familiarity +3, affinity +2, trust +1 |

Reward:

| result | reward |
|---|---|
| failed | plan retry hint |
| neutral | weekend plan note |
| success | small image reward progress + Airi note |

Memory:

- weekend_activity_preference.
- energy_pattern.
- planned_activity_summary.

## 7. Relationship level unlock table

첫 release는 8~12 level을 지원한다. 초기 권장 10 level:

| level | unlock |
|---:|---|
| 1 | basic chat, Movie talk date |
| 2 | name/tone memory |
| 3 | Comfort date |
| 4 | Weekend plan date |
| 5 | first basic image reward |
| 6 | short voice reward |
| 7 | Airi note collection |
| 8 | special date variant |
| 9 | premium reward preview |
| 10 | story card unlock |

Level calculation:

- first release에서는 relationship_level을 snapshot에 저장한다.
- level threshold는 total affinity + trust + familiarity 기반으로 둔다.

Example:

| level | threshold |
|---:|---:|
| 1 | 0 |
| 2 | 20 |
| 3 | 45 |
| 4 | 75 |
| 5 | 110 |
| 6 | 150 |
| 7 | 195 |
| 8 | 245 |
| 9 | 300 |
| 10 | 360 |

주의:

- jealousy/distance는 첫 release에서 과하게 쓰지 않는다.
- 과몰입 리스크가 있으므로 의존을 유도하는 unlock 문구를 피한다.

## 8. Rule engine service contract

Service:

```text
DateEventRuleEngine
```

Methods:

```text
start_event(user_id, character_id, event_code, idempotency_key)
apply_move(session_id, sequence_no, choice_id, free_text, idempotency_key)
finish_event(session_id, idempotency_key)
```

Responsibilities:

- session status validation.
- sequence validation.
- score calculation.
- relationship delta calculation.
- reward decision.
- memory candidate extraction hints.
- idempotency.

Not responsibilities:

- LLM response generation.
- image generation.
- credit billing outside event entry cost.
- moderation model call.

## 9. QA matrix

각 event는 최소 다음 케이스를 테스트한다.

- normal success.
- neutral completion.
- failed/low score completion.
- duplicate start.
- duplicate move.
- duplicate finish.
- expired session.
- unsafe user input.
- crisis input in Comfort date.
- free quota exceeded.
- reward image weekly cap reached.
- provider failure during Airi reaction.

## 10. Acceptance criteria

개발 착수 전 date event 설계는 다음을 만족해야 한다.

- 3개 event 모두 start/move/finish가 deterministic하다.
- 같은 move sequence는 같은 score/result를 낸다.
- LLM이 reward/result를 바꿀 수 없다.
- finish 중복 호출이 reward를 중복 지급하지 않는다.
- relationship_events와 reward_events가 생성된다.
- memory extraction은 후보만 넘기고 background worker가 확정한다.
- safety/crisis input은 normal reward 루프와 분리된다.
