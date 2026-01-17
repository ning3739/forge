# Celery Background Tasks

Celery is a distributed task queue that handles background work for your FastAPI application. When operations take too long for a single HTTP request—sending emails, generating reports, processing files—Celery executes them asynchronously while your API responds immediately.

## Why Use Celery

Without Celery, slow operations block your API. A user registers, your API tries to send a welcome email, and the user waits 5 seconds for the SMTP server to respond. With Celery, your API queues the email task and responds instantly. A background worker handles the actual sending.

Celery also enables scheduled tasks (cron-like jobs), automatic retries on failure, and horizontal scaling by adding more workers.

## When to Enable

Enable Celery if you need:
- Email sending (verification, password reset, notifications)
- Report generation or data exports
- File processing (images, videos, documents)
- Scheduled maintenance tasks
- Batch database operations

**Note**: Celery requires Redis as a message broker. Forge automatically enables Redis when you enable Celery.

## What Forge Generates

Forge creates a complete Celery setup:

**`app/core/celery.py`**: Celery application instance with configuration
**`app/tasks/`**: Directory for your task functions
**`app/core/config/celery.py`**: Environment-based settings

The generated configuration uses Redis database 1 for the task queue and database 2 for results, keeping them separate from your cache (database 0).

## Creating Tasks

### Basic Task

Create `app/tasks/send_email_task.py`:

```python
from app.core.celery import celery_app

@celery_app.task(name="send_email_task")
def send_email_task(recipient: str, subject: str, body: str):
    """Send email asynchronously"""
    # Your email sending logic
    send_email(recipient, subject, body)
    return {"status": "sent", "recipient": recipient}
```

The `@celery_app.task` decorator registers this function as a Celery task. When called with `.delay()`, it runs in a background worker instead of blocking your API.

### Task with Retry Logic

Add automatic retries for transient failures:

```python
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_payment(self, order_id: int, amount: float):
    """Process payment with retry on failure"""
    try:
        return payment_gateway.charge(order_id, amount)
    except PaymentGatewayError as e:
        # Retry after 60 seconds
        raise self.retry(exc=e, countdown=60)
```

**`bind=True`**: Gives access to `self` for calling `self.retry()`
**`max_retries=3`**: Retry up to 3 times before giving up
**`countdown=60`**: Wait 60 seconds between retries

### Task with Database Access

Use the `@with_db_init` decorator for database operations:

```python
from app.core.celery import celery_app, with_db_init

@celery_app.task
@with_db_init
def update_user_stats(user_id: int):
    """Update user statistics"""
    async def _update():
        async for db in get_db():
            user = await db.get(User, user_id)
            user.last_activity = datetime.utcnow()
            await db.commit()
    
    import asyncio
    asyncio.run(_update())
```

The `@with_db_init` decorator initializes the database connection for the worker process.

### Scheduled Tasks

Define periodic tasks in `app/core/celery.py`:

```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'daily-backup': {
        'task': 'app.tasks.backup_task.backup_database',
        'schedule': crontab(hour=3, minute=0),  # 3:00 AM daily
    },
    'hourly-cleanup': {
        'task': 'app.tasks.cleanup_task.cleanup_sessions',
        'schedule': 3600.0,  # Every hour (seconds)
    },
}
```

**Crontab syntax**: `hour=3, minute=0` runs at 3:00 AM. `day_of_week=1` is Monday (0=Sunday).
**Interval syntax**: Use seconds for simple intervals (3600 = 1 hour).

Celery Beat (the scheduler) reads this configuration and queues tasks at the specified times.

## Using Tasks in FastAPI

### Queue a Task

```python
from app.tasks.send_email_task import send_email_task

@router.post("/register")
async def register(email: str):
    # Create user...
    
    # Queue email task
    task = send_email_task.delay(email, "Welcome!", "Welcome to our app")
    
    return {"message": "Registration successful", "task_id": task.id}
```

The `.delay()` method queues the task and returns immediately with a task ID.

### Check Task Status

```python
from celery.result import AsyncResult

@router.get("/task/{task_id}")
async def task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "status": task.status,  # PENDING, STARTED, SUCCESS, FAILURE
        "result": task.result if task.ready() else None
    }
```

### Wait for Result (Use Sparingly)

```python
@router.post("/process")
async def process_data(data: dict):
    task = process_task.delay(data)
    
    try:
        result = task.get(timeout=30)  # Wait up to 30 seconds
        return {"status": "completed", "result": result}
    except TimeoutError:
        return {"status": "processing", "task_id": task.id}
```

**Warning**: `.get()` blocks your API worker. Use only when absolutely necessary.

## Common Task Examples

### 1. Email Sending Task

```python
# app/tasks/email_tasks.py
from app.core.celery import celery_app
from app.utils.email import email_service

@celery_app.task(name="send_verification_email")
def send_verification_email(email: str, code: str):
    """Send email verification"""
    email_service.send_email(
        subject="Verify Your Email",
        recipient=email,
        template="verification_email",
        code=code
    )

@celery_app.task(name="send_password_reset")
def send_password_reset(email: str, code: str):
    """Send password reset email"""
    email_service.send_email(
        subject="Reset Your Password",
        recipient=email,
        template="reset_password_email",
        code=code
    )
```

### 2. Data Processing Task

```python
# app/tasks/data_processing_task.py
from app.core.celery import celery_app
import pandas as pd

@celery_app.task(name="process_csv_file")
def process_csv_file(file_path: str):
    """Process large CSV file"""
    df = pd.read_csv(file_path)
    
    # Process data
    results = []
    for index, row in df.iterrows():
        result = process_row(row)
        results.append(result)
    
    return {
        "total_rows": len(df),
        "processed": len(results),
        "results": results
    }
```

### 3. Report Generation Task

```python
# app/tasks/report_task.py
from app.core.celery import celery_app, with_db_init
from datetime import datetime, timedelta

@celery_app.task(name="generate_monthly_report")
@with_db_init
def generate_monthly_report(month: int, year: int):
    """Generate monthly report"""
    # Fetch data from database
    start_date = datetime(year, month, 1)
    end_date = start_date + timedelta(days=32)
    
    # Generate report
    report = create_report(start_date, end_date)
    
    # Save to file
    filename = f"report_{year}_{month}.pdf"
    save_report(report, filename)
    
    return {"filename": filename, "status": "completed"}
```

### 4. Image Processing Task

```python
# app/tasks/image_task.py
from app.core.celery import celery_app
from PIL import Image

@celery_app.task(name="resize_image")
def resize_image(image_path: str, width: int, height: int):
    """Resize image"""
    img = Image.open(image_path)
    img_resized = img.resize((width, height))
    
    output_path = f"{image_path}_resized.jpg"
    img_resized.save(output_path)
    
    return {"output_path": output_path}

@celery_app.task(name="generate_thumbnails")
def generate_thumbnails(image_path: str):
    """Generate multiple thumbnail sizes"""
    sizes = [(100, 100), (200, 200), (400, 400)]
    thumbnails = []
    
    for width, height in sizes:
        result = resize_image(image_path, width, height)
        thumbnails.append(result)
    
    return thumbnails
```

### 5. Database Cleanup Task

```python
# app/tasks/cleanup_task.py
from app.core.celery import celery_app, with_db_init
from datetime import datetime, timedelta

@celery_app.task(name="cleanup_old_sessions")
@with_db_init
def cleanup_old_sessions():
    """Delete expired sessions"""
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    async def _cleanup():
        async for db in get_db():
            result = await db.execute(
                delete(Session).where(Session.created_at < cutoff_date)
            )
            await db.commit()
            return result.rowcount
    
    import asyncio
    deleted = asyncio.run(_cleanup())
    
    return {"deleted": deleted}
```

### 6. Notification Task

```python
# app/tasks/notification_task.py
from app.core.celery import celery_app

@celery_app.task(name="send_push_notification")
def send_push_notification(user_id: int, title: str, message: str):
    """Send push notification"""
    # Send to notification service
    result = push_service.send(
        user_id=user_id,
        title=title,
        message=message
    )
    return result

@celery_app.task(name="send_bulk_notifications")
def send_bulk_notifications(user_ids: list, title: str, message: str):
    """Send notifications to multiple users"""
    results = []
    for user_id in user_ids:
        task = send_push_notification.delay(user_id, title, message)
        results.append(task.id)
    return {"queued": len(results), "task_ids": results}
```

## Task Chaining and Workflows

### Sequential Tasks (Chain)

```python
from celery import chain

# Execute tasks in sequence
workflow = chain(
    process_data_task.s(data),
    validate_results_task.s(),
    send_notification_task.s()
)
result = workflow.apply_async()
```

### Parallel Tasks (Group)

```python
from celery import group

# Execute tasks in parallel
job = group(
    process_file_task.s(file1),
    process_file_task.s(file2),
    process_file_task.s(file3)
)
result = job.apply_async()
```

### Conditional Execution (Chord)

```python
from celery import chord

# Execute tasks in parallel, then callback
callback = send_summary_task.s()
header = group(
    process_file_task.s(file1),
    process_file_task.s(file2)
)
result = chord(header)(callback)
```

## Running Celery

### Start Worker (Development)

```bash
celery -A app.core.celery:celery_app worker --loglevel=info
```

This starts a worker process that executes tasks from the queue.

### Start Beat (Scheduler)

```bash
celery -A app.core.celery:celery_app beat --loglevel=info
```

Beat schedules periodic tasks. Run this in addition to workers.

### Combined (Development Only)

```bash
celery -A app.core.celery:celery_app worker --beat --loglevel=info
```

### Production Configuration

```bash
celery -A app.core.celery:celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100
```

**`--concurrency=4`**: Run 4 parallel workers. Rule of thumb: `(2 × CPU_cores) + 1`
**`--max-tasks-per-child=100`**: Restart workers after 100 tasks to prevent memory leaks

### Monitor with Flower

```bash
pip install flower
celery -A app.core.celery:celery_app flower --port=5555
```

Open http://localhost:5555 for a web dashboard showing active tasks, worker status, and task history.

## Docker Deployment

Forge configures Celery services in `docker-compose.yml`:

```yaml
services:
  celery_worker:
    build: .
    command: celery -A app.core.celery:celery_app worker --loglevel=info
    depends_on: [redis, postgres]
    volumes: [./secret:/app/secret]

  celery_beat:
    build: .
    command: celery -A app.core.celery:celery_app beat --loglevel=info
    depends_on: [redis, postgres]
    volumes: [./secret:/app/secret]
```

Start everything with:
```bash
docker-compose up -d
```

## Environment Configuration

**Development** (`secret/.env.development`):
```ini
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TIMEZONE=UTC
```

**Production** (`secret/.env.production`):
```ini
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TIMEZONE=UTC
```

The only difference is the hostname: `redis` (Docker service name) vs `localhost`.

## Best Practices

### 1. Keep Tasks Idempotent

Tasks should produce the same result when executed multiple times:

```python
@celery_app.task
def update_user_status(user_id: int, status: str):
    """Idempotent task"""
    # Check current status first
    user = get_user(user_id)
    if user.status != status:
        user.status = status
        save_user(user)
```

### 2. Use Task Timeouts

Prevent tasks from running indefinitely:

```python
@celery_app.task(time_limit=300, soft_time_limit=270)
def long_running_task():
    """Task with 5-minute timeout"""
    # Task will be killed after 300 seconds
    # SoftTimeLimitExceeded raised after 270 seconds
    pass
```

### 3. Handle Failures Gracefully

```python
@celery_app.task(bind=True, max_retries=3)
def reliable_task(self, data):
    try:
        process_data(data)
    except TemporaryError as e:
        # Retry on temporary errors
        raise self.retry(exc=e, countdown=60)
    except PermanentError as e:
        # Log and don't retry
        logger.error(f"Permanent error: {e}")
        return {"status": "failed", "error": str(e)}
```

### 4. Monitor Task Performance

```python
from celery.signals import task_prerun, task_postrun
import time

task_start_times = {}

@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    task_start_times[task_id] = time.time()

@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    if task_id in task_start_times:
        duration = time.time() - task_start_times[task_id]
        logger.info(f"Task {task.name} took {duration:.2f}s")
        del task_start_times[task_id]
```

### 5. Use Task Priorities

```python
# High priority task
@celery_app.task(priority=9)
def urgent_task():
    pass

# Low priority task
@celery_app.task(priority=1)
def background_task():
    pass
```

## Troubleshooting

### Worker Not Processing Tasks

```bash
# Check worker status
celery -A app.core.celery:celery_app inspect active

# Check registered tasks
celery -A app.core.celery:celery_app inspect registered

# Purge all tasks
celery -A app.core.celery:celery_app purge
```

### Task Stuck in Pending

```bash
# Check if Redis is running
redis-cli ping

# Check broker connection
celery -A app.core.celery:celery_app inspect ping
```

### Memory Issues

```python
# Configure worker to restart after processing tasks
celery_app.conf.worker_max_tasks_per_child = 100
celery_app.conf.worker_max_memory_per_child = 200000  # 200MB
```

## See Also

- [Configuration Options](configuration.md) - Celery configuration
- [Redis Caching](redis-caching.md) - Redis setup for Celery
- [Deployment Guide](deployment.md) - Production Celery setup
