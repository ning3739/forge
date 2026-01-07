"""user routesgenerategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="router",
    priority=81,
    requires=["UserCRUDGenerator", "CoreDepsGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate user router (app/routers/v1/users.py)"
)
class UserRouterGenerator(BaseTemplateGenerator):
    """user routesFile generator"""
    
    def generate(self) -> None:
        """generateuser routesfile"""
        # Only generate if authentication is enabled
        if not self.config_reader.has_auth():
            return
        
        self._generate_user_router()
    
    def _generate_user_router(self) -> None:
        """generateuser routes"""
        imports = [
            "from fastapi import APIRouter, Depends, HTTPException, status",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from typing import List",
            "",
            "from app.core.database import get_db",
            "from app.core.deps import get_current_user, get_current_superuser",
            "from app.models.user import User",
            "from app.schemas.user import UserResponse, UserUpdate",
            "from app.crud.user import user_crud",
        ]
        
        content = '''router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Getcurrentuserinformation
    
    Args:
        current_user: currentloginuser
        
    Returns:
        userinformation
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """updatecurrentuserinformation
    
    Args:
        user_update: user update data
        current_user: currentloginuser
        db: Database session
        
    Returns:
        updateafteruserinformation
        
    Raises:
        HTTPException: updatefailure
    """
    # ifupdateUsername，Checkwhetheralreadyexists
    if user_update.username and user_update.username != current_user.username:
        existing_user = await user_crud.get_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # ifupdateEmail，Checkwhetheralreadyexists
    if user_update.email and user_update.email != current_user.email:
        existing_user = await user_crud.get_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    updated_user = await user_crud.update(db, current_user.id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete current user account
    
    Args:
        current_user: currentloginuser
        db: Database session
        
    Raises:
        HTTPException: Deletefailure
    """
    success = await user_crud.delete(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


# ========== Admin routes ==========

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """Get user list (admin only)
    
    Args:
        skip: skip count
        limit: return max count
        current_user: current logged in admin user
        db: Database session
        
    Returns:
        userlist
    """
    users = await user_crud.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """Get specified user information (admin only)
    
    Args:
        user_id: user ID
        current_user: current logged in admin user
        db: Database session
        
    Returns:
        userinformation
        
    Raises:
        HTTPException: user does not exist
    """
    user = await user_crud.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """Update specified user information (admin only)
    
    Args:
        user_id: user ID
        user_update: user update data
        current_user: current logged in admin user
        db: Database session
        
    Returns:
        updateafteruserinformation
        
    Raises:
        HTTPException: user does not exist or update failed
    """
    updated_user = await user_crud.update(db, user_id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """Delete specified user (admin only)
    
    Args:
        user_id: user ID
        current_user: current logged in admin user
        db: Database session
        
    Raises:
        HTTPException: user does not exist or delete failed
    """
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    success = await user_crud.delete(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/users.py",
            docstring="usermanagementrouter",
            imports=imports,
            content=content,
            overwrite=True
        )
