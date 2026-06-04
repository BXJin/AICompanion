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


class ChatTurnService:
    def __init__(self, db: Session, llm_provider: LlmProvider | None = None) -> None:
        self._db = db
        self._llm_provider = llm_provider or MockLlmProvider()
        self._conversations = ConversationRepository(db)
        self._messages = MessageRepository(db)
        self._airi_seed = AiriSeedService(db)

    async def create_turn(self, command: ChatTurnCommand) -> ChatTurnResult:
        if command.character_id != AIRI_CHARACTER_ID:
            raise ValueError("Only Airi is available in the first release")

        character = self._ensure_chat_bootstrap(user_id=command.user_id)
        conversation = self._get_or_create_conversation(
            user_id=command.user_id,
            character=character,
            conversation_id=command.conversation_id,
        )
        history = self._messages.list_for_conversation(conversation_id=conversation.id)
        provider_messages = self._build_provider_messages(history=history, input_text=command.input_text)
        llm_response = await self._llm_provider.complete(route="default_chat", messages=provider_messages)

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
        assistant_message = self._messages.add(
            Message(
                id=str(uuid4()),
                conversation_id=conversation.id,
                user_id=command.user_id,
                character_id=character.id,
                role="assistant",
                content_text=llm_response.text,
                status="visible",
                provider_usage_event_id=None,
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
