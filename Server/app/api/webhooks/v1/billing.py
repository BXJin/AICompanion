from typing import Annotated

from fastapi import APIRouter, Header

from app.dependencies import SettingsDep
from app.schemas.webhooks import BillingWebhookAckResponse
from app.security.webhook import verify_shared_secret_signature

router = APIRouter(prefix="/billing", tags=["billing-webhooks"])


@router.post("/google-play", response_model=BillingWebhookAckResponse)
async def google_play_webhook(
    settings: SettingsDep,
    signature: Annotated[str | None, Header(alias="X-Webhook-Signature")] = None,
    event_id: Annotated[str | None, Header(alias="X-Webhook-Event-ID")] = None,
) -> BillingWebhookAckResponse:
    verify_shared_secret_signature(expected_secret=settings.webhook_shared_secret, provided_signature=signature)
    return BillingWebhookAckResponse(provider="google_play", event_id=event_id)


@router.post("/apple", response_model=BillingWebhookAckResponse)
async def apple_webhook(
    settings: SettingsDep,
    signature: Annotated[str | None, Header(alias="X-Webhook-Signature")] = None,
    event_id: Annotated[str | None, Header(alias="X-Webhook-Event-ID")] = None,
) -> BillingWebhookAckResponse:
    verify_shared_secret_signature(expected_secret=settings.webhook_shared_secret, provided_signature=signature)
    return BillingWebhookAckResponse(provider="apple", event_id=event_id)

