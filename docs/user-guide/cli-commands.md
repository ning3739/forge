# CLI Commands

Forge provides a simple yet powerful command-line interface for generating FastAPI projects.

## Command Overview

| Command | Description |
|---------|-------------|
| `forge init` | Initialize a new FastAPI project (interactive) |
| `forge init <name>` | Initialize project with specific name |
| `forge init --no-interactive` | Initialize with default settings |
| `forge --version` | Show Forge version |
| `forge --help` | Show help message |

## forge init

Initialize a new FastAPI project with interactive prompts or default settings.

### Synopsis

```bash
forge init [NAME] [OPTIONS]
```

### Arguments

**NAME** (optional)
: Project name. If not provided, you'll be prompted to enter it interactively.

Special values:
- `.` - Use current directory as project root (directory name becomes project name)
- Any valid directory name - Creates new directory with that name

### Options

**--interactive / --no-interactive, -i / -I**
: Enable or disable interactive mode (default: enabled)

```bash
# Interactive mode (default)
forge init

# Non-interactive with defaults
forge init my-project --no-interactive
```

### Examples

#### Interactive Mode (Recommended)

```bash
forge init
```

This launches the interactive prompt where you can:
1. Choose project name
2. Select database type
3. Configure authentication
4. Enable/disable features

#### Specify Project Name

```bash
forge init my-api
```

Interactive prompts will start directly with database selection.

#### Use Current Directory

```bash
mkdir my-project
cd my-project
forge init .
```

Project will be created in the current directory.

#### Non-Interactive with Defaults

```bash
forge init production-api --no-interactive
```

Creates project with these defaults:
- Database: PostgreSQL
- ORM: SQLModel
- Migrations: Alembic (enabled)
- Auth: Complete JWT with refresh token
- CORS: Enabled
- Dev Tools: Black + Ruff
- Testing: Enabled
- Redis: Enabled
- Celery: Enabled
- Docker: Enabled

### Interactive Prompts

When running in interactive mode, you'll be asked:

#### 1. Project Name

```
🔨 What is your project name?
> my-api-project
```

Tips:
- Use lowercase with hyphens (kebab-case)
- Avoid spaces and special characters
- Enter `.` to use current directory

#### 2. Database Type

```
? Select database type: (Use arrow keys)
 ❯ PostgreSQL (Recommended)
   MySQL
   SQLite (Development/Small Projects)
```

Recommendations:
- **PostgreSQL** - Production applications, complex queries
- **MySQL** - Wide compatibility, familiar to many
- **SQLite** - Development, small projects, no server needed

#### 3. ORM Type

```
? Select ORM: (Use arrow keys)
 ❯ SQLModel (Recommended)
   SQLAlchemy
```

Recommendations:
- **SQLModel** - Modern, type-safe, integrates with FastAPI
- **SQLAlchemy** - Mature, powerful, extensive features

#### 4. Database Migrations

```
? Enable database migrations? (Y/n)
```

Enables Alembic for database migrations. Recommended: **Yes**

#### 5. Authentication Type

```
? Select authentication type: (Use arrow keys)
 ❯ Complete JWT Auth (Recommended)
   Basic JWT Auth (login/register only)
```

- **Complete JWT** - Login, register, email verification, password reset
- **Basic JWT** - Login and register only

For Complete JWT, you'll also choose:

```
? Enable Refresh Token? (Y/n)
```

#### 6. CORS Configuration

```
? Enable CORS? (Y/n)
```

Enable if building API for web frontends. Recommended: **Yes** for APIs

#### 7. Development Tools

```
? Include development tools? (Use arrow keys)
 ❯ Standard (Black + Ruff)
   None
```

- **Standard** - Black (formatter) + Ruff (linter)
- **None** - Skip dev tools

#### 8. Testing

```
? Include testing setup? (Y/n)
```

Includes pytest, httpx, coverage. Recommended: **Yes**

#### 9. Redis

```
? Enable Redis? (Y/n)
```

For caching, sessions, message queues. Recommended for production.

#### 10. Celery

```
? Enable Celery for background tasks? (Y/n)
```

Requires Redis. For async task processing, scheduled jobs.

#### 11. Docker

```
? Include Docker configuration? (Y/n)
```

Includes Dockerfile and docker-compose.yml. Recommended: **Yes**

### Configuration Summary

After answering all prompts, you'll see a summary:

```
╭──────────────────────── Project Configuration ────────────────────────╮
│                                                                        │
│  my-api-project                                                        │
│                                                                        │
│  📊 Database                                                           │
│    • Database: PostgreSQL                                             │
│    • ORM: SQLModel (Recommended)                                      │
│    • Migrations: Alembic ✓                                            │
│                                                                        │
│  🔐 Authentication & Security                                          │
│    • Auth: Complete JWT Auth ✓                                        │
│    • Refresh Token: Enabled ✓                                         │
│    • CORS: Enabled ✓                                                  │
│                                                                        │
│  🚀 Features                                                           │
│    • Redis: Enabled ✓                                                 │
│    • Celery: Enabled ✓                                                │
│                                                                        │
│  🛠️  Development                                                       │
│    • Dev Tools: Standard (Black + Ruff) ✓                             │
│    • Testing: Enabled (pytest) ✓                                      │
│                                                                        │
│  📦 Deployment                                                         │
│    • Docker: Enabled ✓                                                │
│                                                                        │
╰────────────────────────────────────────────────────────────────────────╯
```

Press Enter to continue with generation.

## forge --version

Display the current version of Forge.

### Synopsis

```bash
forge --version
forge -v
```

### Output

```
Forge CLI v0.1.8.4
```

### Example

```bash
$ forge --version
Forge CLI v0.1.8.4
```

## forge --help

Show help information about Forge commands.

### Synopsis

```bash
forge --help
```

### Output

```
Usage: forge [OPTIONS] COMMAND [ARGS]...

  Forge CLI Tool

  A powerful FastAPI project scaffolding generator

Options:
  -v, --version  Show version information
  --help         Show this message and exit

Commands:
  init  Initialize a new FastAPI project
```

## Global Options

These options work with any command:

**--help**
: Show help message for the command

```bash
forge init --help
```

## Exit Codes

Forge uses standard exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid argument |

## Configuration File

When you run `forge init`, it creates `.forge/config.json` in your project:

```json
{
  "project_name": "my-project",
  "database": {
    "type": "postgresql",
    "orm": "sqlmodel",
    "migration_tool": "alembic"
  },
  "features": {
    "auth": {
      "type": "complete",
      "refresh_token": true
    },
    "cors": true,
    "dev_tools": "standard",
    "testing": true,
    "redis": true,
    "celery": true,
    "docker": true
  },
  "metadata": {
    "created_at": "2024-01-17T10:00:00.000000",
    "forge_version": "0.1.8.4"
  }
}
```

This file:
- Documents all project decisions
- Can be version controlled
- Enables project regeneration
- Allows configuration sharing

## Environment Variables

Forge respects these environment variables:

**FORGE_CONFIG_PATH**
: Custom path for `.forge` directory (default: `.forge`)

```bash
export FORGE_CONFIG_PATH=".config/forge"
forge init my-project
```

## Command Tips

### Automation & CI/CD

Use non-interactive mode in scripts:

```bash
#!/bin/bash
forge init "$PROJECT_NAME" --no-interactive
cd "$PROJECT_NAME"
uv sync
```

### Reusing Configuration

Copy `.forge/config.json` to create similar projects:

```bash
# Create first project
forge init project-1

# Copy config
cp project-1/.forge/config.json /tmp/my-config.json

# Create second project with same config
forge init project-2
cp /tmp/my-config.json project-2/.forge/config.json
```

### Checking Project Configuration

View current project's configuration:

```bash
cat .forge/config.json | jq
```

## Common Workflows

### Quick API Project

```bash
forge init quick-api
# Select SQLite, Basic Auth, minimal features
```

### Production API

```bash
forge init production-api --no-interactive
# Uses all recommended production settings
```

### Microservice

```bash
forge init user-service
# PostgreSQL, Complete Auth, Redis, Celery, Docker
```

### Development Project

```bash
forge init dev-project
# SQLite, Basic Auth, no Redis/Celery
```

## Troubleshooting

### Command Not Found

If `forge` command is not found:

```bash
# Check if installed
pip list | grep ningfastforge

# Reinstall
pip install --upgrade ningfastforge

# Use full path
python -m forge init
```

### Permission Denied

If you get permission errors:

```bash
# Check write permissions
ls -la

# Use user installation
pip install --user ningfastforge
```

### Interactive Prompt Issues

If prompts don't work correctly:

```bash
# Use non-interactive mode
forge init my-project --no-interactive

# Or set environment
export TERM=xterm-256color
forge init
```

## See Also

- [Configuration Options](configuration.md) - All configuration details
- [Quick Start](../getting-started/quickstart.md) - Getting started guide
- [First Project](../getting-started/first-project.md) - Detailed walkthrough
