# Commercial product PRD and core loop

첫 release의 Airi 캐릭터 기준은 `22-Airi-character-profile-v1.md`, relationship/memory update 기준은 `23-Relationship-memory-rule-table.md`를 따른다.

## 제품 정의

차기 서비스는 단순 AI 채팅 앱이 아니라 **AI companion과 대화하고, 데이트형 미니게임을 함께 진행하며, 결과가 관계/보상/스토리/미디어에 반영되는 상용 앱**이다.

핵심 문장:

> 사용자는 AI companion과 매일 대화하고, 함께 짧은 데이트형 콘텐츠를 플레이하며, 결과에 따라 관계와 보상이 누적된다.

## 타깃 사용자

1. 감정적 대화 상대를 원하는 사용자
   - 외로움, 일상 공유, 위로, 관계 몰입.

2. AI 캐릭터와 콘텐츠를 소비하고 싶은 사용자
   - 데이트 이벤트, 사진/음성/스토리 unlock, 캐릭터 성장.

3. 게임형 보상 루프를 원하는 사용자
   - daily mission, mini-game, intimacy progression, collection.

4. 프리미엄 AI 경험에 돈을 낼 수 있는 사용자
   - 음성, 고품질 이미지, 기억, 캐릭터 커스터마이징, 긴 대화.

## 제품 포지셔닝

기존 AI companion 앱과의 차이:

- 기존: 대화/롤플레이 중심.
- 목표: 대화 + 데이트형 미니게임 + 관계 상태 + reward unlock + memory continuity.

기존 연애/미니게임 앱과의 차이:

- 기존: 정해진 스토리/이벤트 중심.
- 목표: 사용자의 실제 대화와 관계 상태가 콘텐츠 결과에 반영됨.

## 핵심 제품 루프

```text
daily entry
-> character greeting with remembered context
-> user chat or date suggestion
-> shared activity/date event/mini-game
-> deterministic game result
-> AI companion reaction
-> relationship state update
-> reward/media/story unlock
-> memory extraction
-> next session starts with continuity
```

## 상용 기준 핵심 경험

무료 사용자도 반드시 체감해야 하는 것:

- 캐릭터가 지난 대화 일부를 기억하는 느낌.
- 짧은 음성 또는 TTS 경험.
- 적어도 주간 단위의 reward/media unlock.
- 광고를 봤을 때 즉시 쓸 수 있는 credit 보상.

유료 사용자가 돈을 내야 하는 이유:

- 광고 제거.
- 긴 대화와 더 많은 기억.
- 더 많은 음성/TTS.
- 이미지/스토리/데이트 이벤트 unlock.
- 캐릭터 관계 progression 속도 증가.
- 고품질 voice/media model 사용.

## 무료/유료 루프

### Free

목표: 이탈 방지와 유료 전환 유도.

- text chat: daily 제한.
- voice input: 매우 제한적 허용.
- TTS: 짧은 응답 위주 허용.
- memory: 핵심 summary 3~5개.
- reward: 주간 1개 수준.
- ads: rewarded ad로 credit 지급.

Free에서 금지하면 안 되는 것:

- 모든 음성 차단.
- 기억 완전 차단.
- reward 완전 차단.

이렇게 하면 사용자는 "광고도 보는데 기본 경험도 없다"고 느끼고 삭제할 가능성이 높다.

### Plus

목표: 일반 사용자 월 구독.

- 광고 제거.
- daily text/voice allowance 증가.
- memory 확장.
- date event와 reward unlock 증가.
- image credit 월 제공.

### Premium

목표: heavy user와 고비용 기능 보호.

- premium voice.
- image/video credit 할인.
- 더 긴 memory.
- custom character slot.
- priority queue.

## 성공 지표

제품 지표:

- D1 retention
- D7 retention
- DAU/MAU
- 평균 대화 turn 수
- daily date event 참여율
- reward unlock rate
- paid conversion rate
- ARPPU
- churn reason

기술 지표:

- STT final latency
- first AI token latency
- first TTS audio start latency
- full turn completion latency
- provider failure rate
- fallback rate
- moderation block rate
- cost per user per day
- queue wait time by plan

## 상용에서 빠지면 안 되는 기능

- 사용자 인증.
- subscription/credit ledger.
- memory delete/export.
- report/block.
- admin user lookup.
- provider cost dashboard.
- AI response safety guard.
- image/media moderation.
- queue/backpressure.
- payment/refund handling.

## 지금 당장 만들지 말아야 할 것

- 무제한 실시간 video call.
- 자체 foundation model 학습.
- UGC marketplace.
- 복잡한 multiplayer.
- 과도한 3D avatar engine.
- 모든 provider 동시 지원.

이 기능들은 매력적이지만 초기 상용화에서는 비용, 운영, 안전 리스크가 크다.
