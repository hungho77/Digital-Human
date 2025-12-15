# Deployment Guide

Complete deployment guide for the Digital Human Restaurant Assistant, covering development, staging, and production environments.

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Development Deployment](#development-deployment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

## Deployment Overview

### Deployment Strategies

| Strategy | Use Case | Complexity | Scalability |
|----------|----------|------------|-------------|
| **Local Dev** | Development & testing | Low | Single user |
| **Docker Single** | Small restaurant | Medium | 1-5 sessions |
| **Docker Compose** | Medium restaurant | Medium | 5-10 sessions |
| **Kubernetes** | Multi-location chain | High | 50+ sessions |

### System Requirements by Deployment

#### Development Environment

```yaml
CPU: 8 cores
RAM: 16GB
GPU: RTX 3060 12GB
Storage: 100GB SSD
OS: Ubuntu 20.04+
```

#### Production Single Server

```yaml
CPU: 16 cores (Ryzen 9 / i9)
RAM: 32GB DDR4/DDR5
GPU: RTX 4080 16GB or RTX 4090 24GB
Storage: 500GB NVMe SSD
Network: 100Mbps+ dedicated
OS: Ubuntu 22.04 LTS Server
```

#### Production Cluster (Optional)

```yaml
Nodes: 3-5 servers
Each Node:
  CPU: 16+ cores
  RAM: 64GB
  GPU: 2× RTX 4080 or 1× RTX 4090
  Storage: 1TB NVMe SSD
Network: 1Gbps+ with low latency
Orchestration: Kubernetes 1.28+
```

## Development Deployment

### Quick Start (Local Development)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/Digital-Human.git
cd Digital-Human

# 2. Setup environment
./scripts/setup_dev.sh

# 3. Activate virtual environment
source venv/bin/activate

# 4. Start services
# Terminal 1: PostgreSQL
sudo systemctl start postgresql

# Terminal 2: Redis
redis-server

# Terminal 3: Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Terminal 4: vLLM Server
python -m vllm.entrypoints.openai.api_server \
  --model ./models/qwen2.5-7b-instruct \
  --dtype float16 \
  --max-model-len 4096

# Terminal 5: Application
python app.py --model wav2lip --avatar_id avator_1 --debug
```

### Development Configuration

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database (local)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=digital_human_dev
POSTGRES_USER=devuser
POSTGRES_PASSWORD=devpassword

# Redis (local)
REDIS_HOST=localhost
REDIS_PORT=6379

# Models (local paths)
MODEL_PATH=./models
VLLM_MODEL=./models/qwen2.5-7b-instruct

# Server
HOST=0.0.0.0
PORT=8010
MAX_SESSIONS=2
WORKERS=1
```

### Development Workflow

```bash
# Start development server with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8010

# Or use make
make run-dev

# Access development dashboard
# http://localhost:8010/dashboard.html
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] All services tested in staging
- [ ] Database backups configured
- [ ] SSL certificates obtained
- [ ] Environment variables secured
- [ ] Monitoring configured
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team trained on operations

### Production Server Setup

#### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  build-essential \
  python3.10 \
  python3.10-venv \
  python3.10-dev \
  postgresql-15 \
  redis-server \
  nginx \
  certbot \
  python3-certbot-nginx

# Install NVIDIA drivers (if not present)
sudo ubuntu-drivers autoinstall
sudo reboot

# Install Docker & NVIDIA Container Runtime
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# NVIDIA Container Runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

#### 2. Application Deployment

```bash
# Create application user
sudo useradd -r -s /bin/bash -m -d /opt/digital-human digitaluser

# Clone application
sudo -u digitaluser git clone https://github.com/YOUR_USERNAME/Digital-Human.git /opt/digital-human/app
cd /opt/digital-human/app

# Setup virtual environment
sudo -u digitaluser python3.10 -m venv /opt/digital-human/venv
sudo -u digitaluser /opt/digital-human/venv/bin/pip install -r requirements.txt

# Download models
sudo -u digitaluser mkdir -p /opt/digital-human/models
# Download and place model files (see environment-setup.md)

# Create production config
sudo -u digitaluser cp .env.production.example /opt/digital-human/.env
sudo -u digitaluser nano /opt/digital-human/.env
```

#### 3. Database Setup

```bash
# PostgreSQL production configuration
sudo -u postgres psql <<EOF
CREATE DATABASE digital_human_prod;
CREATE USER prod_user WITH ENCRYPTED PASSWORD 'STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE digital_human_prod TO prod_user;

-- Enable required extensions
\c digital_human_prod
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\q
EOF

# Run migrations
cd /opt/digital-human/app
/opt/digital-human/venv/bin/python -m alembic upgrade head

# Initialize data
/opt/digital-human/venv/bin/python scripts/init_database.py
```

#### 4. Redis Configuration

```bash
# Configure Redis for production
sudo nano /etc/redis/redis.conf

# Key settings:
# bind 127.0.0.1
# requirepass STRONG_REDIS_PASSWORD
# maxmemory 2gb
# maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

#### 5. Qdrant Setup

```bash
# Run Qdrant in production
docker run -d \
  --name qdrant \
  --restart=unless-stopped \
  -p 6333:6333 \
  -v /opt/digital-human/data/qdrant:/qdrant/storage \
  qdrant/qdrant

# Initialize collections
/opt/digital-human/venv/bin/python scripts/init_qdrant.py
```

### Systemd Service Configuration

#### Application Service

```bash
# Create service file
sudo nano /etc/systemd/system/digital-human.service
```

```ini
[Unit]
Description=Digital Human Restaurant Assistant
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=notify
User=digitaluser
Group=digitaluser
WorkingDirectory=/opt/digital-human/app
Environment="PATH=/opt/digital-human/venv/bin"
EnvironmentFile=/opt/digital-human/.env

ExecStart=/opt/digital-human/venv/bin/gunicorn \
  --bind 0.0.0.0:8010 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 120 \
  --graceful-timeout 30 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --access-logfile /var/log/digital-human/access.log \
  --error-logfile /var/log/digital-human/error.log \
  app:app

Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/digital-human/data /opt/digital-human/logs

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/digital-human
sudo chown digitaluser:digitaluser /var/log/digital-human

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable digital-human
sudo systemctl start digital-human

# Check status
sudo systemctl status digital-human
```

#### vLLM Service

```bash
# Create vLLM service
sudo nano /etc/systemd/system/vllm.service
```

```ini
[Unit]
Description=vLLM Inference Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=digitaluser
Group=digitaluser
WorkingDirectory=/opt/digital-human

ExecStart=/opt/digital-human/venv/bin/python -m vllm.entrypoints.openai.api_server \
  --model /opt/digital-human/models/qwen2.5-7b-instruct \
  --dtype float16 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9 \
  --host 127.0.0.1 \
  --port 8000

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start vLLM
sudo systemctl enable vllm
sudo systemctl start vllm
sudo systemctl status vllm
```

### NGINX Configuration

```bash
# Create NGINX config
sudo nano /etc/nginx/sites-available/digital-human
```

```nginx
# HTTP redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max upload size
    client_max_body_size 50M;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # WebSocket endpoint
    location /ws {
        proxy_pass http://127.0.0.1:8010;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # WebSocket specific timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # Static files
    location /static {
        alias /opt/digital-human/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/digital-human /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Production Environment Variables

```bash
# /opt/digital-human/.env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Application
APP_NAME=Digital-Human-Restaurant
HOST=0.0.0.0
PORT=8010
MAX_SESSIONS=10
WORKERS=4

# Security
SECRET_KEY=GENERATE_STRONG_SECRET_KEY_HERE
API_KEY=GENERATE_API_KEY_HERE
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=digital_human_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=STRONG_REDIS_PASSWORD

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Models
MODEL_PATH=/opt/digital-human/models
VLLM_MODEL=/opt/digital-human/models/qwen2.5-7b-instruct
WHISPER_MODEL=large-v3

# vLLM Configuration
VLLM_API_URL=http://localhost:8000/v1
VLLM_GPU_MEMORY=0.9

# Restaurant Configuration
RESTAURANT_NAME=Your Restaurant Name
RESTAURANT_TIMEZONE=Asia/Ho_Chi_Minh
RESTAURANT_LANGUAGE=vi
```

## Docker Deployment

### Docker Compose Production

```bash
# Navigate to project
cd /opt/digital-human/app

# Copy production compose file
cp docker-compose.prod.yml docker-compose.yml

# Configure environment
cp .env.production .env
nano .env

# Build and start
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f digital-human
```

#### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  # Main application
  digital-human:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: digital-human
    restart: unless-stopped
    ports:
      - "8010:8010"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
      - CUDA_VISIBLE_DEVICES=0
    env_file:
      - .env
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    depends_on:
      - postgres
      - redis
      - qdrant
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8010/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: digital-human-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: digital-human-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Qdrant
  qdrant:
    image: qdrant/qdrant:latest
    container_name: digital-human-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  # NGINX (optional)
  nginx:
    image: nginx:alpine
    container_name: digital-human-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - certbot_data:/var/www/certbot:ro
    depends_on:
      - digital-human

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  certbot_data:

networks:
  default:
    name: digital-human-network
```

### Kubernetes Deployment (Advanced)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-human
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: digital-human
  template:
    metadata:
      labels:
        app: digital-human
    spec:
      containers:
      - name: digital-human
        image: your-registry.com/digital-human:latest
        ports:
        - containerPort: 8010
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: 1
        env:
        - name: ENVIRONMENT
          value: "production"
        envFrom:
        - secretRef:
            name: digital-human-secrets
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        - name: data
          mountPath: /app/data
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
      - name: data
        persistentVolumeClaim:
          claimName: data-pvc
```

## Monitoring & Maintenance

### Monitoring Setup

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'digital-human'
    static_configs:
      - targets: ['localhost:8010']
    metrics_path: '/metrics'
```

#### Grafana Dashboard

```bash
# Install Grafana
sudo apt-get install -y grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Access: http://localhost:3000
# Default: admin/admin
```

### Health Checks

```bash
# Application health
curl http://localhost:8010/health

# Database connectivity
psql -h localhost -U prod_user -d digital_human_prod -c "SELECT 1"

# Redis connectivity
redis-cli -a YOUR_REDIS_PASSWORD ping

# GPU status
nvidia-smi

# Service status
sudo systemctl status digital-human vllm postgres redis-server
```

### Backup Strategy

```bash
# Database backup script
#!/bin/bash
# /opt/digital-human/scripts/backup_db.sh

BACKUP_DIR="/opt/digital-human/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Create backup
pg_dump -h localhost -U prod_user digital_human_prod | gzip > $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

```bash
# Add to crontab
crontab -e
# Daily backup at 2 AM
0 2 * * * /opt/digital-human/scripts/backup_db.sh
```

### Log Rotation

```bash
# /etc/logrotate.d/digital-human
/var/log/digital-human/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 digitaluser digitaluser
    sharedscripts
    postrotate
        systemctl reload digital-human > /dev/null 2>&1 || true
    endscript
}
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check logs
sudo journalctl -u digital-human -n 50 --no-pager
sudo tail -f /var/log/digital-human/error.log

# Check configuration
/opt/digital-human/venv/bin/python app.py --check-config

# Test database connection
/opt/digital-human/venv/bin/python -c "from src.db import test_connection; test_connection()"
```

#### 2. High Memory Usage

```bash
# Check memory
free -h
ps aux --sort=-%mem | head

# Reduce batch size in config
# Edit /opt/digital-human/.env
# BATCH_SIZE=4  # Reduce from 8

# Restart service
sudo systemctl restart digital-human
```

#### 3. Slow Response Times

```bash
# Check GPU utilization
nvidia-smi

# Check service performance
curl http://localhost:8010/metrics | grep latency

# Check database queries
# Enable query logging in PostgreSQL
```

### Recovery Procedures

#### Database Recovery

```bash
# Restore from backup
gunzip < /opt/digital-human/backups/db_backup_20250101_020000.sql.gz | \
  psql -h localhost -U prod_user digital_human_prod
```

#### Service Recovery

```bash
# Emergency restart
sudo systemctl restart digital-human vllm

# If corrupted, redeploy
cd /opt/digital-human/app
git pull origin main
/opt/digital-human/venv/bin/pip install -r requirements.txt
sudo systemctl restart digital-human
```

## Performance Tuning

### GPU Optimization

```bash
# Set GPU clock speed
sudo nvidia-smi -pm 1
sudo nvidia-smi -ac 5001,1590

# Monitor GPU
watch -n 1 nvidia-smi
```

### Application Tuning

```bash
# Adjust worker count (in service file)
# workers = (2 × CPU cores) + 1

# Adjust model memory
# VLLM_GPU_MEMORY=0.95  # Use more GPU

# Enable caching
# ENABLE_MODEL_CACHE=true
```

## Next Steps

1. ✅ Complete deployment
2. 📊 Set up monitoring
3. 🔐 Security hardening
4. 📖 Train operations team
5. 🧪 Load testing
6. 📝 Update documentation

## References

- [Environment Setup](./environment-setup.md)
- [Development Guide](./development.md)
- [Architecture](./architecture.md)
- [API Reference](./api-reference.md)
- [Docker Documentation](../DOCKER.md)

