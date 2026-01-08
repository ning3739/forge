"""Dockerfile generator"""
from core.decorators import Generator
from ..templates.base import BaseTemplateGenerator


@Generator(
    category="deployment",
    priority=100,
    enabled_when=lambda c: c.has_docker(),
    description="Generate Dockerfile"
)
class DockerfileGenerator(BaseTemplateGenerator):
    """Dockerfile file generator"""
    
    def generate(self) -> None:
        """generate Dockerfile"""
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
        """Build base image"""
        return '''# Use official Python runtime as base image
FROM python:3.10-slim

'''
    
    def _build_working_directory(self) -> str:
        """Build working directory"""
        return '''# Set working directory
WORKDIR /app

'''
    
    def _build_dependencies(self) -> str:
        """Build dependency installation"""
        content = '''# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

'''
        
        # Add database client based on database type
        db_type = self.config_reader.get_database_type()
        if db_type == "PostgreSQL":
            content += '''# Install PostgreSQL client libraries
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

'''
        elif db_type == "MySQL":
            content += '''# Install MySQL client libraries
RUN apt-get update && apt-get install -y \\
    default-libmysqlclient-dev \\
    && rm -rf /var/lib/apt/lists/*

'''
        
        content += '''# Copy dependency files and alembic configuration
COPY pyproject.toml README.md alembic.ini ./
COPY alembic ./alembic

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -e .

'''
        return content
    
    def _build_app_copy(self) -> str:
        """Build application copy"""
        return '''# Copy application code
COPY ./app ./app

# Copy environment configuration
COPY ./secret ./secret

# Set Python path to include current directory
ENV PYTHONPATH=/app

'''
    
    def _build_expose(self) -> str:
        """Build port exposure"""
        return '''# Expose port
EXPOSE 8000

'''
    
    def _build_command(self) -> str:
        """Build startup command"""
        return '''# Startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
