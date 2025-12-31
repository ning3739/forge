"""Token CRUD 生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class TokenCRUDGenerator(BaseTemplateGenerator):
    """Token CRUD 文件生成器"""
    
    def generate(self) -> None:
        """生成 Token CRUD 文件
        
        注意：此生成器由 Orchestrator 在 Complete JWT Auth 且有数据库时调用
        """
        orm_type = self.config_reader.get_orm_type()
        
        if orm_type == "SQLModel":
            self._generate_sqlmodel_crud()
        elif orm_type == "SQLAlchemy":
            self._generate_sqlalchemy_crud()
    
    def _generate_sqlmodel_crud(self) -> None:
        """生成 SQLModel Token CRUD 操作"""
        imports = [
            "import secrets",
            "from datetime import datetime, timedelta",
            "from typing import Optional, List",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlmodel import select",
            "from app.models.token import RefreshToken, VerificationCode",
        ]
        
        content = '''class RefreshTokenCRUD:
    """刷新令牌 CRUD 操作类"""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        token: str,
        expires_at: datetime,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> RefreshToken:
        """创建刷新令牌"""
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_name=device_name,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        return db_token
    
    @staticmethod
    async def get_by_token(db: AsyncSession, token: str) -> Optional[RefreshToken]:
        """根据令牌字符串获取刷新令牌"""
        statement = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_tokens(
        db: AsyncSession,
        user_id: int,
        include_revoked: bool = False
    ) -> List[RefreshToken]:
        """获取用户的所有刷新令牌"""
        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)
        
        if not include_revoked:
            statement = statement.where(RefreshToken.is_revoked == False)
        
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_last_used(db: AsyncSession, token_id: int) -> Optional[RefreshToken]:
        """更新令牌最后使用时间"""
        db_token = await db.get(RefreshToken, token_id)
        if not db_token:
            return None
        
        db_token.last_used_at = datetime.utcnow()
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        return db_token
    
    @staticmethod
    async def revoke(db: AsyncSession, token: str) -> bool:
        """撤销刷新令牌"""
        db_token = await RefreshTokenCRUD.get_by_token(db, token)
        if not db_token:
            return False
        
        db_token.revoke()
        db.add(db_token)
        await db.commit()
        return True
    
    @staticmethod
    async def revoke_user_tokens(db: AsyncSession, user_id: int) -> int:
        """撤销用户的所有刷新令牌"""
        tokens = await RefreshTokenCRUD.get_user_tokens(db, user_id, include_revoked=False)
        
        count = 0
        for token in tokens:
            token.revoke()
            db.add(token)
            count += 1
        
        await db.commit()
        return count
    
    @staticmethod
    async def cleanup_expired(db: AsyncSession) -> int:
        """清理过期的令牌"""
        statement = select(RefreshToken).where(
            RefreshToken.expires_at < datetime.utcnow(),
            RefreshToken.is_revoked == False
        )
        result = await db.execute(statement)
        expired_tokens = list(result.scalars().all())
        
        count = 0
        for token in expired_tokens:
            token.revoke()
            db.add(token)
            count += 1
        
        await db.commit()
        return count


class VerificationCodeCRUD:
    """验证码 CRUD 操作类"""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """生成数字验证码"""
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        code_type: str,
        expiration_minutes: int = 60,
        max_attempts: int = 5,
    ) -> VerificationCode:
        """创建验证码"""
        code = VerificationCodeCRUD.generate_code()
        
        db_code = VerificationCode(
            user_id=user_id,
            code=code,
            code_type=code_type,
            expires_at=datetime.utcnow() + timedelta(minutes=expiration_minutes),
            max_attempts=max_attempts,
        )
        
        db.add(db_code)
        await db.commit()
        await db.refresh(db_code)
        return db_code
    
    @staticmethod
    async def get(
        db: AsyncSession,
        user_id: int,
        code: str,
        code_type: str
    ) -> Optional[VerificationCode]:
        """获取验证码"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code == code,
            VerificationCode.code_type == code_type,
            VerificationCode.is_used == False
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def verify(
        db: AsyncSession,
        user_id: int,
        code: str,
        code_type: str
    ) -> Optional[VerificationCode]:
        """验证验证码"""
        db_code = await VerificationCodeCRUD.get(db, user_id, code, code_type)
        
        if not db_code:
            return None
        
        # 增加尝试次数
        db_code.increment_attempts()
        db.add(db_code)
        await db.commit()
        
        # 检查是否有效
        if not db_code.is_valid():
            return None
        
        # 标记为已使用
        db_code.mark_as_used()
        db.add(db_code)
        await db.commit()
        await db.refresh(db_code)
        
        return db_code
    
    @staticmethod
    async def get_latest(
        db: AsyncSession,
        user_id: int,
        code_type: str
    ) -> Optional[VerificationCode]:
        """获取用户最新的验证码"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code_type == code_type
        ).order_by(VerificationCode.created_at.desc())
        
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def invalidate_user_codes(db: AsyncSession, user_id: int, code_type: str) -> int:
        """使用户的所有未使用验证码失效"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code_type == code_type,
            VerificationCode.is_used == False
        )
        result = await db.execute(statement)
        codes = list(result.scalars().all())
        
        count = 0
        for code in codes:
            code.mark_as_used()
            db.add(code)
            count += 1
        
        await db.commit()
        return count
    
    @staticmethod
    async def cleanup_expired(db: AsyncSession) -> int:
        """清理过期的验证码"""
        statement = select(VerificationCode).where(
            VerificationCode.expires_at < datetime.utcnow(),
            VerificationCode.is_used == False
        )
        result = await db.execute(statement)
        expired_codes = list(result.scalars().all())
        
        count = 0
        for code in expired_codes:
            code.mark_as_used()
            db.add(code)
            count += 1
        
        await db.commit()
        return count


# 创建全局实例
refresh_token_crud = RefreshTokenCRUD()
verification_code_crud = VerificationCodeCRUD()
'''
        
        self.file_ops.create_python_file(
            file_path="app/crud/token.py",
            docstring="Token 和验证码 CRUD 操作",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_sqlalchemy_crud(self) -> None:
        """生成 SQLAlchemy Token CRUD 操作"""
        imports = [
            "import secrets",
            "from datetime import datetime, timedelta",
            "from typing import Optional, List",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy import select",
            "from app.models.token import RefreshToken, VerificationCode",
        ]
        
        content = '''class RefreshTokenCRUD:
    """刷新令牌 CRUD 操作类"""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        token: str,
        expires_at: datetime,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> RefreshToken:
        """创建刷新令牌"""
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_name=device_name,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        return db_token
    
    @staticmethod
    async def get_by_token(db: AsyncSession, token: str) -> Optional[RefreshToken]:
        """根据令牌字符串获取刷新令牌"""
        statement = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_tokens(
        db: AsyncSession,
        user_id: int,
        include_revoked: bool = False
    ) -> List[RefreshToken]:
        """获取用户的所有刷新令牌"""
        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)
        
        if not include_revoked:
            statement = statement.where(RefreshToken.is_revoked == False)
        
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_last_used(db: AsyncSession, token_id: int) -> Optional[RefreshToken]:
        """更新令牌最后使用时间"""
        statement = select(RefreshToken).where(RefreshToken.id == token_id)
        result = await db.execute(statement)
        db_token = result.scalar_one_or_none()
        if not db_token:
            return None
        
        db_token.last_used_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_token)
        return db_token
    
    @staticmethod
    async def revoke(db: AsyncSession, token: str) -> bool:
        """撤销刷新令牌"""
        db_token = await RefreshTokenCRUD.get_by_token(db, token)
        if not db_token:
            return False
        
        db_token.revoke()
        await db.commit()
        return True
    
    @staticmethod
    async def revoke_user_tokens(db: AsyncSession, user_id: int) -> int:
        """撤销用户的所有刷新令牌"""
        tokens = await RefreshTokenCRUD.get_user_tokens(db, user_id, include_revoked=False)
        
        count = 0
        for token in tokens:
            token.revoke()
            count += 1
        
        await db.commit()
        return count
    
    @staticmethod
    async def cleanup_expired(db: AsyncSession) -> int:
        """清理过期的令牌"""
        statement = select(RefreshToken).where(
            RefreshToken.expires_at < datetime.utcnow(),
            RefreshToken.is_revoked == False
        )
        result = await db.execute(statement)
        expired_tokens = list(result.scalars().all())
        
        count = 0
        for token in expired_tokens:
            token.revoke()
            count += 1
        
        await db.commit()
        return count


class VerificationCodeCRUD:
    """验证码 CRUD 操作类"""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """生成数字验证码"""
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        code_type: str,
        expiration_minutes: int = 60,
        max_attempts: int = 5,
    ) -> VerificationCode:
        """创建验证码"""
        code = VerificationCodeCRUD.generate_code()
        
        db_code = VerificationCode(
            user_id=user_id,
            code=code,
            code_type=code_type,
            expires_at=datetime.utcnow() + timedelta(minutes=expiration_minutes),
            max_attempts=max_attempts,
        )
        
        db.add(db_code)
        await db.commit()
        await db.refresh(db_code)
        return db_code
    
    @staticmethod
    async def get(
        db: AsyncSession,
        user_id: int,
        code: str,
        code_type: str
    ) -> Optional[VerificationCode]:
        """获取验证码"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code == code,
            VerificationCode.code_type == code_type,
            VerificationCode.is_used == False
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def verify(
        db: AsyncSession,
        user_id: int,
        code: str,
        code_type: str
    ) -> Optional[VerificationCode]:
        """验证验证码"""
        db_code = await VerificationCodeCRUD.get(db, user_id, code, code_type)
        
        if not db_code:
            return None
        
        # 增加尝试次数
        db_code.increment_attempts()
        await db.commit()
        
        # 检查是否有效
        if not db_code.is_valid():
            return None
        
        # 标记为已使用
        db_code.mark_as_used()
        await db.commit()
        await db.refresh(db_code)
        
        return db_code
    
    @staticmethod
    async def get_latest(
        db: AsyncSession,
        user_id: int,
        code_type: str
    ) -> Optional[VerificationCode]:
        """获取用户最新的验证码"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code_type == code_type
        ).order_by(VerificationCode.created_at.desc())
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def invalidate_user_codes(db: AsyncSession, user_id: int, code_type: str) -> int:
        """使用户的所有未使用验证码失效"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code_type == code_type,
            VerificationCode.is_used == False
        )
        result = await db.execute(statement)
        codes = list(result.scalars().all())
        
        count = 0
        for code in codes:
            code.mark_as_used()
            count += 1
        
        await db.commit()
        return count
    
    @staticmethod
    async def cleanup_expired(db: AsyncSession) -> int:
        """清理过期的验证码"""
        statement = select(VerificationCode).where(
            VerificationCode.expires_at < datetime.utcnow(),
            VerificationCode.is_used == False
        )
        result = await db.execute(statement)
        expired_codes = list(result.scalars().all())
        
        count = 0
        for code in expired_codes:
            code.mark_as_used()
            count += 1
        
        await db.commit()
        return count


# 创建全局实例
refresh_token_crud = RefreshTokenCRUD()
verification_code_crud = VerificationCodeCRUD()
'''
        
        self.file_ops.create_python_file(
            file_path="app/crud/token.py",
            docstring="Token 和验证码 CRUD 操作 - SQLAlchemy",
            imports=imports,
            content=content,
            overwrite=True
        )
