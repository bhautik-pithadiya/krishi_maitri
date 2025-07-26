from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.auth import (
    UserSignUpRequest, 
    UserLoginRequest, 
    UserRegistrationRequest,
    AuthResponse, 
    ExtendedAuthResponse,
    TokenVerificationRequest, 
    TokenResponse,
    UserResponse,
    ExtendedUserResponse
)
from app.services.firebase_auth_service import firebase_auth_service
from typing import Optional

router = APIRouter()
security = HTTPBearer()

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: UserSignUpRequest):
    """
    Create a new user account with Firebase Authentication
    """
    try:
        # Check if user already exists
        existing_user = firebase_auth_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        user = firebase_auth_service.create_user(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
            phone_number=request.phone_number
        )
        
        # Create access token
        access_token = firebase_auth_service.create_custom_token(user.uid)
        
        return AuthResponse(
            user=user,
            access_token=access_token,
            token_type="bearer",
            expires_in=3600  # 1 hour
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/register", response_model=ExtendedAuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegistrationRequest):
    """
    Register a new user with complete profile including farm details
    """
    try:
        # Check if user already exists
        existing_user = firebase_auth_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user with complete profile
        user = firebase_auth_service.create_user_with_profile(
            name=request.name,
            email=request.email,
            password=request.password,
            mobile=request.mobile,
            farm_details=request.farmDetails,
            language=request.language
        )
        
        # Create access token
        access_token = firebase_auth_service.create_custom_token(user.uid)
        
        return ExtendedAuthResponse(
            user=user,
            access_token=access_token,
            token_type="bearer",
            expires_in=3600  # 1 hour
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login(request: UserLoginRequest):
    """
    Authenticate user and return access token
    """
    try:
        # Get user by email
        user = firebase_auth_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password (simplified - in production use Firebase Auth REST API)
        if not firebase_auth_service.verify_password(request.email, request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = firebase_auth_service.create_custom_token(user.uid)
        
        return AuthResponse(
            user=user,
            access_token=access_token,
            token_type="bearer",
            expires_in=3600  # 1 hour
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/verify-token", response_model=TokenResponse)
async def verify_token(request: TokenVerificationRequest):
    """
    Verify if a token is valid and return user information
    """
    try:
        # Verify token
        uid = firebase_auth_service.verify_token(request.token)
        if not uid:
            return TokenResponse(
                valid=False,
                error="Invalid token"
            )
        
        # Get user information
        user = firebase_auth_service.get_user_by_uid(uid)
        if not user:
            return TokenResponse(
                valid=False,
                error="User not found"
            )
        
        return TokenResponse(
            valid=True,
            user=user
        )
        
    except ValueError as e:
        return TokenResponse(
            valid=False,
            error=str(e)
        )
    except Exception as e:
        return TokenResponse(
            valid=False,
            error=f"Internal server error: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user information from token
    """
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        
        # Verify token
        uid = firebase_auth_service.verify_token(token)
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user information
        user = firebase_auth_service.get_user_by_uid(uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/profile", response_model=ExtendedUserResponse)
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user profile with farm details and additional information
    """
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        
        # Verify token
        uid = firebase_auth_service.verify_token(token)
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get extended user profile
        user_profile = firebase_auth_service.get_user_profile(uid)
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return user_profile
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/delete-account")
async def delete_account(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Delete current user account
    """
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        
        # Verify token
        uid = firebase_auth_service.verify_token(token)
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Delete user
        success = firebase_auth_service.delete_user(uid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "Account deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Dependency to get current user (can be used in other endpoints if needed)
async def get_current_user_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """
    Dependency to get current authenticated user
    Can be used in other endpoints that require authentication
    """
    try:
        token = credentials.credentials
        uid = firebase_auth_service.verify_token(token)
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = firebase_auth_service.get_user_by_uid(uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


