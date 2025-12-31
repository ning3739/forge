"""用户 Schema 生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class UserSchemaGenerator(BaseTemplateGenerator):
    """用户 Schema 文件生成器"""
    
    def generate(self) -> None:
        """生成用户 Schema 文件
        
        注意：此生成器由 Orchestrator 在启用认证时调用
        """
        auth_type = self.config_reader.get_auth_type()
        
        if auth_type == "basic":
            self._generate_basic_schemas()
        else:  # complete
            self._generate_complete_schemas()
    
    def _generate_basic_schemas(self) -> None:
        """生成 Basic JWT Auth 的 Schemas"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator",
        ]
        
        content = '''# ========== 基础 Schema ==========

class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """用户创建 Schema"""
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
    """用户更新 Schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应 Schema"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== 认证相关 Schema ==========

class UserLogin(BaseModel):
    """用户登录 Schema"""
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    password: str = Field(..., min_length=6)
    
    @model_validator(mode='after')
    def check_username_or_email(self):
        """验证至少提供用户名或邮箱之一"""
        if not self.username and not self.email:
            raise ValueError('必须提供用户名或邮箱')
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
    """令牌响应 Schema"""
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
    """令牌数据 Schema"""
    username: Optional[str] = None
    user_id: Optional[int] = None
'''
        
        self.file_ops.create_python_file(
            file_path="app/schemas/user.py",
            docstring="用户相关 Pydantic Schemas",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_complete_schemas(self) -> None:
        """生成 Complete JWT Auth 的 Schemas"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator",
        ]
        
        content = '''# ========== 基础 Schema ==========

class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """用户创建 Schema"""
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
    """用户更新 Schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应 Schema"""
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ========== 认证相关 Schema ==========

class UserLogin(BaseModel):
    """用户登录 Schema"""
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    password: str = Field(..., min_length=6)
    
    @model_validator(mode='after')
    def check_username_or_email(self):
        """验证至少提供用户名或邮箱之一"""
        if not self.username and not self.email:
            raise ValueError('必须提供用户名或邮箱')
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
    """令牌响应 Schema"""
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
    """令牌数据 Schema"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求 Schema"""
    refresh_token: str = Field(..., description="刷新令牌")


# ========== 邮箱验证相关 Schema ==========

class EmailVerificationRequest(BaseModel):
    """邮箱验证请求 Schema"""
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
    """重发验证码请求 Schema"""
    email: EmailStr


# ========== 密码重置相关 Schema ==========

class PasswordResetRequest(BaseModel):
    """密码重置请求 Schema"""
    email: EmailStr
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com"
            }
        }
    )


class PasswordResetConfirm(BaseModel):
    """密码重置确认 Schema"""
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
    """密码修改 Schema"""
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
            docstring="用户相关 Pydantic Schemas - Complete JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
