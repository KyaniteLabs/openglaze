#!/bin/bash
# OpenGlaze Setup Script
# Initializes a new OpenGlaze installation

set -e

echo "================================================"
echo "  OpenGlaze Setup"
echo "================================================"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required but not installed."
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is required but not installed."
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env with your configuration before continuing:"
    echo "  - Set KRATOS_HOOK_KEY to a secure random string"
    echo "  - Adjust BASE_URL for your domain"
    echo ""
    read -p "Press Enter after configuring .env to continue..."
fi

# Load environment
set -a
source .env
set +a

echo ""
echo "Configuration:"
echo "  BASE_URL: ${BASE_URL:-http://localhost:8768}"
echo "  DATABASE: ${DATABASE_URL:-sqlite}"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p static/css static/js
mkdir -p templates
mkdir -p backups

# Generate Kratos hook key if not set
if [ -z "$KRATOS_HOOK_KEY" ] || [ "$KRATOS_HOOK_KEY" = "your-secret-key-here" ]; then
    KRATOS_HOOK_KEY=$(openssl rand -hex 32)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/KRATOS_HOOK_KEY=.*/KRATOS_HOOK_KEY=$KRATOS_HOOK_KEY/" .env
    else
        sed -i "s/KRATOS_HOOK_KEY=.*/KRATOS_HOOK_KEY=$KRATOS_HOOK_KEY/" .env
    fi
    echo "Generated KRATOS_HOOK_KEY"
fi

# Start services
echo ""
echo "Starting services..."
docker-compose up -d postgres

echo "Waiting for database..."
sleep 5

# Run Kratos migrations
echo "Running Kratos migrations..."
docker-compose up -d kratos-migrate
sleep 5

# Start all services
echo "Starting all services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Check health
echo ""
echo "Checking service health..."

if curl -s http://localhost:8768/health > /dev/null; then
    echo "  ✓ OpenGlaze is running"
else
    echo "  ✗ OpenGlaze is not responding"
fi

if curl -s http://localhost:4433/health/ready > /dev/null; then
    echo "  ✓ Kratos is running"
else
    echo "  ✗ Kratos is not responding"
fi

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Access OpenGlaze at: http://localhost:8768"
echo ""
echo "Kratos Admin: http://localhost:4434"
echo "Kratos Public: http://localhost:4433"
echo ""
if docker-compose ps | grep -q mailhog; then
    echo "Mailhog (email testing): http://localhost:8025"
fi
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo ""
