"""Test user endpoints generator"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class TestUsersGenerator(BaseTemplateGenerator):
    """generate test_users.py file"""
    
    def generate(self) -> None:
        """generate test_users.py"""
        if not self.config_reader.has_testing() or not self.config_reader.has_auth():
            return
        
        content = self._build_user_tests()
        self.file_ops.create_file(
            file_path="tests/api/test_users.py",
            content=content,
            overwrite=True
        )
    
    def _build_user_tests(self) -> str:
        """Build user tests"""
        return '''"""Test user endpoints"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers):
    """Test get current user"""
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "username" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_update_current_user(client: AsyncClient, auth_headers):
    """Test update current user"""
    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"username": "updateduser"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"


@pytest.mark.asyncio
async def test_get_user_without_auth(client: AsyncClient):
    """Test get user without authentication"""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
'''
