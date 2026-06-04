from sqlalchemy.orm import Session

from app.models.domain import Conversation


class ConversationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, conversation: Conversation) -> Conversation:
        self._db.add(conversation)
        return conversation

    def get(self, conversation_id: str) -> Conversation | None:
        return self._db.get(Conversation, conversation_id)
