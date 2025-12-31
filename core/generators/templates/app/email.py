"""Email 配置生成器"""
from pathlib import Path
from core.utils import FileOperations
from core.config_reader import ConfigReader


class ConfigEmailGenerator:
    """Email 配置文件生成器"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """初始化配置生成器
        
        Args:
            project_path: 项目根目录路径
            config_reader: 配置读取器实例
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.file_ops = FileOperations(base_path=project_path)
    
    def generate(self) -> None:
        """生成 email 配置文件"""
        # 只有 Complete JWT Auth 才生成邮件配置
        if self.config_reader.get_auth_type() != "complete":
            return
        
        imports = [
            "from pydantic import Field, SecretStr",
            "from pydantic_settings import BaseSettings",
        ]
        
        content = '''class EmailSettings(BaseSettings):
    """Email configuration settings"""
    
    # SMTP Server Configuration
    EMAIL_HOST: str = Field(
        default="smtp.gmail.com",
        description="SMTP server host"
    )
    
    EMAIL_PORT: int = Field(
        default=587,
        description="SMTP server port"
    )
    
    EMAIL_HOST_USER: str = Field(
        default="",
        description="SMTP username"
    )
    
    EMAIL_HOST_PASSWORD: SecretStr = Field(
        default="",
        description="SMTP password"
    )
    
    # SSL/TLS Configuration
    EMAIL_USE_TLS: bool = Field(
        default=True,
        description="Use TLS for SMTP connection"
    )
    
    EMAIL_USE_SSL: bool = Field(
        default=False,
        description="Use SSL for SMTP connection"
    )
    
    EMAIL_SSL_CERT_REQS: str = Field(
        default="required",
        description="SSL certificate requirements (required/optional/none)"
    )
    
    # Timeout Configuration
    EMAIL_TIMEOUT: int = Field(
        default=30,
        description="SMTP connection timeout in seconds"
    )
    
    # Email Expiration
    EMAIL_EXPIRATION: int = Field(
        default=3600,
        description="Email verification code expiration time in seconds"
    )
    
    # Email From Configuration
    EMAIL_FROM_NAME: str = Field(
        default="",
        description="Email sender name"
    )
    
    EMAIL_FROM_EMAIL: str = Field(
        default="",
        description="Email sender address"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/email.py",
            docstring="Email configuration module",
            imports=imports,
            content=content,
            overwrite=True
        )
