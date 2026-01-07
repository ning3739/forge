"""Token Schema generategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="schema",
    priority=51,
    requires=["TokenModelGenerator"],
    enabled_when=lambda c: c.get_auth_type() == 'complete',
    description="Generate token schemas (app/schemas/token.py)"
)
class TokenSchemaGenerator(BaseTemplateGenerator):
    """Token Schema File generator"""
    
    def generate(self) -> None:
        """generate Token Schema file
        
        Note: This generator is called by Orchestrator when Complete JWT Auth is enabled
        """
        self._generate_token_schemas()
    
    def _generate_token_schemas(self) -> None:
        """generate Token Schemas"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from pydantic import BaseModel, Field, ConfigDict",
        ]
        
        content = '''# ========== Refresh Token Schemas ==========

class RefreshTokenBase(BaseModel):
    """refreshtokenbase Schema"""
    device_name: Optional[str] = Field(None, max_length=200)
    device_type: Optional[str] = Field(None, max_length=50)


class RefreshTokenCreate(RefreshTokenBase):
    """refreshtokenCreate Schema"""
    user_id: int
    token: str
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class RefreshTokenResponse(RefreshTokenBase):
    """refreshtokenresponse Schema"""
    id: int
    user_id: int
    expires_at: datetime
    is_revoked: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    """refreshtokenrequest Schema"""
    refresh_token: str = Field(..., description="Generate token schemas (app/schemas/token.py)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class RefreshTokenRevoke(BaseModel):
    """Revoke refresh token Schema"""
    token: Optional[str] = Field(None, description="Generate token schemas (app/schemas/token.py)")


# ========== Verification Code Schemas ==========

class VerificationCodeBase(BaseModel):
    """Verification code base Schema"""
    code_type: str = Field(..., description="Generate token schemas (app/schemas/token.py)")


class VerificationCodeCreate(VerificationCodeBase):
    """Verification code create Schema"""
    user_id: int
    code: str
    expires_at: datetime
    max_attempts: int = 5


class VerificationCodeResponse(VerificationCodeBase):
    """Verification code response Schema"""
    id: int
    user_id: int
    expires_at: datetime
    is_used: bool
    attempts: int
    max_attempts: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VerificationCodeVerify(BaseModel):
    """Verification code verify Schema"""
    code: str = Field(..., min_length=4, max_length=10)
    code_type: str = Field(..., description="Generate token schemas (app/schemas/token.py)")
    
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
            docstring="Token related Pydantic Schemas - Complete JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
