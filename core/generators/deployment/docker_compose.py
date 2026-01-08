"""Docker Compose generator"""
from core.decorators import Generator
from ..templates.base import BaseTemplateGenerator


@Generator(
    category="deployment",
    priority=101,
    requires=["DockerfileGenerator"],
    enabled_when=lambda c: c.has_docker(),
    description="Generate docker-compose.yml"
)
class DockerComposeGenerator(BaseTemplateGenerator):
    """Docker Compose file generator"""
    
    def generate(self) -> None:
        """generate docker-compose.yml file"""
        content = self._build_version()
        content += self._build_services()
        content += self._build_volumes()
        content += self._build_networks()
        
        self.file_ops.create_file(
            file_path="docker-compose.yml",
            content=content,
            overwrite=True
        )
    
    def _build_version(self) -> str:
        """Build version declaration"""
        return ''
    
    def _build_services(self) -> str:
        """Build services configuration"""
        content = '''services:
  app:
    build: .
    container_name: {project_name}
    ports:
      - "8000:8000"
    env_file:
      - ./secret/.env.production
    environment:
      - ENV=production
'''.format(project_name=self.config_reader.get_project_name())
        
        # Add database connection environment variables
        db_type = self.config_reader.get_database_type()
        if db_type == "PostgreSQL":
            content += '''      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/{project_name}
'''.format(project_name=self.config_reader.get_project_name())
        elif db_type == "MySQL":
            content += '''      - DATABASE_URL=mysql+aiomysql://root:mysql@db:3306/{project_name}
'''.format(project_name=self.config_reader.get_project_name())
        
        # Add Redis environment variables if enabled
        if self.config_reader.has_redis():
            content += '''      - REDIS_CONNECTION_URL=redis://redis:6379
'''
        
        # Add Celery environment variables if enabled
        if self.config_reader.has_celery():
            content += '''      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
'''
        
        # Build dependencies with proper conditions
        content += '''    volumes:
      - ./app:/app/app
    depends_on:
      db-migrate:
        condition: service_completed_successfully
'''
        
        if self.config_reader.has_redis():
            content += '''      redis:
        condition: service_started
'''
        
        content += '''    restart: unless-stopped
    networks:
      - app-network

'''
        
        # Add database service
        content += self._build_database_service()
        
        # Add database migration service
        content += self._build_database_migration_service()
        
        # Add Redis service if enabled
        if self.config_reader.has_redis():
            content += self._build_redis_service()
        
        # Add Celery services if enabled
        if self.config_reader.has_celery():
            content += self._build_celery_services()
        
        return content
    
    def _build_database_service(self) -> str:
        """Build database service configuration"""
        db_type = self.config_reader.get_database_type()
        project_name = self.config_reader.get_project_name()
        
        if db_type == "PostgreSQL":
            return '''  db:
    image: postgres:15-alpine
    container_name: {project_name}_db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB={project_name}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      timeout: 20s
      retries: 10

'''.format(project_name=project_name)
        
        elif db_type == "MySQL":
            return '''  db:
    image: mysql:8.0
    container_name: {project_name}_db
    environment:
      - MYSQL_ROOT_PASSWORD=mysql
      - MYSQL_DATABASE={project_name}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-pmysql"]
      timeout: 20s
      retries: 10

'''.format(project_name=project_name)
        
        return ''
    
    def _build_database_migration_service(self) -> str:
        """Build database migration service configuration"""
        project_name = self.config_reader.get_project_name()
        
        # Build environment variables
        env_vars = '''      - ENV=production
'''
        
        # Add database connection
        db_type = self.config_reader.get_database_type()
        if db_type == "PostgreSQL":
            env_vars += '''      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/{project_name}
'''.format(project_name=project_name)
        elif db_type == "MySQL":
            env_vars += '''      - DATABASE_URL=mysql+aiomysql://root:mysql@db:3306/{project_name}
'''.format(project_name=project_name)
        
        return '''  db-migrate:
    build: .
    container_name: {project_name}_db_migrate
    command: sh -c "alembic revision --autogenerate -m 'Auto migration' && alembic upgrade head"
    env_file:
      - ./secret/.env.production
    environment:
{env_vars}    volumes:
      - ./app:/app/app
      - ./alembic:/app/alembic
      - ./alembic.ini:/app/alembic.ini
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network

'''.format(project_name=project_name, env_vars=env_vars)
    
    def _build_redis_service(self) -> str:
        """Build Redis service configuration"""
        project_name = self.config_reader.get_project_name()
        
        return '''  redis:
    image: redis:7-alpine
    container_name: {project_name}_redis
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - app-network

'''.format(project_name=project_name)
    
    def _build_celery_services(self) -> str:
        """Build Celery services configuration"""
        project_name = self.config_reader.get_project_name()
        
        # Build environment variables
        env_vars = '''      - ENV=production
'''
        
        # Add database connection
        db_type = self.config_reader.get_database_type()
        if db_type == "PostgreSQL":
            env_vars += '''      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/{project_name}
'''.format(project_name=project_name)
        elif db_type == "MySQL":
            env_vars += '''      - DATABASE_URL=mysql+aiomysql://root:mysql@db:3306/{project_name}
'''.format(project_name=project_name)
        
        # Add Redis and Celery environment variables
        env_vars += '''      - REDIS_CONNECTION_URL=redis://redis:6379
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
'''
        
        # Build dependencies with proper conditions
        depends_on_str = '''      db-migrate:
        condition: service_completed_successfully
      redis:
        condition: service_started
'''
        
        return '''  celery-worker:
    build: .
    container_name: {project_name}_celery_worker
    command: celery -A app.core.celery.celery_app worker --loglevel=info
    env_file:
      - ./secret/.env.production
    environment:
{env_vars}    volumes:
      - ./app:/app/app
    depends_on:
{depends_on_str}    restart: unless-stopped
    networks:
      - app-network

  celery-beat:
    build: .
    container_name: {project_name}_celery_beat
    command: celery -A app.core.celery.celery_app beat --loglevel=info
    env_file:
      - ./secret/.env.production
    environment:
{env_vars}    volumes:
      - ./app:/app/app
    depends_on:
{depends_on_str}    restart: unless-stopped
    networks:
      - app-network

'''.format(project_name=project_name, env_vars=env_vars, depends_on_str=depends_on_str)
    
    def _build_volumes(self) -> str:
        """Build volumes configuration"""
        db_type = self.config_reader.get_database_type()
        
        content = '''volumes:
'''
        
        if db_type == "PostgreSQL":
            content += '''  postgres_data:

'''
        elif db_type == "MySQL":
            content += '''  mysql_data:

'''
        
        return content
    
    def _build_networks(self) -> str:
        """Build networks configuration"""
        return '''networks:
  app-network:
    driver: bridge
'''
