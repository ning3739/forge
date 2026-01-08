"""Configuration file reader module"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigValidationError(Exception):
    """Configuration validation error"""
    pass


class ConfigReader:
    """Configuration file reader
    
    Responsible for reading and parsing .forge/config.json configuration file
    """
    
    # Configuration validation rules
    REQUIRED_FIELDS = ['project_name', 'database', 'features']
    VALID_DATABASE_TYPES = ['PostgreSQL', 'MySQL', 'SQLite']
    VALID_ORM_TYPES = ['SQLModel', 'SQLAlchemy']
    VALID_AUTH_TYPES = ['basic', 'complete']
    
    def __init__(self, project_path: Path):
        """Initialize configuration reader
        
        Args:
            project_path: Project root directory path
        """
        self.project_path = Path(project_path)
        self.config: Optional[Dict[str, Any]] = None
        self.config_file = self.project_path / ".forge" / "config.json"
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from .forge/config.json
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: Configuration file does not exist
            json.JSONDecodeError: Configuration file format error
        """
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}\n"
                f"Please run 'forge init' first to create the configuration."
            )
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigValidationError(
                f"Invalid JSON in configuration file: {e}"
            )
        
        return self.config
    
    def validate_config(self) -> bool:
        """Validate configuration file integrity
        
        Returns:
            Whether configuration is valid
            
        Raises:
            ConfigValidationError: Configuration validation failed
        """
        if not self.config:
            raise ConfigValidationError("Configuration not loaded")
        
        # Check required fields
        self._validate_required_fields()
        
        # Validate database configuration
        self._validate_database_config()
        
        # Validate authentication configuration
        self._validate_auth_config()
        
        return True
    
    def _validate_required_fields(self) -> None:
        """Validate required fields"""
        missing_fields = [
            field for field in self.REQUIRED_FIELDS
            if field not in self.config
        ]
        if missing_fields:
            raise ConfigValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
    
    def _validate_database_config(self) -> None:
        """Validate database configuration"""
        db_config = self.config.get('database')
        if not db_config:
            raise ConfigValidationError("Database configuration is required")
        
        if 'type' not in db_config:
            raise ConfigValidationError("Database type is required")
        
        if db_config['type'] not in self.VALID_DATABASE_TYPES:
            raise ConfigValidationError(
                f"Invalid database type: {db_config['type']}. "
                f"Valid types: {', '.join(self.VALID_DATABASE_TYPES)}"
            )
        
        if 'orm' not in db_config:
            raise ConfigValidationError("ORM type is required")
        
        if db_config['orm'] not in self.VALID_ORM_TYPES:
            raise ConfigValidationError(
                f"Invalid ORM type: {db_config['orm']}. "
                f"Valid types: {', '.join(self.VALID_ORM_TYPES)}"
            )
    
    def _validate_auth_config(self) -> None:
        """Validate authentication configuration"""
        features = self.config.get('features', {})
        auth_config = features.get('auth', {})
        auth_type = auth_config.get('type')
        
        if not auth_type or auth_type == 'none':
            raise ConfigValidationError(
                "Authentication is required but not configured"
            )
        
        if auth_type not in self.VALID_AUTH_TYPES:
            raise ConfigValidationError(
                f"Invalid authentication type: {auth_type}. "
                f"Valid types: {', '.join(self.VALID_AUTH_TYPES)}"
            )
    
    # ========== Configuration Getter Methods ==========
    
    def get_project_name(self) -> str:
        """Get project name"""
        return self.config.get('project_name', 'my-project')
    
    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration"""
        db_config = self.config.get('database')
        if not db_config:
            raise ConfigValidationError("Database configuration is required")
        return db_config
    
    def get_database_type(self) -> str:
        """Get database type"""
        return self.get_database_config()['type']
    
    def get_orm_type(self) -> str:
        """Get ORM type"""
        return self.get_database_config()['orm']
    
    def get_migration_tool(self) -> Optional[str]:
        """Get migration tool"""
        return self.get_database_config().get('migration_tool')
    
    def has_migration(self) -> bool:
        """Check if database migration is enabled"""
        return self.get_migration_tool() is not None
    
    def get_features(self) -> Dict[str, Any]:
        """Get feature configuration"""
        return self.config.get('features', {})
    
    def has_auth(self) -> bool:
        """Check if authentication is enabled (authentication is now required)"""
        return True
    
    def get_auth_type(self) -> str:
        """Get authentication type"""
        features = self.get_features()
        auth_config = features.get('auth', {})
        auth_type = auth_config.get('type')
        if not auth_type or auth_type == 'none':
            raise ConfigValidationError(
                "Authentication is required but not configured"
            )
        return auth_type
    
    def has_refresh_token(self) -> bool:
        """Check if Refresh Token is enabled"""
        features = self.get_features()
        auth_config = features.get('auth', {})
        return auth_config.get('refresh_token', False)
    
    def has_cors(self) -> bool:
        """Check if CORS is enabled"""
        return self.get_features().get('cors', False)
    
    def has_dev_tools(self) -> bool:
        """Check if development tools are included"""
        return self.get_features().get('dev_tools', False)
    
    def has_testing(self) -> bool:
        """Check if testing tools are included"""
        return self.get_features().get('testing', False)
    
    def has_docker(self) -> bool:
        """Check if Docker configuration is included"""
        return self.get_features().get('docker', False)
    
    def has_redis(self) -> bool:
        """Check if Redis is enabled"""
        redis_config = self.get_features().get('redis', False)
        # Support both boolean and object format
        if isinstance(redis_config, bool):
            return redis_config
        return redis_config.get('enabled', False)
    
    def get_redis_features(self) -> list:
        """Get Redis features list"""
        redis_config = self.get_features().get('redis', {})
        if isinstance(redis_config, bool):
            return ["caching", "sessions", "queues"] if redis_config else []
        return redis_config.get('features', [])
    
    def has_celery(self) -> bool:
        """Check if Celery is enabled"""
        celery_config = self.get_features().get('celery', False)
        # Support both boolean and object format
        if isinstance(celery_config, bool):
            return celery_config
        return celery_config.get('enabled', False)
    
    def get_celery_features(self) -> list:
        """Get Celery features list"""
        celery_config = self.get_features().get('celery', {})
        if isinstance(celery_config, bool):
            return ["background_tasks", "scheduled_tasks", "task_monitoring"] if celery_config else []
        return celery_config.get('features', [])
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get metadata information"""
        return self.config.get('metadata')
    
    def get_created_at(self) -> Optional[str]:
        """Get configuration creation time"""
        metadata = self.get_metadata()
        return metadata.get('created_at') if metadata else None
    
    def get_forge_version(self) -> Optional[str]:
        """Get Forge version"""
        metadata = self.get_metadata()
        return metadata.get('forge_version') if metadata else None

