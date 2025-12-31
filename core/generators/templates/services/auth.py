"""认证服务生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class AuthServiceGenerator(BaseTemplateGenerator):
    """认证服务文件生成器"""
    
    def generate(self) -> None:
        """生成认证服务文件"""
        # 只有启用认证才生成
        if not self.config_reader.has_auth():
            return
        
        auth_type = self.config_reader.get_auth_type()
        
        if auth_type == "basic":
            self._generate_basic_auth_service()
        else:  # complete
            self._generate_complete_auth_service()
    
    def _generate_basic_auth_service(self) -> None:
        """生成 Basic JWT Auth 的服务"""
        imports = [
            "from datetime import datetime, timedelta",
            "from typing import Optional",
            "from jose import JWTError, jwt",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.config import settings",
            "from app.crud.user import user_crud",
            "from app.models.user import User",
            "from app.schemas.user import UserCreate, Token",
        ]
        
        content = '''class AuthService:
    """认证服务类 - Basic JWT Auth"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            JWT 令牌字符串
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=settings.jwt.JWT_ACCESS_TOKEN_EXPIRATION)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt.JWT_SECRET_KEY.get_secret_value(),
            algorithm=settings.jwt.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
        """注册新用户
        
        Args:
            db: 数据库会话
            user_data: 用户创建数据
            
        Returns:
            创建的用户对象
            
        Raises:
            ValueError: 用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        if await user_crud.get_by_username(db, user_data.username):
            raise ValueError("Username already registered")
        
        # 检查邮箱是否已存在
        if await user_crud.get_by_email(db, user_data.email):
            raise ValueError("Email already registered")
        
        # 创建用户
        user = await user_crud.create(db, user_data)
        return user
    
    @staticmethod
    async def login_user(db: AsyncSession, username: str, password: str) -> Optional[Token]:
        """用户登录
        
        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            Token 对象，如果认证失败则返回 None
        """
        # 认证用户
        user = await user_crud.authenticate(db, username, password)
        if not user:
            return None
        
        # 检查用户是否激活
        if not user.is_active:
            return None
        
        # 创建访问令牌
        access_token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return Token(access_token=access_token, token_type="bearer")


# 全局服务实例
auth_service = AuthService()
'''
        
        self.file_ops.create_python_file(
            file_path="app/services/auth.py",
            docstring="认证服务 - Basic JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_complete_auth_service(self) -> None:
        """生成 Complete JWT Auth 的服务"""
        imports = [
            "from datetime import datetime, timedelta",
            "from typing import Optional",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.config import settings",
            "from app.core.security import security_manager",
            "from app.crud.user import user_crud",
            "from app.crud.token import refresh_token_crud, verification_code_crud",
            "from app.models.user import User",
            "from app.schemas.user import UserCreate, Token",
            "from app.utils.email import email_service",
        ]
        
        content = '''class AuthService:
    """认证服务类 - Complete JWT Auth"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量（已弃用，使用配置中的值）
            
        Returns:
            JWT 令牌字符串
        """
        token, _ = security_manager.create_access_token(data)
        return token
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建刷新令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量（已弃用，使用配置中的值）
            
        Returns:
            JWT 刷新令牌字符串
        """
        token, _ = security_manager.create_refresh_token(data)
        return token
    
    @staticmethod
    async def register_user(
        db: AsyncSession,
        user_data: UserCreate,
        send_verification: bool = True
    ) -> User:
        """注册新用户
        
        Args:
            db: 数据库会话
            user_data: 用户创建数据
            send_verification: 是否发送验证邮件
            
        Returns:
            创建的用户对象
            
        Raises:
            ValueError: 用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        if await user_crud.get_by_username(db, user_data.username):
            raise ValueError("Username already registered")
        
        # 检查邮箱是否已存在
        if await user_crud.get_by_email(db, user_data.email):
            raise ValueError("Email already registered")
        
        # 创建用户（未验证状态）
        user = await user_crud.create(db, user_data)
        
        # 发送验证邮件
        if send_verification:
            await AuthService.send_verification_email(db, user)
        
        return user
    
    @staticmethod
    async def send_verification_email(db: AsyncSession, user: User) -> None:
        """发送邮箱验证邮件
        
        Args:
            db: 数据库会话
            user: 用户对象
        """
        # 创建验证码
        code = await verification_code_crud.create(
            db,
            user_id=user.id,
            code_type="email_verification",
            expiration_minutes=60
        )
        
        # 发送邮件
        await email_service.send_email(
            subject="Email Verification",
            recipient=user.email,
            template="verification",
            username=user.username,
            code=code.code
        )
    
    @staticmethod
    async def verify_email(db: AsyncSession, user_id: int, code: str) -> bool:
        """验证邮箱
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            code: 验证码
            
        Returns:
            验证是否成功
        """
        # 验证验证码
        verified_code = await verification_code_crud.verify(
            db,
            user_id=user_id,
            code=code,
            code_type="email_verification"
        )
        
        if not verified_code:
            return False
        
        # 标记邮箱已验证
        user = await user_crud.verify_email(db, user_id)
        
        if user:
            # 发送欢迎邮件
            await email_service.send_email(
                subject="Welcome!",
                recipient=user.email,
                template="welcome",
                username=user.username
            )
            return True
        
        return False
    
    @staticmethod
    async def login_user(
        db: AsyncSession,
        username: str,
        password: str,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Token]:
        """用户登录
        
        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 密码
            device_name: 设备名称
            device_type: 设备类型
            ip_address: IP 地址
            user_agent: User Agent
            
        Returns:
            Token 对象，如果认证失败则返回 None
        """
        # 认证用户
        user = await user_crud.authenticate(db, username, password)
        if not user:
            return None
        
        # 检查用户是否激活
        if not user.is_active:
            return None
        
        # 检查邮箱是否已验证
        if not user.is_verified:
            return None
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
        # 创建访问令牌
        access_token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        # 创建刷新令牌
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        # 保存刷新令牌到数据库
        expires_at = datetime.utcnow() + timedelta(seconds=settings.jwt.JWT_REFRESH_TOKEN_EXPIRATION)
        await refresh_token_crud.create(
            db,
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            device_name=device_name,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Optional[str]:
        """使用刷新令牌获取新的访问令牌
        
        Args:
            db: 数据库会话
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌，如果刷新失败则返回 None
        """
        # 验证刷新令牌
        db_token = await refresh_token_crud.get_by_token(db, refresh_token)
        
        if not db_token or not db_token.is_valid():
            return None
        
        # 更新最后使用时间
        await refresh_token_crud.update_last_used(db, db_token.id)
        
        # 获取用户
        user = await user_crud.get_by_id(db, db_token.user_id)
        if not user or not user.is_active:
            return None
        
        # 生成新的访问令牌
        access_token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return access_token
    
    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str) -> bool:
        """请求密码重置
        
        Args:
            db: 数据库会话
            email: 用户邮箱
            
        Returns:
            是否成功发送重置邮件
        """
        # 查找用户
        user = await user_crud.get_by_email(db, email)
        if not user:
            # 为了安全，即使用户不存在也返回 True
            return True
        
        # 创建重置码
        code = await verification_code_crud.create(
            db,
            user_id=user.id,
            code_type="password_reset",
            expiration_minutes=60
        )
        
        # 发送重置邮件
        await email_service.send_email(
            subject="Password Reset",
            recipient=user.email,
            template="password_reset",
            username=user.username,
            code=code.code
        )
        
        return True
    
    @staticmethod
    async def reset_password(db: AsyncSession, email: str, code: str, new_password: str) -> bool:
        """重置密码
        
        Args:
            db: 数据库会话
            email: 用户邮箱
            code: 验证码
            new_password: 新密码
            
        Returns:
            是否成功重置密码
        """
        # 查找用户
        user = await user_crud.get_by_email(db, email)
        if not user:
            return False
        
        # 验证验证码
        verified_code = await verification_code_crud.verify(
            db,
            user_id=user.id,
            code=code,
            code_type="password_reset"
        )
        
        if not verified_code:
            return False
        
        # 修改密码
        await user_crud.change_password(db, user.id, new_password)
        
        # 撤销所有刷新令牌（强制重新登录）
        await refresh_token_crud.revoke_user_tokens(db, user.id)
        
        return True
    
    @staticmethod
    async def logout_user(db: AsyncSession, refresh_token: str) -> bool:
        """用户登出（撤销刷新令牌）
        
        Args:
            db: 数据库会话
            refresh_token: 刷新令牌
            
        Returns:
            是否成功登出
        """
        return await refresh_token_crud.revoke(db, refresh_token)
    
    @staticmethod
    async def logout_all_devices(db: AsyncSession, user_id: int) -> int:
        """登出所有设备
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            
        Returns:
            撤销的令牌数量
        """
        return await refresh_token_crud.revoke_user_tokens(db, user_id)


# 全局服务实例
auth_service = AuthService()
'''
        
        self.file_ops.create_python_file(
            file_path="app/services/auth.py",
            docstring="认证服务 - Complete JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
