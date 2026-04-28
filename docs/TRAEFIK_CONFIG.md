# Traefik Configuration Guide

## Overview
Traefik v3.6 configured as reverse proxy and API gateway for NotebookUM with:
- HTTP/HTTPS routing with automatic certificate management
- Circuit breaker middleware for resilience
- Rate limiting for API protection
- TCP passthrough for PostgreSQL
- Health checks and monitoring

## Entry Points

### HTTP/HTTPS (Ports 80/443)
- Redirects HTTP to HTTPS
- TLS certificate management with Let's Encrypt
- SNI routing for multiple domains

### PostgreSQL TCP (Port 5432)
- Direct TCP passthrough to PostgreSQL container
- Enables external connections from app instances
- No authentication at Traefik level (PostgreSQL handles auth)

## Middleware Configuration

### Circuit Breaker (`circuit-breaker`)
```yaml
expression: "NetworkErrorRatio() > 0.5 || (ResponseCodeRatio(500, 502, 503) > 0.3)"
```
- Opens if 50% of requests have network errors OR 30% return 5xx
- Check period: 2 seconds
- Fallback duration: 30 seconds
- Integrates with upstream circuit breaker service

### Rate Limiting (`rate-limit`)
```yaml
average: 100 requests/second per IP
burst: 50 additional requests
```
- Source IP detected with depth=1 (direct client)
- Prevents API abuse
- Applies to all NotebookUM HTTPS routes

### Request Tracing (`request-tracing`)
- Adds headers to all requests:
  - `X-Service: NotebookUM-API`
  - `X-Environment: production`
- Enables request tracking in logs and monitoring

### Compression (`compression`)
- Compresses responses >1KB with gzip
- Reduces bandwidth usage
- Transparent to clients

## Routers

### NotebookUM API
- **Hosts**: `notebookum.universidad.localhost`
- **Services**: FastAPI backend on `notebookum:8000`
- **HTTP**: Redirects to HTTPS
- **HTTPS**: 
  - Applies: rate-limit, circuit-breaker, request-tracing, compression
  - Timeouts: 10s connect, 30s request, 60s idle
  - Health check: `/health` every 30s

### PostgreSQL TCP
- **Entry Point**: `postgresql` (port 5432)
- **Service**: `postgres:5432`
- **Type**: TCP (raw socket)
- **Usage**: Direct database connections for migrations, backups, etc.

## Health Checks

NotebookUM service includes health checks:
```yaml
path: /health
interval: 30s
timeout: 5s
```

If `/health` endpoint returns non-200 for 30s, service marked as down.

## TLS Configuration

### Certificates
- Located in `./certs/` (self-signed for development)
- Production: Replace with Let's Encrypt or purchased certs
- Domains:
  - `universidad.localhost` (main)
  - `*.universidad.localhost` (wildcard)
  - `universidad.local` (alternative)
  - `*.universidad.local` (alternative wildcard)

### Self-Signed Certificate Generation
```bash
cd dockers/traefik/certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365 \
  -subj "/CN=*.universidad.localhost"
```

## Monitoring & Dashboard

### Traefik Dashboard
- **URL**: `http://localhost:8080`
- **Features**:
  - Live router/service status
  - Request metrics
  - Middleware status
  - Circuit breaker state

### Metrics to Monitor
- Circuit breaker: response rate, network errors
- Rate limiter: rejected requests per second
- Response times: histogram by route
- Health check status: services up/down

## Common Tasks

### Add New Route
```yaml
http:
  routers:
    new-service:
      rule: "Host(`new.universidad.localhost`)"
      service: "new-service"
      entryPoints:
        - https
      middlewares:
        - rate-limit
        - circuit-breaker
```

### Disable Rate Limiting for Admin
```yaml
routers:
  admin-service:
    rule: "Host(`admin.universidad.localhost`)"
    # omit rate-limit middleware
```

### Check Traefik Logs
```bash
docker logs traefik
```

## Production Checklist

- [ ] Replace self-signed certs with production certificates
- [ ] Enable ACME for automatic certificate renewal
- [ ] Set `dashboard: false` in traefik.yml
- [ ] Increase circuit breaker fallback_duration based on recovery time
- [ ] Adjust rate-limit based on expected traffic
- [ ] Configure log rotation for Docker volumes
- [ ] Enable persistent health checks (increase timeout)
- [ ] Test circuit breaker activation with load testing
- [ ] Verify PostgreSQL TCP connections work from remote clients
- [ ] Set up monitoring/alerting for circuit breaker state

## Troubleshooting

### Traefik won't start
- Check YAML syntax: `yamllint config.yml`
- Verify certificate files exist: `ls -la certs/`
- Check Docker socket permissions: `ls -l /var/run/docker.sock`

### Routes not responding
- Check rule syntax in dashboard at localhost:8080
- Verify backend service is running: `docker ps`
- Check health check status in dashboard

### Circuit breaker always open
- Review upstream error rates
- Check network connectivity to backend
- Verify backend service health: `curl http://notebookum:8000/health`

### Rate limiting blocking legitimate traffic
- Increase `average` value in rate-limit middleware
- Check for DDoS attacks in logs
- Whitelist specific IPs if needed (requires custom middleware)
