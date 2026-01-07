"""usermodelgenerategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="model",
    priority=40,
    requires=["DatabaseConnectionGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate user model (app/models/user.py)"
)
class UserModelGenerator(BaseTemplateGenerator):
    """usermodelFile generator"""
    
    def generate(self) -> None:
        """generateusermodelfile
        
        Note: This generator is called by Orchestrator when authentication is enabled and database is configured
        """
        orm_type = self.config_reader.get_orm_type()
        auth_type = self.config_reader.get_auth_type()
        
        if orm_type == "SQLModel":
            self._generate_sqlmodel_user(auth_type)
        elif orm_type == "SQLAlchemy":
            self._generate_sqlalchemy_user(auth_type)
    
    def _generate_sqlmodel_user(self, auth_type: str) -> None:
        """generate SQLModel usermodel"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional",
            "from sqlmodel import Field, SQLModel",
        ]
        
        # Basic JWT Auth usermodel
        if auth_type == "basic":
            content = '''class User(SQLModel, table=True):
    """usermodel - Basic JWT Auth"""
    
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
        
        # Complete JWT Auth usermodel
        else:  # complete
            content = '''class User(SQLModel, table=True):
    """usermodel - Complete JWT Auth
    
    Contains complete authentication features:
    - EmailValidate
    - Passwordreset
    - Multi-device login support (via RefreshToken table)
    """
    
    __tablename__ = "users"
    
    # basefield
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str = Field(max_length=255)
    
    # Statusfield
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False, description="Generate user model (app/models/user.py)")
    
    # Timestamps
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
            docstring="usermodeldefinition",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_sqlalchemy_user(self, auth_type: str) -> None:
        """generate SQLAlchemy usermodel"""
        imports = [
            "from datetime import datetime",
            "from sqlalchemy import Boolean, Column, DateTime, Integer, String",
            "from app.core.database import Base",
        ]
        
        # Basic JWT Auth usermodel
        if auth_type == "basic":
            content = '''class User(Base):
    """usermodel - Basic JWT Auth"""
    
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
        
        # Complete JWT Auth usermodel
        else:  # complete
            content = '''class User(Base):
    """usermodel - Complete JWT Auth
    
    Contains complete authentication features:
    - EmailValidate
    - Passwordreset
    - Multi-device login support (via RefreshToken table)
    """
    
    __tablename__ = "users"
    
    # basefield
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Statusfield
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False, comment="EmailwhetheralreadyValidate")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
'''
        
        self.file_ops.create_python_file(
            file_path="app/models/user.py",
            docstring="usermodeldefinition",
            imports=imports,
            content=content,
            overwrite=True
        )
