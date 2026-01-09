"""Edge case tests for Forge CLI"""
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from commands.init import (
    extract_choice,
    handle_existing_project,
    build_project_config,
    save_config_file,
    generate_project,
)
from core.config_reader import ConfigReader, ConfigValidationError
from core.utils import ProjectConfig


class TestEdgeCases:
    """Edge case tests"""
    
    def test_extract_choice_multiple_parentheses(self):
        """Should handle multiple parentheses correctly"""
        result = extract_choice("Option (with) (multiple) (parens)")
        assert result == "Option"
    
    def test_extract_choice_nested_parentheses(self):
        """Should handle nested parentheses"""
        result = extract_choice("Option (with (nested) parens)")
        assert result == "Option"
    
    def test_project_name_with_special_chars(self):
        """Should handle project names with special characters"""
        config = build_project_config(
            name="my-project_v2.0",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool=None,
            features={"auth": {"type": "basic"}}
        )
        assert config["project_name"] == "my-project_v2.0"
    
    def test_project_name_with_spaces(self):
        """Should handle project names with spaces (though not recommended)"""
        config = build_project_config(
            name="my project",
            database="PostgreSQL",
            orm="SQLModel",
            migration_tool=None,
            features={"auth": {"type": "basic"}}
        )
        assert config["project_name"] == "my project"


class TestConfigReaderEdgeCases:
    """Edge cases for ConfigReader"""
    
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
        shutil.rmtree(tmpdir, ignore_errors=True)
    
    def test_missing_config_file(self, temp_dir):
        """Should raise error when config file is missing"""
        reader = ConfigReader(temp_dir)
        with pytest.raises(FileNotFoundError):
            reader.load_config()
    
    def test_invalid_json_config(self, temp_dir):
        """Should raise error for invalid JSON"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        with open(forge_dir / "config.json", "w") as f:
            f.write("{ invalid json }")
        
        reader = ConfigReader(temp_dir)
        with pytest.raises(ConfigValidationError):
            reader.load_config()
    
    def test_missing_required_fields(self, temp_dir):
        """Should raise error for missing required fields"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        with open(forge_dir / "config.json", "w") as f:
            json.dump({"project_name": "test"}, f)  # Missing database and features
        
        reader = ConfigReader(temp_dir)
        reader.load_config()
        with pytest.raises(ConfigValidationError) as exc_info:
            reader.validate_config()
        assert "Missing required fields" in str(exc_info.value)
    
    def test_invalid_database_type(self, temp_dir):
        """Should raise error for invalid database type"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        config = {
            "project_name": "test",
            "database": {"type": "MongoDB", "orm": "SQLModel"},  # Invalid type
            "features": {"auth": {"type": "basic"}}
        }
        with open(forge_dir / "config.json", "w") as f:
            json.dump(config, f)
        
        reader = ConfigReader(temp_dir)
        reader.load_config()
        with pytest.raises(ConfigValidationError) as exc_info:
            reader.validate_config()
        assert "Invalid database type" in str(exc_info.value)
    
    def test_invalid_orm_type(self, temp_dir):
        """Should raise error for invalid ORM type"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        config = {
            "project_name": "test",
            "database": {"type": "PostgreSQL", "orm": "Prisma"},  # Invalid ORM
            "features": {"auth": {"type": "basic"}}
        }
        with open(forge_dir / "config.json", "w") as f:
            json.dump(config, f)
        
        reader = ConfigReader(temp_dir)
        reader.load_config()
        with pytest.raises(ConfigValidationError) as exc_info:
            reader.validate_config()
        assert "Invalid ORM type" in str(exc_info.value)
    
    def test_redis_boolean_format(self, temp_dir):
        """Should handle Redis as boolean"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        config = {
            "project_name": "test",
            "database": {"type": "PostgreSQL", "orm": "SQLModel"},
            "features": {"auth": {"type": "basic"}, "redis": True}
        }
        with open(forge_dir / "config.json", "w") as f:
            json.dump(config, f)
        
        reader = ConfigReader(temp_dir)
        reader.load_config()
        assert reader.has_redis() is True
    
    def test_redis_object_format(self, temp_dir):
        """Should handle Redis as object"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        config = {
            "project_name": "test",
            "database": {"type": "PostgreSQL", "orm": "SQLModel"},
            "features": {"auth": {"type": "basic"}, "redis": {"enabled": True, "features": ["caching"]}}
        }
        with open(forge_dir / "config.json", "w") as f:
            json.dump(config, f)
        
        reader = ConfigReader(temp_dir)
        reader.load_config()
        assert reader.has_redis() is True
        assert "caching" in reader.get_redis_features()
    
    def test_celery_boolean_format(self, temp_dir):
        """Should handle Celery as boolean"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        config = {
            "project_name": "test",
            "database": {"type": "PostgreSQL", "orm": "SQLModel"},
            "features": {"auth": {"type": "basic"}, "celery": True}
        }
        with open(forge_dir / "config.json", "w") as f:
            json.dump(config, f)
        
        reader = ConfigReader(temp_dir)
        reader.load_config()
        assert reader.has_celery() is True


class TestProjectConfigUtils:
    """Tests for ProjectConfig utility"""
    
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
        shutil.rmtree(tmpdir, ignore_errors=True)
    
    def test_project_config_exists_true(self, temp_dir):
        """Should return True when .forge/config.json exists"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        (forge_dir / "config.json").touch()
        
        assert ProjectConfig.exists(temp_dir) is True
    
    def test_project_config_exists_false(self, temp_dir):
        """Should return False when .forge/config.json doesn't exist"""
        assert ProjectConfig.exists(temp_dir) is False
    
    def test_project_config_exists_only_forge_dir(self, temp_dir):
        """Should return False when only .forge dir exists without config.json"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        
        assert ProjectConfig.exists(temp_dir) is False
    
    def test_project_config_load(self, temp_dir):
        """Should load config correctly"""
        forge_dir = temp_dir / ".forge"
        forge_dir.mkdir()
        config = {"project_name": "test", "version": "1.0"}
        with open(forge_dir / "config.json", "w") as f:
            json.dump(config, f)
        
        loaded = ProjectConfig.load(temp_dir)
        assert loaded["project_name"] == "test"
    
    def test_project_config_load_missing(self, temp_dir):
        """Should return None when config doesn't exist"""
        loaded = ProjectConfig.load(temp_dir)
        assert loaded is None


class TestHandleExistingProject:
    """Tests for handle_existing_project function"""
    
    @pytest.fixture
    def temp_project(self):
        tmpdir = tempfile.mkdtemp()
        project_path = Path(tmpdir)
        
        # Create a fake existing project
        forge_dir = project_path / ".forge"
        forge_dir.mkdir()
        config = {
            "project_name": "existing",
            "metadata": {"created_at": "2025-01-01T00:00:00"}
        }
        with open(forge_dir / "config.json", "w") as f:
            json.dump(config, f)
        
        # Create some project files
        (project_path / "app").mkdir()
        (project_path / "app" / "main.py").touch()
        
        yield project_path
        shutil.rmtree(tmpdir, ignore_errors=True)
    
    def test_handle_existing_cancel(self, temp_project):
        """Should exit when user cancels"""
        from click.exceptions import Exit
        mock_style = MagicMock()
        
        with patch('commands.init.questionary') as mock_q:
            mock_q.select.return_value.ask.return_value = "Cancel - Keep existing project"
            
            with pytest.raises(Exit):
                handle_existing_project("existing", mock_style, use_current_dir=False)
    
    def test_handle_existing_overwrite_subdirectory(self, temp_project):
        """Should remove entire directory when overwriting subdirectory"""
        mock_style = MagicMock()
        
        # Create a subdirectory project
        sub_project = temp_project / "sub-project"
        sub_project.mkdir()
        (sub_project / ".forge").mkdir()
        (sub_project / "app").mkdir()
        
        with patch('commands.init.questionary') as mock_q:
            mock_q.select.return_value.ask.return_value = "Overwrite - Regenerate entire project"
            with patch('commands.init.Path') as mock_path:
                mock_path.cwd.return_value = temp_project
                
                result = handle_existing_project("sub-project", mock_style, use_current_dir=False)
                assert result is True
                assert not sub_project.exists()
