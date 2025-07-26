from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.firebase_auth_service import firebase_auth_service
from app.models.auth import UserResponse
from typing import Optional

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """
    Dependency to get current authenticated user.
    Use this dependency in endpoints that require authentication.
    
    Example:
        @app.get("/protected")
        async def protected_endpoint(current_user: UserResponse = Depends(get_current_user)):
            return {"message": f"Hello {current_user.email}"}
    """
    try:
        token = credentials.credentials
        uid = firebase_auth_service.verify_token(token)
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
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
            detail="Authentication failed"
        )

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UserResponse]:
    """
    Optional authentication dependency.
    Returns user if valid token is provided, None otherwise.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        uid = firebase_auth_service.verify_token(token)
        if not uid:
            return None
        
        user = firebase_auth_service.get_user_by_uid(uid)
        return user
        
    except:
        return None
