from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, Text
# Aapke project mein jahan bhi Base defined ho (maslan app/database.py ya app/models/base.py)
from app.core.database import Base  # Apne project structure ke mutabiq path check kar lein

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)