# Mobile user journey and screen IA

작성일: 2026-06-04

이 문서는 첫 상용 모바일 release에서 사용자가 실제로 어떤 화면을 지나고, 어떤 행동을 하며, 어떤 상태 변화를 체감해야 하는지 정의한다.

기준 문서:

- `06-Commercial-product-PRD-and-core-loop.md`
- `13-Mobile-first-commercial-detail-plan.md`
- `15-First-release-scope-decisions.md`
- `Docs/개발/01-Development-plan-and-tech-stack.md`

## 결론

첫 release의 UX는 `Chat-first`로 간다.

핵심은 많은 화면이 아니라 다음 증거를 사용자가 매일 보는 것이다.

1. Airi가 나를 기억한다.
2. 대화와 date event 결과가 관계 상태를 바꾼다.
3. 관계 변화가 reward, diary, voice, image unlock으로 이어진다.

이 3개가 약하면 앱은 단순 AI chat + gallery가 된다. 그러면 Zeta/Character.AI/Nika류와 정면 경쟁하게 되고, 작은 팀이 이기기 어렵다.

## 1. First release navigation model

첫 release는 하단 탭 4개를 기본으로 둔다.

```text
Chat
Date
Rewards
Profile
```

### Chat

역할:

- 첫 진입 화면.
- Airi와 대화.
- voice input / selected TTS.
- memory recall과 relationship 변화의 즉시 피드백.
- 오늘의 date event와 reward hint 노출.

### Date

역할:

- official date event 3개 진입.
- 진행 중인 date session 복귀.
- 완료한 event 결과 확인.

### Rewards

역할:

- unlock된 reward image, voice message, Airi note 확인.
- pending image job 상태 확인.
- premium reward / credit 사용 지점 노출.

### Profile

역할:

- relationship level/status.
- memory list.
- Airi note.
- plan/quota.
- settings/privacy/report/delete path 진입.

주의:

- 첫 release에서 탭을 5개 이상으로 늘리지 않는다.
- Shop은 독립 탭으로 두지 않고, quota 초과, reward 잠금, Profile plan 영역에서 진입시킨다.
- Settings는 Profile 하위로 둔다.

## 2. First-run journey

목표:

- 사용자가 1분 안에 Airi와 첫 대화를 시작해야 한다.
- age/privacy/store-safe policy 동의는 반드시 받되, 첫 경험을 과도하게 막지 않는다.

흐름:

```text
splash
-> age gate
-> login / guest start
-> privacy and AI disclosure consent
-> Airi intro
-> main chat
-> first message
-> first relationship feedback
-> first date event hint
```

### 2.1 Splash

표시:

- app logo/name.
- loading status.

금지:

- 긴 브랜드 설명.
- 마케팅형 hero.
- 불필요한 튜토리얼.

### 2.2 Age gate

목적:

- 미성년/성인 콘텐츠 정책 리스크를 줄인다.
- companion romance 기능이 store-safe romantic/suggestive 범위임을 전제로 한다.

요구:

- 생년 또는 연령 확인.
- 미성년이면 romantic/suggestive 기능 제한 또는 진입 제한 정책 필요.
- age gate 결과는 서버에 저장하되, 개인정보 최소화 원칙을 따른다.

### 2.3 Login / guest start

첫 release 권장:

- guest start 허용.
- 결제, cloud sync, account deletion/export에는 계정 연결 요구.

이유:

- companion 앱은 첫 대화 전 friction이 높으면 이탈이 크다.
- 단, memory/credit/payment는 서버 사용자 ID에 반드시 묶어야 한다.

### 2.4 Privacy and AI disclosure

필수 고지:

- Airi는 AI character다.
- 대화 일부는 memory summary로 저장될 수 있다.
- 사용자는 memory/delete/report를 할 수 있다.
- 생성 media는 moderation을 거친다.
- 위기/의료/법률/금융 조언은 전문 서비스가 아니다.

### 2.5 Airi intro

목표:

- 캐릭터 설명이 아니라 바로 대화하고 싶게 만든다.

내용:

- Airi의 짧은 인사.
- 사용자의 이름 또는 부를 호칭 질문.
- 선호 대화 분위기 1개 선택.

첫 memory 후보:

- preferred_name
- preferred_tone

## 3. Daily return journey

매일 접속의 기본 흐름:

```text
app open
-> Chat tab
-> Airi greeting with remembered context
-> user chat
-> relationship micro feedback
-> date event suggestion
-> reward progress hint
-> memory/diary update in background
```

첫 화면에서 보여줄 것:

- Airi greeting.
- 최근 기억 1개를 자연스럽게 반영한 문장.
- relationship level 또는 affinity/trust/mood 중 1개 요약.
- voice button.
- 오늘 할 수 있는 date/reward hint.

첫 화면에서 과하게 보여주면 안 되는 것:

- 복잡한 스탯 표.
- 과금 팝업.
- 전체 reward 목록.
- 긴 튜토리얼.

## 4. Main chat screen spec

### 4.1 화면 목적

Chat은 앱의 홈이다.

사용자는 여기서 다음을 할 수 있어야 한다.

- 텍스트 입력.
- push-to-talk voice input.
- Airi 답변 듣기.
- 오늘의 date event 진입.
- reward 진행도 확인.
- memory/relationship 변화 확인.

### 4.2 구성

```text
Top bar
  Airi avatar/name
  relationship level
  small status/mood

Message timeline
  Airi/user messages
  system-light relationship feedback
  reward/date hint card

Composer
  text input
  voice button
  send button
  TTS replay if available
```

### 4.3 Chat states

필수 상태:

| 상태 | UI | 서버/기술 요구 |
|---|---|---|
| idle | 입력 가능 | quota 상태 preload |
| sending | 사용자 메시지 pending | idempotency key |
| Airi thinking | local reaction 먼저 표시 | chat request 진행 |
| streaming/rendering | 답변 점진 표시 | first token/first render 측정 |
| TTS pending | 작은 loading 표시 | TTS queue job |
| TTS ready | play button | signed audio URL 또는 playback ticket |
| quota exceeded | daily limit 안내 + ad/shop 진입 | quota service |
| provider degraded | 느림/텍스트 우선 안내 | fallback/slow-mode |
| safety blocked | 부드러운 거절 + report/help path | safety event log |

### 4.4 Relationship feedback

대화 후 relationship 변화는 작게 보여준다.

예:

```text
Trust +1
Airi remembered your movie taste
Reward progress 60%
```

주의:

- 매 turn마다 큰 애니메이션을 띄우지 않는다.
- 숫자만 보여주면 감정 루프가 약하므로 Airi 반응 문장과 함께 보여준다.

### 4.5 Memory feedback

memory 저장 후보가 생기면 즉시 과하게 노출하지 않는다.

권장:

- 대화 중에는 "Airi may remember this" 수준의 작은 indicator.
- memory 확정은 background worker 완료 후 Profile/Memory에서 확인.
- 민감정보는 저장하지 않고 safety event로만 기록한다.

## 5. Voice and TTS journey

첫 release 원칙:

- live call 제외.
- push-to-talk voice input.
- selected short TTS.
- TTS는 모든 응답이 아니라 감정 반응, reward, date completion 중심으로 제한.

흐름:

```text
hold voice button
-> record
-> upload/process STT
-> transcript confirmation or auto-send
-> chat turn
-> optional short TTS job
-> playback
```

필수 상태:

| 상태 | UI |
|---|---|
| permission needed | OS permission 요청 |
| recording | waveform/timer |
| processing | transcript loading |
| transcript failed | retry/text fallback |
| daily voice limit reached | ad reward/shop 진입 |
| TTS limit reached | text-only + upgrade hint |
| TTS failed | text remains available |

비용 보호:

- Free voice input: 1 min/day 또는 3~5회/day.
- Free TTS: 3~5 short replies/day.
- 긴 답변 TTS는 자동 생성하지 않는다.
- TTS 실패는 credit 차감 전이면 미차감, 차감 후 실패면 ledger 환불 기준 필요.

## 6. Date event journey

첫 release date event:

1. Movie talk date
2. Comfort date
3. Weekend plan date

원칙:

- LLM은 대사/감정/힌트만 담당한다.
- event result, score, relationship delta, reward unlock은 rule engine이 판단한다.
- 각 event는 3~7분 안에 끝나야 한다.

### 6.1 Entry

진입 경로:

- Chat hint.
- Date tab.
- Reward locked item.

Date card 구성:

- title.
- short premise.
- expected time.
- reward preview.
- cost/free status.
- relationship requirement.

### 6.2 Start

흐름:

```text
select event
-> start confirmation
-> create date_game_session
-> Airi opening line
-> first choice/input
```

서버 요구:

- session id.
- event template version.
- idempotency key.
- user quota/cooldown check.

### 6.3 Play

입력 방식:

- 짧은 선택지.
- 짧은 자유 입력.
- 선택지 + 한 줄 감상 조합.

주의:

- 자유 입력만으로 만들면 QA와 안전성이 떨어진다.
- 선택지만 있으면 AI companion 느낌이 약하다.
- 따라서 rule engine이 해석 가능한 선택지를 중심으로 하고, 자유 입력은 Airi 반응과 memory 후보에 사용한다.

### 6.4 Finish

완료 흐름:

```text
rule engine result
-> relationship event write
-> reward event write
-> Airi reaction
-> reward unlock or progress
-> memory extraction job
-> return to Chat or Rewards
```

완료 화면 구성:

- Airi reaction.
- relationship delta.
- reward result.
- Airi note 생성 여부.
- 다음 행동 CTA.

CTA 우선순위:

1. Continue chat.
2. View reward.
3. View Airi note.

## 7. Reward gallery journey

역할:

- 사용자가 관계가 쌓이고 있음을 시각적으로 확인하는 곳.
- 단순 이미지 저장소가 아니라 date/memory/relationship 결과의 증거여야 한다.

Reward types:

- basic image reward.
- Airi note.
- short voice message.
- story/date memory card.

Reward states:

| 상태 | 설명 |
|---|---|
| locked | 조건 미달 |
| progress | relationship/event 진행 중 |
| pending | async generation/moderation 중 |
| unlocked | 열람 가능 |
| rejected | moderation 실패 |
| expired | 기간성 reward 종료 |

Locked reward에는 unlock 조건을 명확히 보여준다.

예:

```text
Finish Movie talk date
Reach Trust level 3
Use 10 credits
```

주의:

- Free 사용자에게 모든 reward를 paywall로 막지 않는다.
- weekly/basic reward는 무료에서도 체감 가능해야 한다.
- premium reward는 credit/plan 전환 이유가 되어야 한다.

## 8. Memory and relationship journey

Profile 하위에 다음 두 영역을 둔다.

```text
Relationship
Memory
```

### 8.1 Relationship

표시:

- relationship level.
- affinity/trust/mood.
- 최근 변화 3개.
- 다음 unlock preview.

주의:

- 수치만 나열하지 않는다.
- "왜 바뀌었는지" event log를 사용자가 이해할 수 있어야 한다.

예:

```text
Trust increased after Comfort date
Airi remembered your preferred movie genre
Next: first Airi note unlock
```

### 8.2 Memory

표시:

- Airi가 기억하는 항목.
- 생성/업데이트 날짜.
- source type: chat/date/event.
- delete action.

금지:

- 민감 개인정보를 장기 memory로 저장.
- 삭제 UI 없이 memory만 누적.
- 사용자가 모르는 방식으로 과도한 profiling.

## 9. Shop, subscription, and credit journey

Shop은 사용자가 비용 제한에 걸리거나 reward를 원할 때 자연스럽게 진입해야 한다.

진입 지점:

- chat quota exceeded.
- TTS/voice limit reached.
- premium reward locked.
- image regeneration.
- Profile plan status.

첫 release 상품 구조:

- Free.
- Plus.
- Premium.
- Credit pack.
- Rewarded ad credit.

구매 전 표시:

- 무엇이 늘어나는지.
- daily/monthly allowance.
- credit 사용처.
- subscription renewal/cancel 안내.
- generated media는 moderation될 수 있다는 안내.

위험:

- "구독하면 무제한"으로 보이면 안 된다.
- 고비용 image/voice는 plan allowance와 credit cap을 함께 둔다.
- 결제 성공 후 credit 지급 실패를 대비해 ledger와 webhook idempotency가 필요하다.

## 10. Settings, privacy, report

Profile 하위에 둔다.

필수:

- account.
- subscription management.
- privacy policy.
- terms.
- AI generated content disclosure.
- memory delete/export.
- account deletion request.
- report conversation.
- report media.
- block character.

Report flow:

```text
select target
-> choose reason
-> optional note
-> submit
-> safety/moderation event
-> user confirmation
```

Admin 요구:

- report는 moderation queue로 들어간다.
- admin access는 audit log가 필요하다.
- 신고 대상 media는 임시 disable 가능해야 한다.

## 11. Empty, error, and degraded states

상용 앱은 정상 흐름보다 예외 흐름에서 신뢰가 깨진다.

필수 예외 상태:

| 영역 | 상태 |
|---|---|
| Chat | provider timeout, safety block, quota exceeded |
| Voice | permission denied, STT failed, no speech detected |
| TTS | queue delayed, provider failed, playback failed |
| Date | session expired, duplicate finish, rule error |
| Reward | generation pending, moderation rejected, credit refund pending |
| Payment | purchase pending, webhook delayed, duplicate purchase |
| Memory | extraction delayed, delete pending, export requested |

각 예외는 다음 중 하나를 제공해야 한다.

- retry.
- fallback.
- queue status.
- refund rule.
- support/report path.

## 12. Screen priority

### First release required

1. Age gate / consent.
2. Login / guest start.
3. Chat.
4. Voice input / TTS playback.
5. Date list.
6. Date play.
7. Date result.
8. Reward gallery.
9. Relationship.
10. Memory.
11. Shop / subscription / credit.
12. Settings / privacy / report.

### Backoffice required

1. User lookup.
2. Credit ledger viewer.
3. Provider cost dashboard.
4. Queue monitor.
5. Moderation review.
6. Admin audit log viewer.

### Later

- character marketplace.
- UGC scenario editor.
- live call.
- video reward.
- multi-character world.
- creator monetization.

## 13. Acceptance criteria

이 문서 기준으로 첫 release UX가 통과하려면 다음이 가능해야 한다.

Product:

- 신규 사용자가 1분 안에 Airi와 첫 대화를 시작한다.
- 첫 세션 안에 relationship 또는 memory feedback을 1회 이상 본다.
- 첫 chat 또는 첫 date result에서 memory candidate가 생성되었는지 사용자가 이해할 수 있다.
- Airi의 일상형 persona는 자연스럽게 보이되, 실제 사진/위치/실명/회사명/AI 정체성 부정으로 이어지지 않는다.
- 사용자는 첫날 date event 1개를 발견할 수 있다.
- date event 완료 후 relationship/reward/memory 중 최소 2개가 갱신된다.
- Free 사용자도 voice/TTS/reward 중 최소 2개를 제한적으로 체험한다.

Engineering:

- Chat, TTS, image, memory 작업은 상태가 UI에 노출된다.
- quota exceeded 상태가 plan/ad/credit 진입과 연결된다.
- date result는 rule engine 결과로 기록된다.
- reward unlock은 ledger/event로 추적된다.
- provider 실패 시 fallback 또는 degraded state가 있다.
- portfolio/mockup board의 설명표는 앱 화면이 아니라 QA/기획 산출물로 분리된다.

Safety/ops:

- age gate와 AI disclosure가 있다.
- report/block/delete path가 있다.
- generated media는 moderation status를 가진다.
- generated media는 실제 사진처럼 표현하지 않고 AI-generated 맥락을 가진다.
- admin이 user/report/credit/provider cost를 확인할 수 있다.

## 14. 다음 세부 설계로 넘길 항목

이 문서는 화면과 여정을 정의한다. 다음 항목은 별도 상세화가 필요하다.

- Mobile API contract.
- DB schema and credit ledger.
- Airi character profile v1.
- Relationship rule table.
- Date event 3개 rule spec.
- Credit/plan allowance table.
- Admin minimum screen spec.

단, 새 문서를 추가할 때는 기존 문서에 넣으면 비대해지는 경우에만 분리한다.
