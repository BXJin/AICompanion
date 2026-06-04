from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.domain import ProviderUsageEvent
from app.providers.llm.base import LlmResponse
from app.repositories.provider_usage import ProviderUsageRepository


@dataclass(frozen=True)
class ProviderUsageRecordCommand:
    user_id: str | None
    feature_route: str
    status: str
    provider_response: LlmResponse
    latency_ms: int | None = None


class ProviderUsageService:
    def __init__(self, db: Session) -> None:
        self._provider_usage = ProviderUsageRepository(db)

    def record_llm_usage(self, command: ProviderUsageRecordCommand) -> ProviderUsageEvent:
        response = command.provider_response
        return self._provider_usage.add(
            ProviderUsageEvent(
                id=str(uuid4()),
                user_id=command.user_id,
                feature_route=command.feature_route,
                provider=response.provider_name,
                model=response.model_name,
                status=command.status,
                input_units=response.usage.input_tokens,
                output_units=response.usage.output_tokens,
                latency_ms=command.latency_ms,
                estimated_cost_usd=Decimal(str(response.usage.estimated_cost_usd)),
                metadata_json={"unit_type": "tokens"},
                created_at=datetime.now(UTC),
            )
        )
