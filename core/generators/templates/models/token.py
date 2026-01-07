"""Token model generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="model",
    priority=41,
    requires=["UserModelGenerator"],
    enabled_when=lambda c: c.get_auth_type() == 'complete',
    description="Generate token model (app/models/token.py)"
)
class TokenModelGenerator(BaseTemplateGenerator):
    """Token model file generator"""
    
    def generate(self) -> None:
        """Generate Token model file
        
        Note: This generator is called by Orchestrator when Complete JWT Auth is enabled and database is configured
        """
        orm_type = self.config_reader.get_orm_type()
        
        if orm_type == "SQLModel":
            self._generate_sqlmodel_token()
        elif orm_type == "SQLAlchemy":
            self._generate_sqlalchemy_token()
    
    def _generate_sqlmodel_token(self) -> None:
        """Generate SQLModel Token model"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from sqlmodel import Field, SQLModel, Relationship",
        ]
        
        content = '''class RefreshToken(SQLModel, table=True):
    """Refresh token model
    
    Used to manage user refresh tokens, supports:
    - Multi-device login (one token per device)
    - Token revocation
    - Token expiration management
    """
    
    __tablename__ = "refresh_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Associated user
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Token information
    token: str = Field(unique=True, index=True, max_length=500)
    expires_at: datetime = Field(index=True)
    
    # Device information (optional)
    device_name: Optional[str] = Field(default=None, max_length=100)
    device_type: Optional[str] = Field(default=None, max_length=50)  # web, mobile, desktop
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 max length 45 characters
    user_agent: Optional[str] = Field(default=None, max_length=500)
    
    # Status
    is_revoked: bool = Field(default=False, index=True)
    revoked_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "device_name": "iPhone 13",
                "device_type": "mobile",
                "is_revoked": False,
            }
        }
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        if self.is_revoked:
            return False
        return datetime.utcnow() < self.expires_at
    
    def revoke(self) -> None:
        """Revoke token"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()


class VerificationCode(SQLModel, table=True):
    """Verification code model
    
    Used to manage email verification codes and password reset codes, supports:
    - Verification code expiration management
    - Verification code usage limit
    - Verification code type distinction
    """
    
    __tablename__ = "verification_codes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Associated user
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Verification code information
    code: str = Field(max_length=10, index=True)
    code_type: str = Field(max_length=20, index=True)  # email_verification, password_reset
    expires_at: datetime = Field(index=True)
    
    # Usage status
    is_used: bool = Field(default=False, index=True)
    used_at: Optional[datetime] = Field(default=None)
    attempts: int = Field(default=0)  # Attempt count
    max_attempts: int = Field(default=5)  # Maximum attempts
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "code": "123456",
                "code_type": "email_verification",
                "is_used": False,
                "attempts": 0,
            }
        }
    
    def is_valid(self) -> bool:
        """Check if verification code is valid"""
        if self.is_used:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return datetime.utcnow() < self.expires_at
    
    def increment_attempts(self) -> None:
        """Increment attempt count"""
        self.attempts += 1
    
    def mark_as_used(self) -> None:
        """Mark as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()
'''
        
        self.file_ops.create_python_file(
            file_path="app/models/token.py",
            docstring="Token andVerification code modeldefinition",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_sqlalchemy_token(self) -> None:
        """Generate SQLAlchemy Token model"""
        imports = [
            "from datetime import datetime",
            "from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String",
            "from sqlalchemy.orm import relationship",
            "from app.core.database import Base",
        ]
        
        content = '''class RefreshToken(Base):
    """Refresh token model
    
    Used to manage user refresh tokens, supports:
    - Multi-device login (one token per device)
    - Token revocation
    - Token expiration management
    """
    
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Associated user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Token information
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Device information (optional)
    device_name = Column(String(100), nullable=True)
    device_type = Column(String(50), nullable=True)  # web, mobile, desktop
    ip_address = Column(String(45), nullable=True)  # IPv6 max length 45 characters
    user_agent = Column(String(500), nullable=True)
    
    # Status
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        if self.is_revoked:
            return False
        return datetime.utcnow() < self.expires_at
    
    def revoke(self) -> None:
        """Revoke token"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()


class VerificationCode(Base):
    """Verification code model
    
    Used to manage email verification codes and password reset codes, supports:
    - Verification code expiration management
    - Verification code usage limit
    - Verification code type distinction
    """
    
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Associated user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Verification code information
    code = Column(String(10), nullable=False, index=True)
    code_type = Column(String(20), nullable=False, index=True)  # email_verification, password_reset
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Usage status
    is_used = Column(Boolean, default=False, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)  # Attempt count
    max_attempts = Column(Integer, default=5, nullable=False)  # Maximum attempts
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="verification_codes")
    
    def __repr__(self):
        return f"<VerificationCode(id={self.id}, user_id={self.user_id}, code_type={self.code_type})>"
    
    def is_valid(self) -> bool:
        """Check if verification code is valid"""
        if self.is_used:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return datetime.utcnow() < self.expires_at
    
    def increment_attempts(self) -> None:
        """Increment attempt count"""
        self.attempts += 1
    
    def mark_as_used(self) -> None:
        """Mark as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()
'''
        
        self.file_ops.create_python_file(
            file_path="app/models/token.py",
            docstring="Token andVerification code modeldefinition - SQLAlchemy",
            imports=imports,
            content=content,
            overwrite=True
        )
