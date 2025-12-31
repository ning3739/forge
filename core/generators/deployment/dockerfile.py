"""Dockerfile 生成器"""
from ..templates.base import BaseTemplateGenerator


class DockerfileGenerator(BaseTemplateGenerator):
    """Dockerfile 文件生成器"""
    
    def generate(self) -> None:
        """生成 Dockerfile 文件"""
        content = self._build_base_image()
        content += self._build_working_directory()
        content += self._build_dependencies()
        content += self._build_app_copy()
        content += self._build_expose()
        content += self._build_command()
        
        self.file_ops.create_file(
            file_path="Dockerfile",
            content=content,
            overwrite=True
        )
    
    def _build_base_image(self) -> str:
        """构建基础镜像"""
        return '''# 使用官方 Python 运行时作为基础镜像
FROM python:3.10-slim

'''
    
    def _build_working_directory(self) -> str:
        """构建工作目录"""
        return '''# 设置工作目录
WORKDIR /app

'''
    
    def _build_dependencies(self) -> str:
        """构建依赖安装"""
        content = '''# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

'''
        
        # 如果有数据库，添加数据库客户端
        if self.config_reader.has_database():
            db_type = self.config_reader.get_database_type()
            if db_type == "PostgreSQL":
                content += '''# 安装 PostgreSQL 客户端库
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

'''
            elif db_type == "MySQL":
                content += '''# 安装 MySQL 客户端库
RUN apt-get update && apt-get install -y \\
    default-libmysqlclient-dev \\
    && rm -rf /var/lib/apt/lists/*

'''
        
        content += '''# 复制依赖文件
COPY pyproject.toml ./

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -e .

'''
        return content
    
    def _build_app_copy(self) -> str:
        """构建应用复制"""
        return '''# 复制应用代码
COPY ./app ./app
COPY ./main.py ./

'''
    
    def _build_expose(self) -> str:
        """构建端口暴露"""
        return '''# 暴露端口
EXPOSE 8000

'''
    
    def _build_command(self) -> str:
        """构建启动命令"""
        return '''# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
