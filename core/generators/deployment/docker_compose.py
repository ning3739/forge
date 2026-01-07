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
        return '''version: '3.8'

'''
    
    def _build_services(self) -> str:
        """Build services configuration"""
        content = '''services:
  app:
    build: .
    container_name: {project_name}
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
'''.format(project_name=self.config_reader.get_project_name())
        
        # Add database connection environment variables
        db_type = self.config_reader.get_database_type()
        if db_type == "PostgreSQL":
            content += '''      - DATABASE_URL=postgresql://postgres:postgres@db:5432/{project_name}
'''.format(project_name=self.config_reader.get_project_name())
        elif db_type == "MySQL":
            content += '''      - DATABASE_URL=mysql://root:mysql@db:3306/{project_name}
'''.format(project_name=self.config_reader.get_project_name())
        
        content += '''    volumes:
      - ./app:/app/app
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - app-network

'''
        
        # Add database service
        content += self._build_database_service()
        
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

'''.format(project_name=project_name)
        
        return ''
    
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
