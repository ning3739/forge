# Testing Guide

Forge generates a comprehensive pytest test suite for your FastAPI application. This guide covers running tests, writing new tests, and best practices.

## Test Suite Overview

When you enable tests (`include_tests: true`), Forge generates:

```
tests/
├── __init__.py
├── conftest.py              # Test configuration and fixtures
├── test_main.py             # Main API tests (health check, docs)
└── api/
    ├── __init__.py
    ├── test_auth.py         # Authentication tests
    └── test_users.py        # User management tests
```

## Running Tests

### Install Test Dependencies

```bash
# Using uv (recommended)
uv sync --extra dev

# Using pip
pip install -e ".[dev]"
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run specific test
pytest tests/api/test_auth.py::test_register_user
```

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw
```

## Test Configuration

### conftest.py

The `conftest.py` file contains shared fixtures:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.core.deps import get_db

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
async def engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def db_session(engine):
    """Create test database session"""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    """Create test client"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
```

## Generated Tests

### Main API Tests

**test_main.py**:
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_docs_available(client: AsyncClient):
    """Test API documentation is available"""
    response = await client.get("/docs")
    assert response.status_code == 200
    
    response = await client.get("/redoc")
    assert response.status_code == 200
```

### Authentication Tests

**test_auth.py** (Basic and Complete modes):
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, test_user_verified):
    """Test user login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
```

### User Management Tests

**test_users.py**:
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers):
    """Test getting current user"""
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_update_current_user(client: AsyncClient, auth_headers):
    """Test updating current user"""
    response = await client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"email": "newemail@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"

@pytest.mark.asyncio
async def test_get_user_unauthorized(client: AsyncClient):
    """Test accessing protected endpoint without auth"""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
```

## Writing Custom Tests

### Testing New Endpoints

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, auth_headers):
    """Test creating a new post"""
    response = await client.post(
        "/api/v1/posts",
        headers=auth_headers,
        json={
            "title": "Test Post",
            "content": "This is a test post"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Post"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_posts(client: AsyncClient):
    """Test getting all posts"""
    response = await client.get("/api/v1/posts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

### Testing Database Operations

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.crud.user import create_user

@pytest.mark.asyncio
async def test_create_user_in_db(db_session: AsyncSession):
    """Test creating user directly in database"""
    user_data = {
        "email": "dbtest@example.com",
        "username": "dbtest",
        "hashed_password": "hashed_pass"
    }
    user = await create_user(db_session, user_data)
    
    assert user.id is not None
    assert user.email == "dbtest@example.com"
    assert user.username == "dbtest"
```

### Testing Background Tasks (Celery)

```python
import pytest
from app.tasks.backup_database_task import backup_database_task

def test_backup_task():
    """Test database backup task"""
    result = backup_database_task.apply()
    assert result.successful()
```

### Testing Email Sending (Complete Mode)

```python
import pytest
from unittest.mock import patch, MagicMock
from app.core.email import send_verification_email

@pytest.mark.asyncio
async def test_send_verification_email():
    """Test sending verification email"""
    with patch('app.core.email.aiosmtplib.send') as mock_send:
        mock_send.return_value = MagicMock()
        
        await send_verification_email(
            email="test@example.com",
            token="test_token"
        )
        
        mock_send.assert_called_once()
```

## Custom Fixtures

### Creating Test Data

```python
# In conftest.py

@pytest.fixture
async def test_post(db_session, test_user_verified):
    """Create a test post"""
    from app.models.post import Post
    
    post = Post(
        title="Test Post",
        content="Test content",
        user_id=test_user_verified.id
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post

@pytest.fixture
async def multiple_users(db_session):
    """Create multiple test users"""
    from app.models.user import User
    
    users = []
    for i in range(5):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            hashed_password="hashed_pass",
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        users.append(user)
    
    await db_session.commit()
    return users
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("email,username,password,expected_status", [
    ("valid@example.com", "validuser", "ValidPass123!", 201),
    ("invalid-email", "user", "pass", 422),  # Invalid email
    ("test@example.com", "a", "pass", 422),  # Username too short
    ("test@example.com", "user", "123", 422),  # Password too short
])
@pytest.mark.asyncio
async def test_register_validation(
    client: AsyncClient,
    email,
    username,
    password,
    expected_status
):
    """Test registration input validation"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password
        }
    )
    assert response.status_code == expected_status
```

## Code Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Open HTML report
open htmlcov/index.html
```

### Coverage Configuration

Create `.coveragerc`:

```ini
[run]
source = app
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

## Continuous Integration

### GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv sync --extra dev
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

### Test Organization

1. **One test per function**: Each test should verify one specific behavior
2. **Descriptive names**: Use clear, descriptive test names
3. **AAA Pattern**: Arrange, Act, Assert
4. **Independent tests**: Tests should not depend on each other
5. **Clean up**: Use fixtures to set up and tear down test data

### Test Data

1. **Use fixtures**: Create reusable test data with fixtures
2. **Isolate tests**: Each test should have its own data
3. **Realistic data**: Use data that resembles production
4. **Edge cases**: Test boundary conditions and edge cases

### Async Testing

1. **Mark async tests**: Use `@pytest.mark.asyncio`
2. **Await async calls**: Don't forget to await async functions
3. **Clean up connections**: Properly close database connections
4. **Use async fixtures**: Create async fixtures for async setup

### Performance

1. **Fast tests**: Keep tests fast (< 1 second each)
2. **Parallel execution**: Use `pytest-xdist` for parallel tests
3. **Database optimization**: Use in-memory SQLite for speed
4. **Mock external services**: Don't make real API calls

## Troubleshooting

### Tests Hanging

```python
# Add timeout to async tests
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_something(client):
    # Test code...
```

### Database Locked (SQLite)

```python
# Use separate database file per test
import uuid

TEST_DATABASE_URL = f"sqlite+aiosqlite:///./test_{uuid.uuid4()}.db"
```

### Import Errors

```bash
# Install package in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### Fixture Not Found

```python
# Ensure conftest.py is in correct location
# Check fixture scope matches usage
# Verify fixture name spelling
```

## See Also

- [Configuration Options](configuration.md) - Test configuration
- [Database Setup](database.md) - Test database setup
- [Authentication Guide](authentication.md) - Testing auth
- [CLI Commands](cli-commands.md) - Running tests
