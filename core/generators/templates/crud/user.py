"""user CRUD generategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="crud",
    priority=60,
    requires=["UserModelGenerator", "UserSchemaGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate user CRUD operations (app/crud/user.py)"
)
class UserCRUDGenerator(BaseTemplateGenerator):
    """user CRUD File generator"""
    
    def generate(self) -> None:
        """generateuser CRUD file"""
        # Only generate if authentication is enabled CRUD
        if not self.config_reader.has_auth():
            return
        
        orm_type = self.config_reader.get_orm_type()
        auth_type = self.config_reader.get_auth_type()
        
        if orm_type == "SQLModel":
            self._generate_sqlmodel_crud(auth_type)
        elif orm_type == "SQLAlchemy":
            self._generate_sqlalchemy_crud(auth_type)
    
    def _generate_sqlmodel_crud(self, auth_type: str) -> None:
        """Generate SQLModel CRUD operations (async version)"""
        imports = [
            "from datetime import datetime, timedelta",
            "from typing import Optional, List",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy import select",
            "from app.models.user import User",
            "from app.schemas.user import UserCreate, UserUpdate",
            "from app.core.security import get_password_hash, verify_password",
        ]
        
        # Basic JWT Auth  CRUD
        if auth_type == "basic":
            content = '''class UserCRUD:
    """User CRUD operations class - Basic JWT Auth (async)"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.get(User, user_id)
        return result
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Getalluser"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """Createnewuser"""
        hashed_password = get_password_hash(user_create.password)
        
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """updateuserinformation"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # ifupdatePassword，needhash
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Deleteuser"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        # Try username login
        user = await UserCRUD.get_by_username(db, username)
        
        # If username doesn't exist, try email login
        if not user:
            user = await UserCRUD.get_by_email(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user


# Createglobalinstance
user_crud = UserCRUD()
'''
        
        # Complete JWT Auth  CRUD
        else:  # complete
            imports.append("import secrets")
            
            content = '''class UserCRUD:
    """User CRUD operations class - Complete JWT Auth (async)"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.get(User, user_id)
        return result
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Getalluser"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """Createnewuser"""
        hashed_password = get_password_hash(user_create.password)
        
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            is_verified=False,  # needEmailValidate
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """updateuserinformation"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # ifupdatePassword，needhash
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Deleteuser"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        # Try username login
        user = await UserCRUD.get_by_username(db, username)
        
        # If username doesn't exist, try email login
        if not user:
            user = await UserCRUD.get_by_email(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login time
        user.last_login_at = datetime.utcnow()
        db.add(user)
        await db.commit()
        
        return user
    
    @staticmethod
    async def verify_email(db: AsyncSession, user_id: int) -> Optional[User]:
        """ValidateuserEmail"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.is_verified = True
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, new_password: str) -> Optional[User]:
        """modifyuserPassword"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.hashed_password = get_password_hash(new_password)
        db_user.updated_at = datetime.utcnow()
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user


# Createglobalinstance
user_crud = UserCRUD()
'''
        
        self.file_ops.create_python_file(
            file_path="app/crud/user.py",
            docstring="User CRUD operations (async)",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_sqlalchemy_crud(self, auth_type: str) -> None:
        """Generate SQLAlchemy CRUD operations (async version)"""
        imports = [
            "from datetime import datetime, timedelta",
            "from typing import Optional, List",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy import select",
            "from app.models.user import User",
            "from app.schemas.user import UserCreate, UserUpdate",
            "from app.core.security import get_password_hash, verify_password",
        ]
        
        # Basic and Complete SQLAlchemy CRUD logic is similar, only query method differs
        if auth_type == "basic":
            content = '''class UserCRUD:
    """User CRUD operations class - Basic JWT Auth (async)"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.get(User, user_id)
        return result
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Getalluser"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """Createnewuser"""
        hashed_password = get_password_hash(user_create.password)
        
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """updateuserinformation"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # ifupdatePassword，needhash
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Deleteuser"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        # Try username login
        user = await UserCRUD.get_by_username(db, username)
        
        # If username doesn't exist, try email login
        if not user:
            user = await UserCRUD.get_by_email(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user


# Createglobalinstance
user_crud = UserCRUD()
'''
        else:  # complete
            imports.append("import secrets")
            
            content = '''class UserCRUD:
    """User CRUD operations class - Complete JWT Auth (async)"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.get(User, user_id)
        return result
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Getalluser"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """Createnewuser"""
        hashed_password = get_password_hash(user_create.password)
        
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            is_verified=False,
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """updateuserinformation"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Deleteuser"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = await UserCRUD.get_by_username(db, username)
        
        if not user:
            user = await UserCRUD.get_by_email(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
        return user
    
    @staticmethod
    async def verify_email(db: AsyncSession, user_id: int) -> Optional[User]:
        """ValidateuserEmail"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.is_verified = True
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, new_password: str) -> Optional[User]:
        """modifyuserPassword"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.hashed_password = get_password_hash(new_password)
        db_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_user)
        return db_user


# Createglobalinstance
user_crud = UserCRUD()
'''
        
        self.file_ops.create_python_file(
            file_path="app/crud/user.py",
            docstring="User CRUD operations (async) - SQLAlchemy",
            imports=imports,
            content=content,
            overwrite=True
        )
