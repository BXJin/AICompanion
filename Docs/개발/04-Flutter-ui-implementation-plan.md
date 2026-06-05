# Flutter UI implementation plan from portfolio mockups

작성일: 2026-06-05

이 문서는 `Docs/Portfolio/01.png`, `02.png`, `03.png` 목업을 Flutter 실제 앱 UI로 옮기기 위한 개발 기준이다.

목업은 포트폴리오/화면 설계서 성격이 강하다. Flutter 앱에서는 목업 전체를 픽셀 단위로 복제하지 않고, 실제 사용자가 보는 모바일 화면과 재사용 컴포넌트로 재구성한다.

## 1. Source of truth

우선순위:

```text
1. Docs/기획/16-Mobile-user-journey-and-screen-IA.md
2. Docs/기획/17-Mobile-API-contract.md
3. Docs/기획/31-Mobile-admin-wireframe-design-system-spec.md
4. Docs/Portfolio/01.png, 02.png, 03.png
5. This document
```

판단:

- `Docs/기획/16`은 화면 목적, UX 흐름, 상태 정의의 기준이다.
- `Docs/기획/17`은 API contract의 기준이다.
- `Docs/기획/31`은 디자인 시스템/와이어프레임 기준이다.
- `Docs/Portfolio` 이미지는 시각 참고 자료다.
- 이 문서는 Flutter 구현 단위와 작업 순서를 정의한다.

## 2. Mockup decomposition

### 01.png

성격:

- 마케팅/포트폴리오 보드와 앱 화면이 섞여 있다.

앱에 반영:

- Chat tab.
- Date tab.
- Rewards tab.
- Profile tab.
- relationship stat card.
- quota badge.
- reward summary card.

앱에 넣지 않음:

- iPhone 프레임.
- 브랜드 포스터 레이아웃.
- 하단 마케팅 문구/아이콘 설명.
- 포트폴리오용 큰 hero composition.

### 02.png

성격:

- Onboarding 완료와 main chat 상태 설계서.

앱에 반영:

- Airi intro.
- first chat.
- quota exceeded.
- provider degraded.
- safety blocked.
- pending queue/degraded state.
- chat bubble.
- relationship feedback card.

앱에 넣지 않음:

- 문서 상단 flow chip row.
- QA 기준 설명 박스.
- retention 기준 설명 박스.

### 03.png

성격:

- Date / Rewards / Airi Moment 화면 설계서.

앱에 반영:

- Date list.
- Date play.
- Rewards list.
- reward status badge.
- memory candidate card.
- date result feedback.
- locked/rejected/moderation_hold/duplicate_submit 상태.

앱에 넣지 않음:

- rule engine 설명 표.
- score band 설명 박스.
- 설계서용 상태 설명 카드.

## 3. Flutter screen scope

초기 구현 화면:

```text
Onboarding
  SplashScreen
  AgeGateScreen
  ConsentScreen
  AiriIntroScreen
  GuestStartScreen

Main
  MainShell
  ChatScreen
  DateListScreen
  DatePlayScreen
  RewardsScreen
  ProfileScreen

State
  QuotaExceededView
  ProviderDegradedBanner
  SafetyBlockedMessage
  PendingQueueView
```

초기에는 실제 API 연결 전 mock data로 화면을 완성한다. 이후 `Docs/기획/17-Mobile-API-contract.md` 기준으로 repository/API layer를 연결한다.

## 4. Component inventory

필수 컴포넌트:

- `AiriAvatar`
- `RelationshipStatCard`
- `QuotaBadge`
- `ChatBubble`
- `ReplySuggestionChip`
- `DateEventCard`
- `DateProgressHeader`
- `DateChoiceButton`
- `DateResultCard`
- `RewardTile`
- `StatusBadge`
- `MemoryCandidateCard`
- `ProviderDegradedBanner`
- `SafetyBlockedMessage`
- `PendingQueueView`
- `BottomNav`
- `PrimaryButton`
- `SecondaryButton`
- `IconActionButton`

원칙:

- 앱 화면 컴포넌트와 포트폴리오 보드 컴포넌트를 섞지 않는다.
- 화면 설명용 표/QA 기준 카드는 앱 컴포넌트로 만들지 않는다.
- 서버가 소유하는 상태는 Flutter에서 계산하지 않고 표시만 한다.

## 5. Design tokens

초기 token은 목업의 방향만 가져온다.

```text
color
  background: warm off-white
  surface: white
  primary: muted green
  primaryDark: deep green
  accent: soft lime
  danger: muted red/orange
  warning: muted orange
  textPrimary: near black
  textSecondary: warm gray
  border: light warm gray

radius
  card: 16
  button: 16
  chip: 999
  bottomSheet: 24

spacing
  xs: 4
  sm: 8
  md: 12
  lg: 16
  xl: 24
  xxl: 32
```

주의:

- 목업의 포스터용 큰 타이포그래피를 앱 내부 제목에 그대로 쓰지 않는다.
- iOS/Android 모두에서 텍스트가 잘리지 않도록 line height와 dynamic text를 고려한다.
- 채팅, Date, Rewards는 반복 사용 화면이므로 과한 장식보다 가독성을 우선한다.

## 6. Recommended Flutter structure

초기 폴더명은 `Mobile/`을 권장한다.

```text
Mobile/
  lib/
    app/
      app.dart
      router.dart
      theme/
        app_colors.dart
        app_spacing.dart
        app_typography.dart
        app_theme.dart
    core/
      api/
      errors/
      models/
      widgets/
    features/
      onboarding/
        presentation/
      chat/
        data/
        domain/
        presentation/
      date/
        data/
        domain/
        presentation/
      rewards/
        data/
        domain/
        presentation/
      profile/
        data/
        domain/
        presentation/
```

상태 관리:

- 초기 추천: Riverpod.
- 이유: 화면별 상태, async API, mock repository 교체가 단순하다.
- 대안: Bloc은 팀이 Bloc에 익숙할 때만 선택한다.

라우팅:

- 초기 추천: `go_router`.
- 탭 구조는 `MainShell` 아래에서 관리한다.

## 7. Mock data first policy

첫 Flutter 작업은 API 대기 없이 mock repository로 진행한다.

Mock data로 먼저 구현:

- Airi profile.
- relationship stats.
- chat messages.
- reply suggestions.
- daily quota state.
- date event list.
- date play progress.
- reward list/status.
- memory candidate.
- provider degraded/safety blocked/pending states.

금지:

- mock data에 서버 business rule을 숨겨 넣지 않는다.
- date result, credit, reward unlock, relationship delta를 client-only rule로 확정하지 않는다.
- API 미구현 상태를 화면 내부 if문으로 영구 우회하지 않는다.

## 8. API connection order

Flutter API 연결 순서:

1. app bootstrap.
2. guest auth/session.
3. chat turn.
4. relationship/memory summary read.
5. date event list/start/move/finish.
6. reward gallery.
7. quota/credit status.
8. report/delete/settings.

연결 규칙:

- `/api/mobile/v1/*`만 호출한다.
- admin/webhook API를 호출하지 않는다.
- API shape mismatch는 `handoff.md`에 기록한다.
- `Docs/기획/17-Mobile-API-contract.md`와 실제 schema가 다르면 UI에서 임의 보정하지 않는다.

## 9. State and error UX

반드시 구현할 상태:

- loading.
- empty.
- offline.
- provider_degraded.
- quota_exceeded.
- safety_blocked.
- pending.
- failed.
- retryable.
- locked.
- moderation_hold.
- rejected.
- duplicate_submit.

특히 필요한 UX:

- quota exceeded는 shop/paywall로 이어질 수 있어야 한다.
- provider degraded는 사용자가 앱이 멈춘 것으로 느끼지 않게 배너나 pending view로 표현한다.
- safety blocked는 일반 오류처럼 보이면 안 된다.
- reward pending/rejected/failed는 credit/refund 정책과 연결되어야 한다.

## 10. Build sequence

권장 순서:

1. Flutter project skeleton.
2. theme/design token.
3. MainShell + bottom navigation.
4. mock repository layer.
5. ChatScreen.
6. DateListScreen.
7. DatePlayScreen.
8. RewardsScreen.
9. ProfileScreen.
10. onboarding flow.
11. state/error views.
12. API repository implementation.
13. contract mismatch pass with backend session.

완료 기준:

- 목업의 핵심 화면이 실제 앱 화면으로 분리되어 있다.
- iPhone frame/portfolio board UI는 앱 코드에 없다.
- Chat/Date/Rewards/Profile을 mock data로 이동할 수 있다.
- quota/provider/safety/pending/rejected 상태가 눈에 보인다.
- 서버 소유 상태를 Flutter가 계산하지 않는다.

## 11. Non-goals

초기 Flutter 작업에서 하지 않는다.

- 목업 이미지 전체를 복제하는 포스터 화면.
- iPhone 프레임 렌더링.
- rule engine 설명 표를 앱 화면으로 구현.
- live voice call.
- video generation.
- multi-character UI.
- custom character marketplace.
