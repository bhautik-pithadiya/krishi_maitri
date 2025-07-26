from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserSignUpRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_verified: bool = False
    created_at: Optional[datetime] = None
    
class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class TokenVerificationRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    valid: bool
    user: Optional[UserResponse] = None
    error: Optional[str] = None
