"""Database backup task generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="task",
    priority=60,
    enabled_when=lambda c: c.has_celery(),
    description="Generate database backup task (app/tasks/backup_database_task.py)"
)
class BackupDatabaseTaskGenerator(BaseTemplateGenerator):
    """Database backup task generator"""
    
    def generate(self) -> None:
        """Generate database backup task file"""
        project_name = self.config_reader.get_project_name()
        
        imports = [
            "import gzip",
            "import os", 
            "import subprocess",
            "from datetime import datetime, timedelta",
            "from pathlib import Path",
            "from urllib.parse import urlparse",
            "from typing import Optional, List",
            "",
            "from app.core.celery import celery_app, with_db_init",
            "from app.core.config.settings import settings",
            "from app.core.logger import logger_manager",
        ]
        
        content = f'''logger = logger_manager.get_logger(__name__)


def _parse_database_url(database_url: str) -> dict:
    """Parse database connection URL
    
    Args:
        database_url: Format like mysql://user:password@host:port/database
        
    Returns:
        dict: Contains host, port, user, password, database, db_type
    """
    try:
        parsed = urlparse(database_url)
        
        # Handle different database types
        if parsed.scheme.startswith('mysql'):
            db_type = 'mysql'
            host = parsed.hostname or 'localhost'
            port = parsed.port or 3306
            user = parsed.username or 'root'
            password = parsed.password or ''
            database = parsed.path.lstrip('/') if parsed.path else '{project_name}'
        elif parsed.scheme.startswith('postgresql'):
            db_type = 'postgresql'
            host = parsed.hostname or 'localhost'
            port = parsed.port or 5432
            user = parsed.username or 'postgres'
            password = parsed.password or ''
            database = parsed.path.lstrip('/') if parsed.path else '{project_name}'
        elif parsed.scheme.startswith('sqlite'):
            db_type = 'sqlite'
            # SQLite uses file path
            database_path = database_url.replace('sqlite:///', '').replace('sqlite://', '')
            return {{
                'db_type': db_type,
                'database_path': database_path,
                'database': Path(database_path).stem  # File name as database name
            }}
        else:
            raise ValueError(f"Unsupported database type: {{parsed.scheme}}")
        
        return {{
            'db_type': db_type,
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }}
            
    except Exception as e:
        logger.error(f"Failed to parse database URL: {{e}}")
        raise


def _dump_database(db_config: dict, output_file: Path) -> bool:
    """Export database
    
    Args:
        db_config: Database configuration dictionary
        output_file: Output file path
        
    Returns:
        bool: Whether successful
    """
    try:
        db_type = db_config['db_type']
        
        if db_type == 'mysql':
            return _dump_mysql(db_config, output_file)
        elif db_type == 'postgresql':
            return _dump_postgresql(db_config, output_file)
        elif db_type == 'sqlite':
            return _dump_sqlite(db_config, output_file)
        else:
            logger.error(f"Unsupported database type: {{db_type}}")
            return False
            
    except Exception as e:
        logger.error(f"Error exporting database: {{e}}")
        return False


def _dump_mysql(db_config: dict, output_file: Path) -> bool:
    """Export MySQL database using mysqldump"""
    try:
        # Build mysqldump command
        cmd = [
            'mysqldump',
            f"--host={{db_config['host']}}",
            f"--port={{db_config['port']}}",
            f"--user={{db_config['user']}}",
            '--single-transaction',  # Ensure data consistency
            '--routines',  # Include stored procedures and functions
            '--triggers',  # Include triggers
            '--events',  # Include events
            '--quick',  # Quick mode
            '--lock-tables=false',  # Don't lock tables
            db_config['database']
        ]
        
        # Set password environment variable (more secure)
        env = os.environ.copy()
        if db_config['password']:
            env['MYSQL_PWD'] = db_config['password']
        
        logger.info(f"Starting MySQL database export: {{db_config['database']}}")
        
        # Execute mysqldump
        with open(output_file, 'wb') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                env=env,
                check=True
            )
        
        # Check file size
        file_size = output_file.stat().st_size
        if file_size == 0:
            logger.error("Exported database file is empty")
            return False
        
        file_size_mb = file_size / 1024 / 1024
        logger.info(f"MySQL database export successful: {{output_file.name}} ({{file_size_mb:.2f}} MB)")
        return True
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"mysqldump execution failed: {{error_msg}}")
        return False
    except Exception as e:
        logger.error(f"Error exporting MySQL database: {{e}}")
        return False


def _dump_postgresql(db_config: dict, output_file: Path) -> bool:
    """Export PostgreSQL database using pg_dump"""
    try:
        # Build pg_dump command
        cmd = [
            'pg_dump',
            f"--host={{db_config['host']}}",
            f"--port={{db_config['port']}}",
            f"--username={{db_config['user']}}",
            '--no-password',  # Don't prompt for password
            '--verbose',  # Verbose output
            '--clean',  # Include cleanup commands
            '--if-exists',  # Drop if exists
            '--create',  # Include create database commands
            db_config['database']
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        if db_config['password']:
            env['PGPASSWORD'] = db_config['password']
        
        logger.info(f"Starting PostgreSQL database export: {{db_config['database']}}")
        
        # Execute pg_dump
        with open(output_file, 'wb') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                env=env,
                check=True
            )
        
        # Check file size
        file_size = output_file.stat().st_size
        if file_size == 0:
            logger.error("Exported database file is empty")
            return False
        
        file_size_mb = file_size / 1024 / 1024
        logger.info(f"PostgreSQL database export successful: {{output_file.name}} ({{file_size_mb:.2f}} MB)")
        return True
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"pg_dump execution failed: {{error_msg}}")
        return False
    except Exception as e:
        logger.error(f"Error exporting PostgreSQL database: {{e}}")
        return False


def _dump_sqlite(db_config: dict, output_file: Path) -> bool:
    """Export SQLite database"""
    try:
        database_path = Path(db_config['database_path'])
        
        if not database_path.exists():
            logger.error(f"SQLite database file does not exist: {{database_path}}")
            return False
        
        logger.info(f"Starting SQLite database export: {{database_path}}")
        
        # Use sqlite3 command to export
        cmd = [
            'sqlite3',
            str(database_path),
            '.dump'
        ]
        
        with open(output_file, 'wb') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                check=True
            )
        
        # Check file size
        file_size = output_file.stat().st_size
        if file_size == 0:
            logger.error("Exported database file is empty")
            return False
        
        file_size_mb = file_size / 1024 / 1024
        logger.info(f"SQLite database export successful: {{output_file.name}} ({{file_size_mb:.2f}} MB)")
        return True
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"sqlite3 execution failed: {{error_msg}}")
        return False
    except Exception as e:
        logger.error(f"Error exporting SQLite database: {{e}}")
        return False


def _compress_file(input_file: Path, output_file: Path) -> bool:
    """Compress file
    
    Args:
        input_file: Input file path
        output_file: Output compressed file path
        
    Returns:
        bool: Whether successful
    """
    try:
        logger.info(f"Starting file compression: {{input_file.name}}")
        
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb', compresslevel=6) as f_out:
                f_out.writelines(f_in)
        
        original_size = input_file.stat().st_size
        compressed_size = output_file.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        logger.info(f"Compression complete: {{output_file.name}} "
                   f"({{compressed_size / 1024 / 1024:.2f}} MB, "
                   f"compression ratio: {{compression_ratio:.1f}}%)")
        return True
        
    except Exception as e:
        logger.error(f"Error compressing file: {{e}}")
        return False


def _cleanup_old_backups(backup_dir: Path, database_name: str, retention_days: int) -> None:
    """Clean up old local backup files
    
    Args:
        backup_dir: Backup directory
        database_name: Database name
        retention_days: Retention days
    """
    if retention_days <= 0:
        logger.info("Retention days <= 0, skipping cleanup")
        return
    
    try:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        logger.info(f"Starting cleanup of backup files before {{cutoff_date.strftime('%Y-%m-%d')}}")
        
        # Find matching backup files
        pattern = f"{{database_name}}_backup_*.sql.gz"
        backup_files = list(backup_dir.glob(pattern))
        
        if not backup_files:
            logger.info("No backup files found")
            return
        
        files_to_delete = []
        for backup_file in backup_files:
            # Get file modification time
            file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                files_to_delete.append(backup_file)
        
        if not files_to_delete:
            logger.info("No old backup files to clean up")
            return
        
        logger.info(f"Found {{len(files_to_delete)}} old backup files to delete")
        
        # Delete old files
        success_count = 0
        for file_to_delete in files_to_delete:
            try:
                file_to_delete.unlink()
                logger.info(f"Deleted old backup file: {{file_to_delete.name}}")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to delete file {{file_to_delete.name}}: {{e}}")
        
        logger.info(f"Cleanup complete: successfully deleted {{success_count}} files")
        
    except Exception as e:
        logger.error(f"Error cleaning up old backup files: {{e}}", exc_info=True)


@celery_app.task(
    name="backup_database_task",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # Retry after 5 minutes on failure
    time_limit=3600,  # 1 hour hard timeout
    soft_time_limit=3300,  # 55 minutes soft timeout
)
@with_db_init
def backup_database_task(
    self,
    database_name: Optional[str] = None,
    retention_days: int = 30,
    backup_dir: Optional[str] = None
) -> dict:
    """Backup database to local storage
    
    Args:
        database_name: Database name, defaults to parsed from DATABASE_URL
        retention_days: Retention days, backup files older than this will be automatically deleted (set to 0 or negative to disable cleanup)
        backup_dir: Backup directory, defaults to ./backups/database
        
    Returns:
        dict: Backup result information
    """
    sql_file = None
    gz_file = None
    
    try:
        # 1. Parse database configuration
        database_url = settings.database.DATABASE_URL
        db_config = _parse_database_url(database_url)
        
        if database_name:
            db_config['database'] = database_name
        
        logger.info(f"Starting database backup: {{db_config['database']}}")
        
        # 2. Create backup directory
        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            backup_path = Path('./backups/database')
        
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # 3. Generate file names
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_name = db_config['database']
        sql_file = backup_path / f"{{db_name}}_backup_{{timestamp}}.sql"
        gz_file = backup_path / f"{{db_name}}_backup_{{timestamp}}.sql.gz"
        
        # 4. Export database
        if not _dump_database(db_config, sql_file):
            raise Exception("Database export failed")
        
        # 5. Compress file
        if not _compress_file(sql_file, gz_file):
            raise Exception("File compression failed")
        
        # 6. Clean up original SQL file
        sql_file.unlink(missing_ok=True)
        
        # 7. Clean up old backup files
        if retention_days > 0:
            try:
                _cleanup_old_backups(backup_path, db_name, retention_days)
            except Exception as cleanup_error:
                # Cleanup failure doesn't affect backup success
                logger.warning(f"Failed to clean up old backup files: {{cleanup_error}}")
        
        # 8. Return success result
        backup_file_size = gz_file.stat().st_size
        result = {{
            'success': True,
            'database': db_name,
            'backup_file': str(gz_file),
            'file_size_mb': round(backup_file_size / 1024 / 1024, 2),
            'timestamp': timestamp,
            'retention_days': retention_days,
            'message': 'Backup successful'
        }}
        
        logger.info(f"✅ Backup complete: {{gz_file}} ({{result['file_size_mb']}} MB)")
        return result
        
    except Exception as e:
        logger.error(f"Backup failed: {{e}}", exc_info=True)
        
        # Clean up possible temporary files
        for file in [sql_file, gz_file]:
            if file and file.exists():
                try:
                    file.unlink()
                    logger.debug(f"Cleaned up temporary file: {{file}}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up temporary file {{file}}: {{cleanup_error}}")
        
        # Retry task
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=300)
        
        # Exceeded retry limit, return failure result
        return {{
            'success': False,
            'database': database_name or 'unknown',
            'error': str(e),
            'message': 'Backup failed'
        }}
'''
        
        self.file_ops.create_python_file(
            file_path="app/tasks/backup_database_task.py",
            docstring="Database backup task - backup to local storage",
            imports=imports,
            content=content,
            overwrite=True
        )