from sqlmodel import SQLModel, Relationship, Field ,  Column , JSON
from typing import Optional, List
from datetime import datetime, time
from pydantic import BaseModel
from datetime import datetime, timezone 
from enum import Enum
from sqlalchemy import Column, Enum as SAEnum

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default_factory=None, primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    email: str = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column_kwargs={"onupdate": utcnow},
    )

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    id: Optional[int] = Field(default_factory=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column_kwargs={"onupdate": utcnow},
    )
    messages: List["Message"] = Relationship(back_populates="conversation",sa_relationship_kwargs={"cascade": "all, delete-orphan"},)

class Sender(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: Optional[int] = Field(default_factory=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    sender: Sender = Field(sa_column=Column(SAEnum(Sender), nullable=False))
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow)
    conversation: Conversation = Relationship(back_populates="messages")