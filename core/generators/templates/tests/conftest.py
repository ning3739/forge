"""Pytest configuration generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="test",
    priority=110,
    requires=["DatabaseConnectionGenerator"],
    enabled_when=lambda c: c.has_testing(),
    description="Generate pytest configuration (tests/conftest.py)"
)
class ConftestGenerator(BaseTemplateGenerator):
    """generate pytest conftest.py file"""
    
    def generate(self) -> None:
        """generate conftest.py"""
        if not self.config_reader.has_testing():
            return
        
        content = self._build_conftest()
        self.file_ops.create_file(
            file_path="tests/conftest.py",
            content=content,
            overwrite=True
        )
    
    def _build_conftest(self) -> str:
        """Build conftest.py content"""
        imports = [
            "import pytest",
            "import asyncio",
            "from typing import AsyncGenerator, Generator",
            "from httpx import AsyncClient",
            "from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker",
            "from app.main import app",
            "from app.core.config import settings",
        ]
        
        db_type = self.config_reader.get_database_type()
        if db_type == "PostgreSQL":
            imports.append("from app.core.database import Base")
        else:
            imports.append("from app.core.database import Base")
        
        content = f'''"""Pytest configuration and fixtures"""
{chr(10).join(imports)}


# Test database URL
TEST_DATABASE_URL = settings.database.url.replace(
    settings.database.database_name,
    f"{{settings.database.database_name}}_test"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
'''
        
        # Add auth fixtures if authentication is enabled
        if self.config_reader.has_auth():
            content += self._build_auth_fixtures()
        
        return content
    
    def _build_auth_fixtures(self) -> str:
        """Build authentication fixtures"""
        return '''

@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create test user"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user) -> dict:
    """Get authentication headers"""
    from app.core.security import create_access_token
    
    access_token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {access_token}"}
'''
