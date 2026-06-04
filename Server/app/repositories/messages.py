from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Message


class MessageRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, message: Message) -> Message:
        self._db.add(message)
        return message

    def list_for_conversation(self, *, conversation_id: str, limit: int = 20) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id, Message.status == "visible")
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(self._db.execute(statement).scalars())
        messages.reverse()
        return messages
