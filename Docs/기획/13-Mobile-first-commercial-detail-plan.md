# Mobile-first commercial detail plan

첫 상용 버전은 모바일 앱 기준으로 설계한다. 웹은 admin/backoffice와 landing/payment support 용도로만 본다.

## 세부 설계 목표

상용앱 세부 설계는 "기능을 많이 적는 것"이 아니라 다음 질문에 답하는 것이다.

- 사용자가 앱을 켜자마자 무엇을 하는가?
- 무료 사용자가 삭제하지 않을 만큼 어떤 경험을 받는가?
- 유료 사용자는 어떤 기능 때문에 돈을 내는가?
- AI 비용이 매출보다 커지지 않도록 어디서 제한하는가?
- 장애/신고/환불/부적절 콘텐츠를 운영자가 어떻게 처리하는가?

## 1. Mobile app product flow

설계할 화면:

- splash/onboarding
- login
- age gate
- character select
- main chat
- voice mode
- date event list
- date mini-game
- reward gallery
- memory screen
- relationship/status screen
- shop/credit
- subscription
- settings/privacy
- report/block

화면 IA와 사용자 여정의 기준 문서는 `16-Mobile-user-journey-and-screen-IA.md`다. 이 문서는 화면 목록이 아니라 다음을 확정한다.

- Chat, Date, Rewards, Profile 하단 탭 구조.
- first-run journey.
- daily return journey.
- main chat, voice/TTS, date event, reward, memory/relationship, shop, settings/report 흐름.
- quota exceeded, provider degraded, moderation rejected 같은 예외 상태.
- 첫 release UX acceptance criteria.

첫 release에서 너무 많은 화면을 넣으면 개발이 느려진다. 핵심은 다음 5개다.

1. main chat
2. voice/TTS interaction
3. memory/relationship visible feedback
4. date event or daily event
5. reward gallery/shop

## 2. First release scope

권장 첫 상용 범위:

- 캐릭터 1명 또는 2명.
- text chat.
- 짧은 voice input.
- TTS는 일부 응답만.
- 장기 memory summary.
- relationship state.
- daily/date event 3~5개.
- image reward unlock.
- credit + subscription.
- rewarded ads.
- basic admin ops.

첫 release에서 제외 권장:

- video generation.
- realtime video call.
- multi-character complex story.
- user generated character marketplace.
- self-hosted model.

## 3. Mobile backend API design 대상

모바일 API 계약의 기준 문서는 `17-Mobile-API-contract.md`다.

세부 API 문서에서 정의해야 할 것:

- `POST /auth/session`
- `GET /characters`
- `GET /characters/{id}/state`
- `POST /chat/turn`
- `POST /voice/stt`
- `POST /tts`
- `GET /memories`
- `DELETE /memories/{id}`
- `POST /date-events/{id}/start`
- `POST /date-events/{id}/move`
- `POST /date-events/{id}/finish`
- `GET /rewards`
- `POST /media/generate`
- `GET /media/jobs/{id}`
- `GET /credits/balance`
- `GET /credits/ledger`
- `POST /billing/webhook/google-play`
- `POST /reports`
- `POST /users/delete-request`

각 API는 auth, rate limit, credit 차감, idempotency 여부를 명확히 가져야 한다.

특히 다음 API는 첫 release에서 idempotency key가 필요하다.

- `POST /chat/turn`
- `POST /tts`
- `POST /date-events/{id}/start`
- `POST /date-events/{id}/move`
- `POST /date-events/{id}/finish`
- `POST /media/generate`
- `POST /reports`

## 4. Mobile latency budget

모바일에서 체감 기준:

- chat text response first visible: 1~2초 목표.
- voice input final transcript: 0.3~1.5초 목표.
- first TTS audio start: 2~3초 목표.
- image reward generation: realtime이 아니라 async job 가능.
- video generation: async only.

지켜야 할 원칙:

- 채팅은 즉시 local reaction을 보여준다.
- LLM/TTS/image는 queue 상태를 UI에 표시한다.
- 무료 사용자의 고비용 기능은 기다리게 할 수 있지만, 유료 사용자는 priority queue가 필요하다.

## 5. Mobile monetization design

모바일은 Google Play/App Store 수수료를 고려해야 한다.

Free:

- 광고 있음.
- 짧은 text/voice/TTS 허용.
- basic memory 일부 제공.
- weekly reward 제공.

Plus:

- 광고 제거.
- text/voice/TTS allowance 증가.
- memory 확장.
- image credit 월 제공.

Premium:

- priority queue.
- premium voice.
- 더 많은 image credit.
- custom companion slot.
- event/reward 우선 접근.

Credit:

- image generation.
- video generation.
- premium voice bundle.
- event pack.
- regeneration.

## 6. Mobile risk

기술 리스크:

- 음성/TTS 비용 폭주.
- 이미지 생성 비용 폭주.
- 모바일 네트워크 불안정.
- push notification abuse.
- 앱 심사에서 AI/성인/개인정보 정책 문제.

제품 리스크:

- free가 너무 제한적이면 삭제율 증가.
- plus가 광고 제거 외 매력이 없으면 전환율 낮음.
- 캐릭터가 기억하지 못하면 companion 가치가 약함.
- reward가 대화/관계와 연결되지 않으면 단순 갤러리 앱이 됨.

## 7. 다음 세부 문서 순서

모바일 기준으로 다음 문서를 작성한다.

1. Mobile user journey and screen IA. 완료 기준: `16-Mobile-user-journey-and-screen-IA.md`.
2. Mobile API contract. 완료 기준: `17-Mobile-API-contract.md`.
3. DB schema and credit ledger.
4. Queue/provider runtime detail.
5. Admin/backoffice screen spec.
6. Billing/ad/reward policy.
7. Safety and store review checklist.

다음 단계에서 API contract를 작성할 때는 `16`의 화면 상태를 누락하면 안 된다. 특히 chat sending/thinking/streaming, TTS pending/ready/failed, date session start/move/finish, reward pending/rejected/unlocked, quota exceeded 상태는 API와 DB 상태값으로 연결되어야 한다.
