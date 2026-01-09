"""Unit tests for commands/init.py"""
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from commands.init import (
    extract_choice,
    get_auth_config,
    collect_project_name,
    build_project_config,
    save_config_file,
    build_config_summary_lines,
)


class TestExtractChoice:
    """Tests for extract_choice function"""
    
    def test_extract_choice_with_description(self):
        """Should extract value before parentheses"""
        assert extract_choice("PostgreSQL (Recommended)") == "PostgreSQL"
        assert extract_choice("SQLite (Development/Small Projects)") == "SQLite"
    
    def test_extract_choice_without_description(self):
        """Should return original value if no parentheses"""
        assert extract_choice("MySQL") == "MySQL"
        assert extract_choice("SQLAlchemy") == "SQLAlchemy"
    
    def test_extract_choice_empty_string(self):
        """Should return default for empty string"""
        assert extract_choice("", "default") == "default"
        assert extract_choice("") == ""
    
    def test_extract_choice_none(self):
        """Should return default for None"""
        assert extract_choice(None, "default") == "default"


class TestGetAuthConfig:
    """Tests for get_auth_config function"""
    
    def test_complete_auth(self):
        """Should return complete auth config"""
        config = get_auth_config("Complete JWT Auth (Recommended)")
        assert config["type"] == "complete"
        assert config["refresh_token"] is True
        assert "Email Verification" in config["features"]
        assert "Password Reset" in config["features"]
        assert "Email Service" in config["features"]
    
    def test_basic_auth(self):
        """Should return basic auth config"""
        config = get_auth_config("Basic JWT Auth (login/register only)")
        assert config["type"] == "basic"
        assert config["refresh_token"] is False
        assert config["features"] == []
    
    def test_auth_with_complete_keyword(self):
        """Should detect Complete keyword anywhere in string"""
        config = get_auth_config("Something Complete Something")
        assert config["type"] == "complete"


class TestCollectProjectName:
    """Tests for collect_project_name function"""
    
    def test_with_dot_input(self):
        """Should use current directory name when '.' is provided"""
        mock_style = MagicMock()
        with patch('commands.init.Path') as mock_path:
            mock_path.cwd.return_value.name = "my-current-dir"
            name, use_current_dir = collect_project_name(".", mock_style)
            assert name == "my-current-dir"
            assert use_current_dir is True
    
    def test_with_explicit_name(self):
        """Should use provided name directly"""
        mock_style = MagicMock()
        name, use_current_dir = collect_project_name("my-project", mock_style)
        assert name == "my-project"
        assert use_current_dir is False
    
    def test_with_none_prompts_user(self):
        """Should prompt user when name is None"""
        mock_style = MagicMock()
        with patch('commands.init.questionary') as mock_questionary:
            mock_questionary.text.return_value.ask.return_value = "user-input-project"
            name, use_current_dir = collect_project_name(None, mock_style)
            assert name == "user-input-project"
            assert use_current_dir is False
    
    def test_with_none_and_dot_input(self):
        """Should handle '.' input from prompt"""
        mock_style = MagicMock()
        with patch('commands.init.questionary') as mock_questionary:
            mock_questionary.text.return_value.ask.return_value = "."
            with patch('commands.init.Path') as mock_path:
                mock_path.cwd.return_value.name = "current-dir"
                name, use_current_dir = collect_project_name(None, mock_style)
                assert name == "current-dir"
                assert use_current_dir is True
    
    def test_with_none_and_empty_input(self):
        """Should use default when user provides empty input"""
        mock_style = MagicMock()
        with patch('commands.init.questionary') as mock_questionary:
            mock_questionary.text.return_value.ask.return_value = None
            name, use_current_dir = collect_project_name(None, mock_style)
            assert name == "forge-project"
            assert use_current_dir is False


class TestBuildProjectConfig:
    """Tests for build_project_config function"""
    
    def test_build_config_with_all_options(self):
        """Should build complete config dictionary"""
        features = {
            "auth": {"type": "complete", "refresh_token": True},
            "cors": True,
            "redis": True,
            "celery": True
        }
        config = build_project_config(
            name="test-project",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool="Alembic",
            features=features
        )
        
        assert config["project_name"] == "test-project"
        assert config["database"]["type"] == "PostgreSQL"
        assert config["database"]["orm"] == "SQLModel"
        assert config["database"]["migration_tool"] == "Alembic"
        assert config["features"]["redis"] is True
        assert config["features"]["celery"] is True
    
    def test_build_config_without_migration(self):
        """Should handle None migration tool"""
        config = build_project_config(
            name="test",
            database="SQLite",
            orm="SQLAlchemy",
            migration_tool=None,
            features={}
        )
        assert config["database"]["migration_tool"] is None


class TestSaveConfigFile:
    """Tests for save_config_file function"""
    
    def test_save_config_creates_forge_directory(self):
        """Should create .forge directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config = {
                "project_name": "test",
                "database": {"type": "PostgreSQL"},
                "features": {}
            }
            save_config_file(project_path, config)
            
            forge_dir = project_path / ".forge"
            assert forge_dir.exists()
            assert forge_dir.is_dir()
    
    def test_save_config_creates_config_json(self):
        """Should create config.json file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config = {
                "project_name": "test",
                "database": {"type": "PostgreSQL"},
                "features": {"cors": True}
            }
            save_config_file(project_path, config)
            
            config_file = project_path / ".forge" / "config.json"
            assert config_file.exists()
            
            with open(config_file) as f:
                saved_config = json.load(f)
            
            assert saved_config["project_name"] == "test"
            assert saved_config["features"]["cors"] is True
            assert "metadata" in saved_config
            assert "created_at" in saved_config["metadata"]
            assert "forge_version" in saved_config["metadata"]


class TestBuildConfigSummaryLines:
    """Tests for build_config_summary_lines function"""
    
    def test_summary_includes_project_name(self):
        """Should include project name in summary"""
        lines = build_config_summary_lines(
            name="my-project",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool="Alembic",
            features={"auth": {"type": "basic"}, "cors": True}
        )
        assert any("my-project" in line for line in lines)
    
    def test_summary_includes_database_info(self):
        """Should include database and ORM info"""
        lines = build_config_summary_lines(
            name="test",
            database="MySQL",
            orm="SQLAlchemy",
            migration_tool=None,
            features={"auth": {"type": "basic"}}
        )
        assert any("MySQL" in line and "SQLAlchemy" in line for line in lines)
    
    def test_summary_includes_migration_when_enabled(self):
        """Should include migration tool when enabled"""
        lines = build_config_summary_lines(
            name="test",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool="Alembic",
            features={"auth": {"type": "basic"}}
        )
        assert any("Alembic" in line for line in lines)
    
    def test_summary_excludes_migration_when_disabled(self):
        """Should not include migration line when disabled"""
        lines = build_config_summary_lines(
            name="test",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool=None,
            features={"auth": {"type": "basic"}}
        )
        # Should not have a dedicated migration line
        migration_lines = [l for l in lines if "Migration" in l]
        assert len(migration_lines) == 0
    
    def test_summary_includes_redis_celery(self):
        """Should include Redis and Celery when enabled"""
        lines = build_config_summary_lines(
            name="test",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool=None,
            features={
                "auth": {"type": "basic"},
                "redis": True,
                "celery": True
            }
        )
        assert any("Redis" in line for line in lines)
        assert any("Celery" in line for line in lines)
    
    def test_summary_includes_complete_auth_features(self):
        """Should include auth features for complete auth"""
        lines = build_config_summary_lines(
            name="test",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool=None,
            features={
                "auth": {
                    "type": "complete",
                    "refresh_token": True,
                    "features": ["Email Verification", "Password Reset"]
                }
            }
        )
        assert any("Complete JWT Auth" in line for line in lines)
        assert any("Email Verification" in line for line in lines)
