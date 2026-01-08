"""Celery app generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="app",
    priority=47,
    enabled_when=lambda c: c.has_celery(),
    requires=["CeleryConfigGenerator"],
    description="Generate Celery application instance (app/core/celery.py)"
)
class CeleryAppGenerator(BaseTemplateGenerator):
    """Celery application instance generator"""
    
    def generate(self) -> None:
        """Generate Celery application instance file"""
        # Get database type for proper import
        db_type = self.config_reader.get_database_type().lower()
        
        imports = [
            "from celery import Celery",
            "from celery.schedules import crontab",
            "from app.core.config.settings import settings",
            "import asyncio",
            "from functools import wraps",
            f"from app.core.database.{db_type} import {db_type}_manager",
            "from app.core.logger import logger_manager",
        ]
        
        content = f'''def with_db_init(func):
    """Decorator: Automatically initialize database connection for Celery tasks"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logger_manager.get_logger(__name__)
        
        # Initialize database connection (Celery worker needs separate initialization)
        async def init_db():
            try:
                await {db_type}_manager.initialize()
                logger.debug("Database initialized successfully for Celery task")
            except Exception as e:
                logger.error(f"Failed to initialize database for Celery task: {{e}}")
                raise
        
        # Run async initialization in Celery task
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(init_db())
        except Exception as e:
            logger.error(f"Database initialization failed in Celery task: {{e}}")
            raise
        
        # Execute original task
        return func(*args, **kwargs)
    
    return wrapper


class CeleryManager:
    def __init__(self):
        self.celery_app = Celery(
            "app",
            broker=settings.celery.CELERY_BROKER_URL,
            backend=settings.celery.CELERY_RESULT_BACKEND,
        )
    
    def setup(self):
        self.celery_app.conf.update(
            broker_connection_retry_on_startup=True,
            accept_content=settings.celery.CELERY_ACCEPT_CONTENT,
            task_serializer=settings.celery.CELERY_TASK_SERIALIZER,
            result_serializer=settings.celery.CELERY_RESULT_SERIALIZER,
            timezone=settings.celery.CELERY_TIMEZONE,
            enable_utc=settings.celery.CELERY_ENABLE_UTC,
        )
    
    def autodiscovery(self):
        self.celery_app.autodiscover_tasks(
            packages=["app.tasks"],
            force=True,
        )
    
    def start(self):
        self.celery_app.start()
    
    def close(self):
        self.celery_app.close()


# Create a celery app instance
celery_app = Celery(
    "app",
    broker=settings.celery.CELERY_BROKER_URL,
    backend=settings.celery.CELERY_RESULT_BACKEND,
)

# Configure the celery app
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    accept_content=settings.celery.CELERY_ACCEPT_CONTENT,
    task_serializer=settings.celery.CELERY_TASK_SERIALIZER,
    result_serializer=settings.celery.CELERY_RESULT_SERIALIZER,
    timezone=settings.celery.CELERY_TIMEZONE,
    enable_utc=settings.celery.CELERY_ENABLE_UTC,
    
    # Optimization configuration: suitable for 2GB memory server
    worker_concurrency=1,  # 1 worker process (save memory)
    worker_prefetch_multiplier=1,  # Avoid worker prefetching too many tasks
    task_acks_late=True,  # Acknowledge task after completion
    worker_max_tasks_per_child=100,  # Restart worker after processing 100 tasks
    task_time_limit=3600,  # Task timeout: 1 hour
    task_soft_time_limit=3000,  # Soft timeout: 50 minutes
    
    # Configuration to prevent duplicate task execution
    task_reject_on_worker_lost=True,  # Reject tasks when worker crashes to avoid duplicates
    task_ignore_result=False,  # Save task results for tracking
    
    # Ensure tasks execute only once
    task_always_eager=False,  # Ensure tasks execute asynchronously
    worker_disable_rate_limits=False,  # Enable rate limiting
    
    # Use unique identifiers to prevent duplicates
    task_store_eager_result=True,  # Store eager mode results
)

# Auto-discover tasks
# Remove force=True to avoid duplicate task registration
celery_app.autodiscover_tasks(
    packages=["app.tasks"],
    force=False,  # Set to False to avoid duplicate task registration
)

# Configure Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {{
    'backup-database-daily': {{
        'task': 'app.tasks.backup_database_task.backup_database_task',
        'schedule': crontab(hour=3, minute=0),  # Execute daily at 3:00 AM
        'args': (),
        'kwargs': {{
            'retention_days': 30,  # Keep backups for 30 days
        }},
        'options': {{
            'expires': 3600,  # Task expiration time: 1 hour
        }}
    }}
}}
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/celery.py",
            docstring="Celery configuration and application instance",
            imports=imports,
            content=content,
            overwrite=True
        )