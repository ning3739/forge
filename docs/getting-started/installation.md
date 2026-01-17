# Installation

## Requirements

Before installing Forge, ensure you have:

- **Python 3.9+** - Forge requires Python 3.9 or higher
- **pip** or **uv** - Package manager for installing Python packages

## Installation Methods

### From PyPI (Recommended)

The easiest way to install Forge is from PyPI using pip:

```bash
pip install ningfastforge
```

**Tip**: For faster installation, you can use [uv](https://docs.astral.sh/uv/):
```bash
uv pip install ningfastforge
```

### Upgrade to Latest Version

Keep Forge up to date to get the latest features and bug fixes:

```bash
pip install --upgrade ningfastforge
```

### From Source

If you want to contribute or use the development version:

```bash
# Clone the repository
git clone https://github.com/ning3739/forge.git
cd forge

# Install with uv
uv sync

# Or with pip
pip install -e .
```

## Verify Installation

After installation, verify that Forge is installed correctly:

```bash
forge --version
```

You should see output like:

```
Forge CLI v0.1.8.3
```

## System Dependencies

Depending on what features you enable in your generated project, you may need additional system dependencies:

### Database Drivers

**PostgreSQL**:
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Python driver (automatically installed)
pip install psycopg2-binary
```

**MySQL**:
```bash
# macOS
brew install mysql

# Ubuntu/Debian
sudo apt-get install mysql-server

# Python driver (automatically installed)
pip install pymysql
```

**SQLite**:
SQLite is included with Python, no additional installation needed.

### Redis

If you enable Redis features:

```bash
# macOS
brew install redis

# Ubuntu/Debian
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Docker

For Docker deployment:

```bash
# macOS
brew install --cask docker

# Ubuntu/Debian
sudo apt-get install docker.io docker-compose
```

## Next Steps

Now that you have Forge installed, proceed to:

- [Quick Start](quickstart.md) - Learn the basics
- [First Project](first-project.md) - Create your first project

## Troubleshooting

### Command Not Found

If you get `command not found: forge` after installation:

1. Check your Python scripts directory is in PATH:
   ```bash
   echo $PATH
   ```

2. Find where pip installs scripts:
   ```bash
   python -m site --user-base
   ```

3. Add the scripts directory to your PATH in `~/.bashrc` or `~/.zshrc`:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

### Python Version Issues

If you have multiple Python versions:

```bash
# Use specific Python version
python3.11 -m pip install ningfastforge

# Create alias if needed
alias forge='python3.11 -m forge'
```

### Permission Errors

If you encounter permission errors:

```bash
# Install for user only
pip install --user ningfastforge

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ningfastforge
```
