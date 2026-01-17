# Authentication Guide

This guide explains how authentication works in Forge-generated projects. We'll cover both authentication modes, how to use them, and how to customize them for your needs.

## Understanding JWT Authentication

Forge uses JWT (JSON Web Tokens) for authentication. Here's how it works in simple terms:

1. **User registers** with email, username, and password
2. **Password is hashed** using Argon2 (a secure hashing algorithm) and stored in the database
3. **User logs in** with username and password
4. **Server verifies** the password and generates a JWT token
5. **Client stores** the token (usually in localStorage or a cookie)
6. **Client sends** the token with each API request in the Authorization header
7. **Server validates** the token and identifies the user

The beauty of JWT is that the server doesn't need to store session data - everything needed to identify the user is in the token itself.

## Two Authentication Modes

Forge offers two authentication modes. The difference is in the features, not the security - both use the same JWT mechanism.

### Basic JWT Auth

This is the minimal authentication system. It includes:

- **User Registration**: Create new user accounts
- **User Login**: Get a JWT token
- **Password Hashing**: Passwords are securely hashed with Argon2
- **Token-based Access**: Protect endpoints with JWT tokens
- **User Management**: Get and update user information

**When to use Basic Auth**:
- You're building an internal tool or MVP
- You don't need email verification
- You want to handle password resets yourself
- You want the simplest possible setup

**What you get**:
- User model with email, username, hashed_password, is_active
- Login and register endpoints
- JWT token generation (30-minute expiration by default)
- User CRUD operations
- Password hashing with Argon2

### Complete JWT Auth

This is a full-featured authentication system. It includes everything in Basic Auth, plus:

- **Email Verification**: Users must verify their email before logging in
- **Password Reset**: Users can reset forgotten passwords via email
- **Refresh Tokens**: Long-lived tokens (7 days) to get new access tokens without re-logging in
- **Multi-Device Login**: Track which devices a user is logged in from
- **Device Management**: Users can see and revoke sessions from specific devices
- **Email Service**: SMTP email sending with HTML templates
- **Logout Functionality**: Revoke refresh tokens on logout

**When to use Complete Auth**:
- You're building a production application
- You need email verification for security
- You want users to stay logged in across sessions
- You want to track user devices

**What you get**:
- Everything from Basic Auth
- RefreshToken model (stores device info, IP address, user agent)
- VerificationCode model (for email verification and password reset)
- Email service with SMTP support
- HTML email templates (verification, password reset, welcome)
- Additional endpoints for email verification, password reset, refresh tokens, device management

## Generated Files

When you choose authentication, Forge generates these files:

### Models (app/models/)

**user.py** - The User model:

```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)  # Complete Auth only
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

The `is_verified` field is only included in Complete Auth. In Basic Auth, users can log in immediately after registration.

**token.py** (Complete Auth only) - Refresh tokens and verification codes:

```python
class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    token: str = Field(unique=True, index=True)  # UUID
    device_name: str | None  # "Chrome on Windows"
    device_type: str | None  # "web", "mobile", "desktop"
    ip_address: str | None
    user_agent: str | None
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: datetime = Field(default_factory=datetime.utcnow)

class VerificationCode(SQLModel, table=True):
    __tablename__ = "verification_codes"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    code: str = Field(unique=True, index=True)  # 6-digit code
    code_type: str  # "email_verification" or "password_reset"
    expires_at: datetime
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Schemas (app/schemas/)

**user.py** - Request and response models:

```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool  # Complete Auth only
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None  # Complete Auth only
    token_type: str = "bearer"
```

### CRUD Operations (app/crud/)

**user.py** - Database operations for users:

- `get(user_id)` - Get user by ID
- `get_by_email(email)` - Get user by email
- `get_by_username(username)` - Get user by username
- `create(user_data)` - Create new user
- `update(user_id, user_data)` - Update user
- `delete(user_id)` - Delete user
- `authenticate(username, password)` - Verify credentials

**token.py** (Complete Auth only) - Refresh token operations:

- `create_refresh_token(user_id, device_info)` - Create new refresh token
- `get_by_token(token)` - Get refresh token by value
- `get_user_tokens(user_id)` - Get all user's refresh tokens
- `revoke_token(token)` - Revoke a specific token
- `revoke_user_tokens(user_id)` - Revoke all user's tokens
- `cleanup_expired()` - Delete expired tokens

### Services (app/services/)

**auth.py** - Business logic for authentication:

The auth service handles all authentication operations. Here's what it does:

**For Basic Auth**:
- `register_user(user_data)` - Hash password, create user
- `login_user(username, password)` - Verify credentials, generate JWT token
- `get_current_user(token)` - Decode JWT and get user

**For Complete Auth** (includes all Basic Auth functions plus):
- `register_user(user_data, send_verification=True)` - Create user and send verification email
- `login_user(username, password, device_info)` - Verify credentials, check email verification, create refresh token
- `verify_email(user_id, code)` - Verify email with 6-digit code
- `send_verification_email(user)` - Generate code and send email
- `request_password_reset(email)` - Generate reset code and send email
- `reset_password(email, code, new_password)` - Reset password with code
- `refresh_access_token(refresh_token)` - Generate new access token
- `logout_user(refresh_token)` - Revoke specific refresh token
- `logout_all_devices(user_id)` - Revoke all user's refresh tokens

### Routers (app/routers/v1/)

**auth.py** - Authentication endpoints:

**Basic Auth endpoints**:
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

**Complete Auth endpoints** (includes all Basic Auth endpoints plus):
- `POST /api/v1/auth/logout` - Logout from current device
- `POST /api/v1/auth/logout-all` - Logout from all devices
- `POST /api/v1/auth/refresh` - Get new access token using refresh token
- `POST /api/v1/auth/verify-email` - Verify email with code
- `POST /api/v1/auth/resend-verification` - Resend verification email
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with code
- `POST /api/v1/auth/change-password` - Change password (requires current password)
- `GET /api/v1/auth/devices` - List all login devices

**users.py** - User management endpoints:
- `GET /api/v1/users/me` - Get current user info
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Email Service (Complete Auth only)

**app/utils/email.py** - SMTP email sending:

The email service handles all email sending. It includes:

- **SMTP Backend**: Connects to your email server (Gmail, SendGrid, etc.)
- **Template Rendering**: Uses Jinja2 to render HTML email templates
- **Retry Logic**: Automatically retries failed emails with exponential backoff
- **Timeout Handling**: Prevents hanging on slow email servers
- **Error Handling**: Graceful error handling with detailed logging

**Email Templates** (static/email_template/):

- **base.html**: Base template with common styling
- **verification.html**: Email verification template
- **password_reset.html**: Password reset template
- **welcome.html**: Welcome email template

All templates receive these variables:
- `recipient`: User's email address
- `code`: 6-digit verification/reset code
- `expiration_minutes`: How long the code is valid (60 minutes default)
- `year`: Current year
- `app_name`: Your application name

## Using Authentication in Your Code

### Protecting Endpoints

To require authentication for an endpoint, use the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    # current_user is automatically populated from the JWT token
    return {"message": f"Hello {current_user.username}!"}
```

When a client calls this endpoint, they must include the JWT token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

If the token is missing or invalid, FastAPI automatically returns a 401 Unauthorized error.

### Requiring Verified Users (Complete Auth only)

If you want to ensure users have verified their email:

```python
from app.core.deps import get_current_verified_user

@router.get("/verified-only")
async def verified_endpoint(
    current_user: User = Depends(get_current_verified_user)
):
    # Only users with is_verified=True can access this
    return {"message": "You are verified!"}
```

### Optional Authentication

Sometimes you want to know who the user is if they're logged in, but allow anonymous access too:

```python
from app.core.deps import get_current_user_optional

@router.get("/optional-auth")
async def optional_auth_endpoint(
    current_user: User | None = Depends(get_current_user_optional)
):
    if current_user:
        return {"message": f"Hello {current_user.username}!"}
    return {"message": "Hello guest!"}
```

## Configuration

Authentication settings are in `secret/.env.development`:

### JWT Settings

```ini
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRATION=1800  # 30 minutes in seconds
JWT_REFRESH_TOKEN_EXPIRATION=604800  # 7 days in seconds (Complete Auth only)
JWT_ISSUER=my_api
JWT_AUDIENCE=my_api_users
```

**Important**: Change `JWT_SECRET_KEY` to a strong random value in production! Generate one with:

```python
import secrets
print(secrets.token_urlsafe(32))
```

### Email Settings (Complete Auth only)

```ini
# SMTP Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_TIMEOUT=30
EMAIL_EXPIRATION=3600  # Verification code expiration (1 hour)

# Email From Configuration
EMAIL_FROM_NAME=My API
EMAIL_FROM_EMAIL=noreply@yourdomain.com
```

### Gmail Setup

To use Gmail for sending emails:

1. Enable 2-Factor Authentication in your Google Account
2. Go to Security → 2-Step Verification → App passwords
3. Generate a password for "Mail"
4. Use that 16-character password in `EMAIL_HOST_PASSWORD`

**Never use your regular Gmail password** - it won't work and is less secure.

### Other Email Providers

**SendGrid**:
```ini
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

**Mailgun**:
```ini
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
```

**AWS SES**:
```ini
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-ses-smtp-username
EMAIL_HOST_PASSWORD=your-ses-smtp-password
```

## How Refresh Tokens Work (Complete Auth)

Refresh tokens solve a common problem: access tokens expire quickly (30 minutes) for security, but users don't want to log in every 30 minutes.

Here's the flow:

1. **User logs in** → Server returns both access token (30 min) and refresh token (7 days)
2. **User makes API calls** → Uses access token in Authorization header
3. **Access token expires** → API returns 401 Unauthorized
4. **Client refreshes token** → Sends refresh token to `/api/v1/auth/refresh`
5. **Server validates refresh token** → Returns new access token
6. **Client continues** → Uses new access token

The refresh token is stored in the database with device information, so you can:
- Track which devices a user is logged in from
- Revoke specific devices (logout from one device)
- Revoke all devices (logout from all devices)

### Multi-Device Login

Each time a user logs in, a new refresh token is created with device information:

```python
{
  "device_name": "Chrome on Windows",
  "device_type": "web",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
}
```

Users can see all their active sessions:

```bash
GET /api/v1/auth/devices
```

Response:
```json
[
  {
    "id": 1,
    "device_name": "Chrome on Windows",
    "device_type": "web",
    "ip_address": "192.168.1.100",
    "last_used_at": "2024-01-18T10:30:00",
    "created_at": "2024-01-15T08:00:00"
  },
  {
    "id": 2,
    "device_name": "Safari on iPhone",
    "device_type": "mobile",
    "ip_address": "192.168.1.101",
    "last_used_at": "2024-01-18T09:15:00",
    "created_at": "2024-01-16T14:20:00"
  }
]
```

## Email Verification Flow (Complete Auth)

When a user registers:

1. **User submits registration** → POST /api/v1/auth/register
2. **Server creates user** → is_verified=False
3. **Server generates 6-digit code** → Stores in verification_codes table
4. **Server sends email** → Uses verification.html template
5. **User receives email** → Contains 6-digit code
6. **User submits code** → POST /api/v1/auth/verify-email
7. **Server validates code** → Sets is_verified=True
8. **User can now login** → Login requires is_verified=True

If the user doesn't receive the email, they can request a new one:

```bash
POST /api/v1/auth/resend-verification
{
  "email": "user@example.com"
}
```

Verification codes expire after 1 hour (configurable via `EMAIL_EXPIRATION`).

## Password Reset Flow (Complete Auth)

When a user forgets their password:

1. **User requests reset** → POST /api/v1/auth/forgot-password
2. **Server generates 6-digit code** → Stores in verification_codes table
3. **Server sends email** → Uses password_reset.html template
4. **User receives email** → Contains 6-digit code
5. **User submits code + new password** → POST /api/v1/auth/reset-password
6. **Server validates code** → Updates password
7. **Server revokes all refresh tokens** → Forces re-login on all devices

For security, the API always returns success even if the email doesn't exist. This prevents attackers from discovering which emails are registered.

## Security Best Practices

### 1. Strong Secret Keys

Generate a strong JWT secret key:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Use this in production, not the default value.

### 2. HTTPS in Production

Always use HTTPS in production. JWT tokens can be stolen if transmitted over HTTP.

### 3. Token Expiration

Keep access tokens short-lived (30 minutes is good). Use refresh tokens for longer sessions.

### 4. Password Requirements

The generated code doesn't enforce password complexity. Consider adding validation:

```python
from pydantic import validator

class UserCreate(BaseModel):
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

### 5. Rate Limiting

If you enabled Redis, use the rate limiting decorator on authentication endpoints:

```python
from app.core.decorators.rate_limit import rate_limit

@router.post("/login")
@rate_limit(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
async def login(user_data: UserLogin):
    # Login logic
    pass
```

### 6. Account Lockout

Consider implementing account lockout after multiple failed login attempts. The generated code doesn't include this, but you can add it to the auth service.

## Customizing Authentication

### Adding Custom User Fields

Edit `app/models/user.py`:

```python
class User(SQLModel, table=True):
    # Existing fields...
    
    # Add custom fields
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
```

Create a migration:

```bash
alembic revision --autogenerate -m "add user profile fields"
alembic upgrade head
```

Update schemas in `app/schemas/user.py` to include the new fields.

### Customizing Email Templates

Edit the HTML files in `static/email_template/`:

- `verification.html` - Email verification
- `password_reset.html` - Password reset
- `welcome.html` - Welcome email
- `base.html` - Base template (inherited by others)

Templates use Jinja2 syntax. Available variables:

```html
<p>Hello {{ recipient }}!</p>
<p>Your verification code is: <strong>{{ code }}</strong></p>
<p>This code expires in {{ expiration_minutes }} minutes.</p>
<p>&copy; {{ year }} {{ app_name }}</p>
```

### Changing Token Expiration

Edit `secret/.env.development`:

```ini
# 1 hour access tokens
JWT_ACCESS_TOKEN_EXPIRATION=3600

# 30 day refresh tokens
JWT_REFRESH_TOKEN_EXPIRATION=2592000
```

## Troubleshooting

### "Invalid credentials" Error

- Check username/password are correct
- Verify user exists: `SELECT * FROM users WHERE username='testuser'`
- Check password hashing is working (hashed_password should start with `$argon2`)

### "Email not verified" Error (Complete Auth)

- User must verify email before logging in
- Check verification code: `SELECT * FROM verification_codes WHERE user_id=1`
- Resend verification email if needed

### Email Not Sending (Complete Auth)

1. Check SMTP settings in `.env.development`
2. Test SMTP connection:
   ```python
   from app.utils.email import email_service
   email_service.test_connection()
   ```
3. Check logs: `logs/app_development.log`
4. For Gmail, ensure you're using an App Password
5. Check spam folder

### "Token expired" Error

- Access tokens expire after 30 minutes (default)
- Use refresh token to get a new access token: POST /api/v1/auth/refresh
- Or log in again

### Refresh Token Not Working

- Check token hasn't been revoked: `SELECT * FROM refresh_tokens WHERE token='...'`
- Check token hasn't expired
- Check `is_revoked` is False

## Next Steps

- **[Database Guide](database.md)** - Learn about models and migrations
- **[Testing Guide](testing.md)** - Test your authentication endpoints
- **[Best Practices](best-practices.md)** - Security tips and patterns
- **[Deployment Guide](deployment.md)** - Deploy with proper security
