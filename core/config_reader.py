"""配置文件读取器模块"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigReader:
    """配置文件读取器类
    
    负责读取和解析 .forge/config.json 配置文件
    """
    
    def __init__(self, project_path: Path):
        """初始化配置读取器
        
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.config: Optional[Dict[str, Any]] = None
        self.config_file = self.project_path / ".forge" / "config.json"
        
    def load_config(self) -> Dict[str, Any]:
        """从 .forge/config.json 读取配置
        
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式错误
        """
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}\n"
                f"Please run 'forge init' first to create the configuration."
            )
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        return self.config
    
    def validate_config(self) -> bool:
        """验证配置文件的完整性
        
        Returns:
            配置是否有效
        """
        if not self.config:
            return False
        
        # 检查必需字段
        required_fields = ['project_name', 'features']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: {field}")
        
        return True
    
    def get_project_name(self) -> str:
        """获取项目名称"""
        return self.config.get('project_name', 'my-project')
    
    def get_database_config(self) -> Optional[Dict[str, str]]:
        """获取数据库配置
        
        Returns:
            数据库配置字典，如果未配置数据库则返回 None
        """
        return self.config.get('database')
    
    def get_database_type(self) -> Optional[str]:
        """获取数据库类型
        
        Returns:
            数据库类型 (PostgreSQL/MySQL) 或 None
        """
        db_config = self.get_database_config()
        return db_config.get('type') if db_config else None
    
    def get_orm_type(self) -> Optional[str]:
        """获取 ORM 类型
        
        Returns:
            ORM 类型 (SQLModel/SQLAlchemy) 或 None
        """
        db_config = self.get_database_config()
        return db_config.get('orm') if db_config else None
    
    def get_migration_tool(self) -> Optional[str]:
        """获取迁移工具
        
        Returns:
            迁移工具名称 (Alembic) 或 None
        """
        db_config = self.get_database_config()
        return db_config.get('migration_tool') if db_config else None
    
    def has_migration(self) -> bool:
        """检查是否启用数据库迁移"""
        return self.get_migration_tool() is not None
    
    def get_features(self) -> Dict[str, Any]:
        """获取功能配置"""
        return self.config.get('features', {})
    
    def has_database(self) -> bool:
        """检查是否配置了数据库"""
        return self.get_database_config() is not None
    
    def has_auth(self) -> bool:
        """检查是否启用认证"""
        features = self.get_features()
        auth_config = features.get('auth', {})
        return auth_config.get('type') != 'none'
    
    def get_auth_type(self) -> Optional[str]:
        """获取认证类型 (basic/complete/none)"""
        features = self.get_features()
        auth_config = features.get('auth', {})
        return auth_config.get('type')
    
    def has_refresh_token(self) -> bool:
        """检查是否启用 Refresh Token"""
        features = self.get_features()
        auth_config = features.get('auth', {})
        return auth_config.get('refresh_token', False)
    
    def has_cors(self) -> bool:
        """检查是否启用 CORS"""
        features = self.get_features()
        return features.get('cors', False)
    
    def has_dev_tools(self) -> bool:
        """检查是否包含开发工具"""
        features = self.get_features()
        return features.get('dev_tools', False)
    
    def has_testing(self) -> bool:
        """检查是否包含测试工具"""
        features = self.get_features()
        return features.get('testing', False)
    
    def has_docker(self) -> bool:
        """检查是否包含 Docker 配置"""
        features = self.get_features()
        return features.get('docker', False)
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """获取元数据信息"""
        return self.config.get('metadata')
    
    def get_created_at(self) -> Optional[str]:
        """获取配置创建时间"""
        metadata = self.get_metadata()
        return metadata.get('created_at') if metadata else None
    
    def get_forge_version(self) -> Optional[str]:
        """获取 Forge 版本"""
        metadata = self.get_metadata()
        return metadata.get('forge_version') if metadata else None
