import hmac

from fastapi import HTTPException, status


def verify_shared_secret_signature(*, expected_secret: str, provided_signature: str | None) -> None:
    if not provided_signature or not hmac.compare_digest(expected_secret, provided_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

