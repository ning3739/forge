"""用户模型生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class UserModelGenerator(BaseTemplateGenerator):
    """用户模型文件生成器"""
    
    def generate(self) -> None:
        """生成用户模型文件
        
        注意：此生成器由 Orchestrator 在启用认证且有数据库时调用
        """
        orm_type = self.config_reader.get_orm_type()
        auth_type = self.config_reader.get_auth_type()
        
        if orm_type == "SQLModel":
            self._generate_sqlmodel_user(auth_type)
        elif orm_type == "SQLAlchemy":
            self._generate_sqlalchemy_user(auth_type)
    
    def _generate_sqlmodel_user(self, auth_type: str) -> None:
        """生成 SQLModel 用户模型"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from sqlmodel import Field, SQLModel",
        ]
        
        # Basic JWT Auth 的用户模型
        if auth_type == "basic":
            content = '''class User(SQLModel, table=True):
    """用户模型 - Basic JWT Auth"""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "is_active": True,
                "is_superuser": False,
            }
        }
'''
        
        # Complete JWT Auth 的用户模型
        else:  # complete
            content = '''class User(SQLModel, table=True):
    """用户模型 - Complete JWT Auth
    
    包含完整的认证功能：
    - 邮箱验证
    - 密码重置
    - 多设备登录支持（通过 RefreshToken 表）
    """
    
    __tablename__ = "users"
    
    # 基础字段
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str = Field(max_length=255)
    
    # 状态字段
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False, description="邮箱是否已验证")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
            }
        }
'''
        
        self.file_ops.create_python_file(
            file_path="app/models/user.py",
            docstring="用户模型定义",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_sqlalchemy_user(self, auth_type: str) -> None:
        """生成 SQLAlchemy 用户模型"""
        imports = [
            "from datetime import datetime",
            "from sqlalchemy import Boolean, Column, DateTime, Integer, String",
            "from app.core.database import Base",
        ]
        
        # Basic JWT Auth 的用户模型
        if auth_type == "basic":
            content = '''class User(Base):
    """用户模型 - Basic JWT Auth"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
'''
        
        # Complete JWT Auth 的用户模型
        else:  # complete
            content = '''class User(Base):
    """用户模型 - Complete JWT Auth
    
    包含完整的认证功能：
    - 邮箱验证
    - 密码重置
    - 多设备登录支持（通过 RefreshToken 表）
    """
    
    __tablename__ = "users"
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 状态字段
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False, comment="邮箱是否已验证")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
'''
        
        self.file_ops.create_python_file(
            file_path="app/models/user.py",
            docstring="用户模型定义",
            imports=imports,
            content=content,
            overwrite=True
        )
