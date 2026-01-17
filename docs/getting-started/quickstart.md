# Quick Start Guide

Welcome to Forge! This guide will walk you through creating your first FastAPI project in about 10 minutes. By the end, you'll have a fully functional API with authentication, database support, and more.

## What is Forge?

Forge is a code generator that creates production-ready FastAPI projects. Instead of manually setting up database connections, authentication, testing, and deployment configurations, Forge asks you a few questions and generates everything for you.

Think of it as a smart project template that adapts to your needs. You choose what features you want, and Forge generates only the code you need - no bloat, no unnecessary dependencies.

## Installation

First, install Forge using pip:

```bash
pip install ningfastforge
```

Or if you prefer uv (it's faster):

```bash
uv tool install ningfastforge
```

Verify the installation:

```bash
forge --version
```

You should see the version number. If you see an error, make sure Python 3.9+ is installed and your PATH is configured correctly.

## Creating Your First Project

### The Interactive Way (Recommended)

Run this command and Forge will guide you through the setup:

```bash
forge init
```

Forge will ask you several questions. Let's go through each one and understand what it means:

#### 1. Project Name

```
Project name (use '.' for current directory): my-api
```

This is the name of your project directory. Forge will create a folder with this name and generate all files inside it.

**Special case**: If you type `.` (a dot), Forge will generate the project in your current directory instead of creating a new folder. This is useful if you've already created a project folder.

#### 2. Database Type

```
Database: 
  PostgreSQL (Recommended)
> MySQL
  SQLite (Development/Small Projects)
```

This determines which database your API will use. Here's what each option means:

- **PostgreSQL**: The most popular choice for production APIs. It's powerful, reliable, and handles complex queries well. Choose this if you're building a real application.

- **MySQL**: Another solid production database. Choose this if you're already using MySQL in your infrastructure or if your hosting provider supports MySQL better.

- **SQLite**: A file-based database that doesn't require a separate database server. Perfect for development, testing, or small applications. The database is just a single file on your disk.

**What Forge generates**: Based on your choice, Forge will install the appropriate database driver (asyncpg for PostgreSQL, aiomysql for MySQL, aiosqlite for SQLite) and create database connection code that works with your chosen database.

#### 3. ORM Framework

```
ORM:
> SQLModel (Recommended)
  SQLAlchemy
```

ORM stands for Object-Relational Mapping - it's how your Python code talks to the database.

- **SQLModel**: A modern ORM built specifically for FastAPI. It combines SQLAlchemy and Pydantic, giving you type safety and automatic API validation. This is the recommended choice for new projects.

- **SQLAlchemy**: The traditional Python ORM. It's been around longer and has more features, but requires more boilerplate code. Choose this if you're already familiar with SQLAlchemy or need its advanced features.

**What Forge generates**: Your database models (like User, Post, etc.) will be written using your chosen ORM. The code structure is slightly different between the two, but both work great.

#### 4. Database Migrations

```
Enable database migrations (Alembic)? (Y/n)
```

Database migrations are like version control for your database schema. When you add a new field to your User model, Alembic creates a migration file that updates the database structure.

**Say Yes if**: You plan to change your database structure over time (which you probably will).

**Say No if**: You're just experimenting and don't care about tracking database changes.

**What Forge generates**: If you say Yes, Forge creates an `alembic/` directory with migration configuration. You'll be able to run commands like `alembic upgrade head` to update your database.

#### 5. Authentication Type

```
Authentication:
> Complete JWT Auth (Recommended)
  Basic JWT Auth (login/register only)
```

Authentication is how users log into your API. Forge generates all the authentication code for you.

- **Complete JWT Auth**: A full-featured authentication system with:
  - User registration and login
  - Email verification (users must verify their email before logging in)
  - Password reset via email
  - Refresh tokens (so users don't have to log in every 30 minutes)
  - Multi-device login tracking (users can see which devices they're logged in from)
  - Logout and logout-all functionality

- **Basic JWT Auth**: Just the essentials:
  - User registration and login
  - JWT tokens for API access
  - That's it - no email verification, no password reset

**What Forge generates**: 
- For Basic: User model, login/register endpoints, JWT token generation
- For Complete: Everything in Basic, plus email service, verification codes, password reset endpoints, refresh token management, and HTML email templates

**Important**: If you choose Complete Auth, you'll need to configure an SMTP email server (like Gmail) to send verification emails. We'll cover this later.

#### 6. Redis Cache

```
Enable Redis (caching, sessions, queues)? (Y/n)
```

Redis is an in-memory data store that makes your API faster. It's used for:
- **Caching**: Store frequently accessed data in memory for instant retrieval
- **Sessions**: Manage user sessions across multiple servers
- **Message queues**: Required if you want to use Celery (next question)

**Say Yes if**: You want caching or plan to use background tasks (Celery).

**Say No if**: You're building a simple API and don't need these features.

**What Forge generates**: Redis connection manager with both async (for FastAPI) and sync (for Celery) clients, plus a rate limiting decorator you can use on your endpoints.

#### 7. Celery Background Tasks

```
Enable Celery (background tasks, job queues)? (Y/n)
```

Celery lets you run tasks in the background without blocking your API. Common uses:
- Sending emails (so your API doesn't wait for the email to send)
- Generating reports
- Processing uploaded files
- Scheduled tasks (like daily database backups)

**Note**: Celery requires Redis, so if you said No to Redis, this option won't appear.

**What Forge generates**: Celery configuration, a database backup task that runs daily at 3 AM, and task management code. The backup task supports all three database types and automatically compresses backups.

#### 8. CORS

```
Enable CORS? (Y/n)
```

CORS (Cross-Origin Resource Sharing) allows your API to be called from web browsers on different domains.

**Say Yes if**: You're building a web frontend that will call this API (which is very common).

**Say No if**: Your API will only be called from the same domain or from non-browser clients.

**What Forge generates**: CORS middleware configuration in your FastAPI app. You can configure which domains are allowed in the `.env` file.

#### 9. Dev Tools

```
Include dev tools (Black + Ruff)? (Y/n)
```

Development tools help you write better code:
- **Black**: Automatically formats your Python code to follow best practices
- **Ruff**: A fast linter that catches common mistakes and style issues

**Say Yes if**: You want to maintain clean, consistent code (recommended).

**What Forge generates**: These tools are added to your `pyproject.toml` dependencies. You can run `black app/` to format code and `ruff check app/` to check for issues.

#### 10. Testing

```
Include testing setup (pytest)? (Y/n)
```

Testing ensures your API works correctly and doesn't break when you make changes.

**What Forge generates**: 
- pytest configuration
- Test fixtures (reusable test setup code)
- Example tests for your authentication and user endpoints
- A test database setup (uses SQLite for reliability)

You can run tests with `pytest` and check coverage with `pytest --cov=app`.

#### 11. Docker

```
Include Docker configs? (Y/n)
```

Docker packages your entire application into a container that runs the same way everywhere.

**Say Yes if**: You plan to deploy your API to a server or cloud platform.

**What Forge generates**:
- `Dockerfile`: Instructions for building your application image
- `docker-compose.yml`: Configuration for running your app with database, Redis, etc.
- `.dockerignore`: Files to exclude from the Docker image

### The Quick Way (Non-Interactive)

If you want to skip all the questions and use recommended defaults:

```bash
forge init my-project --no-interactive
```

This creates a project with:
- MySQL database
- SQLModel ORM
- Complete JWT Auth
- Redis and Celery enabled
- CORS, dev tools, testing, and Docker all enabled

## Understanding Your Generated Project

After Forge finishes, you'll have a project structure like this:

```
my-project/
├── app/                    # Your application code
│   ├── main.py            # FastAPI app entry point
│   ├── core/              # Core functionality
│   │   ├── config/        # Configuration management
│   │   ├── database/      # Database connections
│   │   ├── security.py    # Password hashing
│   │   ├── deps.py        # Dependency injection
│   │   └── logger.py      # Logging setup
│   ├── models/            # Database models (tables)
│   ├── schemas/           # API request/response models
│   ├── crud/              # Database operations
│   ├── services/          # Business logic
│   ├── routers/           # API endpoints
│   └── tasks/             # Background tasks (if Celery enabled)
├── secret/                # Environment variables (NEVER commit to Git!)
│   ├── .env.development   # Development settings
│   └── .env.production    # Production settings
├── tests/                 # Test code (if testing enabled)
├── alembic/               # Database migrations (if enabled)
├── pyproject.toml         # Python dependencies
└── README.md              # Project documentation
```

Let's understand the key directories:

**app/core/**: This is where the "plumbing" lives - database connections, configuration loading, security utilities. You rarely need to modify these files.

**app/models/**: Define your database tables here. Forge generates a User model for you. When you want to add a new table (like Post or Product), you create a new file here.

**app/schemas/**: Define what data your API accepts and returns. These are Pydantic models that automatically validate incoming data and generate API documentation.

**app/routers/**: Define your API endpoints here. Forge generates authentication and user management endpoints. You'll add your own endpoints here as you build your API.

**secret/**: Contains environment variables like database passwords and JWT secret keys. This directory is in `.gitignore` so you don't accidentally commit secrets to Git.

## Running Your Project

### Step 1: Install Dependencies

Navigate to your project and install the required packages:

```bash
cd my-project
uv sync
```

This reads `pyproject.toml` and installs all dependencies. If you don't have uv, use `pip install -e .` instead.

### Step 2: Configure Your Environment

Open `secret/.env.development` in your text editor. This file contains all the settings your API needs to run.

**Database Configuration** (Required):

Find the `DATABASE_URL` line and update it with your database credentials:

```ini
# For PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/mydb

# For MySQL
DATABASE_URL=mysql+aiomysql://root:yourpassword@localhost:3306/mydb

# For SQLite (no changes needed)
DATABASE_URL=sqlite+aiosqlite:///./mydb.db
```

Replace `yourpassword` with your actual database password, and `mydb` with your database name.

**JWT Secret Key** (Important for Production):

Find the `JWT_SECRET_KEY` line:

```ini
JWT_SECRET_KEY=your-secret-key-here-change-in-production
```

For development, you can leave the default value. But for production, you MUST change this to a strong random key. You can generate one with:

```python
import secrets
print(secrets.token_urlsafe(32))
```

**Email Configuration** (Only if you chose Complete Auth):

If you chose Complete JWT Auth, you need to configure email settings so your API can send verification emails and password reset emails.

For Gmail users, update these lines:

```ini
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_FROM_EMAIL=your-email@gmail.com
EMAIL_FROM_NAME=My API
```

**Important**: Gmail requires an "App Password", not your regular Gmail password. Here's how to get one:

1. Go to your Google Account settings
2. Enable 2-Factor Authentication if you haven't already
3. Go to Security → 2-Step Verification → App passwords
4. Generate a password for "Mail"
5. Use that 16-character password in `EMAIL_HOST_PASSWORD`

For other email providers (SendGrid, Mailgun, AWS SES), update the SMTP settings accordingly.

### Step 3: Create Your Database

Before running your API, you need to create the database.

**For PostgreSQL**:
```bash
createdb mydb
```

**For MySQL**:
```bash
mysql -u root -p -e "CREATE DATABASE mydb;"
```

**For SQLite**:
No setup needed! The database file will be created automatically when you run migrations.

### Step 4: Run Database Migrations

Now create the database tables:

```bash
uv run alembic upgrade head
```

This command reads your model definitions (like the User model) and creates the corresponding tables in your database. You'll see output like:

```
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial migration
```

If you see errors, check that:
- Your database is running
- Your `DATABASE_URL` in `.env.development` is correct
- You created the database in Step 3

### Step 5: Start Your API

Now you're ready to run your API:

```bash
uv run uvicorn app.main:app --reload
```

The `--reload` flag makes the server restart automatically when you change code - perfect for development.

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

Success! Your API is now running. Open your browser and visit:

- **http://127.0.0.1:8000/docs** - Interactive API documentation (Swagger UI)
- **http://127.0.0.1:8000/redoc** - Alternative documentation (ReDoc)
- **http://127.0.0.1:8000/health** - Health check endpoint

The `/docs` page is particularly useful - you can test all your API endpoints directly from the browser without writing any code.

### Step 6: Start Background Services (Optional)

If you enabled Redis and Celery, you need to start these services in separate terminal windows.

**Terminal 2 - Start Redis**:

```bash
# macOS (using Homebrew)
brew services start redis

# Linux
sudo systemctl start redis

# Or using Docker
docker run -d -p 6379:6379 redis:7-alpine
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

**Terminal 3 - Start Celery Worker**:

```bash
cd my-project
uv run celery -A app.core.celery:celery_app worker --loglevel=info
```

This starts a Celery worker that processes background tasks. You'll see output showing the worker is ready.

**Terminal 4 - Start Celery Beat** (for scheduled tasks):

```bash
cd my-project
uv run celery -A app.core.celery:celery_app beat --loglevel=info
```

This starts the scheduler that triggers periodic tasks (like the daily database backup at 3 AM).

**Optional - Start Flower** (Celery monitoring dashboard):

```bash
pip install flower
uv run celery -A app.core.celery:celery_app flower
```

Then visit http://localhost:5555 to see a web dashboard showing all your Celery tasks, their status, and execution history.

## Testing Your API

Let's test the authentication system to make sure everything works.

### Register a New User

Open a new terminal and run:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

You should get a response with the new user's information:

```json
{
  "id": 1,
  "email": "test@example.com",
  "username": "testuser",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-18T10:30:00"
}
```

**Note**: If you chose Complete Auth, `is_verified` will be `false` and the user will receive a verification email. For Basic Auth, users can log in immediately.

### Login to Get an Access Token

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "550e8400-e29b-41d4-a716-446655440000",
  "token_type": "bearer"
}
```

Copy the `access_token` value - you'll need it for the next request.

### Access a Protected Endpoint

Now use your token to access the user info endpoint:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

Replace `YOUR_ACCESS_TOKEN_HERE` with the actual token from the previous response.

You should get your user information back, proving that authentication is working correctly.

### Using the Interactive Docs

Instead of using curl, you can test your API in the browser:

1. Go to http://127.0.0.1:8000/docs
2. Click on "POST /api/v1/auth/register"
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

You'll see the response right there in the browser. This is much easier than writing curl commands!

## What's Next?

Congratulations! You now have a fully functional FastAPI project. Here's what you can do next:

### Learn More About Your Project

- **[Configuration Guide](../user-guide/configuration.md)** - Understand all the configuration options in `.env` files
- **[Database Guide](../user-guide/database.md)** - Learn how to create models and run migrations
- **[Authentication Guide](../user-guide/authentication.md)** - Deep dive into the authentication system
- **[Testing Guide](../user-guide/testing.md)** - Write tests for your API

### Add Features to Your API

- **[Redis Caching](../user-guide/redis-caching.md)** - Speed up your API with caching (if you enabled Redis)
- **[Celery Tasks](../user-guide/celery-tasks.md)** - Create background tasks (if you enabled Celery)
- **[Best Practices](../user-guide/best-practices.md)** - Tips and patterns for building great APIs

### Deploy Your API

- **[Deployment Guide](../user-guide/deployment.md)** - Deploy to production with Docker

## Getting Help

If you run into issues:

1. Check the error message carefully - it usually tells you what's wrong
2. Make sure all services are running (database, Redis if enabled)
3. Check that your `.env.development` file has correct settings
4. Look at the logs in `logs/app_development.log`

Still stuck? Get help here:

- **Documentation**: https://ningfastforge.readthedocs.io/
- **GitHub Issues**: https://github.com/ning3739/forge/issues
- **PyPI Package**: https://pypi.org/project/ningfastforge/

## Common Issues

**"Module not found" errors**: Run `uv sync` again to reinstall dependencies.

**Database connection errors**: Check that your database is running and `DATABASE_URL` is correct.

**"Alembic can't find models"**: Make sure you ran `alembic upgrade head` after creating the database.

**Email not sending** (Complete Auth): Check your SMTP settings and make sure you're using an App Password for Gmail.

**Redis connection errors**: Make sure Redis is running with `redis-cli ping`.

Now go build something amazing! 🚀
