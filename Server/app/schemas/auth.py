from typing import Literal

from pydantic import BaseModel, Field


class AuthSessionRequest(BaseModel):
    auth_provider: Literal["guest", "apple", "google", "email"] = "guest"
    device_id: str | None = Field(default=None, min_length=1, max_length=128)


class AuthSessionResponse(BaseModel):
    user_id: str
    session_id: str
    access_token: str
    refresh_token: str
    expires_in: int = Field(gt=0)
    refresh_expires_in: int = Field(gt=0)
    token_type: Literal["Bearer"] = "Bearer"

