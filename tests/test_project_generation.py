"""Integration tests for project generation"""
import json
import pytest
import tempfile
import shutil
from pathlib import Path

from commands.init import (
    save_config_file,
    generate_project,
    build_project_config,
    DEFAULT_NON_INTERACTIVE_CONFIG,
)
from core.project_generator import ProjectGenerator
from core.config_reader import ConfigReader


class TestProjectGeneration:
    """Integration tests for full project generation"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary directory for project generation"""
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
        shutil.rmtree(tmpdir, ignore_errors=True)
    
    def test_generate_minimal_project(self, temp_project_dir):
        """Should generate a minimal project structure"""
        config = build_project_config(
            name="test-project",
            database="SQLite",
            orm="SQLModel",
            migration_tool=None,
            features={
                "auth": {"type": "basic", "refresh_token": False, "features": []},
                "cors": False,
                "dev_tools": False,
                "testing": False,
                "docker": False
            }
        )
        
        generate_project(temp_project_dir, config)
        
        # Check basic structure
        assert (temp_project_dir / ".forge" / "config.json").exists()
        assert (temp_project_dir / "app").exists()
        assert (temp_project_dir / "app" / "main.py").exists()
        assert (temp_project_dir / "app" / "core").exists()
    
    def test_generate_full_project(self, temp_project_dir):
        """Should generate a full project with all features"""
        config = build_project_config(
            name="full-project",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool="Alembic",
            features=DEFAULT_NON_INTERACTIVE_CONFIG["features"]
        )
        
        generate_project(temp_project_dir, config)
        
        # Check all directories exist
        assert (temp_project_dir / "app").exists()
        assert (temp_project_dir / "app" / "core").exists()
        assert (temp_project_dir / "app" / "models").exists()
        assert (temp_project_dir / "app" / "schemas").exists()
        assert (temp_project_dir / "app" / "routers").exists()
        assert (temp_project_dir / "app" / "services").exists()
        
        # Check config files
        assert (temp_project_dir / "pyproject.toml").exists()
        assert (temp_project_dir / ".gitignore").exists()
        
        # Check Docker files (docker enabled)
        assert (temp_project_dir / "Dockerfile").exists()
        assert (temp_project_dir / "docker-compose.yml").exists()
        
        # Check Alembic (migration enabled)
        assert (temp_project_dir / "alembic").exists()
        assert (temp_project_dir / "alembic.ini").exists()
        
        # Check tests directory (testing enabled)
        assert (temp_project_dir / "tests").exists()
    
    def test_generate_project_with_mysql(self, temp_project_dir):
        """Should generate project with MySQL configuration"""
        config = build_project_config(
            name="mysql-project",
            database="MySQL",
            orm="SQLModel",
            migration_tool="Alembic",
            features={
                "auth": {"type": "basic", "refresh_token": False, "features": []},
                "cors": True,
                "dev_tools": False,
                "testing": False,
                "docker": True
            }
        )
        
        generate_project(temp_project_dir, config)
        
        # Check database connection file exists
        db_dir = temp_project_dir / "app" / "core" / "database"
        assert db_dir.exists()
    
    def test_generate_project_with_sqlite(self, temp_project_dir):
        """Should generate project with SQLite configuration"""
        config = build_project_config(
            name="sqlite-project",
            database="SQLite",
            orm="SQLAlchemy",
            migration_tool=None,
            features={
                "auth": {"type": "basic", "refresh_token": False, "features": []},
                "cors": True,
                "dev_tools": False,
                "testing": False,
                "docker": False
            }
        )
        
        generate_project(temp_project_dir, config)
        
        # SQLite project should not have Docker files
        assert not (temp_project_dir / "Dockerfile").exists()
        assert not (temp_project_dir / "docker-compose.yml").exists()
    
    def test_config_file_content(self, temp_project_dir):
        """Should save correct config content"""
        config = build_project_config(
            name="config-test",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool="Alembic",
            features={
                "auth": {"type": "complete", "refresh_token": True, "features": ["Email Verification"]},
                "cors": True,
                "redis": True,
                "celery": True
            }
        )
        
        save_config_file(temp_project_dir, config)
        
        config_file = temp_project_dir / ".forge" / "config.json"
        with open(config_file) as f:
            saved = json.load(f)
        
        assert saved["project_name"] == "config-test"
        assert saved["database"]["type"] == "PostgreSQL"
        assert saved["database"]["orm"] == "SQLModel"
        assert saved["features"]["redis"] is True
        assert saved["features"]["celery"] is True
        assert saved["features"]["auth"]["type"] == "complete"


class TestConfigReader:
    """Tests for ConfigReader"""
    
    @pytest.fixture
    def temp_project_with_config(self):
        """Create a temp project with config file"""
        tmpdir = tempfile.mkdtemp()
        project_path = Path(tmpdir)
        
        # Create config
        config = {
            "project_name": "test",
            "database": {
                "type": "PostgreSQL",
                "orm": "SQLModel",
                "migration_tool": "Alembic"
            },
            "features": {
                "auth": {"type": "complete", "refresh_token": True},
                "cors": True,
                "redis": True,
                "celery": True,
                "testing": True,
                "docker": True
            },
            "metadata": {
                "created_at": "2025-01-01T00:00:00",
                "forge_version": "0.1.0"
            }
        }
        
        forge_dir = project_path / ".forge"
        forge_dir.mkdir(parents=True)
        with open(forge_dir / "config.json", "w") as f:
            json.dump(config, f)
        
        yield project_path
        shutil.rmtree(tmpdir, ignore_errors=True)
    
    def test_load_config(self, temp_project_with_config):
        """Should load config correctly"""
        reader = ConfigReader(temp_project_with_config)
        reader.load_config()
        
        assert reader.get_project_name() == "test"
        assert reader.get_database_type() == "PostgreSQL"
        assert reader.get_orm_type() == "SQLModel"
    
    def test_has_auth(self, temp_project_with_config):
        """Should detect auth configuration"""
        reader = ConfigReader(temp_project_with_config)
        reader.load_config()
        
        assert reader.has_auth() is True
        assert reader.get_auth_type() == "complete"
    
    def test_has_features(self, temp_project_with_config):
        """Should detect feature flags"""
        reader = ConfigReader(temp_project_with_config)
        reader.load_config()
        
        assert reader.has_redis() is True
        assert reader.has_celery() is True
        assert reader.has_docker() is True
        assert reader.has_testing() is True
