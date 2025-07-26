from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class LocationDetails(BaseModel):
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FarmDetails(BaseModel):
    location: Optional[LocationDetails] = None
    cropName: Optional[str] = None
    farmSize: Optional[str] = None
    experience: Optional[str] = None

class UserRegistrationRequest(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    password: str
    confirmPassword: str
    farmDetails: Optional[FarmDetails] = None
    language: Optional[str] = "en"
    
    @validator('confirmPassword')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('mobile')
    def validate_mobile(cls, v):
        # Basic mobile number validation
        if not v.isdigit() or len(v) < 10:
            raise ValueError('Invalid mobile number')
        return v

class UserSignUpRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class ExtendedUserResponse(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_verified: bool = False
    created_at: Optional[datetime] = None
    # Additional fields for registered users
    mobile: Optional[str] = None
    farmDetails: Optional[FarmDetails] = None
    language: Optional[str] = None

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

class ExtendedAuthResponse(BaseModel):
    user: ExtendedUserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class TokenVerificationRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    valid: bool
    user: Optional[UserResponse] = None
    error: Optional[str] = None
