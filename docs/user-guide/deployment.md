# Deployment Guide

This guide covers deploying your Forge-generated FastAPI application to production using Docker, cloud platforms, and traditional servers.

## Docker Deployment

When you enable Docker (`use_docker: true`), Forge generates production-ready Docker configuration.

### Generated Files

```
your-project/
├── Dockerfile              # Application container
├── docker-compose.yml      # Multi-service orchestration
└── .dockerignore          # Files to exclude from image
```

### Quick Start

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application
COPY . .

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Compose

**PostgreSQL Example**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./app:/app/app

  celery_worker:
    build: .
    command: celery -A app.core.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery_beat:
    build: .
    command: celery -A app.core.celery beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
```

### Environment Configuration

Create `.env.production`:

```ini
# Database
DB_USER=myapi_user
DB_PASSWORD=secure_production_password
DB_NAME=myapi_prod

# Application
SECRET_KEY=your-super-secret-key-change-this-in-production
ENVIRONMENT=production

# Redis (if enabled)
REDIS_URL=redis://redis:6379/0

# Email (if complete auth)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@yourdomain.com
```

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use strong database passwords
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure email service
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set resource limits
- [ ] Enable health checks

## Cloud Platforms

### AWS (Elastic Beanstalk)

**1. Install EB CLI**:
```bash
pip install awsebcli
```

**2. Initialize**:
```bash
eb init -p docker my-api
```

**3. Create Environment**:
```bash
eb create production-env
```

**4. Deploy**:
```bash
eb deploy
```

**5. Configure Environment Variables**:
```bash
eb setenv SECRET_KEY=your-secret-key \
         DATABASE_URL=your-db-url \
         REDIS_URL=your-redis-url
```

### Google Cloud Platform (Cloud Run)

**1. Build Image**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/my-api
```

**2. Deploy**:
```bash
gcloud run deploy my-api \
  --image gcr.io/PROJECT_ID/my-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="SECRET_KEY=your-secret-key,DATABASE_URL=your-db-url"
```

### Heroku

**1. Create Heroku App**:
```bash
heroku create my-api
```

**2. Add PostgreSQL**:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

**3. Add Redis** (if enabled):
```bash
heroku addons:create heroku-redis:hobby-dev
```

**4. Set Environment Variables**:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ENVIRONMENT=production
```

**5. Deploy**:
```bash
git push heroku main
```

**6. Run Migrations**:
```bash
heroku run alembic upgrade head
```

### DigitalOcean App Platform

**1. Create `app.yaml`**:
```yaml
name: my-api
services:
- name: web
  github:
    repo: your-username/your-repo
    branch: main
  build_command: pip install -e .
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  envs:
  - key: SECRET_KEY
    value: ${SECRET_KEY}
  - key: DATABASE_URL
    value: ${DATABASE_URL}
  http_port: 8080

databases:
- name: db
  engine: PG
  version: "15"
```

**2. Deploy**:
```bash
doctl apps create --spec app.yaml
```

## Traditional Server Deployment

### Using Systemd (Ubuntu/Debian)

**1. Install Dependencies**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx
```

**2. Set Up Application**:
```bash
cd /opt
sudo git clone https://github.com/your-username/your-api.git
cd your-api
sudo python3.11 -m venv venv
sudo venv/bin/pip install -e .
```

**3. Create Systemd Service** (`/etc/systemd/system/myapi.service`):
```ini
[Unit]
Description=My FastAPI Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/your-api
Environment="PATH=/opt/your-api/venv/bin"
ExecStart=/opt/your-api/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

**4. Start Service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable myapi
sudo systemctl start myapi
```

**5. Configure Nginx** (`/etc/nginx/sites-available/myapi`):
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**6. Enable Site**:
```bash
sudo ln -s /etc/nginx/sites-available/myapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**7. Set Up SSL with Let's Encrypt**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## Performance Optimization

### Gunicorn with Uvicorn Workers

```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Worker Count Formula

```python
workers = (2 * CPU_CORES) + 1
```

For a 2-core machine: `(2 * 2) + 1 = 5 workers`

### Docker Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Monitoring and Logging

### Application Logging

Generated projects include structured logging:

```python
from app.core.logger_manager import get_logger

logger = get_logger(__name__)

@router.get("/items")
async def get_items():
    logger.info("Fetching items")
    # ... logic ...
    logger.info("Items fetched successfully", extra={"count": len(items)})
    return items
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Prometheus Metrics

Add `prometheus-fastapi-instrumentator`:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### Sentry Error Tracking

```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=1.0,
)
```

## Database Management

### Backup Strategy

**Automated Backups** (if Celery enabled):
```python
# Runs daily at 2 AM
@celery_app.task
def backup_database_task():
    # PostgreSQL
    subprocess.run([
        "pg_dump",
        "-U", DB_USER,
        "-h", DB_HOST,
        DB_NAME,
        "-f", f"backup_{date}.sql"
    ])
```

**Manual Backup**:
```bash
# PostgreSQL
pg_dump -U user dbname > backup.sql

# MySQL
mysqldump -u user -p dbname > backup.sql
```

### Connection Pooling

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Number of connections to maintain
    max_overflow=10,  # Additional connections when pool is full
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)
```

## Security

### HTTPS/SSL

**Let's Encrypt (Free)**:
```bash
sudo certbot --nginx -d api.yourdomain.com
```

**Custom Certificate**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/endpoint")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "This endpoint is rate limited"}
```

## Scaling

### Horizontal Scaling

**Load Balancer** (Nginx):
```nginx
upstream api_backend {
    server api1.internal:8000;
    server api2.internal:8000;
    server api3.internal:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

### Database Read Replicas

```python
# Write to primary
write_engine = create_async_engine(PRIMARY_DB_URL)

# Read from replica
read_engine = create_async_engine(REPLICA_DB_URL)
```

### Caching Strategy

```python
from redis import asyncio as aioredis

redis = await aioredis.from_url("redis://localhost")

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    # Check cache
    cached = await redis.get(f"item:{item_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    item = await db.get(Item, item_id)
    
    # Cache result
    await redis.setex(
        f"item:{item_id}",
        3600,  # 1 hour TTL
        json.dumps(item.dict())
    )
    
    return item
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs app

# Check if ports are available
lsof -i :8000

# Rebuild without cache
docker-compose build --no-cache
```

### Database Connection Issues

```bash
# Test database connectivity
docker-compose exec app python -c "from app.core.database import engine; print(engine)"

# Check environment variables
docker-compose exec app env | grep DATABASE_URL
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Reduce worker count
# Implement connection pooling
# Add memory limits in docker-compose.yml
```

## See Also

- [Configuration Options](configuration.md) - Deployment configuration
- [Database Setup](database.md) - Production database
- [Authentication Guide](authentication.md) - Security in production
- [Testing Guide](testing.md) - Pre-deployment testing
