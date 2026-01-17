# Changelog

All notable changes to this project will be documented in this file.

## [0.1.8.4] - 2026-01-18

### Added

- **Read the Docs Documentation**: Added comprehensive documentation infrastructure
  - Created MkDocs configuration with Material theme
  - Added .readthedocs.yaml for automatic documentation building
  - Created 9 core documentation pages:
    - Home page with project overview
    - Installation guide with troubleshooting
    - Quick start tutorial with step-by-step examples
    - First project walkthrough with detailed setup
    - Architecture overview with Mermaid diagrams
    - Generator system deep dive with examples
    - Complete CLI commands reference
    - ConfigReader API documentation
    - Changelog (version history)
  - Documentation features:
    - Light/dark theme toggle
    - Full-text search
    - Code syntax highlighting with copy buttons
    - Architecture diagrams using Mermaid
    - Responsive design for all devices
  - Documentation ready for deployment at https://forge.readthedocs.io

## [0.1.8.3] - 2026-01-16

### Fixed

- **Token Schema Generation**: Fixed incomplete token schema generation in base authentication mode
  - Token schema now properly generated when using basic authentication option
  - Ensures all required authentication schemas are created regardless of auth mode

## [0.1.8.2] - 2026-01-10

### Fixed

- **Docker**: Fixed missing `static` directory in Dockerfile causing "Email template not found" error in production
  - Dockerfile now copies `static/email_template` directory when complete authentication is enabled
  - Resolves 404 error when sending verification emails in Docker containers

## [0.1.8.1] - 2026-01-10

### Improved

- **Version Update Prompt**: Simplified and optimized version update user experience
  - Removed redundant "Skip for now" option
  - Streamlined to two clear choices: "Yes, update automatically" or "No, continue with current version"
  - Update command now displayed upfront before prompting user
  - Choosing "No" continues execution without exiting the program
  - Improved user flow and reduced decision fatigue

## [0.1.8] - 2026-01-10

### Added

- **Current Directory Support**: Use `.` as project name to generate project in current directory (`forge init .`)
- **Comprehensive Test Suite**: Added complete test infrastructure for both Forge CLI and generated projects
  - **Forge CLI Tests**: 62 tests covering core functionality (81% code coverage)
  - **Generated Project Tests**: 12 tests for authentication, user management, and API endpoints
  - All tests pass out-of-the-box without manual configuration

### Fixed

- **Test Fixtures**: Fixed user authentication fixtures in generated projects
  - Split into `test_user_verified` (for login tests) and `test_user_unverified` (for email verification tests)
  - Fixed `auth_headers` to use `security_manager.create_access_token()` with correct payload
  - Added backward compatibility alias `test_user = test_user_verified`

- **Test Configuration**: Fixed multiple test setup issues
  - Changed to file-based SQLite (`sqlite+aiosqlite:///./test.db`) for reliable async testing
  - Fixed metadata import to use `SQLModel.metadata` instead of `Base.metadata`
  - Fixed `AsyncClient` initialization to use `ASGITransport` (httpx 0.24+ compatibility)
  - Added proper database dependency override and test isolation

- **Test Methods & Endpoints**: Corrected HTTP methods and paths
  - Changed `test_update_current_user` from PATCH to PUT
  - Fixed endpoint paths: `/forgot-password`, `/resend-verification`
  - Updated login tests to use JSON payload instead of form data

- **Template Syntax**: Fixed f-string escaping issues in test generators

### Improved

- **Test Documentation**: Enhanced README with clear installation and usage instructions
  - Added `uv sync --extra dev` command for installing test dependencies
  - Included examples for coverage and specific test file execution
  
- **Project Overwrite Logic**: Enhanced handling of existing projects when using current directory
- **Next Steps Display**: Improved instructions when generating in current directory

## [0.1.7.1] - 2026-01-09

### Improved

- **Documentation**: Optimized README.md structure and accuracy

## [0.1.7] - 2026-01-08

### Fixed

- **Docker Configuration**: Fixed Docker Compose generator to use correct async database drivers (`mysql+aiomysql://`, `postgresql+asyncpg://`)
- **Environment Configuration**: Fixed production environment files to use Docker service names (`db:3306`, `redis:6379`) instead of localhost
- **Docker Compose**: Removed obsolete `version` field from docker-compose.yml generation
- **README Documentation**: Fixed Docker deployment instructions to use `docker-compose up --build` for multi-service projects
- **Configuration Summary**: Added Redis and Celery information to init command's Configuration Summary display

### Improved

- **Production Deployment**: Enhanced Docker Compose setup with proper service dependencies and health checks
- **Environment Separation**: Clear distinction between development (localhost) and production (Docker service names) configurations
- **Documentation**: Comprehensive Docker deployment guide with service descriptions and environment configuration instructions

## [0.1.6] - 2026-01-08

### Improved

- **Documentation Consistency**: Unified README.md generator with Forge project documentation
- **Feature Documentation**: Enhanced feature descriptions with proper emoji and formatting
- **Technology Coverage**: Updated documentation to include Redis, Celery, and SQLite support
- **Project Structure**: Added comprehensive project structure documentation including Redis/Celery files
- **Installation Guide**: Improved installation and quick start sections with better formatting

### Fixed

- **Character Encoding**: Fixed emoji display issues in generated README files
- **Feature Descriptions**: Corrected feature list formatting and descriptions
- **Documentation Links**: Updated all documentation links to use proper Forge repository references

### Technical Details

- README generator now produces documentation consistent with Forge project README
- Added comprehensive feature coverage including background tasks, caching, and database backup
- Improved documentation structure with better organization and visual hierarchy
- Fixed character encoding issues that caused malformed emoji in generated files

## [0.1.5] - 2026-01-08

### Fixed

- **Celery Beat Schedule Issue**: Fixed critical issue where Celery Beat was creating malformed database filenames due to environment variable conflicts
- **Task Configuration**: Removed `CELERY_BEAT_SCHEDULE` from environment variables to prevent conflicts with code-based configuration
- **Database Backup Task**: Fixed task reference path from `'backup_database_task'` to `'app.tasks.backup_database_task.backup_database_task'`
- **Environment Configuration**: Updated environment file generators to use comments instead of actual `CELERY_BEAT_SCHEDULE` variables

### Improved

- **Celery Beat Reliability**: Celery Beat now creates proper `celerybeat-schedule.db` files instead of malformed JSON-based filenames
- **Task Scheduling**: All periodic tasks are now configured exclusively in code (`app/core/celery.py`) for better maintainability
- **Error Prevention**: Eliminated the creation of files with names like `{"cleanup_tokens": {"task": "...", "schedule": ...}}.db`

### Technical Details

- Celery Beat schedule configuration moved entirely to code-based approach
- Environment files now contain only comments about where task scheduling is configured
- Fixed generator templates to prevent future environment variable conflicts
- Improved task discovery and execution reliability

## [0.1.4] - 2025-01-08

### Added

- **SQLite Database Support**: Added full SQLite support alongside existing MySQL and PostgreSQL support
- **Enhanced Database Backup**: Multi-database backup task now supports MySQL (mysqldump), PostgreSQL (pg_dump), and SQLite (sqlite3)
- **Improved Redis Integration**: Better Redis connection management with async/sync client support
- **Enhanced Celery Integration**: Comprehensive background task system with database backup scheduling

### Fixed

- **Schema File Naming**: Fixed schema file naming from `user_schema.py`/`token_schema.py` to `user.py`/`token.py`
- **Chinese Comments**: Replaced all Chinese comments in generated core files with English comments for better internationalization
- **Generator Architecture**: Moved application code generators from config generators to dedicated template generators
  - `app/core/celery.py` now generated by `CeleryAppGenerator` 
  - `app/core/redis.py` now generated by `RedisAppGenerator`
  - `app/tasks/backup_database_task.py` now generated by `BackupDatabaseTaskGenerator`

### Improved

- **Celery Commands**: Updated Celery startup instructions to recommend separate worker and beat processes for better stability
- **Database Support**: Full support for MySQL, PostgreSQL, and SQLite with appropriate tooling and configurations
- **Code Organization**: Better separation between configuration generators and application template generators

### Technical Details

- Removed `hello_task` and replaced with comprehensive `backup_database_task` supporting all database types
- Updated all import references to use new schema file names
- Improved generator dependency management and priority ordering
- All generated code now uses English comments consistently
- Enhanced Redis and Celery integration with proper async/sync handling

## [0.1.3] - 2025-01-07

### Changed

- Internal refactoring: Improved code generator architecture with decorator-based system
- Better code organization and maintainability

### Technical Details

- No user-facing changes - all improvements are internal
- Generated projects remain identical to 0.1.2
- Fully backward compatible

## [0.1.2] - 2025-01-06

### Changed

- Updated documentation URLs to use http://127.0.0.1:8000
- Updated author email address

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
