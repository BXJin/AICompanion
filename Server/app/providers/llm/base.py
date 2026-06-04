from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class LlmUsage(BaseModel):
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0)


class LlmResponse(BaseModel):
    text: str
    usage: LlmUsage
    provider_name: str
    model_name: str


class LlmProvider(ABC):
    @abstractmethod
    async def complete(self, *, route: str, messages: list[dict[str, str]]) -> LlmResponse:
        raise NotImplementedError

