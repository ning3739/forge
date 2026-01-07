"""Authentication service generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="service",
    priority=70,
    requires=["UserCRUDGenerator", "SecurityGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate authentication service (app/services/auth.py)"
)
class AuthServiceGenerator(BaseTemplateGenerator):
    """Authentication service file generator"""
    
    def generate(self) -> None:
        """generate authentication service file"""
        # Only generate if authentication is enabled
        if not self.config_reader.has_auth():
            return
        
        auth_type = self.config_reader.get_auth_type()
        
        if auth_type == "basic":
            self._generate_basic_auth_service()
        else:  # complete
            self._generate_complete_auth_service()
    
    def _generate_basic_auth_service(self) -> None:
        """generate service for Basic JWT Auth"""
        imports = [
            "from datetime import datetime, timedelta",
            "from typing import Optional",
            "from jose import JWTError, jwt",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.config import settings",
            "from app.crud.user import user_crud",
            "from app.models.user import User",
            "from app.schemas.user import UserCreate, Token",
        ]
        
        content = '''class AuthService:
    """Authentication service class - Basic JWT Auth"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Createaccesstoken
        
        Args:
            data: Data to encode
            expires_delta: Expiration time delta
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=settings.jwt.JWT_ACCESS_TOKEN_EXPIRATION)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt.JWT_SECRET_KEY.get_secret_value(),
            algorithm=settings.jwt.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Register new user
        
        Args:
            db: Database session
            user_data: userCreatedata
            
        Returns:
            Createuserobject
            
        Raises:
            ValueError: Username or emailalreadyexists
        """
        # CheckUsernamewhetheralreadyexists
        if await user_crud.get_by_username(db, user_data.username):
            raise ValueError("Username already registered")
        
        # CheckEmailwhetheralreadyexists
        if await user_crud.get_by_email(db, user_data.email):
            raise ValueError("Email already registered")
        
        # Createuser
        user = await user_crud.create(db, user_data)
        return user
    
    @staticmethod
    async def login_user(db: AsyncSession, username: str, password: str) -> Optional[Token]:
        """User login
        
        Args:
            db: Database session
            username: Username or email
            password: Password
            
        Returns:
            Token object, returns None if authentication fails
        """
        # Authenticate user
        user = await user_crud.authenticate(db, username, password)
        if not user:
            return None
        
        # Checkuserwhetheractivate
        if not user.is_active:
            return None
        
        # Createaccesstoken
        access_token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return Token(access_token=access_token, token_type="bearer")


# Global service instance
auth_service = AuthService()
'''
        
        self.file_ops.create_python_file(
            file_path="app/services/auth.py",
            docstring="Authentication service - Basic JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_complete_auth_service(self) -> None:
        """generate service for Complete JWT Auth"""
        imports = [
            "from datetime import datetime, timedelta",
            "from typing import Optional",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.config import settings",
            "from app.core.security import security_manager",
            "from app.crud.user import user_crud",
            "from app.crud.token import refresh_token_crud, verification_code_crud",
            "from app.models.user import User",
            "from app.schemas.user import UserCreate, Token",
            "from app.utils.email import email_service",
        ]
        
        content = '''class AuthService:
    """Authentication service class - Complete JWT Auth"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Createaccesstoken
        
        Args:
            data: Data to encode
            expires_delta: Expiration time delta (deprecated, use value from configuration)
            
        Returns:
            JWT token string
        """
        token, _ = security_manager.create_access_token(data)
        return token
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Createrefreshtoken
        
        Args:
            data: Data to encode
            expires_delta: Expiration time delta (deprecated, use value from configuration)
            
        Returns:
            JWT refresh token string
        """
        token, _ = security_manager.create_refresh_token(data)
        return token
    
    @staticmethod
    async def register_user(
        db: AsyncSession,
        user_data: UserCreate,
        send_verification: bool = True
    ) -> User:
        """Register new user
        
        Args:
            db: Database session
            user_data: userCreatedata
            send_verification: whethersendValidateemail
            
        Returns:
            Createuserobject
            
        Raises:
            ValueError: Username or emailalreadyexists
        """
        # CheckUsernamewhetheralreadyexists
        if await user_crud.get_by_username(db, user_data.username):
            raise ValueError("Username already registered")
        
        # CheckEmailwhetheralreadyexists
        if await user_crud.get_by_email(db, user_data.email):
            raise ValueError("Email already registered")
        
        # Create user (unverified status)
        user = await user_crud.create(db, user_data)
        
        # sendValidateemail
        if send_verification:
            await AuthService.send_verification_email(db, user)
        
        return user
    
    @staticmethod
    async def send_verification_email(db: AsyncSession, user: User) -> None:
        """sendEmailValidateemail
        
        Args:
            db: Database session
            user: userobject
        """
        # Create verification code
        code = await verification_code_crud.create(
            db,
            user_id=user.id,
            code_type="email_verification",
            expiration_minutes=60
        )
        
        # sendemail
        await email_service.send_email(
            subject="Email Verification",
            recipient=user.email,
            template="verification",
            username=user.username,
            code=code.code
        )
    
    @staticmethod
    async def verify_email(db: AsyncSession, user_id: int, code: str) -> bool:
        """Verify Email
        
        Args:
            db: Database session
            user_id: user ID
            code: Verification code
            
        Returns:
            Validatewhethersuccess
        """
        # Verify verification code
        verified_code = await verification_code_crud.verify(
            db,
            user_id=user_id,
            code=code,
            code_type="email_verification"
        )
        
        if not verified_code:
            return False
        
        # Mark email as verified
        user = await user_crud.verify_email(db, user_id)
        
        if user:
            # Send welcome email
            await email_service.send_email(
                subject="Welcome!",
                recipient=user.email,
                template="welcome",
                username=user.username
            )
            return True
        
        return False
    
    @staticmethod
    async def login_user(
        db: AsyncSession,
        username: str,
        password: str,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Token]:
        """User login
        
        Args:
            db: Database session
            username: Username or email
            password: Password
            device_name: Device name
            device_type: Device type
            ip_address: IP address
            user_agent: User Agent
            
        Returns:
            Token object, returns None if authentication fails
        """
        # Authenticate user
        user = await user_crud.authenticate(db, username, password)
        if not user:
            return None
        
        # Checkuserwhetheractivate
        if not user.is_active:
            return None
        
        # CheckEmailwhetheralreadyValidate
        if not user.is_verified:
            return None
        
        # Update last login time
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
        # Createaccesstoken
        access_token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        # Createrefreshtoken
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        # Save refresh token to database
        expires_at = datetime.utcnow() + timedelta(seconds=settings.jwt.JWT_REFRESH_TOKEN_EXPIRATION)
        await refresh_token_crud.create(
            db,
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            device_name=device_name,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Optional[str]:
        """userefreshtokenGetnewaccesstoken
        
        Args:
            db: Database session
            refresh_token: refreshtoken
            
        Returns:
            New access token, return None if refresh fails
        """
        # Validate refresh token
        db_token = await refresh_token_crud.get_by_token(db, refresh_token)
        
        if not db_token or not db_token.is_valid():
            return None
        
        # Update last used time
        await refresh_token_crud.update_last_used(db, db_token.id)
        
        # Getuser
        user = await user_crud.get_by_id(db, db_token.user_id)
        if not user or not user.is_active:
            return None
        
        # generatenewaccesstoken
        access_token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return access_token
    
    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str) -> bool:
        """Request password reset
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            whethersuccesssendresetemail
        """
        # finduser
        user = await user_crud.get_by_email(db, email)
        if not user:
            # For security, return True even if user does not exist
            return True
        
        # Create reset code
        code = await verification_code_crud.create(
            db,
            user_id=user.id,
            code_type="password_reset",
            expiration_minutes=60
        )
        
        # sendresetemail
        await email_service.send_email(
            subject="Password Reset",
            recipient=user.email,
            template="password_reset",
            username=user.username,
            code=code.code
        )
        
        return True
    
    @staticmethod
    async def reset_password(db: AsyncSession, email: str, code: str, new_password: str) -> bool:
        """Reset password
        
        Args:
            db: Database session
            email: User email
            code: Verification code
            new_password: New password
            
        Returns:
            whethersuccessReset password
        """
        # finduser
        user = await user_crud.get_by_email(db, email)
        if not user:
            return False
        
        # Verify verification code
        verified_code = await verification_code_crud.verify(
            db,
            user_id=user.id,
            code=code,
            code_type="password_reset"
        )
        
        if not verified_code:
            return False
        
        # Change password
        await user_crud.change_password(db, user.id, new_password)
        
        # Revoke all refresh tokens (force re-login)
        await refresh_token_crud.revoke_user_tokens(db, user.id)
        
        return True
    
    @staticmethod
    async def logout_user(db: AsyncSession, refresh_token: str) -> bool:
        """User logout (revoke refresh token)
        
        Args:
            db: Database session
            refresh_token: refreshtoken
            
        Returns:
            whethersuccesslogout
        """
        return await refresh_token_crud.revoke(db, refresh_token)
    
    @staticmethod
    async def logout_all_devices(db: AsyncSession, user_id: int) -> int:
        """Logout all devices
        
        Args:
            db: Database session
            user_id: user ID
            
        Returns:
            Revoke tokenquantity
        """
        return await refresh_token_crud.revoke_user_tokens(db, user_id)


# Global service instance
auth_service = AuthService()
'''
        
        self.file_ops.create_python_file(
            file_path="app/services/auth.py",
            docstring="Authentication service - Complete JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
