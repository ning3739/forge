# Development Setup

This guide explains how to set up a development environment for contributing to Forge.

## Prerequisites

- Python 3.9 or higher
- Git
- [uv](https://docs.astral.sh/uv/) package manager

## Clone the Repository

```bash
git clone https://github.com/ning3739/forge.git
cd forge
```

## Install Dependencies

```bash
uv sync
```

## Project Structure

```
forge/
├── main.py                 # CLI entry point
├── commands/
│   └── init.py             # Interactive configuration collection
├── core/
│   ├── config_reader.py    # Configuration reading
│   ├── project_generator.py # Main generation coordinator
│   ├── decorators/
│   │   └── generator.py    # @Generator decorator
│   ├── generators/
│   │   ├── orchestrator.py # Generator discovery and execution
│   │   ├── structure.py    # Directory structure creation
│   │   ├── configs/        # Config file generators
│   │   ├── deployment/     # Docker generators
│   │   └── templates/      # Application code generators
│   └── utils/
│       ├── file_operations.py  # File writing utilities
│       └── version_checker.py  # Update checking
├── ui/
│   ├── colors.py           # Terminal colors
│   ├── components.py       # UI components
│   └── logo.py             # ASCII logo
├── tests/                  # Test files
└── docs/                   # Documentation
```

## Running Locally

Run the CLI during development:

```bash
uv run main.py init
```

Or with Python directly:

```bash
python main.py init
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_decorators.py

# Run with coverage
uv run pytest --cov=core
```

## Code Quality

### Formatting

Format code with Black:

```bash
uv run black .
```

### Linting

Check code with Ruff:

```bash
uv run ruff check .
```

### Type Checking

Run mypy:

```bash
uv run mypy core/
```

## Building

### Test Build

Run the test build script:

```bash
./scripts/test_build.sh
```

### Build Package

```bash
uv run -m build
```

The built package will be in `dist/`.

## Version Management

Update the version number:

```bash
uv run scripts/update_version.py
```

This updates version in:
- `core/__version__.py`
- `pyproject.toml`

## Development Workflow

1. **Create a branch** for your feature or fix
2. **Make changes** following the code conventions
3. **Write tests** for new functionality
4. **Run tests** to ensure nothing is broken
5. **Format and lint** your code
6. **Submit a pull request**

## Key Files to Understand

| File | Purpose |
|------|---------|
| `core/decorators/generator.py` | Defines `@Generator` decorator and global registry |
| `core/generators/orchestrator.py` | Discovers, filters, sorts, and executes generators |
| `core/config_reader.py` | Reads and validates project configuration |
| `core/project_generator.py` | Coordinates the generation process |
| `commands/init.py` | Handles interactive configuration collection |

## Debugging Tips

### View Generator Registry

```python
from core.decorators import GENERATOR_REGISTRY
print(GENERATOR_REGISTRY)
```

### Test a Single Generator

```python
from pathlib import Path
from core.config_reader import ConfigReader
from core.generators.templates.app.main import MainGenerator

config_reader = ConfigReader(Path("./test-project"))
generator = MainGenerator(Path("./test-project"), config_reader)
generator.generate()
```

### Inspect Generated Files

After running `forge init`, examine the generated files in the project directory to verify output.
