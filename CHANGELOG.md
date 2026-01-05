# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2025-01-06

### Added
- Python 3.13 support in CI and package metadata
- Link to CHANGELOG in README
- PyPI publishing automation via GitHub Actions

### Changed
- Updated documentation for PyPI publishing
- Improved README structure and clarity
- Removed `.github/README.md` to fix GitHub display

### Fixed
- Removed incorrect test command from development setup
- Fixed package URLs in workflow files
- Updated all documentation to use correct package name `ningfastforge`

## [0.1.0] - 2025-01-05

### Added
- Initial release of Forge CLI
- Interactive project initialization with `forge init`
- Support for PostgreSQL and MySQL databases
- Support for SQLModel and SQLAlchemy ORMs
- JWT authentication (Basic and Complete modes)
- Alembic database migrations
- Docker and Docker Compose configuration generation
- **Testing setup with pytest** - Includes test fixtures and sample tests
  - `conftest.py` with database fixtures
  - `test_main.py` for API endpoint tests
  - `test_auth.py` for authentication tests
  - `test_users.py` for user endpoint tests
- Development tools (Black + Ruff)
- Beautiful terminal UI with cyberpunk color scheme
- Configuration-first architecture with `.forge/config.json`

### Changed
- **[BREAKING]** All code comments and docstrings converted to English
- Refactored project structure for better maintainability
- Simplified code logic and removed redundant functions
- Improved error handling and validation
- Updated README with comprehensive documentation

### Removed
- Duplicate files (`init_refactored.py`, `config_reader_refactored.py`)
- Unnecessary documentation files
- Chinese comments and docstrings
- Unused dataclass definitions
- Redundant helper methods
- `info` command (not needed)
- `docker` command (Docker config is generated via `forge init` options)
- `helpers.py` (PyPI stats helper, only used by removed info command)

### Fixed
- Import organization and consistency
- Code style and formatting
- Type annotations
- Module exports

### Technical Details
- Reduced codebase by ~10% while maintaining all functionality
- All Python files compile successfully
- All CLI commands working correctly
- Zero breaking changes to generated projects
