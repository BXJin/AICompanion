# Live ops playbook

작성일: 2026-06-05

이 문서는 AI Companion / 연애 시뮬레이션 앱을 실제로 운영할 때 운영자가 매일 보는 것과, 문제가 생겼을 때 어떤 순서로 줄일지 정리한다.

## 1. 운영자가 매일 봐야 하는 것

Daily dashboard:

- active users: DAU, new users, returning users.
- core loop: first chat success, second chat rate, date event start/finish.
- latency: chat p50/p95, TTS first audio p95, STT final p95, image queue p95.
- cost: provider spend today, cost/user/day, top 1% user cost, failed provider cost.
- quota: quota exceeded count, shop/paywall view, credit refund count.
- safety: report count, blocked content count, moderation backlog, unsafe media rejection.
- ops: API 5xx, provider error, queue backlog, oldest job age, billing webhook failures.
- quality: image rejection rate, character consistency complaints, TTS failure rate.

운영 판단:

- DAU가 늘어도 cost/user/day가 같이 오르면 성장으로 보지 않는다.
- latency가 좋아도 first chat -> second chat이 낮으면 캐릭터/UX 문제다.
- 신고가 적어도 report 진입률이 낮으면 안전하다는 증거가 아니다.
- 결제 전환이 높아도 refund/CS가 같이 늘면 가격/기대치 문제다.

## 2. 주간 운영 회의

Weekly agenda:

1. Product loop: first chat, second chat, D1/D7, date event completion.
2. Character quality: Airi tone complaint, memory mismatch, image consistency issue.
3. Cost and abuse: provider cost, top spenders, quota abuse, retry storm.
4. Safety and CS: report categories, moderation SLA, refund/chargeback, account deletion.
5. Release control: prompt/provider/model/config changes and rollback criteria.
6. Action items: owner, due date, metric expected to move.

## 3. CS 카테고리와 1차 처리

| Category | Example | First action | Escalation |
|---|---|---|---|
| Billing | 결제했는데 credit 없음 | ledger/source reference 확인 | store webhook/reconciliation |
| Refund | 실패했는데 차감됨 | provider event + ledger 확인 | compensating ledger |
| Character | Airi가 기억을 틀림 | memory event/retrieval 확인 | memory delete/fix |
| Image quality | 얼굴이 매번 다름 | asset lineage/prompt version 확인 | regen/refund/provider review |
| Safety | 부적절한 답변 | safety event/report 확인 | content disable/prompt patch |
| Privacy | 기억 삭제/계정 삭제 | deletion job 생성/상태 확인 | privacy owner |
| Voice | TTS 지연/실패 | job/provider latency 확인 | fallback voice/text-only |

CS 금지:

- DB balance를 직접 수정하지 않는다. 반드시 ledger event로 보정한다.
- 사용자의 민감 대화 원문을 불필요하게 열람하지 않는다.
- prompt를 운영자가 임의로 즉시 바꾸지 않는다. 버전/rollback이 필요하다.
- 이미지 moderation 상태를 건너뛰고 수동 공개하지 않는다.

## 4. Prompt / model / provider 변경 운영

모든 변경은 운영 이벤트로 기록한다.

```text
Change:
- date:
- owner:
- target: prompt / model / provider / voice / safety rule
- affected feature:
- rollout scope:
- expected effect:
- rollback trigger:
- dashboard to watch:
```

변경 후 24시간 관찰:

- chat completion rate.
- safety block rate.
- report rate.
- cost per chat.
- latency p95.
- memory extraction quality.
- Airi tone complaint.

rollback 기준 예시:

- report rate가 이전 7일 평균 대비 2배 이상.
- cost/chat이 30% 이상 증가.
- chat p95가 30% 이상 악화.
- Airi 캐릭터 말투 불일치 CS가 유의미하게 증가.
- safety block이 급감했는데 신고가 증가.

## 5. 비용 폭주 대응

대응 순서:

1. feature_route별 비용을 확인한다.
2. offending route, user segment, provider를 분리한다.
3. high-cost feature kill switch 또는 slow mode를 켠다.
4. free plan allowance를 일시적으로 낮춘다.
5. image/video queue를 pause한다.
6. 실패 provider retry를 줄이고 fallback/text-only로 전환한다.
7. credit refund 정책을 확인하고 필요한 보정 ledger를 생성한다.

금지:

- 조용히 품질만 낮추고 공지/UX 상태를 숨기지 않는다.
- paid user의 유료 allowance를 임의로 줄이지 않는다.
- 실패한 provider 호출 비용을 사용자에게 떠넘기지 않는다.

## 6. Provider 장애 대응

대응 순서:

1. provider status와 내부 최근 배포를 확인한다.
2. affected route를 분리한다: chat, STT, TTS, image.
3. fallback provider가 있으면 traffic을 전환한다.
4. fallback이 없으면 degraded mode를 켠다.
5. 모바일에 pending/failed/retry 상태를 보여준다.
6. paid 사용자의 실패 차감은 refund/compensating ledger로 처리한다.
7. incident 기록과 postmortem action item을 남긴다.

## 7. Safety incident 대응

SEV0/SEV1 예시:

- unsafe generated media가 여러 사용자에게 노출.
- 미성년자처럼 보이는 캐릭터가 romantic/sexual context로 노출.
- self-harm/crisis 응답이 부적절.
- 개인정보가 prompt/context/log에 과다 포함.

대응 순서:

1. 노출 차단: asset disable, prompt rollback, feature kill switch.
2. 영향 범위 확인: user count, asset count, route, prompt/model version.
3. 증거 보존: safety event, report, admin audit, provider request id.
4. 임시 정책 적용: stricter moderation, image queue pause, text-only mode.
5. 사용자/스토어/법무 커뮤니케이션 필요성 판단.
6. postmortem 작성: root cause, missed detection, prevention.

## 8. Relationship / memory 운영

관찰 지표:

- memory_saved count.
- memory_deleted count.
- memory complaint count.
- retrieval miss complaint.
- relationship level correction request.
- repeated hallucinated memory reports.

운영 기준:

- 사용자가 삭제한 memory는 retrieval에서 즉시 제외된다.
- 민감정보 memory는 저장하지 않는다.
- Airi가 모르는 내용을 아는 척하는 빈도가 높으면 memory prompt를 줄인다.
- relationship delta는 LLM이 아니라 서버 rule/service가 결정한다.
- 수동 보정이 필요하면 admin audit와 reason을 남긴다.

## 9. Feature kill switch 목록

필수 kill switch:

- chat provider route.
- STT.
- TTS.
- image generation.
- reward media unlock.
- date event start.
- credit spend for high-cost routes.
- rewarded ads.
- billing grant.
- memory extraction.
- memory retrieval.
- unsafe prompt category.

kill switch UX:

- 기능이 사라진 것처럼 보이게 하지 않는다.
- "일시적으로 사용할 수 없음", "보상/credit 상태는 유지됨"을 명확히 보여준다.
- paid user에게 영향이 있으면 CS/보정 기준을 같이 둔다.

## 10. 운영자가 직접 DB를 만지면 안 되는 영역

- credit balance.
- subscription entitlement.
- reward unlock.
- relationship level.
- memory deletion state.
- generated media moderation state.
- report/moderation decision.

이 영역은 반드시 service/admin API를 통해 변경하고 audit/ledger/event를 남긴다.
