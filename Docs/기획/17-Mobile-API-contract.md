# Mobile API contract

작성일: 2026-06-04

이 문서는 첫 상용 모바일 release의 API 계약 초안이다.

기준 문서:

- `13-Mobile-first-commercial-detail-plan.md`
- `16-Mobile-user-journey-and-screen-IA.md`
- `07-Data-model-state-and-ledger-design.md`
- `18-DB-schema-and-ledger-migration-plan.md`
- `19-Date-event-rule-spec.md`
- `20-Credit-plan-allowance-policy.md`
- `22-Airi-character-profile-v1.md`
- `23-Relationship-memory-rule-table.md`
- `25-OpenAPI-Pydantic-schema-plan.md`
- `Docs/개발/01-Development-plan-and-tech-stack.md`

## 결론

첫 release API는 기능별 endpoint 목록이 아니라 다음 원칙을 지켜야 한다.

1. 모든 사용자 요청은 auth/user/device/plan/quota context를 가진다.
2. 중복 호출 가능성이 있는 write API는 idempotency key를 요구한다.
3. chat, TTS, image, memory, moderation 같은 느린 작업은 상태 조회가 가능해야 한다.
4. reward, credit, relationship 변경은 LLM 응답이 아니라 server rule/ledger 결과로 기록한다.
5. provider usage와 cost는 request 단위로 추적한다.

## 1. Common API rules

Base path:

```text
/api/mobile/v1
```

공통 headers:

```text
Authorization: Bearer <access_token>
X-Device-Id: <device_id>
X-Request-Id: <uuid>
Idempotency-Key: <uuid>  # write API 중 중복 방지가 필요한 요청
```

공통 response shape:

```json
{
  "data": {},
  "meta": {
    "requestId": "uuid",
    "serverTime": "2026-06-04T00:00:00Z"
  }
}
```

공통 error shape:

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Daily TTS limit reached.",
    "retryable": false,
    "details": {}
  },
  "meta": {
    "requestId": "uuid"
  }
}
```

공통 error code:

| code | 의미 | UI 처리 |
|---|---|---|
| UNAUTHENTICATED | 로그인 필요 | login/account 연결 |
| FORBIDDEN | 권한 없음 | 차단/권한 안내 |
| AGE_RESTRICTED | age policy 제한 | 제한 모드/진입 차단 |
| QUOTA_EXCEEDED | 무료/플랜 한도 초과 | ad/shop/upgrade 진입 |
| CREDIT_REQUIRED | credit 부족 | credit shop 진입 |
| IDEMPOTENCY_CONFLICT | 같은 key로 다른 payload 재시도 | retry 중단 |
| SAFETY_BLOCKED | safety policy 차단 | 부드러운 안내/report |
| PROVIDER_DEGRADED | provider 장애/느림 | text-only/slow mode |
| JOB_PENDING | async job 진행 중 | pending UI |
| NOT_FOUND | 리소스 없음 | empty/error |
| VALIDATION_ERROR | request schema 오류 | client bug로 기록 |

## 2. Auth and user

### POST /auth/session

목적:

- guest 또는 provider login으로 mobile session을 만든다.

Request:

```json
{
  "authProvider": "guest|apple|google|email",
  "providerToken": "string|null",
  "device": {
    "deviceId": "string",
    "platform": "ios|android",
    "appVersion": "string",
    "locale": "string",
    "timezone": "Asia/Seoul"
  }
}
```

Response:

```json
{
  "data": {
    "accessToken": "string",
    "refreshToken": "string",
    "user": {
      "id": "uuid",
      "status": "active",
      "isGuest": true,
      "ageGateStatus": "unknown|verified_adult|restricted"
    }
  }
}
```

주의:

- guest start는 허용하되 결제, export, account deletion에는 account link가 필요하다.
- device fingerprint 원문은 저장하지 않는다.

### POST /users/age-gate

목적:

- age policy 결과를 저장한다.

Request:

```json
{
  "birthYear": 1998,
  "country": "KR",
  "confirmation": true
}
```

Response:

```json
{
  "data": {
    "ageGateStatus": "verified_adult|restricted",
    "romanceAllowed": true
  }
}
```

### POST /users/delete-request

목적:

- 계정 삭제 요청을 접수한다.

요구:

- auth 필수.
- guest는 즉시 삭제 가능하되 payment/ledger가 있으면 계정 연결 또는 추가 확인 필요.
- admin/audit event 생성.

## 3. App bootstrap

### GET /app/bootstrap

목적:

- 앱 첫 화면에 필요한 상태를 한 번에 가져온다.

Response:

```json
{
  "data": {
    "user": {
      "id": "uuid",
      "plan": "free|plus|premium",
      "ageGateStatus": "verified_adult"
    },
    "character": {
      "id": "airi",
      "name": "Airi",
      "status": "available"
    },
    "relationship": {
      "level": 1,
      "affinity": 10,
      "trust": 5,
      "mood": "warm",
      "nextUnlockHint": "First Airi note"
    },
    "quota": {
      "textTurnsRemaining": 50,
      "voiceSecondsRemaining": 60,
      "ttsRepliesRemaining": 5
    },
    "daily": {
      "greeting": "string",
      "dateHint": {},
      "rewardHint": {}
    }
  }
}
```

주의:

- Chat 첫 화면은 bootstrap 결과만으로 즉시 그릴 수 있어야 한다.
- provider 호출 없이 server-side cached greeting 또는 저비용 route를 사용한다.

## 4. Characters and relationship

### GET /characters

목적:

- 사용 가능한 캐릭터 목록 조회.

첫 release:

- Airi 1명만 public.

### GET /characters/{characterId}/state

목적:

- relationship, memory summary, unlock hint 조회.

Response:

```json
{
  "data": {
    "characterId": "airi",
    "relationship": {
      "level": 3,
      "affinity": 34,
      "trust": 22,
      "familiarity": 18,
      "mood": "playful",
      "recentEvents": []
    },
    "nextUnlocks": []
  }
}
```

## 5. Chat

### POST /chat/turn

목적:

- 텍스트 또는 voice transcript 기반 Airi 응답을 생성한다.

Headers:

```text
Idempotency-Key: required
```

Request:

```json
{
  "characterId": "airi",
  "conversationId": "uuid|null",
  "input": {
    "type": "text|voice_transcript",
    "text": "string"
  },
  "clientContext": {
    "screen": "chat|date_result",
    "localTime": "2026-06-04T21:00:00+09:00"
  },
  "tts": {
    "requested": false,
    "style": "warm|soft|playful|null"
  }
}
```

Response:

```json
{
  "data": {
    "conversationId": "uuid",
    "messageId": "uuid",
    "reply": {
      "messageId": "uuid",
      "text": "string",
      "emotion": "warm|playful|concerned|shy|neutral",
      "intent": "chat|date_invite|comfort|memory_recall|reward_hint|fallback"
    },
    "relationshipFeedback": {
      "changed": true,
      "summary": "Trust +1",
      "eventId": "uuid"
    },
    "memoryFeedback": {
      "candidateCreated": true,
      "summary": "Airi may remember your movie taste.",
      "memoryId": "uuid|null",
      "extractionJobId": "uuid|null"
    },
    "dateSuggestion": {
      "eventId": "movie_talk",
      "title": "Movie talk date"
    },
    "ttsJob": null
  }
}
```

요구:

- quota check.
- safety precheck/post-validation.
- memory retrieval.
- provider usage event.
- message save.
- relationship event/snapshot update.
- optional memory extraction async job.

주의:

- TTS를 같은 요청에서 blocking하지 않는다.
- provider 장애 시 fallback reply 또는 PROVIDER_DEGRADED error를 반환한다.

### GET /conversations/{conversationId}/messages

목적:

- 대화 history pagination.

Query:

```text
cursor
limit
```

주의:

- 무한 scroll은 cursor 기반.
- 삭제/anonymized message 상태를 고려한다.

## 6. Voice and TTS

### POST /voice/stt

목적:

- PTT voice input을 transcript로 바꾼다.

Request:

- multipart audio file 또는 upload ticket 방식.

Response:

```json
{
  "data": {
    "transcript": "string",
    "durationSeconds": 12.3,
    "quota": {
      "voiceSecondsRemaining": 47.7
    }
  }
}
```

요구:

- file size/duration limit.
- voice quota check.
- provider usage event.

### POST /tts

목적:

- 특정 message 또는 짧은 text에 대해 TTS job 생성.

Headers:

```text
Idempotency-Key: required
```

Request:

```json
{
  "characterId": "airi",
  "sourceMessageId": "uuid",
  "style": "warm|soft|playful|careful"
}
```

Response:

```json
{
  "data": {
    "jobId": "uuid",
    "status": "queued|running|succeeded|failed",
    "estimatedWaitSeconds": 3
  }
}
```

### GET /tts/jobs/{jobId}

Response:

```json
{
  "data": {
    "jobId": "uuid",
    "status": "queued|running|succeeded|failed",
    "audio": {
      "playbackUrl": "signed-url",
      "expiresAt": "2026-06-04T00:10:00Z"
    },
    "errorCode": null
  }
}
```

## 7. Memories

### GET /memories

Query:

```text
characterId=airi
status=active|candidate|hidden|rejected
limit=50
```

Response:

```json
{
  "data": {
    "items": [
      {
        "id": "uuid",
        "characterId": "airi",
        "summary": "You like quiet movie nights.",
        "memoryType": "user_preference",
        "status": "active",
        "importance": 3,
        "sourceMessageId": "uuid|null",
        "createdAt": "2026-06-04T00:00:00Z",
        "lastUsedAt": "2026-06-04T00:00:00Z|null",
        "deletedAt": null
      }
    ]
  }
}
```

### POST /memories/{memoryId}/activate

목적:

- candidate memory를 active 상태로 전환한다.

Response:

```json
{
  "data": {
    "memory": {
      "id": "uuid",
      "characterId": "airi",
      "summary": "You like quiet movie nights.",
      "memoryType": "user_preference",
      "status": "active",
      "importance": 3,
      "sourceMessageId": "uuid|null",
      "createdAt": "2026-06-04T00:00:00Z",
      "lastUsedAt": null,
      "deletedAt": null
    }
  }
}
```

주의:

- 첫 구현에서는 provider-backed extraction 전까지 candidate 검증/활성화 흐름을 검증하기 위한 API다.
- active 또는 candidate 상태만 허용한다.
- deleted memory는 활성화할 수 없다.

### DELETE /memories/{memoryId}

목적:

- 사용자가 memory 삭제.

요구:

- memory status를 즉시 hidden/deleted로 변경.
- embedding/source link background delete.
- audit/safety 필요 여부는 데이터 성격에 따라 결정.
- 이후 retrieval과 `GET /memories?status=active`에서 즉시 제외된다.

## 8. Date events

### GET /date-events

목적:

- available official date events 조회.

Response:

```json
{
  "data": {
    "items": [
      {
        "id": "movie_talk",
        "title": "Movie talk date",
        "estimatedMinutes": 5,
        "status": "available|locked|cooldown",
        "rewardPreview": {},
        "entryCost": 0
      }
    ]
  }
}
```

### POST /date-events/{eventId}/start

Headers:

```text
Idempotency-Key: required
```

Response:

```json
{
  "data": {
    "sessionId": "uuid",
    "eventId": "movie_talk",
    "step": {
      "sequenceNo": 1,
      "airiLine": "string",
      "choices": []
    }
  }
}
```

### POST /date-events/{eventId}/move

Headers:

```text
Idempotency-Key: required
```

Request:

```json
{
  "sessionId": "uuid",
  "sequenceNo": 1,
  "choiceId": "string",
  "freeText": "string|null"
}
```

Response:

```json
{
  "data": {
    "sessionId": "uuid",
    "status": "active|completed",
    "step": {},
    "partialFeedback": {
      "mood": "warm"
    }
  }
}
```

### POST /date-events/{eventId}/finish

Headers:

```text
Idempotency-Key: required
```

Response:

```json
{
  "data": {
    "sessionId": "uuid",
    "result": "success|neutral|failed",
    "score": 82,
    "airiReaction": "string",
    "relationshipEvent": {
      "id": "uuid",
      "summary": "Affinity +3"
    },
    "reward": {
      "eventId": "uuid",
      "status": "pending|unlocked",
      "type": "image|note|voice"
    },
    "memoryJobId": "uuid"
  }
}
```

주의:

- finish 중복 호출은 같은 결과를 반환해야 한다.
- LLM은 result를 결정하지 않는다.
- reward/relationship은 transaction 또는 재시도 가능한 outbox pattern이 필요하다.

## 9. Rewards and media

### GET /rewards

Query:

```text
characterId=airi
status=locked|progress|pending|unlocked
```

### POST /media/generate

목적:

- premium image reward/regeneration job 생성.

Headers:

```text
Idempotency-Key: required
```

Request:

```json
{
  "characterId": "airi",
  "sourceType": "reward_event|date_event",
  "sourceId": "uuid",
  "mediaType": "image",
  "quality": "basic|premium"
}
```

Response:

```json
{
  "data": {
    "jobId": "uuid",
    "status": "queued",
    "creditLedgerId": "uuid|null",
    "estimatedWaitSeconds": 30
  }
}
```

요구:

- credit/quota check.
- prompt template + visual profile.
- prompt moderation.
- async job.
- output moderation.
- refund/alternative policy.

### GET /media/jobs/{jobId}

Response:

```json
{
  "data": {
    "jobId": "uuid",
    "status": "queued|running|pending_moderation|approved|rejected|failed",
    "asset": {
      "id": "uuid",
      "url": "signed-url"
    },
    "refund": {
      "status": "none|pending|completed"
    }
  }
}
```

## 10. Credits, plans, billing

### GET /credits/balance

Response:

```json
{
  "data": {
    "balances": [
      {
        "currencyType": "credit",
        "bucket": "free_daily|ad_reward|subscription_allowance|purchased",
        "amount": 10,
        "expiresAt": null
      }
    ]
  }
}
```

### GET /credits/ledger

Query:

```text
cursor
limit
```

### GET /plans

목적:

- Free/Plus/Premium allowance와 가격 표시.

주의:

- "unlimited" 표현 금지.
- plan allowance, credit 사용처, renewal/cancel 안내 포함.

### POST /billing/webhook/google-play

목적:

- Google Play subscription/IAP webhook 처리.

요구:

- server-to-server endpoint.
- mobile client 직접 호출 금지.
- idempotency.
- transaction verification.
- credit ledger write.

### POST /billing/webhook/apple

목적:

- Apple App Store Server Notifications 처리.

요구:

- Google Play와 동일하게 중복/지연/역순 도착을 전제로 처리한다.

## 11. Reports and safety

### POST /reports

Headers:

```text
Idempotency-Key: required
```

Request:

```json
{
  "targetType": "message|media_asset|character",
  "targetId": "uuid",
  "reason": "unsafe|sexual|minor|harassment|privacy|other",
  "note": "string|null"
}
```

Response:

```json
{
  "data": {
    "reportId": "uuid",
    "status": "open"
  }
}
```

요구:

- moderation queue.
- safety event.
- admin audit when reviewed.

### POST /blocks

목적:

- 캐릭터 또는 사용자 컨텐츠 차단.

첫 release:

- Airi 단일 캐릭터라 block은 safety/report path 중심으로 설계한다.

## 12. Admin-facing API boundary

Mobile API와 admin API는 분리한다.

Admin 최소 API:

- user lookup.
- conversation inspector.
- credit ledger viewer.
- provider cost dashboard.
- queue monitor.
- moderation review.
- admin audit log viewer.

원칙:

- admin access는 별도 auth/RBAC.
- 대화 원문/이미지 열람은 reason 필수.
- 모든 admin action은 admin_audit_logs에 저장.

## 13. API acceptance criteria

개발 착수 전 이 API 계약은 다음을 만족해야 한다.

- Chat 첫 화면은 `GET /app/bootstrap`만으로 기본 렌더링 가능.
- `POST /chat/turn`은 idempotency, quota, safety, provider usage, relationship feedback을 가진다.
- TTS/image/memory는 async job 상태 조회가 가능하다.
- date event start/move/finish는 중복 호출에 안전하다.
- reward unlock과 credit 차감은 ledger/event로 추적된다.
- quota exceeded는 UI가 ad/shop/upgrade로 연결할 수 있는 error details를 가진다.
- report/delete/memory delete path가 모바일에서 접근 가능하다.
- billing webhook은 mobile client API와 분리되어 있다.

## 14. 다음 상세화 필요

- endpoint별 Pydantic schema. 기준: `25-OpenAPI-Pydantic-schema-plan.md`.
- OpenAPI spec 자동 생성 기준. 기준: `25-OpenAPI-Pydantic-schema-plan.md`.
- auth token refresh flow.
- websocket/SSE streaming 여부.
- outbox/retry pattern.
- API rate limit table.
- plan별 allowance table.
