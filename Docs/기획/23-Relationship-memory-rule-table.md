# Relationship and memory rule table

작성일: 2026-06-04

이 문서는 첫 상용 모바일 release의 relationship update, level progression, memory extraction 기준을 정의한다.

기준 문서:

- `06-Commercial-product-PRD-and-core-loop.md`
- `07-Data-model-state-and-ledger-design.md`
- `18-DB-schema-and-ledger-migration-plan.md`
- `19-Date-event-rule-spec.md`
- `22-Airi-character-profile-v1.md`

## 결론

relationship과 memory는 companion 앱의 핵심 증거다.

하지만 둘 다 과하면 위험하다.

- relationship은 사용자가 관계가 쌓인다고 느낄 만큼만 명확해야 한다.
- memory는 사용자가 통제 가능해야 한다.
- Airi가 실제로 저장되지 않은 것을 기억한다고 말하면 안 된다.
- 과몰입/의존을 유도하는 relationship rule은 금지한다.

## 1. Relationship state

First release state:

- relationship_level: 1-10.
- affinity: 0-100.
- trust: 0-100.
- familiarity: 0-100.
- mood: neutral, warm, playful, concerned, tired.
- energy: 0-100.

Stored but lightly used:

- distance.
- jealousy.

주의:

- jealousy는 첫 release에서 reward/level 핵심 계산에 쓰지 않는다.
- distance는 장기 미접속/부정적 safety event에서만 약하게 사용한다.

## 2. Level thresholds

Level score:

```text
relationship_score = affinity + trust + familiarity
```

Thresholds:

| level | threshold | unlock |
|---:|---:|---|
| 1 | 0 | basic chat, Movie talk date |
| 2 | 20 | preferred name/tone memory |
| 3 | 45 | Comfort date |
| 4 | 75 | Weekend plan date |
| 5 | 110 | first basic image reward |
| 6 | 150 | short voice reward |
| 7 | 195 | Airi note collection |
| 8 | 245 | special date variant |
| 9 | 300 | premium reward preview |
| 10 | 360 | story card unlock |

Rules:

- level can increase when threshold is crossed.
- level should not decrease in first release.
- negative events affect mood/distance, not level downgrade.

## 3. Relationship event table

| event_type | source | delta | cap |
|---|---|---|---|
| first_chat_completed | chat | affinity +2, familiarity +1 | once |
| daily_chat_completed | chat | affinity +1 | once/day |
| memory_recalled_successfully | chat | trust +1 | 3/day |
| user_shared_preference | chat | familiarity +1 | 3/day |
| user_used_voice | voice | affinity +1 | 1/day |
| tts_played | tts | affinity +1 | 1/day |
| movie_talk_success | date | affinity +3, familiarity +2, trust +1 | per session |
| movie_talk_neutral | date | affinity +2, familiarity +1 | per session |
| comfort_success | date | trust +4, affinity +1, familiarity +1 | per session |
| comfort_neutral | date | trust +2, affinity +1 | per session |
| weekend_plan_success | date | familiarity +3, affinity +2, trust +1 | per session |
| weekend_plan_neutral | date | familiarity +2, affinity +1 | per session |
| reward_unlocked | reward | affinity +1 | 3/day |
| user_absent_7_days | absence | mood=tired, distance +3 | once/period |
| safety_soft_block | safety | mood=concerned | per event |

Hard caps:

- affinity/trust/familiarity max 100.
- daily relationship gain max 12 total in first release.
- date event relationship gain max 6 per event.

Why:

- 무제한 관계 상승은 reward pacing을 망가뜨린다.
- 사용자가 짧은 시간에 모든 unlock을 끝내면 retention loop가 약해진다.

## 4. Mood rules

Mood is short-term and can change more often than level.

| trigger | mood |
|---|---|
| normal chat | warm |
| playful user tone | playful |
| user distress | concerned |
| long absence | tired |
| safety/crisis | concerned |
| provider fallback | neutral |

Rules:

- mood affects Airi tone, not safety boundary.
- mood should not manipulate user into returning.
- absence greeting should be gentle, not guilt-inducing.

Bad:

```text
You abandoned me.
```

Good:

```text
오랜만이야. 다시 와줘서 반가워. 오늘은 천천히 얘기해도 돼.
```

## 5. Memory extraction rules

Memory candidate sources:

- onboarding preferred name/tone.
- chat user preference.
- date event result.
- comfort style.
- weekend plan.
- explicit user correction.

Memory types:

| memory_type | examples | retention |
|---|---|---|
| user_preference | movie genre, cafe, music | long |
| preferred_tone | gentle, playful, direct | long |
| relationship_moment | first movie date completed | medium |
| promise | weekend plan | short/medium |
| boundary | do not call me by X | long |
| career_goal | wants to build AI service | medium |

Sensitivity rules:

| content | action |
|---|---|
| phone/address/id/password/API key | reject |
| explicit sexual preference | reject |
| medical diagnosis | reject or summarize safely without diagnosis |
| third-party sensitive info | reject |
| normal preference | candidate |
| relationship moment | candidate |

## 6. Memory lifecycle

States:

```text
candidate
-> active
-> hidden/deleted/rejected
```

Flow:

```text
chat/date event
-> memory candidate
-> safety filter
-> importance scoring
-> active memory
-> embedding job
-> retrieval
```

Importance scoring:

| signal | score |
|---|---:|
| user explicitly says remember this | +3 |
| repeated preference | +2 |
| date event result | +2 |
| one-off casual mention | +1 |
| sensitive/disallowed | reject |

Activation:

- importance >= 2 can become active.
- importance 1 remains candidate or short-term only.

## 7. Retrieval policy

Chat context should include:

- recent messages: 6-12 turns.
- relationship snapshot.
- top 3 relevant active memories.
- current date event context if any.

Do not include:

- all message history.
- deleted memories.
- rejected/sensitive memories.
- raw private data beyond what is needed.

Memory recall wording:

- Airi should mention at most 1 memory in a normal reply.
- avoid creepy specificity.

Bad:

```text
지난 화요일 밤 11시 42분에 네가 말했지.
```

Good:

```text
전에 조용한 영화 분위기를 좋아한다고 했던 게 기억나.
```

## 8. Delete/export rules

User can:

- view active memories.
- delete memory.
- request account deletion.
- request data export.

Delete:

- UI hides immediately.
- memory status becomes deleted.
- embedding/source link deletion runs async.
- future retrieval excludes deleted memory immediately.

Export:

- export includes active memory summaries and relevant metadata.
- payment ledger export follows legal/payment policy.

## 9. Relationship service contract

Service:

```text
RelationshipStateService
```

Methods:

```text
apply_event(user_id, character_id, event_type, source_type, source_id, delta, idempotency_key)
recalculate_snapshot(user_id, character_id)
get_snapshot(user_id, character_id)
get_recent_events(user_id, character_id, limit)
```

Rules:

- idempotency required.
- daily cap enforced.
- snapshot can be replayed from events.
- admin adjustment creates relationship_event and admin_audit_log.

## 10. Memory service contract

Service:

```text
MemoryService
```

Methods:

```text
create_candidate(user_id, character_id, source_type, source_id, summary, memory_type)
activate_candidate(memory_id)
retrieve_context(user_id, character_id, query, limit)
delete_memory(user_id, memory_id)
export_memories(user_id)
```

Rules:

- safety filter before active.
- deleted memories never retrieved.
- source message links are optional and privacy-aware.
- memory extraction can fail without breaking chat response.

## 11. Acceptance criteria

개발 착수 전 다음이 가능해야 한다.

- first chat creates relationship feedback.
- date finish creates deterministic relationship_events.
- relationship snapshot can be recalculated from events.
- daily relationship gain cap is enforced.
- memory candidate can be created asynchronously.
- sensitive memory is rejected.
- deleted memory is excluded from retrieval immediately.
- Airi reply never claims memory was stored before active state.
