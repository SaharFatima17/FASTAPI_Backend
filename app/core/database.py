from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⚠️ 'yourpassword' ki jagah apna PostgreSQL password likhein
DATABASE_URL = "postgresql://postgres:sahar17@localhost:5432/fastapi_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Dependency Injection Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()