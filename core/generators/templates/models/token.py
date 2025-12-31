"""Token 模型生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class TokenModelGenerator(BaseTemplateGenerator):
    """Token 模型文件生成器"""
    
    def generate(self) -> None:
        """生成 Token 模型文件
        
        注意：此生成器由 Orchestrator 在 Complete JWT Auth 且有数据库时调用
        """
        orm_type = self.config_reader.get_orm_type()
        
        if orm_type == "SQLModel":
            self._generate_sqlmodel_token()
        elif orm_type == "SQLAlchemy":
            self._generate_sqlalchemy_token()
    
    def _generate_sqlmodel_token(self) -> None:
        """生成 SQLModel Token 模型"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from sqlmodel import Field, SQLModel, Relationship",
        ]
        
        content = '''class RefreshToken(SQLModel, table=True):
    """刷新令牌模型
    
    用于管理用户的刷新令牌，支持：
    - 多设备登录（每个设备一个令牌）
    - 令牌撤销
    - 令牌过期管理
    """
    
    __tablename__ = "refresh_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 关联用户
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # 令牌信息
    token: str = Field(unique=True, index=True, max_length=500)
    expires_at: datetime = Field(index=True)
    
    # 设备信息（可选）
    device_name: Optional[str] = Field(default=None, max_length=100)
    device_type: Optional[str] = Field(default=None, max_length=50)  # web, mobile, desktop
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 最长 45 字符
    user_agent: Optional[str] = Field(default=None, max_length=500)
    
    # 状态
    is_revoked: bool = Field(default=False, index=True)
    revoked_at: Optional[datetime] = Field(default=None)
    
    # 时间戳
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
        """检查令牌是否有效"""
        if self.is_revoked:
            return False
        return datetime.utcnow() < self.expires_at
    
    def revoke(self) -> None:
        """撤销令牌"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()


class VerificationCode(SQLModel, table=True):
    """验证码模型
    
    用于管理邮箱验证码和密码重置码，支持：
    - 验证码过期管理
    - 验证码使用次数限制
    - 验证码类型区分
    """
    
    __tablename__ = "verification_codes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 关联用户
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # 验证码信息
    code: str = Field(max_length=10, index=True)
    code_type: str = Field(max_length=20, index=True)  # email_verification, password_reset
    expires_at: datetime = Field(index=True)
    
    # 使用状态
    is_used: bool = Field(default=False, index=True)
    used_at: Optional[datetime] = Field(default=None)
    attempts: int = Field(default=0)  # 尝试次数
    max_attempts: int = Field(default=5)  # 最大尝试次数
    
    # 时间戳
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
        """检查验证码是否有效"""
        if self.is_used:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return datetime.utcnow() < self.expires_at
    
    def increment_attempts(self) -> None:
        """增加尝试次数"""
        self.attempts += 1
    
    def mark_as_used(self) -> None:
        """标记为已使用"""
        self.is_used = True
        self.used_at = datetime.utcnow()
'''
        
        self.file_ops.create_python_file(
            file_path="app/models/token.py",
            docstring="Token 和验证码模型定义",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_sqlalchemy_token(self) -> None:
        """生成 SQLAlchemy Token 模型"""
        imports = [
            "from datetime import datetime",
            "from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String",
            "from sqlalchemy.orm import relationship",
            "from app.core.database import Base",
        ]
        
        content = '''class RefreshToken(Base):
    """刷新令牌模型
    
    用于管理用户的刷新令牌，支持：
    - 多设备登录（每个设备一个令牌）
    - 令牌撤销
    - 令牌过期管理
    """
    
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 令牌信息
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # 设备信息（可选）
    device_name = Column(String(100), nullable=True)
    device_type = Column(String(50), nullable=True)  # web, mobile, desktop
    ip_address = Column(String(45), nullable=True)  # IPv6 最长 45 字符
    user_agent = Column(String(500), nullable=True)
    
    # 状态
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", backref="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"
    
    def is_valid(self) -> bool:
        """检查令牌是否有效"""
        if self.is_revoked:
            return False
        return datetime.utcnow() < self.expires_at
    
    def revoke(self) -> None:
        """撤销令牌"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()


class VerificationCode(Base):
    """验证码模型
    
    用于管理邮箱验证码和密码重置码，支持：
    - 验证码过期管理
    - 验证码使用次数限制
    - 验证码类型区分
    """
    
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 验证码信息
    code = Column(String(10), nullable=False, index=True)
    code_type = Column(String(20), nullable=False, index=True)  # email_verification, password_reset
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # 使用状态
    is_used = Column(Boolean, default=False, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)  # 尝试次数
    max_attempts = Column(Integer, default=5, nullable=False)  # 最大尝试次数
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", backref="verification_codes")
    
    def __repr__(self):
        return f"<VerificationCode(id={self.id}, user_id={self.user_id}, code_type={self.code_type})>"
    
    def is_valid(self) -> bool:
        """检查验证码是否有效"""
        if self.is_used:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return datetime.utcnow() < self.expires_at
    
    def increment_attempts(self) -> None:
        """增加尝试次数"""
        self.attempts += 1
    
    def mark_as_used(self) -> None:
        """标记为已使用"""
        self.is_used = True
        self.used_at = datetime.utcnow()
'''
        
        self.file_ops.create_python_file(
            file_path="app/models/token.py",
            docstring="Token 和验证码模型定义 - SQLAlchemy",
            imports=imports,
            content=content,
            overwrite=True
        )
