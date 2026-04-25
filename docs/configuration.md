# Configuration Guide

Complete configuration reference for OpenGlaze.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BASE_URL` | Yes | `http://localhost:8768` | Public URL |
| `DATABASE_URL` | Yes | `sqlite:///openglaze.db` | Database connection |
| `KRATOS_PUBLIC_URL` | Yes | `http://kratos:4433` | Kratos public API |
| `KRATOS_ADMIN_URL` | Yes | `http://kratos:4434` | Kratos admin API |
| `KRATOS_HOOK_KEY` | Yes | - | Webhook secret |

## SSL/TLS Configuration

### Using nginx

```nginx
server {
    listen 443 ssl http2;
    server_name openglaze.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/openglaze.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/openglaze.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://openglaze:8768;
        proxy_set_header Host $host;
    }
}
```

Start: `docker-compose --profile prod up -d`

## Health Checks

```bash
# Application
curl http://localhost:8768/health

# Database
docker-compose exec postgres pg_isready

# Kratos
curl http://localhost:4433/health/ready
```

## Next Steps

- [Installation Guide](installation.md)
