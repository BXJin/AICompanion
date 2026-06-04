# AI Companion + Date Mini-Game Project

## 한 줄 정의

AI 캐릭터와 평소에는 대화로 관계를 쌓고, 앱 안에서는 보드게임/데이트/영화 감상형 미니게임을 같이 하며, 결과가 관계도·보상·스토리·사진/영상 콘텐츠 해금에 반영되는 companion 서비스.

## 시장 판단

이 조합은 완전히 없는 장르는 아니다. 요소별로는 이미 검증되어 있다.

| 영역 | 대표 예시 | 이미 검증된 점 | 비고 |
|---|---|---|---|
| AI companion / 캐릭터챗 | Zeta, Character.AI, Nika | 캐릭터와 대화, 스토리, 메모리, 이미지 생성 | 대화/롤플레잉 중심 |
| AI dating sim / relationship RPG | Nika Aurora City, Love and Deepspace | 관계 레벨, 데이트, 콘텐츠 해금, 보상 루프 | LLM보다는 게임/이벤트 구조 중심 |
| AI game companion | Questie | 화면/게임 맥락을 보고 실시간 반응 | 사용자가 하는 외부 게임을 보조 |
| AI game master | WhisperGames | AI가 퀴즈/파티게임/스토리게임 진행 | companion 관계보다는 게임 진행자 |
| 보드게임 AI 도우미 | BoardBuddy/Ludomentor류 | 룰 설명, 규칙 질의응답 | 연애/친구형 companion과는 거리가 있음 |

따라서 "AI 캐릭터와 보드게임을 한다" 자체는 희귀하지 않다. 차별점은 다음처럼 잡아야 한다.

```text
대화형 AI companion
+ 데이트형 미니게임
+ 승패/선택 결과가 관계도와 해금 콘텐츠에 반영
+ 사진/영상/음성/스토리 보상
+ 캐릭터가 이전 게임 결과를 기억하고 다음 대화에 반영
```

## 참고 서비스 요약

### Zeta

Zeta는 캐릭터와 무제한 채팅하고, 사용자가 스토리의 주인공처럼 전개를 주도하는 서비스다. Google Play 설명 기준으로 캐릭터가 작은 특징과 비밀, 대화 순간을 기억하고, 대화 기반 이미지를 생성하는 기능을 강조한다.

출처: https://play.google.com/store/apps/details?hl=en-US&id=com.scatterlab.messenger

### Nika / Aurora City

Nika는 AI girlfriend/boyfriend companion, Aurora City는 AI dating simulator RPG 성격이 강하다. 공식 설명 기준으로 30단계 Bond System, AI 이미지/영상, voice calls, diary, story generator, UGC scenario marketplace를 제공한다. Aurora City는 RPG stats, jobs, seasonal events, relationship levels를 통해 dates/sleepovers/marriage를 해금하는 구조를 설명한다.

출처: https://nika.team/en/

### Love and Deepspace

Love and Deepspace는 LLM companion 서비스는 아니지만, companion와의 dates, Kitty Cards, claw machine, audio/visual stories, affinity, memories, combat reward 구조가 강하다. "데이트형 콘텐츠 + 미니게임 + 보상/메모리/스토리 해금"이 이미 상용적으로 검증된 방향이라는 근거가 된다.

출처: https://en.wikipedia.org/wiki/Love_and_Deepspace

### Questie

Questie는 사용자의 게임 화면을 실시간으로 보고 voice chat으로 반응하는 AI gaming companion이다. companion가 게임을 "같이 하는 느낌"을 주는 방향은 검증되어 있지만, 앱 내부에서 companion와 데이트형 보드게임을 하는 구조와는 다르다.

출처: https://www.questie.ai/

### WhisperGames

WhisperGames는 AI Game Master가 파티게임, 퀴즈, 수수께끼, 미스터리, 솔로 어드벤처를 진행한다. AI가 게임 규칙을 설명하고 질문을 던지며 사용자의 음성에 반응하는 구조다. 다만 관계형 companion보다 게임 진행자에 가깝다.

출처: https://whispergames.ai/

## 핵심 제품 구조

```text
User
-> Chat / Voice input
-> Character dialogue
-> Relationship state update
-> Mini-game invitation
-> Game rule engine
-> Result judgement
-> Reward / unlock
-> Memory / story event update
-> Character response + generated media
```

## 기술적으로 중요한 분리

LLM에게 게임 판정을 맡기면 안 된다.

```text
GameRuleEngine
- 승패 판정
- 점수 계산
- 턴 상태
- 보상 조건
- 해금 조건

LLM
- 캐릭터 말투
- 감정 반응
- 힌트/장난/칭찬
- 이벤트 대사
- 스토리 문장 생성
```

이렇게 분리해야 같은 입력에 같은 결과가 나오고, 보상 악용을 막을 수 있다.

## MVP 제안

풀스케일 dating sim으로 시작하면 범위가 너무 크다. 첫 MVP는 하나의 게임 루프만 잡는 게 맞다.

### MVP 1: Airi와 짧은 카드 선택 게임

- 하루 1~3회 플레이
- 사용자는 선택지 2~3개 중 하나 선택
- 서버가 결과 판정
- Airi가 짧게 반응
- 관계도/친밀도/기분이 소폭 변화
- 일정 조건 달성 시 사진/음성/짧은 스토리 해금

### MVP 2: 영화 감상 데이트

- 사용자가 영화/장르/감상 포인트를 입력
- Airi가 같이 본 것처럼 대화하되, 실제 경험을 과도하게 주장하지 않음
- 대화 결과로 "감상 카드" 또는 "데이트 기록" 생성
- 다음 대화에서 해당 감상 기록을 기억

### MVP 3: 보드게임 룰 엔진

- 틱택토/카드 뽑기/주사위/간단한 추리게임처럼 판정이 쉬운 게임부터 시작
- 게임 결과가 relationship state에 반영
- LLM은 "졌을 때 삐짐", "이겼을 때 놀림", "아슬아슬했을 때 긴장" 같은 반응만 담당

## 차별점 후보

| 차별점 | 설명 |
|---|---|
| 결과 기억 | "지난번에 네가 이겼잖아"처럼 게임 결과를 다음 대화에 반영 |
| 관계 기반 난이도/반응 | 친밀도가 높아질수록 장난, 질투, 특별 대사 증가 |
| 콘텐츠 보상 | 사진, 음성 메시지, 짧은 영상, 스토리 이벤트 해금 |
| 데이트 로그 | 같이 한 게임/영화/대화가 앨범처럼 쌓임 |
| 룰 엔진 분리 | LLM hallucination 없이 안정적인 게임 결과 제공 |

## 리스크

| 리스크 | 이유 | 대응 |
|---|---|---|
| AI 여친앱 정책 리스크 | 캐릭터 나이, 선정성, 과몰입 유도 이슈 | 성인 캐릭터 명시, 안전 정책, 수위 제한 |
| 보상 악용 | LLM이 보상을 임의로 지급하면 경제 구조 붕괴 | GameRuleEngine이 보상 판정 |
| 비용 증가 | 이미지/영상 생성은 대화보다 비쌈 | 보상형/쿨다운/광고/유료 재화 |
| 차별성 약화 | AI companion 앱은 이미 많음 | "같이 노는 데이트형 게임 루프"를 전면에 둠 |
| 범위 과대 | chat, game, reward, media를 동시에 만들면 느려짐 | MVP는 1개 게임 + 1개 보상 루프로 제한 |

## 현재 판단

이 아이디어는 "AI companion" 하나만으로 보면 흔하다. 하지만 "캐릭터와 실제로 앱 안에서 데이트형 미니게임을 하고, 결과가 관계/보상/스토리에 반영된다"는 구조는 포트폴리오와 MVP 모두에서 쓸 만한 차별점이 있다.

다만 첫 구현은 3D/실시간 렌더링보다 웹/앱 서비스 구조에 가깝다. PromptMotionLab의 UE5 렌더링 자산보다는 서버 구조, provider 구조, 캐릭터 말투 평가, latency 관리 경험을 재활용하는 쪽이 현실적이다.
