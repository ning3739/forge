"""dockerignore generator"""
from core.decorators import Generator
from ..templates.base import BaseTemplateGenerator


@Generator(
    category="deployment",
    priority=102,
    enabled_when=lambda c: c.has_docker(),
    description="Generate .dockerignore"
)
class DockerignoreGenerator(BaseTemplateGenerator):
    """.dockerignore file generator"""
    
    def generate(self) -> None:
        """generate .dockerignore file"""
        content = self._build_python_section()
        content += self._build_venv_section()
        content += self._build_ide_section()
        content += self._build_git_section()
        content += self._build_env_section()
        content += self._build_testing_section()
        content += self._build_docs_section()
        content += self._build_misc_section()
        
        self.file_ops.create_file(
            file_path=".dockerignore",
            content=content,
            overwrite=True
        )
    
    def _build_python_section(self) -> str:
        """Build Python-related ignore rules"""
        return '''# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
build
develop-eggs
dist
downloads
eggs
.eggs
lib
lib64
parts
sdist
var
wheels
*.egg-info
.installed.cfg
*.egg

'''
    
    def _build_venv_section(self) -> str:
        """Build virtual environment ignore rules"""
        return '''# Virtual Environment
.venv
venv
ENV
env

'''
    
    def _build_ide_section(self) -> str:
        """Build IDE ignore rules"""
        return '''# IDE
.vscode
.idea
*.swp
*.swo
*~

'''
    
    def _build_git_section(self) -> str:
        """Build Git ignore rules"""
        return '''# Git
.git
.gitignore
.gitattributes

'''
    
    def _build_env_section(self) -> str:
        """Build environment variables ignore rules"""
        return '''# Environment Variables
.env
.env.*
!.env.example
!secret/.env.*

'''
    
    def _build_testing_section(self) -> str:
        """Build testing-related ignore rules"""
        return '''# Testing
.pytest_cache
.coverage
htmlcov
.tox
tests

'''
    
    def _build_docs_section(self) -> str:
        """Build documentation ignore rules"""
        return '''# Documentation
docs
*.md
!README.md

'''
    
    def _build_misc_section(self) -> str:
        """Build miscellaneous ignore rules"""
        return '''# Misc
.DS_Store
Thumbs.db
*.log
logs
.forge
docker-compose.yml
Dockerfile
'''
