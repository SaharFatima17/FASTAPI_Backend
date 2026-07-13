from pydantic import BaseModel, EmailStr

# Signup request input validation
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Login request input validation
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Clean Response serialization (Password leak nahi hoga)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True