# Testing Guide

Testing ensures your API works correctly and continues working as you make changes. Forge generates a complete pytest test suite that verifies your authentication, user management, and core functionality.

## Why Test

Without tests, every code change is risky. You might break login, registration, or other critical features without realizing it until users complain. With tests, you get immediate feedback—if something breaks, the tests fail and show you exactly what went wrong.

Tests also serve as documentation, showing how your API endpoints work and what they expect.

## Generated Test Suite

Forge creates a working test suite:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_main.py             # Core API tests
└── api/
    ├── test_auth.py         # Authentication tests
    └── test_users.py        # User management tests
```

**conftest.py**: Contains reusable test components (database, client, auth fixtures)
**test_main.py**: Tests health checks and documentation endpoints
**test_auth.py**: Tests registration, login, token refresh, email verification
**test_users.py**: Tests user profile endpoints and authorization

## Running Tests

Install test dependencies:

```bash
uv sync --extra dev
# or: pip install -e ".[dev]"
```

Run all tests:

```bash
pytest
```

Output:
```
tests/test_main.py ✓✓
tests/api/test_auth.py ✓✓✓✓
tests/api/test_users.py ✓✓✓

========== 9 passed in 2.34s ==========
```

Run with details:

```bash
pytest -v  # Show test names
pytest tests/api/test_auth.py  # Run specific file
pytest tests/api/test_auth.py::test_register_user  # Run specific test
```

Check code coverage:

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

Aim for 80%+ coverage. Green lines are tested, red lines are not.

## Test Configuration

The `conftest.py` file sets up everything tests need.

### Test Database

Tests use a temporary SQLite database:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
async def engine():
    """Create test database"""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

**Why SQLite?** It's fast and doesn't require a running database server. Your code works with both SQLite and PostgreSQL/MySQL thanks to SQLAlchemy.

**`scope="session"`**: Database is created once, used by all tests, then cleaned up.

### Test Sessions

Each test gets its own database session that rolls back after the test:

```python
@pytest.fixture
async def db_session(engine):
    """Create test session"""
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback()
```

The rollback ensures tests don't affect each other.

### Test Client

The test client makes HTTP requests to your API:

```python
@pytest.fixture
async def client(db_session):
    """Create test client"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app)) as ac:
        yield ac
```

**Dependency override**: Your API uses the test database instead of the real one.
**AsyncClient**: Makes requests without starting a web server—fast and no network needed.

## Example Tests

### Health Check

```python
@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

**`@pytest.mark.asyncio`**: Marks this as an async test
**`client`**: Test client fixture from conftest.py
**`assert`**: Verifies the response is correct

### User Registration

```python
@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
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
    assert "id" in data
```

**Status 201**: "Created" - more specific than 200
**Check response data**: Verify email matches, ID exists
**No password check**: Passwords should never be in responses

### Protected Endpoint

```python
@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

**`auth_headers`**: Fixture providing authentication token
**Tests authorization**: Verifies endpoint requires authentication

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
