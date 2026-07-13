from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserLogin
from app.core.security import SecurityHelper

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register_new_user(self, user_data: UserCreate):
        # 1. Check if email already exists
        existing_user = self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered"
            )
        
        # 2. Hash the secure password
        hashed_password = SecurityHelper.hash_password(user_data.password)
        
        # 3. Save to database via repository
        return self.user_repo.create_user(user_data, hashed_password)

    def authenticate_user(self, login_data: UserLogin):
        # 1. Find user by email
        user = self.user_repo.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid Email or Password"
            )
        
        # 2. Verify encrypted password
        if not SecurityHelper.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid Email or Password"
            )
            
        return {"status": "success", "message": "Logged in successfully", "user_id": user.id}