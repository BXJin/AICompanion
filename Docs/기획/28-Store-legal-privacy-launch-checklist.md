# Store, legal, privacy, and launch checklist

작성일: 2026-06-04

이 문서는 AI Companion 첫 상용 모바일 release가 Google Play와 Apple App Store 심사, 개인정보, 구독/credit, AI disclosure 리스크를 통과하기 위해 필요한 체크리스트를 정의한다.

법률 자문 문서가 아니다. 실제 출시 전에는 launch country별 변호사/세무/스토어 정책 검토가 필요하다.

## 1. Release policy position

첫 release의 정책 포지션:

- Airi는 성인 캐릭터로만 정의한다.
- 미성년자처럼 보이거나 해석될 수 있는 외형, 말투, 상황을 금지한다.
- explicit adult content는 제공하지 않는다.
- romantic/suggestive content는 store-safe 범위로 제한한다.
- AI generated image reward는 moderation 통과 후 노출한다.
- 사용자는 report, block, memory delete, account deletion request를 앱 안에서 찾을 수 있어야 한다.
- 결제, 구독, credit은 앱 안에서 가격, 제공량, 소진 우선순위, 실패/환불 상태를 숨기지 않는다.

## 2. Google Play implications

출시 전 재확인해야 할 Google Play 항목:

- AI-generated content disclosure and reporting path.
- User Data policy and Data safety form.
- Account deletion requirement.
- Generated media moderation and reporting.
- Subscription, in-app purchase, refund, cancellation display.
- Ads and rewarded ad disclosure.

Google Play에서 특히 위험한 부분:

- 사용자가 AI 생성 콘텐츠를 신고할 수 없는 구조.
- 계정 삭제 요청 경로가 앱/웹 중 한쪽에만 있고 안내가 불명확한 구조.
- 대화, 메모리, generated media, device identifiers의 수집 목적과 보관 기간이 privacy policy와 Data safety form에서 불일치하는 구조.
- 구독 제공량과 credit 제공량이 실제 차감 정책과 다른 구조.

## 3. Apple App Store implications

출시 전 재확인해야 할 Apple 항목:

- objectionable content moderation.
- user-generated or AI-generated content report/block flow.
- in-app purchase and subscription information.
- account deletion path.
- privacy nutrition labels.
- data retention and deletion behavior.
- safety handling for emotional/romantic companion experiences.

Apple에서 특히 위험한 부분:

- AI companion가 정서적 몰입을 유도하지만 safety/report/delete 경로가 약한 구조.
- generated image reward가 moderation 없이 바로 공개되는 구조.
- restore purchase, manage subscription, cancellation 안내가 약한 구조.
- account deletion이 앱 안에서 찾기 어렵거나 실제 삭제/익명화 정책과 다르게 설명되는 구조.

## 4. Required in-app paths

첫 release에 필요한 최소 설정/도움말 경로:

| Path | Required action |
|---|---|
| Settings > AI disclosure | Airi가 AI companion이며 응답/이미지가 AI generated일 수 있음을 명시 |
| Settings > Privacy | 수집 데이터, 이용 목적, 보관 기간, 삭제 요청 링크 |
| Settings > Terms | 서비스 약관, 구독/credit 약관, 금지 행위 |
| Settings > Report | 대화, 이미지, 캐릭터 응답 신고 |
| Settings > Memory | 저장된 memory 조회/삭제 |
| Settings > Account | account deletion request |
| Settings > Subscription | plan, allowance, renewal, cancel 안내 |
| Settings > Restore purchases | iOS/Android 구매 복원 |
| Settings > Support | 결제, 안전, 삭제 요청 문의 |

## 5. AI disclosure checklist

앱 안에서 명확해야 하는 문구:

- Airi is an AI companion, not a human.
- Responses may be inaccurate or fictional.
- Generated media is AI-generated.
- The service is not medical, legal, financial, or emergency support.
- Users can report unsafe or unwanted content.
- Users can delete memories and request account deletion.

금지:

- Airi가 실제 사람처럼 오해될 수 있는 소개.
- 상담/치료/진단을 제공한다는 표현.
- AI 이미지가 실제 사진이라는 표현.
- 삭제 요청이 즉시 모든 백업에서 물리 삭제된다는 과장 표현.

## 6. Privacy coverage

Privacy policy와 Data safety/App privacy labels에 반영해야 할 데이터:

- account identifier.
- device identifier.
- conversation content.
- voice input and transcription.
- generated TTS audio metadata.
- generated image/media metadata.
- memories and relationship state.
- payment/subscription status.
- credit ledger and usage events.
- provider usage and cost logs.
- report/moderation events.
- crash, diagnostic, analytics events.

각 데이터마다 필요한 정의:

- collected or generated.
- purpose.
- storage location.
- retention period.
- deletion/anonymization behavior.
- third-party provider sharing.
- user visibility.
- admin access policy.

## 7. Deletion and retention

최소 정책:

- Memory delete는 앱에서 즉시 요청 가능해야 한다.
- Account deletion request는 앱에서 접근 가능해야 한다.
- 삭제 요청 후 처리 상태를 사용자에게 보여줘야 한다.
- credit ledger, billing, fraud, tax, audit 등 법적/회계 보관이 필요한 데이터는 삭제 대신 익명화 또는 보관 예외로 분리해야 한다.
- generated media는 사용자 삭제, moderation rejection, account deletion과 연결되어야 한다.

개발 요구사항:

- `memories.deleted_at`.
- `media_assets.deleted_at` or inaccessible status.
- `account_deletion_requests`.
- `admin_audit_logs`.
- deletion job status.
- privacy export/delete runbook.

## 8. Content safety checklist

첫 release moderation 기준:

- explicit sexual content: block.
- minor sexualization or ambiguous minor-like character: block.
- self-harm/crisis: safe response and support routing.
- harassment/hate/violent sexual content: block.
- illegal instructions: block.
- user request to generate real-person sexualized image: block.
- generated media before moderation: not visible.

운영 요구사항:

- report queue.
- moderation status.
- admin review action.
- audit log.
- repeated offender handling.
- emergency kill switch for image reward.

## 9. Subscription and credit checklist

스토어/CS 리스크를 줄이기 위해 앱에서 보여야 하는 정보:

- plan price.
- renewal period.
- included daily/monthly allowance.
- purchased credit amount.
- credit spend priority.
- what happens on provider failure.
- refund/restore purchase path.
- subscription cancellation is handled by app store account settings.
- allowance reset timing.
- expired or unused purchased credit policy.

출시 전 반드시 확정할 항목:

- Plus monthly price.
- Premium monthly price.
- credit pack prices.
- purchased credit expiration.
- tax/store fee assumptions.
- refund and chargeback handling.

## 10. Store listing checklist

Store listing에 필요한 자료:

- app name and subtitle.
- AI companion disclosure.
- store-safe screenshots.
- privacy policy URL.
- support URL/email.
- terms URL.
- account deletion URL or in-app path documentation.
- subscription product descriptions.
- generated media moderation statement.
- age rating questionnaire answers.
- data safety/privacy labels.

스크린샷 주의:

- explicit romantic implication을 피한다.
- Airi가 미성년자처럼 보이는 장면을 피한다.
- AI-generated reward image는 실제 사진처럼 오해되지 않게 한다.
- 가격/구독 제공량이 실제 상품과 일치해야 한다.

## 11. Launch country checklist

국가별로 확정해야 할 항목:

- minimum age and age gate behavior.
- privacy policy language.
- terms language.
- tax and store fee assumption.
- refund and consumer protection requirement.
- crisis/safety support copy.
- data transfer disclosure.
- subscription renewal wording.

첫 release 권장:

- 국가를 좁게 시작한다.
- privacy/terms/refund 문구를 해당 국가 기준으로 먼저 닫는다.
- provider latency and cost가 안정적인 지역부터 연다.

## 12. Acceptance criteria

Public beta 전:

- AI disclosure screen exists.
- report/block path exists.
- memory delete path exists.
- account deletion request path exists.
- privacy/terms draft exists.
- generated media moderation status exists.
- subscription/credit display matches backend policy.

Commercial launch 전:

- Google Play policy recheck complete.
- Apple App Review Guideline recheck complete.
- privacy policy published.
- terms published.
- support and deletion URL ready.
- Data safety/App privacy labels completed.
- subscription products and credit packs match in-app copy.
- legal/accounting retention exceptions documented.

## 13. Sources to recheck before submission

- Google Play AI-generated content policy: https://support.google.com/googleplay/android-developer/answer/13985936
- Google Play AI-generated content overview: https://support.google.com/googleplay/android-developer/answer/14094294
- Google Play account deletion requirements: https://support.google.com/googleplay/android-developer/answer/13327111
- Google Play User Data policy: https://support.google.com/googleplay/android-developer/answer/10144311
- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/

