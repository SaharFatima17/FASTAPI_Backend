from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

# Easy shortcut dependency injection
def get_db_session(db: Session = Depends(get_db)):
    return db