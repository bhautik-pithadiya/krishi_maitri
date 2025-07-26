import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from app.models.auth import UserResponse, ExtendedUserResponse, FarmDetails

load_dotenv()

# Initialize password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_HOURS = 24

class FirebaseAuthService:
    def __init__(self):
        if not firebase_admin._apps:
            self._initialize_firebase()
        self.db = firestore.client()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Create credentials from environment variables
            firebase_config = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
            }
            
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise e
    
    def create_user(self, email: str, password: str, display_name: Optional[str] = None, 
                   phone_number: Optional[str] = None) -> UserResponse:
        """Create a new user in Firebase Auth"""
        try:
            user_creation_args = {
                'email': email,
                'password': password,
                'email_verified': False,
            }
            
            if display_name:
                user_creation_args['display_name'] = display_name
            if phone_number:
                user_creation_args['phone_number'] = phone_number
            
            user_record = auth.create_user(**user_creation_args)
            
            return UserResponse(
                uid=user_record.uid,
                email=user_record.email,
                display_name=user_record.display_name,
                phone_number=user_record.phone_number,
                email_verified=user_record.email_verified,
                created_at=datetime.fromtimestamp(user_record.user_metadata.creation_timestamp / 1000)
            )
        except auth.EmailAlreadyExistsError:
            raise ValueError("Email already exists")
        except Exception as e:
            raise ValueError(f"Error creating user: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        try:
            user_record = auth.get_user_by_email(email)
            return UserResponse(
                uid=user_record.uid,
                email=user_record.email,
                display_name=user_record.display_name,
                phone_number=user_record.phone_number,
                email_verified=user_record.email_verified,
                created_at=datetime.fromtimestamp(user_record.user_metadata.creation_timestamp / 1000)
            )
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            raise ValueError(f"Error fetching user: {str(e)}")
    
    def get_user_by_uid(self, uid: str) -> Optional[UserResponse]:
        """Get user by UID"""
        try:
            user_record = auth.get_user(uid)
            return UserResponse(
                uid=user_record.uid,
                email=user_record.email,
                display_name=user_record.display_name,
                phone_number=user_record.phone_number,
                email_verified=user_record.email_verified,
                created_at=datetime.fromtimestamp(user_record.user_metadata.creation_timestamp / 1000)
            )
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            raise ValueError(f"Error fetching user: {str(e)}")
    
    def verify_password(self, email: str, password: str) -> bool:
        """
        Verify user password. Note: Firebase Auth doesn't provide direct password verification
        via Admin SDK, so this is a simplified implementation.
        In production, you'd typically use Firebase Auth REST API or client SDK.
        """
        # This is a simplified implementation - in real scenarios, you'd use Firebase Auth REST API
        # For now, we'll just check if the user exists
        user = self.get_user_by_email(email)
        return user is not None
    
    def create_custom_token(self, uid: str) -> str:
        """Create a custom JWT token for the user"""
        try:
            payload = {
                "uid": uid,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_TIME_HOURS)
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return token
        except Exception as e:
            raise ValueError(f"Error creating token: {str(e)}")
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user UID"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload.get("uid")
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def delete_user(self, uid: str) -> bool:
        """Delete user from Firebase Auth"""
        try:
            auth.delete_user(uid)
            return True
        except auth.UserNotFoundError:
            return False
        except Exception as e:
            raise ValueError(f"Error deleting user: {str(e)}")
    
    def create_user_with_profile(self, name: str, email: str, password: str, mobile: str, 
                               farm_details: Optional[FarmDetails] = None, 
                               language: str = "en") -> ExtendedUserResponse:
        """Create a new user with extended profile information"""
        try:
            # First, create user in Firebase Auth
            user_creation_args = {
                'email': email,
                'password': password,
                'display_name': name,
                'phone_number': mobile if mobile.startswith('+') else f"+91{mobile}",
                'email_verified': False,
            }
            
            user_record = auth.create_user(**user_creation_args)
            
            # Prepare user profile data for Firestore
            profile_data = {
                'uid': user_record.uid,
                'email': email,
                'display_name': name,
                'mobile': mobile,
                'language': language,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'email_verified': False
            }
            
            # Add farm details if provided
            if farm_details:
                farm_dict = farm_details.dict(exclude_unset=True)
                if farm_dict:  # Only add if there's actual data
                    profile_data['farmDetails'] = farm_dict
            
            # Store user profile in Firestore
            self.db.collection('users').document(user_record.uid).set(profile_data)
            
            return ExtendedUserResponse(
                uid=user_record.uid,
                email=user_record.email,
                display_name=user_record.display_name,
                phone_number=user_record.phone_number,
                email_verified=user_record.email_verified,
                created_at=datetime.fromtimestamp(user_record.user_metadata.creation_timestamp / 1000),
                mobile=mobile,
                farmDetails=farm_details,
                language=language
            )
            
        except auth.EmailAlreadyExistsError:
            raise ValueError("Email already exists")
        except Exception as e:
            raise ValueError(f"Error creating user with profile: {str(e)}")
    
    def get_user_profile(self, uid: str) -> Optional[ExtendedUserResponse]:
        """Get extended user profile with farm details"""
        try:
            # Get user from Firebase Auth
            user_record = auth.get_user(uid)
            
            # Get additional profile data from Firestore
            profile_doc = self.db.collection('users').document(uid).get()
            
            if profile_doc.exists:
                profile_data = profile_doc.to_dict()
                farm_details = None
                
                # Convert farm details back to FarmDetails model if exists
                if 'farmDetails' in profile_data:
                    farm_details = FarmDetails(**profile_data['farmDetails'])
                
                return ExtendedUserResponse(
                    uid=user_record.uid,
                    email=user_record.email,
                    display_name=user_record.display_name,
                    phone_number=user_record.phone_number,
                    email_verified=user_record.email_verified,
                    created_at=datetime.fromtimestamp(user_record.user_metadata.creation_timestamp / 1000),
                    mobile=profile_data.get('mobile'),
                    farmDetails=farm_details,
                    language=profile_data.get('language', 'en')
                )
            else:
                # Return basic user info if no profile exists
                return ExtendedUserResponse(
                    uid=user_record.uid,
                    email=user_record.email,
                    display_name=user_record.display_name,
                    phone_number=user_record.phone_number,
                    email_verified=user_record.email_verified,
                    created_at=datetime.fromtimestamp(user_record.user_metadata.creation_timestamp / 1000)
                )
                
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            raise ValueError(f"Error fetching user profile: {str(e)}")
    
    def update_user_profile(self, uid: str, farm_details: Optional[FarmDetails] = None, 
                          language: Optional[str] = None) -> bool:
        """Update user profile information"""
        try:
            update_data = {
                'updated_at': datetime.utcnow()
            }
            
            if farm_details:
                farm_dict = farm_details.dict(exclude_unset=True)
                if farm_dict:
                    update_data['farmDetails'] = farm_dict
            
            if language:
                update_data['language'] = language
            
            # Update in Firestore
            self.db.collection('users').document(uid).update(update_data)
            return True
            
        except Exception as e:
            raise ValueError(f"Error updating user profile: {str(e)}")

# Create a singleton instance
firebase_auth_service = FirebaseAuthService()
