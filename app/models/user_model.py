from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base  # Aapka existing database Base path
import datetime

# 1. Aapka existing User model (Isko bilkul touch nahi kiya)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


# 2. Naya ChatSession model (Add kiya)
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_key = Column(String, unique=True, index=True, nullable=False) # E.g., "session_123"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship: Ek session ke andar boht saare messages ho sakte hain
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


# 3. Naya ChatMessage model (Add kiya)
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False) # 'user' ya 'assistant'
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship back to ChatSession
    session = relationship("ChatSession", back_populates="messages")