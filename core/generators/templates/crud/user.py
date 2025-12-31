"""用户 CRUD 生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class UserCRUDGenerator(BaseTemplateGenerator):
    """用户 CRUD 文件生成器"""
    
    def generate(self) -> None:
        """生成用户 CRUD 文件"""
        # 只有启用认证且有数据库才生成 CRUD
        if not self.config_reader.has_auth():
            return
        
        if not self.config_reader.has_database():
            return
        
        orm_type = self.config_reader.get_orm_type()
        auth_type = self.config_reader.get_auth_type()
        
        if orm_type == "SQLModel":
            self._generate_sqlmodel_crud(auth_type)
        elif orm_type == "SQLAlchemy":
            self._generate_sqlalchemy_crud(auth_type)
    
    def _generate_sqlmodel_crud(self, auth_type: str) -> None:
        """生成 SQLModel CRUD 操作（异步版本）"""
        imports = [
            "from datetime import datetime, timedelta",
            "from typing import Optional, List",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy import select",
            "from app.models.user import User",
            "from app.schemas.user import UserCreate, UserUpdate",
            "from app.core.security import get_password_hash, verify_password",
        ]
        
        # Basic JWT Auth 的 CRUD
        if auth_type == "basic":
            content = '''class UserCRUD:
    """用户 CRUD 操作类 - Basic JWT Auth (异步)"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await db.get(User, user_id)
        return result
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """创建新用户"""
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
        """更新用户信息"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # 如果更新密码，需要哈希
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
        """删除用户"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        # 尝试用户名登录
        user = await UserCRUD.get_by_username(db, username)
        
        # 如果用户名不存在，尝试邮箱登录
        if not user:
            user = await UserCRUD.get_by_email(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user


# 创建全局实例
user_crud = UserCRUD()
'''
        
        # Complete JWT Auth 的 CRUD
        else:  # complete
            imports.append("import secrets")
            
            content = '''class UserCRUD:
    """用户 CRUD 操作类 - Complete JWT Auth (异步)"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await db.get(User, user_id)
        return result
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """创建新用户"""
        hashed_password = get_password_hash(user_create.password)
        
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            is_verified=False,  # 需要邮箱验证
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # 如果更新密码，需要哈希
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
        """删除用户"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        # 尝试用户名登录
        user = await UserCRUD.get_by_username(db, username)
        
        # 如果用户名不存在，尝试邮箱登录
        if not user:
            user = await UserCRUD.get_by_email(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.add(user)
        await db.commit()
        
        return user
    
    @staticmethod
    async def verify_email(db: AsyncSession, user_id: int) -> Optional[User]:
        """验证用户邮箱"""
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
        """修改用户密码"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.hashed_password = get_password_hash(new_password)
        db_user.updated_at = datetime.utcnow()
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user


# 创建全局实例
user_crud = UserCRUD()
'''
        
        self.file_ops.create_python_file(
            file_path="app/crud/user.py",
            docstring="用户 CRUD 操作（异步）",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_sqlalchemy_crud(self, auth_type: str) -> None:
        """生成 SQLAlchemy CRUD 操作（异步版本）"""
        imports = [
            "from datetime import datetime, timedelta",
            "from typing import Optional, List",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy import select",
            "from app.models.user import User",
            "from app.schemas.user import UserCreate, UserUpdate",
            "from app.core.security import get_password_hash, verify_password",
        ]
        
        # Basic 和 Complete 的 SQLAlchemy CRUD 逻辑类似，只是查询方式不同
        if auth_type == "basic":
            content = '''class UserCRUD:
    """用户 CRUD 操作类 - Basic JWT Auth (异步)"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await db.get(User, user_id)
        return result
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """创建新用户"""
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
        """更新用户信息"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # 如果更新密码，需要哈希
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
        """删除用户"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        # 尝试用户名登录
        user = await UserCRUD.get_by_username(db, username)
        
        # 如果用户名不存在，尝试邮箱登录
        if not user:
            user = await UserCRUD.get_by_email(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user


# 创建全局实例
user_crud = UserCRUD()
'''
        else:  # complete
            imports.append("import secrets")
            
            content = '''class UserCRUD:
    """用户 CRUD 操作类 - Complete JWT Auth (异步)"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await db.get(User, user_id)
        return result
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """创建新用户"""
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
        """更新用户信息"""
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
        """删除用户"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
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
        """验证用户邮箱"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.is_verified = True
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, new_password: str) -> Optional[User]:
        """修改用户密码"""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.hashed_password = get_password_hash(new_password)
        db_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_user)
        return db_user


# 创建全局实例
user_crud = UserCRUD()
'''
        
        self.file_ops.create_python_file(
            file_path="app/crud/user.py",
            docstring="用户 CRUD 操作（异步） - SQLAlchemy",
            imports=imports,
            content=content,
            overwrite=True
        )
