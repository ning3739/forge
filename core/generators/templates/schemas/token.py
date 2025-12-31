"""Token Schema 生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class TokenSchemaGenerator(BaseTemplateGenerator):
    """Token Schema 文件生成器"""
    
    def generate(self) -> None:
        """生成 Token Schema 文件
        
        注意：此生成器由 Orchestrator 在 Complete JWT Auth 时调用
        """
        self._generate_token_schemas()
    
    def _generate_token_schemas(self) -> None:
        """生成 Token Schemas"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from pydantic import BaseModel, Field, ConfigDict",
        ]
        
        content = '''# ========== Refresh Token Schemas ==========

class RefreshTokenBase(BaseModel):
    """刷新令牌基础 Schema"""
    device_name: Optional[str] = Field(None, max_length=200)
    device_type: Optional[str] = Field(None, max_length=50)


class RefreshTokenCreate(RefreshTokenBase):
    """刷新令牌创建 Schema"""
    user_id: int
    token: str
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class RefreshTokenResponse(RefreshTokenBase):
    """刷新令牌响应 Schema"""
    id: int
    user_id: int
    expires_at: datetime
    is_revoked: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求 Schema"""
    refresh_token: str = Field(..., description="刷新令牌")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class RefreshTokenRevoke(BaseModel):
    """撤销刷新令牌 Schema"""
    token: Optional[str] = Field(None, description="要撤销的令牌，不提供则撤销所有")


# ========== Verification Code Schemas ==========

class VerificationCodeBase(BaseModel):
    """验证码基础 Schema"""
    code_type: str = Field(..., description="验证码类型: email_verification 或 password_reset")


class VerificationCodeCreate(VerificationCodeBase):
    """验证码创建 Schema"""
    user_id: int
    code: str
    expires_at: datetime
    max_attempts: int = 5


class VerificationCodeResponse(VerificationCodeBase):
    """验证码响应 Schema"""
    id: int
    user_id: int
    expires_at: datetime
    is_used: bool
    attempts: int
    max_attempts: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VerificationCodeVerify(BaseModel):
    """验证码验证 Schema"""
    code: str = Field(..., min_length=4, max_length=10)
    code_type: str = Field(..., description="验证码类型")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "123456",
                "code_type": "email_verification"
            }
        }
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/schemas/token.py",
            docstring="Token 相关 Pydantic Schemas - Complete JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
