# Installation Guide

Complete guide to setting up OpenGlaze.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Installation](#docker-installation)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [Post-Installation](#post-installation)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Docker Installation

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### Manual Installation

- Python 3.10+
- PostgreSQL 14+ (or SQLite for development)

## Docker Installation

### Quick Start

```bash
# Clone repository
git clone https://github.com/openglaze/openglaze.git
cd openglaze

# Run setup script
./scripts/setup.sh

# Or manually:
cp .env.example .env
docker-compose up -d
```

### Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| OpenGlaze | http://localhost:8768 | Main application |
| Kratos Public | http://localhost:4433 | Authentication |
| Kratos Admin | http://localhost:4434 | User management |
| Mailhog | http://localhost:8025 | Email testing (dev) |

### Production Checklist

- [ ] Change all default passwords in `.env`
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper email SMTP
- [ ] Set up SSL/TLS (use nginx profile)
- [ ] Configure payment providers
- [ ] Set up backups

## Manual Installation

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Database Setup

**SQLite (Development):**
```bash
# Database will be created automatically
python server.py
```

**PostgreSQL (Production):**
```bash
# Create database
createdb openglaze

# Set DATABASE_URL
export DATABASE_URL=postgres://user:password@localhost:5432/openglaze

# Initialize schema
python -c "import server; server.init_db()"
```

### 3. Kratos Setup

```bash
# Install Kratos (macOS)
brew install ory/tap/kratos

# Or download binary
curl https://github.com/ory/kratos/releases/download/v1.0.0/kratos_1.0.0_linux_amd64.tar.gz | tar -xz

# Run migrations
kratos migrate -c kratos/config.yml sql -e --yes

# Start Kratos
kratos serve -c kratos/config.yml
```

### 4. Start Application

```bash
# Development
python server.py

# Production
gunicorn -w 4 -b 0.0.0.0:8768 server:app
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BASE_URL` | Yes | http://localhost:8768 | Public URL of your instance |
| `DATABASE_URL` | Yes | sqlite:///openglaze.db | Database connection string |
| `KRATOS_PUBLIC_URL` | Yes | http://localhost:4433 | Kratos public API |
| `KRATOS_ADMIN_URL` | Yes | http://localhost:4434 | Kratos admin API |
| `KRATOS_HOOK_KEY` | Yes | - | Secret for Kratos webhooks |
| `STRIPE_API_KEY` | No | - | Stripe API key |
| `STRIPE_WEBHOOK_SECRET` | No | - | Stripe webhook secret |

### Payment Provider Setup

**Stripe:**
1. Create account at stripe.com
2. Get API keys from Dashboard > Developers > API keys
3. Create products and prices
4. Add price IDs to `.env`
5. Set up webhook endpoint

**PayPal:**
1. Create developer account at developer.paypal.com
2. Create REST API app
3. Get Client ID and Secret
4. Configure webhook

**BTCPay Server:**
1. Set up BTCPay Server instance
2. Create store and API key
3. Configure webhook

## Post-Installation

### Create Admin User

```bash
# Via Kratos CLI
kratos identity create -c kratos/config.yml \
  --schema-id default \
  --trait email:admin@example.com \
  --trait tier:studio
```

### Apply Template

```bash
curl -X POST http://localhost:8768/api/templates/cone10-reduction-community/apply \
  -H "Cookie: ory_kratos_session=YOUR_SESSION"
```

### Set Up Backups

```bash
# Add to crontab
0 2 * * * /path/to/openglaze/scripts/backup.sh
```

## Troubleshooting

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U openglaze -d openglaze
```

### Kratos Issues

```bash
# Check Kratos logs
docker-compose logs kratos

# Verify configuration
docker-compose exec kratos cat /etc/config/kratos/config.yml

# Reset Kratos database (WARNING: deletes all users)
docker-compose exec kratos kratos migrate -c /etc/config/kratos/config.yml sql -e --yes
```

### Payment Webhooks Not Working

1. Verify webhook URL is publicly accessible
2. Check webhook secret in `.env`
3. Verify Stripe/PayPal dashboard shows webhook deliveries
4. Check application logs: `docker-compose logs openglaze`

### Email Not Sending

1. For development, use Mailhog profile:
   ```bash
   docker-compose --profile dev up -d
   ```
2. For production, configure SMTP in `kratos/config.yml`

---

Need help? [Open an issue](https://github.com/openglaze/openglaze/issues) or join our [Discord](https://discord.gg/openglaze).
