# Testing

When testing is enabled, Forge generates a pytest configuration with async support and fixtures for database and authentication testing.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Fixtures and configuration
├── api/
│   ├── __init__.py
│   ├── test_auth.py     # Authentication tests
│   └── test_users.py    # User endpoint tests
└── unit/
    └── __init__.py
```

## Configuration

pytest is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

## Fixtures

The `tests/conftest.py` file provides essential fixtures:

### Database Session

```python
@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides a database session for each test"""
    # Creates a fresh session
    # Rolls back changes after each test
    # Clears all data for test isolation
```

### Test Client

```python
@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Provides an HTTP client for API testing"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
```

### Test Users

```python
@pytest.fixture
async def test_user_verified(db_session: AsyncSession):
    """Creates a verified user for login tests"""
    # Returns a User with is_verified=True

@pytest.fixture
async def test_user_unverified(db_session: AsyncSession):
    """Creates an unverified user for verification tests"""
    # Returns a User with is_verified=False
```

### Auth Headers

```python
@pytest.fixture
async def auth_headers(test_user_verified) -> dict:
    """Provides authentication headers"""
    access_token, _ = security_manager.create_access_token({
        "user_id": test_user_verified.id
    })
    return {"Authorization": f"Bearer {access_token}"}
```

## Writing Tests

### API Tests

```python
# tests/api/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "Password123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user_verified):
    """Test user login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_verified.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_protected_route(client: AsyncClient, auth_headers):
    """Test accessing protected endpoint"""
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    assert response.status_code == 200
```

### Unit Tests

```python
# tests/unit/test_security.py
import pytest
from app.core.security import get_password_hash, verify_password

def test_password_hashing():
    """Test password hash and verify"""
    password = "SecurePass123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
```

### Testing with Database

```python
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test user creation in database"""
    from app.crud.user import user_crud
    from app.schemas.user import UserCreate
    
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Password123!"
    )
    
    user = await user_crud.create(db_session, user_data)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
```

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run with Verbose Output

```bash
uv run pytest -v
```

### Run Specific File

```bash
uv run pytest tests/api/test_auth.py
```

### Run Specific Test

```bash
uv run pytest tests/api/test_auth.py::test_register
```

### Run with Coverage

```bash
uv run pytest --cov=app --cov-report=html
```

Coverage report is generated in `htmlcov/index.html`.

## Test Database

Tests use SQLite by default, configured in `conftest.py`:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
```

This keeps tests isolated from your development database. The test database is:
- Created fresh for each test session
- Cleaned up after tests complete
- Uses file-based SQLite for async compatibility

## Best Practices

1. **Test isolation**: Each test should be independent
2. **Use fixtures**: Avoid duplicating setup code
3. **Test edge cases**: Invalid inputs, missing data, errors
4. **Mock external services**: Don't call real APIs in tests
5. **Keep tests fast**: Use in-memory databases when possible
6. **Name tests clearly**: `test_<what>_<condition>_<expected>`
