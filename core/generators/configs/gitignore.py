"""gitignore generategenerator"""
from core.decorators import Generator
from ..templates.base import BaseTemplateGenerator


@Generator(
    category="config",
    priority=3,
    description="Generate .gitignore file"
)
class GitignoreGenerator(BaseTemplateGenerator):
    """gitignore File generator"""
    
    def generate(self) -> None:
        """generate .gitignore file"""
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
        """Build Python related ignore rules"""
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
        """Buildvirtual environment ignore rules"""
        return '''# Virtual Environment
.venv/
venv/
ENV/
env/

'''
    
    def _build_ide_section(self) -> str:
        """Build IDE ignore rules"""
        return '''# IDE
.vscode/
.idea/
*.swp
*.swo
*~

'''
    
    def _build_env_section(self) -> str:
        """Buildenvironment variablesignore rules"""
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
        """Builddatabaseignore rules"""
        return '''# Database
*.db
*.sqlite3

'''
    
    def _build_testing_section(self) -> str:
        """Buildtestrelated ignore rules"""
        return '''# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

'''
    
    def _build_tools_section(self) -> str:
        """Buildutilityrelated ignore rules"""
        return '''# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/

'''
    
    def _build_os_section(self) -> str:
        """Buildoperating systemignore rules"""
        return '''# OS
.DS_Store
Thumbs.db

'''
    
    def _build_logs_section(self) -> str:
        """Buildloggingignore rules"""
        return '''# Logs
*.log
logs/
'''
