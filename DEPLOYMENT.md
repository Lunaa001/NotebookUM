# 🚀 DEPLOYMENT GUIDE - NotebookUM

**Status:** Production Ready (FASE 1-5 Complete)

---

## 📋 Índice
1. [Local Development](#local-development)
2. [Docker - Single Container](#docker-single-container)
3. [Docker Compose - Full Stack](#docker-compose-full-stack)
4. [Production Deployment](#production-deployment)
5. [Health Checks & Monitoring](#health-checks--monitoring)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ Local Development

### Paso 1: Setup Inicial
```bash
# Clone repo
git clone https://github.com/tu-usuario/NotebookUM.git
cd NotebookUM

# Install dependencies
uv sync

# Copy environment
cp .env.example .env
```

### Paso 2: Database Setup
```bash
# Start PostgreSQL (Docker)
cd dockers/PostgreSQL
docker-compose up -d
cd ../../

# Wait for DB to be ready
sleep 10

# Apply migrations
uv run alembic upgrade head
```

### Paso 3: Run Tests
```bash
uv run pytest tests/ -v
# Expected: 78 passed, 7 skipped
```

### Paso 4: Start Server
```bash
# Dev server with auto-reload (hot reload not available with Granian)
uv run granian --interface asgi --host 0.0.0.0 --port 8000 main:app

# Docs available at:
# - Swagger: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

---

## 🐳 Docker - Single Container

### Build Image

```bash
# Build with version tag
docker build -t notebookum:1.2.0 .

# Also tag as latest
docker tag notebookum:1.2.0 notebookum:latest
```

### Run Container

```bash
# Prerequisites: PostgreSQL running elsewhere (port 5432)
docker run -d \
  --name notebookum \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg://notebookum:notebookum123@db-host:5432/notebookum" \
  -e GEMMA4_API_KEY="sk-..." \
  -e DEBUG="false" \
  notebookum:1.2.0

# Check logs
docker logs -f notebookum

# Stop
docker stop notebookum
docker rm notebookum
```

---

## 🐋 Docker Compose - Full Stack (RECOMENDADO)

### Setup

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15.4-bullseye
    container_name: notebookum-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: notebookum
      POSTGRES_PASSWORD: notebookum123
      POSTGRES_DB: notebookum
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U notebookum"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - notebookum-network

  # NotebookUM API
  notebookum:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: notebookum-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://notebookum:notebookum123@postgres:5432/notebookum
      GEMMA4_API_KEY: ${GEMMA4_API_KEY}
      DEBUG: "false"
      VERSION: "1.2.0"
    depends_on:
      postgres:
        condition: service_healthy
    command: >
      sh -c "
      echo 'Running migrations...' &&
      alembic upgrade head &&
      echo 'Starting server...' &&
      granian --interface asgi --host 0.0.0.0 --port 8000 main:app
      "
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - notebookum-network
    volumes:
      - /tmp/notebookum_uploads:/tmp/notebookum_uploads

  # Optional: Adminer for DB Management
  adminer:
    image: adminer:latest
    container_name: notebookum-adminer
    restart: unless-stopped
    ports:
      - "8080:8080"
    depends_on:
      - postgres
    networks:
      - notebookum-network
    environment:
      ADMINER_DEFAULT_SERVER: postgres

volumes:
  postgres_data:

networks:
  notebookum-network:
    driver: bridge
```

### Ejecutar Stack

```bash
# Set environment variable (if not in .env)
export GEMMA4_API_KEY="sk-8d8bd2869b3d4c19b734a6f5c82482aa"

# Start all services
docker-compose up -d

# Check status
docker-compose ps
# OUTPUT:
# NAME                   STATUS
# notebookum-postgres    Up (healthy)
# notebookum-api         Up (healthy)
# notebookum-adminer     Up

# View logs
docker-compose logs -f notebookum

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Access Services

- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **Adminer (DB):** http://localhost:8080

Credentials para Adminer:
- System: PostgreSQL
- Server: postgres
- User: notebookum
- Password: notebookum123
- Database: notebookum

---

## 🌍 Production Deployment

### Recomendaciones

1. **Never commit credentials** - Use `.env.local` ignored by git
2. **Use environment variables** - All config via env vars
3. **Enable production mode** - Set `DEBUG=false`
4. **Enable CORS restrictively** - Set specific `ALLOWED_ORIGINS`
5. **Use SSL/TLS** - Proxy with nginx/traefik
6. **Monitor logs** - Use centralized logging (ELK, Datadog, etc)

### Example: AWS ECS Deployment

```yaml
# ecs-task-definition.json
{
  "family": "notebookum",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "notebookum-api",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/notebookum:1.2.0",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "false"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:notebookum/db-url"
        },
        {
          "name": "GEMMA4_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:notebookum/gemma4-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/notebookum",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### Example: Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notebookum
  labels:
    app: notebookum
spec:
  replicas: 3
  selector:
    matchLabels:
      app: notebookum
  template:
    metadata:
      labels:
        app: notebookum
    spec:
      containers:
      - name: notebookum
        image: notebookum:1.2.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: notebookum-secrets
              key: database-url
        - name: GEMMA4_API_KEY
          valueFrom:
            secretKeyRef:
              name: notebookum-secrets
              key: gemma4-key
        - name: DEBUG
          value: "false"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: notebookum-service
spec:
  selector:
    app: notebookum
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## 💚 Health Checks & Monitoring

### Health Endpoint

```bash
curl http://localhost:8000/api/v1/health

# Response:
{
  "status": "healthy",
  "timestamp": "2026-04-27T10:00:00",
  "version": "1.2.0",
  "app_name": "NotebookUM"
}
```

### Monitoring Checklist

- [ ] API response time < 200ms
- [ ] DB connection pool healthy
- [ ] Gemma4 API availability > 99%
- [ ] Disk space for uploads > 10GB
- [ ] Memory usage < 80% of limit
- [ ] Error rate < 1%

### Logging

```bash
# Production: send logs to centralized system
docker-compose logs notebookum | tail -100

# Check error patterns
docker-compose logs notebookum | grep ERROR
```

---

## 🔧 Troubleshooting

### "Connection refused" - Database

```bash
# Check if postgres is running
docker-compose ps postgres

# If not:
docker-compose up -d postgres
sleep 10

# Retry migrations
docker-compose run --rm notebookum alembic upgrade head
```

### "GEMMA4_API_KEY not found"

```bash
# Ensure .env has the key
cat .env | grep GEMMA4_API_KEY

# Or pass as env var
docker-compose run -e GEMMA4_API_KEY="sk-..." notebookum sh
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
docker-compose run -p 8001:8000 notebookum
```

### PDF Upload Fails

```bash
# Check uploads directory permissions
ls -la /tmp/notebookum_uploads/

# Ensure write permissions
chmod 777 /tmp/notebookum_uploads

# Test PDF extraction
uv run python -c "
from app.services.pdf_extraction_service import PDFExtractionService
text = PDFExtractionService.extract_text('test.pdf')
print(f'OK: {len(text)} chars')
"
```

### Gemma4 API Returns Empty Summary

```bash
# This is handled automatically - AIService checks both "content" and "reasoning"
# If still failing, check:
# 1. API key validity: curl -H "Authorization: Bearer $GEMMA4_API_KEY" https://ai.cloud.um.edu.ar/api/v1/health
# 2. Model availability: gemma4-26b-16g
# 3. Max tokens: try with max_tokens=150
```

---

## 📊 Performance Tuning

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_doc_user ON documentos(usuario_id);
CREATE INDEX idx_doc_fecha ON documentos(fecha_creacion DESC);

-- Check slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

### Application Optimization

```python
# In config.py - adjust based on load
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_RECYCLE = 3600
```

### Caching Strategy

```python
# Add Redis for caching (future)
# - Cache extracted text for same PDF hash
# - Cache summaries by document_id
# - TTL: 24 hours
```

---

## 📝 Maintenance

### Database Backups

```bash
# Automated daily backup
docker-compose exec -T postgres pg_dump -U notebookum notebookum > backup-$(date +%Y%m%d).sql

# Or use AWS S3
aws s3 cp backup-20260427.sql s3://my-bucket/backups/
```

### Upgrade Procedure

```bash
# 1. Backup database
docker-compose exec postgres pg_dump -U notebookum notebookum > backup.sql

# 2. Stop services
docker-compose down

# 3. Pull latest code
git pull origin main

# 4. Build new image
docker build -t notebookum:1.3.0 .

# 5. Update docker-compose.yml with new version

# 6. Run migrations
docker-compose run --rm notebookum alembic upgrade head

# 7. Start services
docker-compose up -d

# 8. Verify health
curl http://localhost:8000/api/v1/health
```

---

**Last Updated:** 2026-04-27 | **Version:** 1.2.0
