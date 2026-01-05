# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-01-05

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
