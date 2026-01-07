"""Core Dependencies generategenerator - generate app/core/deps.py"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=20,
    requires=["SecurityGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate core dependencies (app/core/deps.py)"
)
class CoreDepsGenerator(BaseTemplateGenerator):
    """generate app/core/deps.py - coredependenciesinjectionfunction"""
    
    def generate(self) -> None:
        """generate app/core/deps.py"""
        if not self.config_reader.has_auth():
            return
        
        imports = [
            "from fastapi import Depends, HTTPException, status",
            "from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.database import get_db",
            "from app.core.security import security_manager",
            "from app.crud.user import user_crud",
            "from app.models.user import User",
        ]
        
        content = '''# HTTP Bearer authenticationscheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """GetcurrentAuthenticate user
    
    Args:
        credentials: HTTP Bearer authenticationcredentials
        db: Database session
    
    Returns:
        User: currentuserobject
    
    Raises:
        HTTPException: 401 - Not authenticated or authentication failed
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # decode token
    payload = security_manager.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await user_crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser
    
    Args:
        current_user: currentuser
    
    Returns:
        User: Current superuser object
    
    Raises:
        HTTPException: 403 - Insufficient permissions
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/deps.py",
            docstring="coredependenciesinjectionfunction",
            imports=imports,
            content=content,
            overwrite=True
        )
