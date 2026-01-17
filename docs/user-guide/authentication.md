# Authentication Guide

Forge provides flexible JWT-based authentication with three modes: None, Basic, and Complete. This guide covers setup, usage, and customization.

## Authentication Modes

### None

No authentication system. Choose this when:
- Building a public API
- Implementing custom authentication
- Authentication is handled by external service

### Basic

JWT token authentication with core features:
- User registration
- User login
- Password hashing (bcrypt)
- Token-based API access
- User management endpoints

### Complete

Everything in Basic, plus:
- Email verification
- Password reset functionality
- Email templates
- Token refresh mechanism
- Resend verification email

## Generated Components

### Models

**User Model** (`app/models/user.py`):
```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)  # Complete mode only
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Token Model** (`app/models/token.py`):
```python
class Token(SQLModel, table=True):
    __tablename__ = "tokens"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    token: str = Field(unique=True, index=True)
    token_type: str  # "access", "refresh", "verification", "reset"
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Schemas

**User Schemas** (`app/schemas/user.py`):
```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool  # Complete mode only
    created_at: datetime
```

**Token Schemas** (`app/schemas/token.py`):
```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None  # Complete mode only

class TokenData(BaseModel):
    user_id: int
    username: str
```

### API Endpoints

#### Basic Mode Endpoints

**Register**:
```text
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Login**:
```text
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Get Current User**:
```text
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Update Current User**:
```text
PUT /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "email": "newemail@example.com"
}
```

#### Complete Mode Additional Endpoints

**Verify Email**:
```text
POST /api/v1/auth/verify-email
Content-Type: application/json

{
  "token": "verification_token_here"
}
```

**Resend Verification**:
```text
POST /api/v1/auth/resend-verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Forgot Password**:
```text
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Reset Password**:
```text
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "reset_token_here",
  "new_password": "NewSecurePass123!"
}
```

**Refresh Token**:
```text
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh_token_here"
}
```

## Security Configuration

### JWT Settings

Configuration in `app/core/settings.py`:

```python
class Settings(BaseSettings):
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-here"  # Change in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Complete mode only
    
    # Email Configuration (Complete mode only)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = ""
    EMAILS_FROM_NAME: str = "My API"
```

### Password Hashing

Uses bcrypt for secure password hashing:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Token Generation

```python
from datetime import datetime, timedelta
import jwt

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

## Using Authentication

### Protecting Endpoints

Use the `get_current_user` dependency:

```python
from fastapi import Depends
from app.core.deps import get_current_user
from app.models.user import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}!"}
```

### Requiring Verified Users (Complete Mode)

```python
from app.core.deps import get_current_verified_user

@router.get("/verified-only")
async def verified_route(
    current_user: User = Depends(get_current_verified_user)
):
    return {"message": "You are verified!"}
```

### Optional Authentication

```python
from app.core.deps import get_current_user_optional

@router.get("/optional-auth")
async def optional_auth_route(
    current_user: User | None = Depends(get_current_user_optional)
):
    if current_user:
        return {"message": f"Hello {current_user.username}!"}
    return {"message": "Hello guest!"}
```

## Email Configuration (Complete Mode)

### SMTP Setup

Update `.env.development`:

```ini
# Gmail Example
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME=My API

# SendGrid Example
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
EMAILS_FROM_EMAIL=noreply@yourdomain.com
EMAILS_FROM_NAME=My API
```

### Gmail Setup

1. Enable 2-Factor Authentication
2. Generate App Password:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use app password in `SMTP_PASSWORD`

### Email Templates

Located in `static/email_template/`:

**Verification Email** (`verification_email.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <title>Verify Your Email</title>
</head>
<body>
    <h1>Welcome to {{ app_name }}!</h1>
    <p>Please verify your email by clicking the link below:</p>
    <a href="{{ verification_url }}">Verify Email</a>
</body>
</html>
```

**Password Reset Email** (`reset_password_email.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <title>Reset Your Password</title>
</head>
<body>
    <h1>Password Reset Request</h1>
    <p>Click the link below to reset your password:</p>
    <a href="{{ reset_url }}">Reset Password</a>
</body>
</html>
```

## Client Integration

### JavaScript/TypeScript

```typescript
// Register
const register = async (email: string, username: string, password: string) => {
  const response = await fetch('http://localhost:8000/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username, password })
  });
  return response.json();
};

// Login
const login = async (username: string, password: string) => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
};

// Authenticated Request
const getProfile = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/api/v1/users/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

### Python Client

```python
import requests

# Register
response = requests.post(
    'http://localhost:8000/api/v1/auth/register',
    json={
        'email': 'user@example.com',
        'username': 'johndoe',
        'password': 'SecurePass123!'
    }
)

# Login
response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={'username': 'johndoe', 'password': 'SecurePass123!'}
)
token = response.json()['access_token']

# Authenticated Request
response = requests.get(
    'http://localhost:8000/api/v1/users/me',
    headers={'Authorization': f'Bearer {token}'}
)
user = response.json()
```

## Customization

### Adding Custom Fields

Edit `app/models/user.py`:

```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    # Existing fields...
    
    # Add custom fields
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
```

Create migration:
```bash
alembic revision --autogenerate -m "Add user profile fields"
alembic upgrade head
```

### Custom Authentication Logic

Override in `app/services/auth.py`:

```python
async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> User | None:
    # Add custom logic here
    # Example: Check if user is banned
    user = await get_user_by_username(db, username)
    if not user or user.is_banned:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
```

### Rate Limiting

Add rate limiting to auth endpoints:

```python
from app.core.decorators import rate_limit

@router.post("/login")
@rate_limit(max_requests=5, window_seconds=60)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    # Login logic...
```

## Security Best Practices

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use HTTPS in production
- [ ] Set secure cookie flags
- [ ] Implement rate limiting
- [ ] Add CORS configuration
- [ ] Enable password complexity requirements
- [ ] Implement account lockout after failed attempts
- [ ] Log authentication events
- [ ] Regular security audits
- [ ] Keep dependencies updated

### Password Requirements

Add validation in `app/schemas/user.py`:

```python
from pydantic import validator

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### Token Security

```python
# Rotate tokens regularly
# Invalidate tokens on password change
# Store refresh tokens securely
# Use short expiration times
# Implement token blacklist for logout
```

## Troubleshooting

### "Invalid credentials" Error

- Check username/password are correct
- Verify user exists in database
- Check password hashing is working

### "Token expired" Error

- Token has exceeded `ACCESS_TOKEN_EXPIRE_MINUTES`
- Use refresh token to get new access token (Complete mode)
- Re-login to get new token

### Email Not Sending (Complete Mode)

- Check SMTP credentials in `.env`
- Verify SMTP server allows connections
- Check spam folder
- Review application logs for errors

### "User not verified" Error (Complete Mode)

- User must verify email before accessing protected routes
- Resend verification email
- Check email delivery

## See Also

- [Configuration Options](configuration.md) - Auth configuration
- [Database Setup](database.md) - User model and migrations
- [Testing Guide](testing.md) - Testing authentication
- [Deployment Guide](deployment.md) - Production security
