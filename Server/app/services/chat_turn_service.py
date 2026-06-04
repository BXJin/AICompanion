from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.domain import Character, Conversation, Message
from app.providers.llm.base import LlmProvider
from app.providers.llm.mock import MockLlmProvider
from app.repositories.conversations import ConversationRepository
from app.repositories.messages import MessageRepository
from app.services.airi_seed_service import AIRI_CHARACTER_ID, AiriSeedService
from app.services.app_bootstrap_service import AppBootstrapService
from app.services.memory_service import MemoryCandidateResult, MemoryService
from app.services.provider_usage_service import ProviderUsageRecordCommand, ProviderUsageService
from app.services.quota_service import QuotaService
from app.services.relationship_state_service import RelationshipApplyResult, RelationshipDelta, RelationshipStateService


@dataclass(frozen=True)
class ChatTurnCommand:
    user_id: str
    character_id: str
    conversation_id: str | None
    input_text: str


@dataclass(frozen=True)
class ChatReply:
    message_id: str
    text: str
    emotion: Literal["warm", "playful", "concerned", "shy", "neutral"]
    intent: Literal["chat", "date_invite", "comfort", "memory_recall", "reward_hint", "fallback"]


@dataclass(frozen=True)
class ChatTurnResult:
    conversation_id: str
    user_message_id: str
    reply: ChatReply
    relationship_feedback: RelationshipApplyResult | None
    memory_feedback: MemoryCandidateResult | None


class ChatTurnService:
    def __init__(self, db: Session, llm_provider: LlmProvider | None = None) -> None:
        self._db = db
        self._llm_provider = llm_provider or MockLlmProvider()
        self._conversations = ConversationRepository(db)
        self._messages = MessageRepository(db)
        self._airi_seed = AiriSeedService(db)
        self._provider_usage = ProviderUsageService(db)
        self._quota = QuotaService(db)
        self._relationship_state = RelationshipStateService(db)
        self._memory_service = MemoryService(db)

    async def create_turn(self, command: ChatTurnCommand) -> ChatTurnResult:
        if command.character_id != AIRI_CHARACTER_ID:
            raise ValueError("Only Airi is available in the first release")

        character = self._ensure_chat_bootstrap(user_id=command.user_id)
        conversation = self._get_or_create_conversation(
            user_id=command.user_id,
            character=character,
            conversation_id=command.conversation_id,
        )
        self._quota.consume(user_id=command.user_id, plan="free", feature="text_turn")
        history = self._messages.list_for_conversation(conversation_id=conversation.id)
        provider_messages = self._build_provider_messages(history=history, input_text=command.input_text)
        llm_response = await self._llm_provider.complete(route="default_chat", messages=provider_messages)
        provider_usage = self._provider_usage.record_llm_usage(
            ProviderUsageRecordCommand(
                user_id=command.user_id,
                feature_route="default_chat",
                status="success",
                provider_response=llm_response,
            )
        )

        now = datetime.now(UTC)
        user_message = self._messages.add(
            Message(
                id=str(uuid4()),
                conversation_id=conversation.id,
                user_id=command.user_id,
                character_id=character.id,
                role="user",
                content_text=command.input_text,
                status="visible",
                provider_usage_event_id=None,
                created_at=now,
            )
        )
        self._db.flush()
        relationship_feedback = self._relationship_state.apply_chat_event(
            user_id=command.user_id,
            character_id=character.id,
            source_message_id=user_message.id,
            event_type="first_chat_completed",
            delta=RelationshipDelta(affinity=2, familiarity=1),
        )
        memory_feedback = self._memory_service.create_preference_candidate_from_chat(
            user_id=command.user_id,
            character_id=character.id,
            source_message_id=user_message.id,
            text=command.input_text,
        )
        if memory_feedback.candidate_created:
            preference_relationship_feedback = self._relationship_state.apply_chat_event(
                user_id=command.user_id,
                character_id=character.id,
                source_message_id=user_message.id,
                event_type="user_shared_preference",
                delta=RelationshipDelta(familiarity=1),
            )
            relationship_feedback = self._merge_relationship_feedback(
                primary=relationship_feedback,
                secondary=preference_relationship_feedback,
            )
        assistant_message = self._messages.add(
            Message(
                id=str(uuid4()),
                conversation_id=conversation.id,
                user_id=command.user_id,
                character_id=character.id,
                role="assistant",
                content_text=llm_response.text,
                status="visible",
                provider_usage_event_id=provider_usage.id,
                created_at=now,
            )
        )
        conversation.last_message_at = now
        self._db.commit()

        return ChatTurnResult(
            conversation_id=conversation.id,
            user_message_id=user_message.id,
            reply=ChatReply(
                message_id=assistant_message.id,
                text=assistant_message.content_text,
                emotion="warm",
                intent="chat",
            ),
            relationship_feedback=relationship_feedback,
            memory_feedback=memory_feedback,
        )

    def _ensure_chat_bootstrap(self, *, user_id: str) -> Character:
        character = self._airi_seed.ensure_airi_character()
        AppBootstrapService(self._db).ensure_initial_relationship(user_id=user_id, character=character)
        return character

    def _get_or_create_conversation(
        self,
        *,
        user_id: str,
        character: Character,
        conversation_id: str | None,
    ) -> Conversation:
        now = datetime.now(UTC)
        if conversation_id is None:
            return self._conversations.add(
                Conversation(
                    id=str(uuid4()),
                    user_id=user_id,
                    character_id=character.id,
                    status="active",
                    title=None,
                    created_at=now,
                    last_message_at=None,
                )
            )

        conversation = self._conversations.get(conversation_id)
        if conversation is None or conversation.user_id != user_id or conversation.character_id != character.id:
            raise ValueError("Conversation was not found for this user and character")
        if conversation.status != "active":
            raise ValueError("Conversation is not active")
        return conversation

    def _build_provider_messages(self, *, history: list[Message], input_text: str) -> list[dict[str, str]]:
        messages = [
            {
                "role": "system",
                "content": "You are Airi, a warm and store-safe AI companion. Keep replies short.",
            }
        ]
        messages.extend({"role": message.role, "content": message.content_text} for message in history)
        messages.append({"role": "user", "content": input_text})
        return messages

    def _merge_relationship_feedback(
        self,
        *,
        primary: RelationshipApplyResult,
        secondary: RelationshipApplyResult,
    ) -> RelationshipApplyResult:
        if not primary.changed:
            return secondary
        if not secondary.changed:
            return primary
        summary = ", ".join(part for part in [primary.summary, secondary.summary] if part)
        return RelationshipApplyResult(
            changed=True,
            summary=summary,
            event_id=secondary.event_id or primary.event_id,
            snapshot=secondary.snapshot,
        )
