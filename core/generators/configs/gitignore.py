"""gitignore 生成器"""
from ..templates.base import BaseTemplateGenerator


class GitignoreGenerator(BaseTemplateGenerator):
    """gitignore 文件生成器"""
    
    def generate(self) -> None:
        """生成 .gitignore 文件"""
        content = self._build_python_section()
        content += self._build_venv_section()
        content += self._build_ide_section()
        content += self._build_env_section()
        content += self._build_database_section()
        content += self._build_testing_section()
        content += self._build_tools_section()
        content += self._build_os_section()
        content += self._build_logs_section()
        
        self.file_ops.create_file(
            file_path=".gitignore",
            content=content,
            overwrite=True
        )
    
    def _build_python_section(self) -> str:
        """构建 Python 相关忽略规则"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

'''
    
    def _build_venv_section(self) -> str:
        """构建虚拟环境忽略规则"""
        return '''# Virtual Environment
.venv/
venv/
ENV/
env/

'''
    
    def _build_ide_section(self) -> str:
        """构建 IDE 忽略规则"""
        return '''# IDE
.vscode/
.idea/
*.swp
*.swo
*~

'''
    
    def _build_env_section(self) -> str:
        """构建环境变量忽略规则"""
        return '''# Environment Variables
.env
.env.local
.env.*.local
secret/.env.development
secret/.env.production

# Keep example files
!.env.example
!secret/.env.example

'''
    
    def _build_database_section(self) -> str:
        """构建数据库忽略规则"""
        return '''# Database
*.db
*.sqlite3

'''
    
    def _build_testing_section(self) -> str:
        """构建测试相关忽略规则"""
        return '''# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

'''
    
    def _build_tools_section(self) -> str:
        """构建工具相关忽略规则"""
        return '''# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/

'''
    
    def _build_os_section(self) -> str:
        """构建操作系统忽略规则"""
        return '''# OS
.DS_Store
Thumbs.db

'''
    
    def _build_logs_section(self) -> str:
        """构建日志忽略规则"""
        return '''# Logs
*.log
logs/
'''
