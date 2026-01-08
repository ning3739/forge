"""Tasks __init__.py generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="task",
    priority=59,
    enabled_when=lambda c: c.has_celery(),
    description="Generate tasks __init__.py (app/tasks/__init__.py)"
)
class TasksInitGenerator(BaseTemplateGenerator):
    """Tasks __init__.py generator"""
    
    def generate(self) -> None:
        """Generate tasks __init__.py file"""
        
        imports = [
            "from .backup_database_task import backup_database_task",
        ]
        
        content = '''# Export all tasks
__all__ = [
    "backup_database_task"
]
'''
        
        self.file_ops.create_python_file(
            file_path="app/tasks/__init__.py",
            docstring="Celery tasks module\n\nThis module contains all Celery async task definitions.\n\nUsage:\n    from app.tasks.backup_database_task import backup_database_task\n    \n    # Execute task asynchronously\n    result = backup_database_task.delay()\n    \n    # Get task result\n    task_result = result.get()",
            imports=imports,
            content=content,
            overwrite=True
        )