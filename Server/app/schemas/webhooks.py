from typing import Literal

from pydantic import BaseModel


class BillingWebhookAckResponse(BaseModel):
    status: Literal["accepted"] = "accepted"
    provider: str
    event_id: str | None = None

