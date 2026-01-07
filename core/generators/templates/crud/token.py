"""Token CRUD generategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="crud",
    priority=61,
    requires=["TokenModelGenerator", "TokenSchemaGenerator"],
    enabled_when=lambda c: c.get_auth_type() == 'complete',
    description="Generate token CRUD operations (app/crud/token.py)"
)
class TokenCRUDGenerator(BaseTemplateGenerator):
    """Token CRUD File generator"""
    
    def generate(self) -> None:
        """generate Token CRUD file
        
        Note: This generator is called by Orchestrator when Complete JWT Auth is enabled and database is configured
        """
        orm_type = self.config_reader.get_orm_type()
        
        if orm_type == "SQLModel":
            self._generate_sqlmodel_crud()
        elif orm_type == "SQLAlchemy":
            self._generate_sqlalchemy_crud()
    
    def _generate_sqlmodel_crud(self) -> None:
        """Generate SQLModel Token CRUD operations"""
        imports = [
            "import secrets",
            "from datetime import datetime, timedelta",
            "from typing import Optional, List",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlmodel import select",
            "from app.models.token import RefreshToken, VerificationCode",
        ]
        
        content = '''class RefreshTokenCRUD:
    """Refresh token CRUD operations class"""
    
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
        """Createrefreshtoken"""
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
        """Get refresh token by token string"""
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
        """Getuserallrefreshtoken"""
        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)
        
        if not include_revoked:
            statement = statement.where(RefreshToken.is_revoked == False)
        
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_last_used(db: AsyncSession, token_id: int) -> Optional[RefreshToken]:
        """Update token last used time"""
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
        """Revoke refresh token"""
        db_token = await RefreshTokenCRUD.get_by_token(db, token)
        if not db_token:
            return False
        
        db_token.revoke()
        db.add(db_token)
        await db.commit()
        return True
    
    @staticmethod
    async def revoke_user_tokens(db: AsyncSession, user_id: int) -> int:
        """Revoke all user refresh tokens"""
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
        """cleanexpirationtoken"""
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
    """Verification code CRUD operations class"""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Generate numeric verification code"""
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        code_type: str,
        expiration_minutes: int = 60,
        max_attempts: int = 5,
    ) -> VerificationCode:
        """Create verification code"""
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
        """Get verification code"""
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
        """Verify verification code"""
        db_code = await VerificationCodeCRUD.get(db, user_id, code, code_type)
        
        if not db_code:
            return None
        
        # Increment attempt count
        db_code.increment_attempts()
        db.add(db_code)
        await db.commit()
        
        # Checkwhethervalid
        if not db_code.is_valid():
            return None
        
        # Mark as used
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
        """Get user's latest verification code"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code_type == code_type
        ).order_by(VerificationCode.created_at.desc())
        
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def invalidate_user_codes(db: AsyncSession, user_id: int, code_type: str) -> int:
        """Invalidate all unused user verification codes"""
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
        """Clean up expired verification codes"""
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


# Createglobalinstance
refresh_token_crud = RefreshTokenCRUD()
verification_code_crud = VerificationCodeCRUD()
'''
        
        self.file_ops.create_python_file(
            file_path="app/crud/token.py",
            docstring="Token and verification code CRUD operations",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_sqlalchemy_crud(self) -> None:
        """Generate SQLAlchemy Token CRUD operations"""
        imports = [
            "import secrets",
            "from datetime import datetime, timedelta",
            "from typing import Optional, List",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy import select",
            "from app.models.token import RefreshToken, VerificationCode",
        ]
        
        content = '''class RefreshTokenCRUD:
    """Refresh token CRUD operations class"""
    
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
        """Createrefreshtoken"""
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
        """Get refresh token by token string"""
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
        """Getuserallrefreshtoken"""
        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)
        
        if not include_revoked:
            statement = statement.where(RefreshToken.is_revoked == False)
        
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_last_used(db: AsyncSession, token_id: int) -> Optional[RefreshToken]:
        """Update token last used time"""
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
        """Revoke refresh token"""
        db_token = await RefreshTokenCRUD.get_by_token(db, token)
        if not db_token:
            return False
        
        db_token.revoke()
        await db.commit()
        return True
    
    @staticmethod
    async def revoke_user_tokens(db: AsyncSession, user_id: int) -> int:
        """Revoke all user refresh tokens"""
        tokens = await RefreshTokenCRUD.get_user_tokens(db, user_id, include_revoked=False)
        
        count = 0
        for token in tokens:
            token.revoke()
            count += 1
        
        await db.commit()
        return count
    
    @staticmethod
    async def cleanup_expired(db: AsyncSession) -> int:
        """cleanexpirationtoken"""
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
    """Verification code CRUD operations class"""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Generate numeric verification code"""
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        code_type: str,
        expiration_minutes: int = 60,
        max_attempts: int = 5,
    ) -> VerificationCode:
        """Create verification code"""
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
        """Get verification code"""
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
        """Verify verification code"""
        db_code = await VerificationCodeCRUD.get(db, user_id, code, code_type)
        
        if not db_code:
            return None
        
        # Increment attempt count
        db_code.increment_attempts()
        await db.commit()
        
        # Checkwhethervalid
        if not db_code.is_valid():
            return None
        
        # Mark as used
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
        """Get user's latest verification code"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code_type == code_type
        ).order_by(VerificationCode.created_at.desc())
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def invalidate_user_codes(db: AsyncSession, user_id: int, code_type: str) -> int:
        """Invalidate all unused user verification codes"""
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
        """Clean up expired verification codes"""
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


# Createglobalinstance
refresh_token_crud = RefreshTokenCRUD()
verification_code_crud = VerificationCodeCRUD()
'''
        
        self.file_ops.create_python_file(
            file_path="app/crud/token.py",
            docstring="Token and verification code CRUD operations - SQLAlchemy",
            imports=imports,
            content=content,
            overwrite=True
        )
