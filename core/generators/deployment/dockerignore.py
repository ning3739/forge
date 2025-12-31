"""dockerignore 生成器"""
from ..templates.base import BaseTemplateGenerator


class DockerignoreGenerator(BaseTemplateGenerator):
    """.dockerignore 文件生成器"""
    
    def generate(self) -> None:
        """生成 .dockerignore 文件"""
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
        """构建 Python 相关忽略规则"""
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
        """构建虚拟环境忽略规则"""
        return '''# Virtual Environment
.venv
venv
ENV
env

'''
    
    def _build_ide_section(self) -> str:
        """构建 IDE 忽略规则"""
        return '''# IDE
.vscode
.idea
*.swp
*.swo
*~

'''
    
    def _build_git_section(self) -> str:
        """构建 Git 忽略规则"""
        return '''# Git
.git
.gitignore
.gitattributes

'''
    
    def _build_env_section(self) -> str:
        """构建环境变量忽略规则"""
        return '''# Environment Variables
.env
.env.*
!.env.example

'''
    
    def _build_testing_section(self) -> str:
        """构建测试相关忽略规则"""
        return '''# Testing
.pytest_cache
.coverage
htmlcov
.tox
tests

'''
    
    def _build_docs_section(self) -> str:
        """构建文档忽略规则"""
        return '''# Documentation
*.md
docs

'''
    
    def _build_misc_section(self) -> str:
        """构建其他忽略规则"""
        return '''# Misc
.DS_Store
Thumbs.db
*.log
logs
.forge
docker-compose.yml
Dockerfile
'''
