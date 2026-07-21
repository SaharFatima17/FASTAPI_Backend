from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate, hashed_pwd: str) -> User:
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pwd
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user