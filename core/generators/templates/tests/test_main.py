"""Test main API endpoints generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="test",
    priority=111,
    requires=["MainGenerator"],
    enabled_when=lambda c: c.has_testing(),
    description="Generate main API tests (tests/test_main.py)"
)
class TestMainGenerator(BaseTemplateGenerator):
    """generate test_main.py file"""
    
    def generate(self) -> None:
        """generate test_main.py"""
        if not self.config_reader.has_testing():
            return
        
        content = self._build_test_main()
        self.file_ops.create_file(
            file_path="tests/test_main.py",
            content=content,
            overwrite=True
        )
    
    def _build_test_main(self) -> str:
        """Build test_main.py content"""
        return '''"""Test main API endpoints"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_docs(client: AsyncClient):
    """Test API documentation endpoint"""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi(client: AsyncClient):
    """Test OpenAPI schema endpoint"""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
'''
