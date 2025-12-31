"""数据库依赖注入文件生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class DatabaseDependenciesGenerator(BaseTemplateGenerator):
    """数据库依赖注入生成器"""
    
    def generate(self) -> None:
        """生成 app/core/database/dependencies.py"""
        if not self.config_reader.has_database():
            return
        
        # 只有启用认证时才生成 dependencies.py
        if not self.config_reader.has_auth():
            return
        
        db_type = self.config_reader.get_database_type()
        auth_type = self.config_reader.get_auth_type()
        
        # 根据数据库类型确定管理器名称
        if db_type == "PostgreSQL":
            db_manager = "postgresql_manager"
            db_import = "from app.core.database.postgresql import postgresql_manager"
        else:  # MySQL
            db_manager = "mysql_manager"
            db_import = "from app.core.database.mysql import mysql_manager"
        
        imports = [
            "from fastapi import Depends, HTTPException, Response",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy import func",
        ]
        
        # 根据 ORM 类型添加导入
        orm_type = self.config_reader.get_orm_type()
        if orm_type == "SQLModel":
            imports.append("from sqlmodel import select")
        else:
            imports.append("from sqlalchemy import select")
        
        imports.extend([
            "from fastapi.security import APIKeyCookie",
            db_import,
            "from app.core.logger import logger_manager",
        ])
        
        # 根据认证类型添加不同的导入和内容
        if auth_type == "complete":
            imports.extend([
                "from app.crud.auth_crud import get_auth_crud",
                "from app.models.auth_model import Token, TokenType",
                "from app.core.security import security_manager",
                "from app.core.config.settings import settings",
            ])
            
            content = self._generate_complete_auth_dependencies(db_manager)
        else:  # basic
            imports.extend([
                "from app.crud.user_crud import get_user_crud",
                "from app.core.security import security_manager",
            ])
            
            content = self._generate_basic_auth_dependencies(db_manager)
        
        self.file_ops.create_python_file(
            file_path="app/core/database/dependencies.py",
            docstring="FastAPI 依赖注入",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_complete_auth_dependencies(self, db_manager: str) -> str:
        """生成完整认证的依赖注入代码"""
        return f'''get_access_token_cookie = APIKeyCookie(
    name="access_token",
    auto_error=False,
    scheme_name="Bearer",
    description="Access token for authentication",
)

get_refresh_token_cookie = APIKeyCookie(
    name="refresh_token",
    auto_error=False,
    scheme_name="Bearer",
    description="Refresh token for authentication",
)


class Dependencies:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_crud = get_auth_crud(db)
        self.{db_manager.split('_')[0]}_manager = {db_manager}
        self.security_manager = security_manager
        self.logger = logger_manager.get_logger(__name__)
    
    async def get_current_user(
        self,
        access_token: str = Depends(get_access_token_cookie),
        db: AsyncSession = Depends({db_manager}.get_db),
    ):
        """获取当前用户（需要认证）"""
        self.logger.info(
            f"get_current_user called with access_token: "
            f"{{'***' if access_token else 'None'}}"
        )
        
        if not access_token:
            self.logger.warning("No access_token provided in request")
            raise HTTPException(
                status_code=401,
                detail="Unauthorized access",
            )
        
        # 验证 access token
        try:
            self.logger.info("Attempting to decode access token")
            token_data = security_manager.decode_token(access_token)
            
            if token_data:
                self.logger.info(
                    f"Token decoded successfully, user_id: {{token_data.get('user_id')}}"
                )
                user_id = token_data.get("user_id")
                
                if user_id:
                    self.logger.info(f"Validating token in database for user_id: {{user_id}}")
                    
                    # 验证 access token 在数据库中的有效性
                    valid_access_token = await db.execute(
                        select(Token).where(
                            Token.user_id == user_id,
                            Token.type == TokenType.access,
                            Token.is_active == True,
                            Token.expired_at > func.utc_timestamp(),
                        )
                    )
                    valid_token = valid_access_token.scalar_one_or_none()
                    
                    if valid_token:
                        self.logger.info(f"Valid token found in database: {{valid_token.id}}")
                        
                        # 从数据库中获取用户信息
                        user = await self.auth_crud.get_user_by_id(user_id)
                        
                        if (
                            user
                            and user.is_active
                            and user.is_verified
                            and not user.is_deleted
                        ):
                            self.logger.info(f"User authenticated via access token: {{user.email}}")
                            return user
                        else:
                            self.logger.warning(
                                f"User validation failed - "
                                f"active: {{user.is_active if user else 'N/A'}}, "
                                f"verified: {{user.is_verified if user else 'N/A'}}, "
                                f"deleted: {{user.is_deleted if user else 'N/A'}}"
                            )
                    else:
                        self.logger.warning(f"No valid token found in database for user_id: {{user_id}}")
                else:
                    self.logger.warning("No user_id found in decoded token")
            else:
                self.logger.warning("Token decode returned None")
        except Exception as e:
            self.logger.warning(f"Access token validation failed: {{str(e)}}")
        
        # 如果所有 token 都无效，抛出未授权错误
        self.logger.warning("All token validation attempts failed")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access",
        )
    
    async def cleanup_tokens(
        self,
        response: Response,
    ) -> bool:
        """清理用户 tokens（登出时使用）"""
        response.delete_cookie(
            "access_token",
            domain=settings.domain.COOKIE_DOMAIN,
            path="/",
        )
        self.logger.info("Access token cookie deleted")
        
        response.delete_cookie(
            "refresh_token",
            domain=settings.domain.COOKIE_DOMAIN,
            path="/",
        )
        self.logger.info("Refresh token cookie deleted")
        
        return True
'''
    
    def _generate_basic_auth_dependencies(self, db_manager: str) -> str:
        """生成基础认证的依赖注入代码"""
        return f'''get_access_token_cookie = APIKeyCookie(
    name="access_token",
    auto_error=False,
    scheme_name="Bearer",
    description="Access token for authentication",
)


class Dependencies:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_crud = get_user_crud(db)
        self.{db_manager.split('_')[0]}_manager = {db_manager}
        self.security_manager = security_manager
        self.logger = logger_manager.get_logger(__name__)
    
    async def get_current_user(
        self,
        access_token: str = Depends(get_access_token_cookie),
        db: AsyncSession = Depends({db_manager}.get_db),
    ):
        """获取当前用户（需要认证）"""
        self.logger.info(
            f"get_current_user called with access_token: "
            f"{{'***' if access_token else 'None'}}"
        )
        
        if not access_token:
            self.logger.warning("No access_token provided in request")
            raise HTTPException(
                status_code=401,
                detail="Unauthorized access",
            )
        
        # 验证 access token
        try:
            self.logger.info("Attempting to decode access token")
            token_data = security_manager.decode_token(access_token)
            
            if token_data:
                self.logger.info(
                    f"Token decoded successfully, user_id: {{token_data.get('user_id')}}"
                )
                user_id = token_data.get("user_id")
                
                if user_id:
                    # 从数据库中获取用户信息
                    user = await self.user_crud.get_user_by_id(user_id)
                    
                    if user and user.is_active and not user.is_deleted:
                        self.logger.info(f"User authenticated: {{user.email}}")
                        return user
                    else:
                        self.logger.warning(
                            f"User validation failed - "
                            f"active: {{user.is_active if user else 'N/A'}}, "
                            f"deleted: {{user.is_deleted if user else 'N/A'}}"
                        )
                else:
                    self.logger.warning("No user_id found in decoded token")
            else:
                self.logger.warning("Token decode returned None")
        except Exception as e:
            self.logger.warning(f"Access token validation failed: {{str(e)}}")
        
        # 如果验证失败，抛出未授权错误
        self.logger.warning("Token validation failed")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access",
        )
'''
