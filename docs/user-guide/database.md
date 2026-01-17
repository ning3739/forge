# Database Setup

When you create a project with Forge, you choose one of three database systems. This choice affects how your application stores data, what drivers get installed, and how you'll deploy to production. Let's walk through what each option means and how to work with them.

## Choosing Your Database

During `forge init`, you'll see this prompt:

```bash
? Select database: 
  PostgreSQL (Recommended for production)
  MySQL
❯ SQLite (Good for development)
```

**PostgreSQL** is the recommended choice for production applications. It's a powerful, open-source database with excellent performance, strong data integrity guarantees, and support for complex queries. Most modern cloud platforms offer managed PostgreSQL services, making deployment straightforward.

**MySQL** is a solid alternative if you're already using MySQL infrastructure or your hosting provider specializes in MySQL. It's widely supported and performs well for most use cases.

**SQLite** is perfect for development and small applications. It stores everything in a single file, requires no server setup, and is included with Python. However, it's not recommended for production applications with multiple workers or high concurrency needs.

The good news? You can develop with SQLite and deploy with PostgreSQL by simply changing your `DATABASE_URL` environment variable. The generated code works with all three.

## PostgreSQL Setup

PostgreSQL is a powerful, open-source relational database that's become the standard for modern web applications. When you choose PostgreSQL, Forge configures your project to use `asyncpg`, an async Python driver that allows your FastAPI application to handle database queries without blocking other requests.

### Installing PostgreSQL

First, you need PostgreSQL running on your machine. The installation process varies by operating system:

**macOS with Homebrew**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

This installs PostgreSQL 15 and starts it as a background service. You can verify it's running with `brew services list`.

**Ubuntu/Debian Linux**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Start on boot
```

**Windows**:
Download the installer from [postgresql.org](https://www.postgresql.org/download/windows/) and follow the setup wizard. Remember the password you set for the `postgres` user—you'll need it.

### Creating Your Database

Once PostgreSQL is installed, you need to create a database for your application. Connect to PostgreSQL as the superuser:

```bash
# macOS/Linux
psql -U postgres

# Windows (use SQL Shell from Start menu)
```

Now create your database and a dedicated user:

```sql
-- Create the database
CREATE DATABASE myapi;

-- Create a user with a strong password
CREATE USER myapi_user WITH PASSWORD 'your_secure_password_here';

-- Grant all privileges on the database to your user
GRANT ALL PRIVILEGES ON DATABASE myapi TO myapi_user;

-- Exit psql
\q
```

**Why create a separate user?** It's a security best practice. Your application doesn't need superuser privileges—it only needs access to its own database.

### Configuring Your Application

Now tell your Forge application how to connect to PostgreSQL. Open `secret/.env.development` and set the `DATABASE_URL`:

```ini
DATABASE_URL=postgresql+asyncpg://myapi_user:your_secure_password_here@localhost:5432/myapi
```

Let's break down this connection string:
- `postgresql+asyncpg://` - Use PostgreSQL with the asyncpg driver
- `myapi_user:your_secure_password_here` - Your database credentials
- `@localhost:5432` - PostgreSQL server location (localhost) and port (5432 is default)
- `/myapi` - The database name

For production, you'll use a different URL pointing to your production database server:

```ini
# Production (.env.production)
DATABASE_URL=postgresql+asyncpg://myapi_user:production_password@db.example.com:5432/myapi_prod
```

### Python Dependencies

When you choose PostgreSQL, Forge automatically adds `asyncpg` to your `pyproject.toml`:

```toml
asyncpg = "^0.29.0"  # Async PostgreSQL driver
```

This driver is what allows your FastAPI application to query PostgreSQL asynchronously, keeping your API responsive even during database operations.

## MySQL Setup

MySQL is another popular open-source relational database. When you choose MySQL, Forge configures your project to use `aiomysql`, an async driver that works similarly to asyncpg but for MySQL databases.

### Installing MySQL

**macOS with Homebrew**:
```bash
brew install mysql
brew services start mysql
```

**Ubuntu/Debian Linux**:
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo mysql_secure_installation  # Follow prompts to secure your installation
```

**Windows**:
Download the installer from [mysql.com](https://dev.mysql.com/downloads/installer/) and run the setup wizard.

### Creating Your Database

Connect to MySQL as root:

```bash
mysql -u root -p
# Enter your root password
```

Create your database and user:

```sql
-- Create the database
CREATE DATABASE myapi;

-- Create a user (replace 'localhost' with '%' to allow remote connections)
CREATE USER 'myapi_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON myapi.* TO 'myapi_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

### Configuring Your Application

Update `secret/.env.development`:

```ini
DATABASE_URL=mysql+aiomysql://myapi_user:your_secure_password@localhost:3306/myapi
```

The connection string format:
- `mysql+aiomysql://` - Use MySQL with the aiomysql async driver
- `myapi_user:your_secure_password` - Your credentials
- `@localhost:3306` - MySQL server and default port
- `/myapi` - Database name

### Python Dependencies

Forge adds these to your `pyproject.toml`:

```toml
aiomysql = "^0.2.0"  # Async MySQL driver
cryptography = "^41.0.0"  # Required by aiomysql for secure connections
```

## SQLite Setup

SQLite is the simplest database option—it's just a file on your disk. There's no server to install, no users to create, no ports to configure. Python includes SQLite support by default, making it perfect for development, testing, and small applications.

### Why SQLite is Great for Development

When you're building a new feature or learning FastAPI, you don't want to spend time setting up PostgreSQL or MySQL. SQLite lets you start coding immediately. The entire database is a single file (usually `app.db`) that you can easily backup, delete, or share with teammates.

### Installation

There's nothing to install! SQLite comes with Python. However, you do need the async driver:

```bash
# This is automatically added to your pyproject.toml
pip install aiosqlite
```

### Configuration

Update `secret/.env.development`:

```ini
DATABASE_URL=sqlite+aiosqlite:///./app.db
```

This creates a file called `app.db` in your project root. The `./` means "current directory."

### When NOT to Use SQLite

SQLite has limitations that make it unsuitable for production applications:

**Concurrency**: SQLite locks the entire database file during writes. If you have multiple workers or high traffic, this becomes a bottleneck.

**No Network Access**: SQLite is a local file. You can't connect to it from multiple servers, which rules out horizontal scaling.

**Limited Concurrent Writes**: Only one process can write at a time. For read-heavy applications this is fine, but write-heavy applications will struggle.

**Best Practice**: Develop with SQLite, deploy with PostgreSQL. Your code works with both—just change the `DATABASE_URL`.

### Python Dependencies

```toml
aiosqlite = "^0.19.0"  # Async SQLite driver
```

## Database Migrations with Alembic

When you build an application, your database schema evolves. You add new tables, modify columns, create indexes. Database migrations are how you track and apply these changes in a controlled, reversible way.

Forge uses Alembic, the standard migration tool for SQLAlchemy-based applications. Think of migrations as "version control for your database schema."

### Why Migrations Matter

Imagine you deploy your application to production with a `users` table. A week later, you add a `phone_number` column. How do you update the production database without losing data?

**Without migrations**: You manually run SQL commands, hope you don't make typos, and pray you remember what you changed when you need to replicate it on another server.

**With migrations**: You generate a migration file that describes the change, test it locally, commit it to version control, and apply it to production with a single command. If something goes wrong, you can roll back.

### Initial Migration

After Forge generates your project, create the initial migration to set up your database tables:

```bash
# Generate a migration from your models
alembic revision --autogenerate -m "Initial migration"
```

This command:
1. Looks at your models in `app/models/`
2. Compares them to your current database (which is empty)
3. Generates a Python file in `alembic/versions/` with the SQL needed to create your tables

Now apply the migration:

```bash
alembic upgrade head
```

This runs the migration, creating all your tables. Check your database—you'll see `users`, `refresh_tokens` (if using Complete Auth), and an `alembic_version` table that tracks which migrations have been applied.

### Creating New Migrations

Let's say you want to add a `bio` field to your User model. First, modify the model:

```python
# app/models/user.py
class User(SQLModel, table=True):
    # ... existing fields ...
    bio: Optional[str] = Field(default=None, max_length=500)
```

Now generate a migration:

```bash
alembic revision --autogenerate -m "Add bio field to users"
```

Alembic detects the change and creates a new migration file. **Always review this file before applying it!** Auto-generation is smart but not perfect. Open `alembic/versions/xxx_add_bio_field_to_users.py` and verify the changes look correct.

Apply the migration:

```bash
alembic upgrade head
```

Your database now has the `bio` column, and all existing users have `NULL` for this field (which is fine because we made it optional).

### Common Migration Commands

```bash
# Show current database version
alembic current

# Show migration history
alembic history --verbose

# Upgrade to latest version
alembic upgrade head

# Upgrade one version at a time
alembic upgrade +1

# Downgrade one version (undo last migration)
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade to beginning (careful!)
alembic downgrade base
```

### Migration Best Practices

**1. Always review auto-generated migrations**: Alembic is smart but can miss complex changes like renaming columns (it sees a drop + add instead of a rename).

**2. Test migrations locally first**: Run `alembic upgrade head` on your development database before deploying to production.

**3. Make migrations reversible**: Ensure your `downgrade()` function properly undoes the `upgrade()` function.

**4. One logical change per migration**: Don't bundle unrelated changes. If you're adding a table and modifying another, consider separate migrations.

**5. Never edit applied migrations**: Once a migration is applied to production, don't modify it. Create a new migration to fix issues.

**6. Commit migrations to version control**: Migration files are code. They belong in Git alongside your models.

## ORM Configuration

### SQLModel (Recommended)

Generated code uses SQLModel for type-safe database operations:

```python
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
```

### SQLAlchemy

If you chose SQLAlchemy:

```python
from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

## Database Connection

### Connection Pool

Generated projects use async connection pooling:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max overflow connections
)

async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)
```

### Dependency Injection

Use FastAPI's dependency injection:

```python
from app.core.deps import get_db

@router.get("/users/")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

## Docker Database Setup

When using Docker (`use_docker: true`), databases are configured in `docker-compose.yml`:

### PostgreSQL Service

```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### MySQL Service

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Backup and Restore

### Celery Backup Task

If you enabled Celery, a database backup task is included:

```python
# Runs daily at 2 AM
@celery_app.task
def backup_database_task():
    """Backup database based on type"""
    # PostgreSQL: pg_dump
    # MySQL: mysqldump
    # SQLite: file copy
```

### Manual Backup

**PostgreSQL**:
```bash
pg_dump -U user dbname > backup.sql
```

**MySQL**:
```bash
mysqldump -u user -p dbname > backup.sql
```

**SQLite**:
```bash
cp app.db backup.db
```

### Restore

**PostgreSQL**:
```bash
psql -U user dbname < backup.sql
```

**MySQL**:
```bash
mysql -u user -p dbname < backup.sql
```

**SQLite**:
```bash
cp backup.db app.db
```

## Best Practices

### Development

1. Use SQLite for quick prototyping
2. Enable SQL query logging (`echo=True`)
3. Use migrations from the start
4. Test with production database type before deploying

### Production

1. Use PostgreSQL or MySQL
2. Disable SQL query logging (`echo=False`)
3. Use connection pooling
4. Set up regular backups
5. Monitor database performance
6. Use read replicas for scaling
7. Implement proper indexing

### Security

1. Never commit `.env` files
2. Use strong database passwords
3. Limit database user permissions
4. Use SSL/TLS for connections
5. Keep database software updated
6. Regular security audits

## Troubleshooting

### Connection Refused

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Ensure database server is running:
```bash
# PostgreSQL
brew services start postgresql@15

# MySQL
brew services start mysql
```

### Authentication Failed

```
sqlalchemy.exc.OperationalError: authentication failed
```

**Solution**: Check credentials in `.env.development`:
- Verify username and password
- Ensure user has proper permissions
- Check database exists

### Database Does Not Exist

```
sqlalchemy.exc.OperationalError: database "myapi" does not exist
```

**Solution**: Create the database:
```bash
# PostgreSQL
createdb myapi

# MySQL
mysql -u root -p -e "CREATE DATABASE myapi;"
```

### Migration Conflicts

```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution**: 
```bash
# Check current state
alembic current

# Upgrade to latest
alembic upgrade head

# Or start fresh (development only!)
alembic downgrade base
alembic upgrade head
```

## See Also

- [Configuration Options](configuration.md) - Database configuration
- [Authentication Guide](authentication.md) - User models and auth
- [Testing Guide](testing.md) - Database testing
- [Deployment Guide](deployment.md) - Production database setup
