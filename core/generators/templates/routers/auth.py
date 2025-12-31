"""认证路由生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class AuthRouterGenerator(BaseTemplateGenerator):
    """认证路由文件生成器"""
    
    def generate(self) -> None:
        """生成认证路由文件"""
        # 只有启用认证才生成
        if not self.config_reader.has_auth():
            return
        
        auth_type = self.config_reader.get_auth_type()
        
        if auth_type == "basic":
            self._generate_basic_auth_router()
        else:  # complete
            self._generate_complete_auth_router()
    
    def _generate_basic_auth_router(self) -> None:
        """生成 Basic JWT Auth 的路由"""
        imports = [
            "from fastapi import APIRouter, Depends, HTTPException, status",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.database import get_db",
            "from app.schemas.user import UserCreate, UserResponse, UserLogin, Token",
            "from app.services.auth import auth_service",
        ]
        
        content = '''router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """注册新用户
    
    Args:
        user_data: 用户注册数据
        db: 数据库会话
        
    Returns:
        创建的用户信息
        
    Raises:
        HTTPException: 用户名或邮箱已存在
    """
    try:
        user = await auth_service.register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录
    
    Args:
        user_login: 登录凭证
        db: 数据库会话
        
    Returns:
        访问令牌
        
    Raises:
        HTTPException: 认证失败
    """
    # 优先使用 email，其次使用 username
    login_identifier = user_login.email or user_login.username
    
    token = await auth_service.login_user(db, login_identifier, user_login.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/auth.py",
            docstring="认证路由 - Basic JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_complete_auth_router(self) -> None:
        """生成 Complete JWT Auth 的路由"""
        imports = [
            "from fastapi import APIRouter, Depends, HTTPException, status, Request",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.database import get_db",
            "from app.core.deps import get_current_user",
            "from app.models.user import User",
            "from app.schemas.user import (",
            "    UserCreate,",
            "    UserResponse,",
            "    UserLogin,",
            "    Token,",
            "    EmailVerificationRequest,",
            "    ResendVerificationRequest,",
            "    PasswordResetRequest,",
            "    PasswordResetConfirm,",
            "    PasswordChange,",
            ")",
            "from app.schemas.token import RefreshTokenRequest, RefreshTokenResponse",
            "from app.services.auth import auth_service",
            "from app.crud.user import user_crud",
            "from app.crud.token import refresh_token_crud",
        ]
        
        content = '''router = APIRouter(prefix="/auth", tags=["Authentication"])


# ========== 注册和登录 ==========

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """注册新用户
    
    注册后会发送邮箱验证邮件，用户需要验证邮箱后才能登录。
    
    Args:
        user_data: 用户注册数据
        db: 数据库会话
        
    Returns:
        创建的用户信息
        
    Raises:
        HTTPException: 用户名或邮箱已存在
    """
    try:
        user = await auth_service.register_user(db, user_data, send_verification=True)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """用户登录
    
    登录成功后返回访问令牌和刷新令牌。
    用户必须已验证邮箱才能登录。
    
    Args:
        user_login: 登录凭证
        request: 请求对象
        db: 数据库会话
        
    Returns:
        访问令牌和刷新令牌
        
    Raises:
        HTTPException: 认证失败或邮箱未验证
    """
    # 获取设备信息
    user_agent = request.headers.get("User-Agent", "Unknown")
    ip_address = request.client.host if request.client else None
    
    # 优先使用 email，其次使用 username
    login_identifier = user_login.email or user_login.username
    
    token = await auth_service.login_user(
        db,
        login_identifier,
        user_login.password,
        device_name=user_agent[:100] if user_agent else None,
        device_type="web",
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password, or email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


@router.post("/logout")
async def logout(
    refresh_token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登出
    
    撤销指定的刷新令牌。
    
    Args:
        refresh_token_request: 刷新令牌请求
        db: 数据库会话
        
    Returns:
        成功消息
    """
    success = await auth_service.logout_user(db, refresh_token_request.refresh_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """登出所有设备
    
    撤销当前用户的所有刷新令牌。
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        撤销的令牌数量
    """
    count = await auth_service.logout_all_devices(db, current_user.id)
    return {"message": f"Successfully logged out from {count} devices"}


# ========== 令牌刷新 ==========

@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """刷新访问令牌
    
    使用刷新令牌获取新的访问令牌。
    
    Args:
        refresh_token_request: 刷新令牌请求
        db: 数据库会话
        
    Returns:
        新的访问令牌
        
    Raises:
        HTTPException: 刷新令牌无效或已过期
    """
    access_token = await auth_service.refresh_access_token(db, refresh_token_request.refresh_token)
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ========== 邮箱验证 ==========

@router.post("/verify-email")
async def verify_email(
    verification: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """验证邮箱
    
    使用验证码验证用户邮箱。
    
    Args:
        verification: 邮箱验证请求
        db: 数据库会话
        
    Returns:
        成功消息
        
    Raises:
        HTTPException: 验证码无效或已过期
    """
    # 查找用户
    user = await user_crud.get_by_email(db, verification.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 验证邮箱
    success = await auth_service.verify_email(db, user.id, verification.code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """重新发送验证邮件
    
    Args:
        request: 重发验证请求
        db: 数据库会话
        
    Returns:
        成功消息
        
    Raises:
        HTTPException: 用户不存在或邮箱已验证
    """
    # 查找用户
    user = await user_crud.get_by_email(db, request.email)
    if not user:
        # 为了安全，即使用户不存在也返回成功
        return {"message": "If the email exists, a verification code has been sent"}
    
    # 检查是否已验证
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # 发送验证邮件
    await auth_service.send_verification_email(db, user)
    
    return {"message": "Verification email sent"}


# ========== 密码重置 ==========

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """请求密码重置
    
    发送密码重置邮件到用户邮箱。
    
    Args:
        request: 密码重置请求
        db: 数据库会话
        
    Returns:
        成功消息
    """
    await auth_service.request_password_reset(db, request.email)
    
    # 为了安全，总是返回成功消息
    return {"message": "If the email exists, a password reset code has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """重置密码
    
    使用验证码重置密码。
    
    Args:
        reset_data: 密码重置确认数据
        db: 数据库会话
        
    Returns:
        成功消息
        
    Raises:
        HTTPException: 验证码无效或已过期
    """
    success = await auth_service.reset_password(
        db,
        reset_data.email,
        reset_data.code,
        reset_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code"
        )
    
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码
    
    用户修改自己的密码（需要提供旧密码）。
    
    Args:
        password_data: 密码修改数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        成功消息
        
    Raises:
        HTTPException: 旧密码错误
    """
    # 验证旧密码
    user = await user_crud.authenticate(db, current_user.username, password_data.old_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # 修改密码
    await user_crud.change_password(db, current_user.id, password_data.new_password)
    
    # 撤销所有刷新令牌（强制重新登录）
    await refresh_token_crud.revoke_user_tokens(db, current_user.id)
    
    return {"message": "Password changed successfully. Please login again."}


# ========== 设备管理 ==========

@router.get("/devices", response_model=list[RefreshTokenResponse])
async def list_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有登录设备
    
    列出当前用户的所有活跃登录设备。
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        设备列表
    """
    tokens = await refresh_token_crud.get_user_tokens(db, current_user.id, include_revoked=False)
    return tokens
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/auth.py",
            docstring="认证路由 - Complete JWT Auth",
            imports=imports,
            content=content,
            overwrite=True
        )
