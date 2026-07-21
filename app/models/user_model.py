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


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    borrowed_at = Column(DateTime, default=datetime.datetime.utcnow)
    due_date = Column(DateTime)
    returned_at = Column(DateTime, nullable=True)
    status = Column(String, default="borrowed") # 'borrowed' or 'returned'