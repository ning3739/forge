"""user Schema generategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="schema",
    priority=50,
    requires=["UserModelGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate user schemas (app/schemas/user.py)"
)
class UserSchemaGenerator(BaseTemplateGenerator):
    """user Schema File generator"""
    
    def generate(self) -> None:
        """generateuser Schema file
        
        Note: This generator is called by Orchestrator when authentication is enabled
        """
        auth_type = self.config_reader.get_auth_type()
        
        if auth_type == "basic":
            self._generate_basic_schemas()
        else:  # complete
            self._generate_complete_schemas()
    
    def _generate_basic_schemas(self) -> None:
        """generate Basic JWT Auth  Schemas"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator",
        ]
        
        content = '''# ========== base Schema ==========

class UserBase(BaseModel):
    """userbase Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """userCreate Schema"""
    password: str = Field(..., min_length=6, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "strongpassword123"
            }
        }
    )


class UserUpdate(BaseModel):
    """userupdate Schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """userresponse Schema"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== authenticationrelated Schema ==========

class UserLogin(BaseModel):
    """User login Schema"""
    username: Optional[str] = Field(None, description="Generate user schemas (app/schemas/user.py)")
    email: Optional[EmailStr] = Field(None, description="Generate user schemas (app/schemas/user.py)")
    password: str = Field(..., min_length=6)
    
    @model_validator(mode='after')
    def check_username_or_email(self):
        """Validate that at least username or email is provided"""
        if not self.username and not self.email:
            raise ValueError('Must provide username or email')
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        }
    )


class Token(BaseModel):
    """tokenresponse Schema"""
    access_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    """tokendata Schema"""
    username: Optional[str] = None
    user_id: Optional[int] = None
'''
        
        self.file_ops.create_python_file(
            file_path="app/schemas/user.py",
            docstring="userrelated Pydantic Schemas",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_complete_schemas(self) -> None:
        """generate Complete JWT Auth  Schemas"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator",
        ]
        
        content = '''# ========== base Schema ==========

class UserBase(BaseModel):
    """userbase Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """userCreate Schema"""
    password: str = Field(..., min_length=6, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "strongpassword123"
            }
        }
    )


class UserUpdate(BaseModel):
    """userupdate Schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """userresponse Schema"""
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ========== authenticationrelated Schema ==========

class UserLogin(BaseModel):
    """User login Schema"""
    username: Optional[str] = Field(None, description="Generate user schemas (app/schemas/user.py)")
    email: Optional[EmailStr] = Field(None, description="Generate user schemas (app/schemas/user.py)")
    password: str = Field(..., min_length=6)
    
    @model_validator(mode='after')
    def check_username_or_email(self):
        """Validate that at least username or email is provided"""
        if not self.username and not self.email:
            raise ValueError('Must provide username or email')
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        }
    )


class Token(BaseModel):
    """tokenresponse Schema"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    """tokendata Schema"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    """refreshtokenrequest Schema"""
    refresh_token: str = Field(..., description="Generate user schemas (app/schemas/user.py)")


# ========== EmailValidaterelated Schema ==========

class EmailVerificationRequest(BaseModel):
    """EmailValidaterequest Schema"""
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "code": "123456"
            }
        }
    )


class ResendVerificationRequest(BaseModel):
    """Resend verification code request Schema"""
    email: EmailStr


# ========== Passwordresetrelated Schema ==========

class PasswordResetRequest(BaseModel):
    """Passwordresetrequest Schema"""
    email: EmailStr
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com"
            }
        }
    )


class PasswordResetConfirm(BaseModel):
    """Passwordresetconfirm Schema"""
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "code": "123456",
                "new_password": "newstrongpassword123"
            }
        }
    )


class PasswordChange(BaseModel):
    """Passwordmodify Schema"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newstrongpassword123"
            }
        }
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/schemas/user.py",
            docstring="userrelated Pydantic Schemas - Complete JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
