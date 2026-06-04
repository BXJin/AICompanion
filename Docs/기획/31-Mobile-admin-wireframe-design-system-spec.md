# Mobile and admin wireframe/design system spec

작성일: 2026-06-04

이 문서는 첫 상용 release의 모바일 앱과 최소 admin 화면을 실제 구현 가능한 수준으로 정리한다. `16-Mobile-user-journey-and-screen-IA.md`가 사용자 여정과 상태를 정의했다면, 이 문서는 화면 배치, 주요 컴포넌트, copy, permission, store screenshot 기준을 정의한다.

목표는 고해상도 디자인 시안을 대체하는 것이 아니다. 개발자가 Flutter/admin skeleton을 만들 때 화면 구조와 상태 처리를 임의로 해석하지 않도록 하는 baseline이다.

## 1. Product UI direction

첫 release UI 원칙:

- Chat-first.
- Airi와 관계 상태가 첫 화면에서 즉시 보여야 한다.
- Date, Reward, Memory는 별도 기능처럼 흩어지지 않고 Chat loop와 연결되어야 한다.
- Shop은 독립 탭이 아니라 quota/reward/profile 맥락에서 진입한다.
- 무료 사용자는 제한을 이해해야 하지만, 첫날 경험이 과금 벽처럼 느껴지면 안 된다.
- provider degraded, queue pending, moderation rejected, quota exceeded 상태를 숨기지 않는다.

시각 톤:

- companion 서비스이지만 과한 성인/선정적 분위기를 피한다.
- Airi는 adult-coded이되 store-safe romantic/suggestive 범위로 표현한다.
- 운영/설정 화면은 감성보다 명확성을 우선한다.
- paywall은 제공량, reset, credit 차감 기준을 숨기지 않는다.

## 2. Navigation

하단 탭:

| Tab | Purpose | Primary CTA |
|---|---|---|
| Chat | Airi와 일상 대화, voice/TTS, 관계 상태 | Send message |
| Date | 오늘 가능한 date event, 진행 중 session | Start date |
| Rewards | unlocked/pending/rejected reward gallery | View reward |
| Profile | Airi profile, memory, plan, settings | Manage |

Global entry:

- Shop/paywall: quota exceeded, reward locked, Profile plan card에서 진입.
- Settings: Profile 상단.
- Report: Chat message long press, media detail, Settings.
- Memory delete: Profile > Memory.
- Account deletion: Profile > Settings > Account.

## 3. Mobile screen wireframes

### 3.1 Onboarding and age gate

Layout:

```text
[Airi hero visual]
[AI companion disclosure]
[Age gate]
[Terms/Privacy consent]
[Start]
```

Required copy:

- Airi is an AI companion.
- Responses and media may be AI-generated.
- This app is not emergency, medical, legal, or financial support.
- Explicit adult content is not supported.

States:

- loading.
- consent unchecked.
- underage blocked or restricted.
- network error.
- continue as guest.
- sign in.

Acceptance:

- user cannot start without AI disclosure and required consent.
- underage policy routes match PM decision.
- privacy/terms links open.

### 3.2 Chat home

Layout:

```text
[Top: Airi name + relationship level + mood chip]
[Conversation list]
[Context hint: remembered topic/date hint/quota notice]
[Input row: text input + voice button + send]
[Optional TTS playback chip]
```

Primary states:

- empty first greeting.
- sending.
- thinking.
- streaming.
- provider degraded.
- quota exceeded.
- safety blocked.
- offline/retry.
- TTS pending/ready/failed.

Message actions:

- copy.
- report.
- delete local view if supported.
- regenerate only when cost policy allows.

Acceptance:

- first screen shows Airi, relationship level, and a clear input.
- quota exceeded connects to ad/shop/upgrade with exact reason.
- provider degraded gives useful fallback, not a silent failure.
- report path is reachable from a message.

### 3.3 Voice input

Layout:

```text
[Recording modal/sheet]
[Waveform or level indicator]
[Timer + remaining allowance]
[Cancel] [Send]
```

Permission copy:

- Microphone permission is used to transcribe your voice message to Airi.
- Voice input may be processed by an AI/STT provider.

States:

- permission needed.
- recording.
- processing.
- transcription ready.
- STT failed.
- limit reached.

Acceptance:

- user can fall back to text input.
- failed STT does not charge credit unless policy explicitly says otherwise.
- remaining allowance is visible before recording if limited.

### 3.4 Date tab

Layout:

```text
[Today with Airi]
[Recommended date event card]
[Relationship requirement/progress]
[Reward hint]
[Start date]
[Past date summaries]
```

States:

- no event available.
- event available.
- session active.
- session expired.
- event completed.
- reward pending.
- quota/credit required.

Acceptance:

- only official event templates from `19` are shown.
- result/reward is deterministic and not decided by LLM.
- user sees why an event is locked.

### 3.5 Date play screen

Layout:

```text
[Scene title]
[Airi reaction]
[Situation prompt]
[Choice buttons]
[Progress indicator]
[Finish/result]
```

States:

- move pending.
- duplicate move ignored.
- finish pending.
- result computed.
- reward unlock pending.
- network retry.

Acceptance:

- choices are clear and tappable.
- duplicate submit does not create duplicate reward/credit events.
- result screen explains relationship/reward change.

### 3.6 Rewards gallery

Layout:

```text
[Filter: All / Unlocked / Pending / Rejected]
[Reward grid]
[Reward detail]
[Moderation status]
[Report]
```

States:

- locked.
- progress.
- generation pending.
- moderation pending.
- unlocked.
- rejected.
- failed/refunded.

Acceptance:

- generated media is not visible before moderation pass.
- rejected media explains status without exposing unsafe output.
- reward detail has report path.

### 3.7 Profile and memory

Layout:

```text
[Airi profile header]
[Relationship stats]
[Memory cards]
[Plan/credit summary]
[Settings]
```

Memory card actions:

- view.
- delete.
- report if unsafe.

Acceptance:

- user can see what Airi remembers at a summary level.
- memory deletion is obvious and has status.
- plan/credit summary matches backend ledger.

### 3.8 Shop/paywall

Layout:

```text
[Current plan]
[Usage/allowance]
[Plus plan]
[Premium plan]
[Credit packs]
[Restore purchases]
[Terms/refund note]
```

Required display:

- renewal period.
- included allowance.
- credit amount.
- reset timing.
- cancellation path.
- restore purchase.
- provider failure/refund policy summary.

Acceptance:

- no unlimited claim unless backend cap truly supports it.
- price/product ids are environment-specific.
- purchase pending and webhook delayed states are handled.

### 3.9 Settings/privacy/support

Layout:

```text
[AI disclosure]
[Privacy]
[Terms]
[Report content]
[Memory management]
[Account deletion request]
[Subscription management]
[Support]
```

Acceptance:

- report/delete/account deletion paths match `28`.
- AI disclosure is reachable after onboarding.
- support path is visible.

## 4. Component baseline

Core components:

| Component | Usage |
|---|---|
| ChatMessageBubble | user/Airi messages, streaming, error |
| RelationshipChip | level, mood, affinity hint |
| QuotaNotice | remaining usage, upgrade/ad/shop CTA |
| ProviderStatusBanner | degraded/fallback/queued |
| VoiceRecordButton | permission/recording/processing |
| DateEventCard | event status, requirement, reward |
| ChoiceButton | deterministic date move |
| RewardTile | locked/pending/unlocked/rejected |
| MemoryCard | memory summary/delete status |
| PlanCard | allowance, price, renewal |
| CreditBalanceBadge | current credit and pending adjustments |
| ReportSheet | target, category, details |
| DeleteConfirmSheet | memory/account/media delete |

Component rules:

- Buttons must have fixed hit area and loading state.
- Cost-impacting actions require disabled/loading/idempotency states.
- Quota notices must include feature route and reset/upgrade option.
- Error components must show retry only when retry is safe.
- Report/delete components must not be hidden behind long text.

## 5. Design tokens

Initial token set:

| Token | Value |
|---|---|
| spacing_xs | 4 |
| spacing_sm | 8 |
| spacing_md | 12 |
| spacing_lg | 16 |
| spacing_xl | 24 |
| radius_sm | 6 |
| radius_md | 8 |
| radius_lg | 12 |
| min_touch_target | 44 |

Color roles:

- background.
- surface.
- surface_muted.
- text_primary.
- text_secondary.
- accent.
- success.
- warning.
- danger.
- premium.
- disabled.

Typography roles:

- screen_title.
- section_title.
- body.
- caption.
- button.
- metric.

Accessibility:

- minimum touch target 44px.
- text contrast must pass platform baseline.
- voice-only flow must have text fallback.
- color cannot be the only status indicator.

## 6. Admin wireframes

### 6.1 User lookup

Layout:

```text
[Search user]
[User identity summary]
[Plan/credit summary]
[Recent safety/report flags]
[Actions]
```

Actions:

- view ledger.
- view reports.
- request deletion status.
- manual credit adjustment if authorized.

### 6.2 Credit ledger viewer

Layout:

```text
[User summary]
[Balance snapshot]
[Ledger table]
[Replay check]
[Adjustment request]
```

Acceptance:

- append-only ledger is visible.
- adjustment requires reason.
- approval is required for high-risk action.

### 6.3 Provider cost dashboard

Layout:

```text
[Daily spend]
[Cost by route]
[Provider failure/fallback]
[Top expensive users]
[Kill switch status]
```

Acceptance:

- operator can identify runaway cost.
- kill switch status is visible.
- provider route attribution exists.

### 6.4 Queue monitor

Layout:

```text
[Queue list]
[Oldest job age]
[Retry/dead letter count]
[Pause/resume controls]
[Job detail]
```

Acceptance:

- expensive queues can be paused.
- failed jobs retain enough trace for debugging.

### 6.5 Moderation review

Layout:

```text
[Report/moderation queue]
[Target content summary]
[Policy category]
[Decision buttons]
[Audit reason]
```

SLA draft:

- SEV0 safety exposure: immediate triage.
- user report involving self-harm/crisis: same day triage.
- generated media rejection appeal: 3 business days.
- general content report: 5 business days.

### 6.6 Admin audit log

Layout:

```text
[Filters: admin/user/action/date]
[Audit event table]
[Diff or action metadata]
[Export restricted]
```

Acceptance:

- every sensitive admin action has actor, reason, target, timestamp.
- audit log is immutable from normal admin UI.

## 7. Store screenshot strategy

Required screenshots:

- Chat with Airi and relationship level.
- Date event card and safe choice UI.
- Reward gallery with safe unlocked/pending states.
- Memory/profile with user control.
- Plan/credit screen with transparent allowance.

Avoid:

- suggestive visual that could imply explicit adult content.
- minor-like styling.
- fake unlimited claims.
- screenshots showing unsafe generated media.
- screenshots where AI disclosure is absent from onboarding material.

## 8. Definition of ready for design implementation

Mobile ready:

- screen list exists.
- each screen has default/loading/error/empty states.
- quota/provider/moderation/payment states are represented.
- reusable components are listed.
- permission copy exists.
- store screenshot direction exists.

Admin ready:

- minimum 6 admin screens have layout and actions.
- moderation SLA draft exists.
- sensitive actions require RBAC and audit.
- cost/queue/moderation operations are visible.

