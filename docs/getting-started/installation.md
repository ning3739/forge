# Installation

## Requirements

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Install from PyPI

The recommended way to install Forge:

```bash
pip install ningfastforge
```

## Verify Installation

After installation, verify that Forge is available:

```bash
forge --version
```

You should see output like:

```
Forge CLI v0.1.8
```

## Install from Source

For development or to get the latest changes:

```bash
git clone https://github.com/ning3739/forge.git
cd forge
uv build
pip install dist/ningfastforge-*.whl
```

## Optional Dependencies

Depending on the features you enable when generating a project, you may need additional tools installed on your system:

**For PostgreSQL projects:**
- PostgreSQL client libraries (`libpq-dev` on Ubuntu, `postgresql` on macOS)

**For MySQL projects:**
- MySQL client libraries (`default-libmysqlclient-dev` on Ubuntu, `mysql` on macOS)

**For Docker deployment:**
- Docker and Docker Compose

These are only needed on your development machine if you plan to run the generated project locally. The generated Docker configurations include all necessary dependencies.

## Next Steps

Once installed, proceed to the [Quickstart](quickstart.md) guide to create your first project.
