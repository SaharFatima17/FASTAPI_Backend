from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db_session)):
    auth_service = AuthService(db)
    return auth_service.register_new_user(user_data)

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db_session)):
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data)

@router.get("/profile/{user_id}", response_model=UserResponse)
def get_profile(user_id: int, db: Session = Depends(get_db_session)):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user