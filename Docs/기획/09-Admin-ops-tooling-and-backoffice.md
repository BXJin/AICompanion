# Admin, ops tooling, and backoffice

첫 release 전에 반드시 구현할 최소 admin 화면과 RBAC/audit 기준은 `21-Admin-minimum-screen-spec.md`를 따른다.

상용 AI companion 앱은 운영툴 없이는 출시하면 안 된다. 이유는 단순하다. AI 앱은 비용, 안전, CS, abuse, 결제 문제가 매일 발생한다.

## 운영툴이 필요한 이유

- 사용자가 "기억 삭제해줘"라고 요청한다.
- 결제는 됐는데 credit이 안 들어온다.
- 이미지 생성 결과가 정책 위반이다.
- 특정 사용자가 API를 과도하게 호출한다.
- provider 장애로 queue가 밀린다.
- 무료 사용자의 광고 보상이 중복 지급된다.
- 캐릭터 답변이 부적절하다는 신고가 들어온다.

이것을 DB 직접 조회로 처리하면 운영 사고가 난다.

## Admin role

### Super Admin

- 전체 권한.
- 결제/credit 조정.
- provider kill switch.
- policy 변경.

### CS Operator

- 사용자 조회.
- 구독 상태 확인.
- credit 지급/회수 요청.
- 환불 상태 확인.
- 단, 원문 대화 열람은 제한.

### Moderator

- 신고된 대화/이미지 검토.
- 제재 처리.
- 콘텐츠 정책 판단.

### Content Ops

- date event template.
- reward table.
- character copy.
- prompt/fewshot pack 관리.

### Developer Ops

- provider status.
- queue status.
- logs/latency/error 확인.
- rollout/rollback.

### Finance Ops

- revenue.
- provider cost.
- margin.
- refund.
- plan별 unit economics.

## 필수 admin 화면

### 1. User lookup

조회 항목:

- user id
- 가입일
- plan
- app version
- device
- country
- credit balance
- recent provider cost
- moderation status

주의:

- 이메일/전화번호는 hash 또는 masked display.
- 대화 원문 접근은 별도 권한과 사유 입력 필요.

### 2. Conversation inspector

목적:

- 신고/장애/품질 이슈 확인.

표시:

- message timeline
- model/provider
- latency
- safety result
- memory injected 여부
- generated behavior
- TTS/image job 여부

필수:

- admin audit log.
- 개인정보 최소 노출.

### 3. Memory manager

기능:

- 사용자 memory 목록 조회.
- memory importance 확인.
- memory 삭제.
- 잘못 추출된 memory 비활성화.
- memory source 확인.

사용자도 앱에서 memory 삭제/수정 요청이 가능해야 한다.

### 4. Credit ledger viewer

기능:

- credit 입출금 내역.
- subscription allowance 지급 내역.
- ad reward 지급 내역.
- purchased credit 사용 내역.
- idempotency key 확인.

credit 문제는 반드시 ledger 기준으로 해결한다.

### 5. Provider cost dashboard

필수 지표:

- provider별 비용.
- model별 비용.
- feature별 비용.
- user plan별 비용.
- DAU 대비 cost/user/day.
- fallback rate.
- timeout rate.

위험 알림:

- free user cost spike.
- image/video job spike.
- provider failure.
- queue latency 증가.
- budget threshold 초과.

### 6. Queue monitor

Queue:

- chat queue.
- voice queue.
- TTS queue.
- image generation queue.
- memory extraction queue.
- moderation queue.

지표:

- waiting jobs.
- average wait time.
- p90 wait time.
- failed jobs.
- retry count.

### 7. Content/event manager

기능:

- date event template 생성.
- reward policy 설정.
- event 기간 설정.
- plan별 접근 제한.
- A/B test group.

LLM에게 게임 판정을 맡기지 않고, rule engine template을 운영자가 관리해야 한다.

### 8. Prompt/version manager

기능:

- character prompt version.
- fewshot pack.
- safety policy version.
- model route version.
- rollout percentage.
- rollback.

prompt 변경도 배포와 같다. 버전, 테스트, rollback이 필요하다.

### 9. Moderation review

대상:

- 신고된 대화.
- 생성 이미지.
- character policy violation.
- self-harm or crisis.
- adult/minor risk.

기능:

- approve/reject.
- warning.
- temporary ban.
- permanent ban.
- escalate to human review.

### 10. Experiment dashboard

지표:

- D1/D7 retention.
- paid conversion.
- average turns.
- ad view rate.
- image credit purchase rate.
- memory feature usage.
- date event completion.

## 운영 알림

필수 alert:

- provider cost daily cap 70/90/100%.
- queue p90 wait > threshold.
- LLM fallback rate spike.
- TTS/image provider error spike.
- payment webhook failure.
- credit ledger mismatch.
- moderation queue backlog.
- app crash/freezing spike.

## CS 시나리오

### 결제했는데 credit 없음

1. payment event 확인.
2. credit ledger idempotency 확인.
3. 누락이면 manual credit grant.
4. audit log 기록.

### AI가 이상한 말을 함

1. conversation inspector에서 turn 확인.
2. prompt/model/safety version 확인.
3. 신고 처리.
4. 필요 시 prompt rollback 또는 safety rule update.

### 이미지가 부적절함

1. media asset moderation status 확인.
2. provider prompt/result 확인.
3. asset disable.
4. user에게 credit refund 여부 판단.

## PromptMotionLab과의 차이

PromptMotionLab은 포트폴리오 데모라서 로그와 테스트 CSV 중심이면 충분했다.

상용앱은 다음이 추가되어야 한다.

- admin UI.
- audit log.
- CS workflow.
- refund/credit adjustment.
- provider cost dashboard.
- moderation review.
- prompt rollout.
- experiment tracking.
