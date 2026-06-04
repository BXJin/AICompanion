from app.providers.llm.base import LlmProvider, LlmResponse, LlmUsage


class MockLlmProvider(LlmProvider):
    async def complete(self, *, route: str, messages: list[dict[str, str]]) -> LlmResponse:
        last_user_message = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        text = f"Airi remembers the start of this conversation. You said: {last_user_message}".strip()
        return LlmResponse(
            text=text,
            usage=LlmUsage(input_tokens=10, output_tokens=18, estimated_cost_usd=0.0),
            provider_name="mock",
            model_name=f"mock-{route}",
        )

