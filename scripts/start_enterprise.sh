#!/bin/bash

# Enterprise CRM Startup Script
# Starts all services with health checks and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🚀 Enterprise CRM - Startup Script                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env created. Please update with your values."
        print_warning "Edit .env file before continuing."
        exit 1
    else
        print_error ".env.example not found!"
        exit 1
    fi
fi

# Check if Docker is running
print_status "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi
print_success "Docker is running"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found!"
    exit 1
fi

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down > /dev/null 2>&1 || true
print_success "Existing containers stopped"

# Pull latest images
print_status "Pulling Docker images..."
docker-compose pull

# Build application image
print_status "Building application image..."
docker-compose build

# Start infrastructure services first (postgres, redis)
print_status "Starting infrastructure services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

# Wait for PostgreSQL
print_status "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U crm_user > /dev/null 2>&1; then
        print_success "PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL failed to start"
        docker-compose logs postgres
        exit 1
    fi
    echo -n "."
    sleep 1
done

# Wait for Redis
print_status "Waiting for Redis to be ready..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Redis failed to start"
        docker-compose logs redis
        exit 1
    fi
    echo -n "."
    sleep 1
done

# Run database migrations
print_status "Running database migrations..."
docker-compose run --rm app alembic upgrade head
print_success "Migrations completed"

# Start application services
print_status "Starting application services..."
docker-compose up -d app celery-worker celery-beat flower

# Wait for FastAPI app
print_status "Waiting for FastAPI application..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "FastAPI application is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        print_error "FastAPI application failed to start"
        docker-compose logs app
        exit 1
    fi
    echo -n "."
    sleep 2
done

# Start monitoring services
print_status "Starting monitoring services (Prometheus, Grafana)..."
docker-compose up -d prometheus grafana

print_success "All services started successfully!"

# Display service URLs
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              📡 Service URLs                               ║${NC}"
echo -e "${CYAN}╠════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC} FastAPI Application:  ${GREEN}http://localhost:8000${NC}              "
echo -e "${CYAN}║${NC} API Documentation:    ${GREEN}http://localhost:8000/docs${NC}         "
echo -e "${CYAN}║${NC} Health Check:         ${GREEN}http://localhost:8000/health${NC}       "
echo -e "${CYAN}║${NC} Metrics:              ${GREEN}http://localhost:8000/metrics${NC}      "
echo -e "${CYAN}║${NC}                                                             "
echo -e "${CYAN}║${NC} Celery Flower:        ${GREEN}http://localhost:5555${NC}              "
echo -e "${CYAN}║${NC} Prometheus:           ${GREEN}http://localhost:9091${NC}              "
echo -e "${CYAN}║${NC} Grafana:              ${GREEN}http://localhost:3000${NC}              "
echo -e "${CYAN}║${NC}   (default: admin/admin)                                    "
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Display useful commands
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              🛠️  Useful Commands                           ║${NC}"
echo -e "${CYAN}╠════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC} View logs:            ${YELLOW}docker-compose logs -f${NC}             "
echo -e "${CYAN}║${NC} Stop services:        ${YELLOW}docker-compose down${NC}                "
echo -e "${CYAN}║${NC} Restart service:      ${YELLOW}docker-compose restart app${NC}         "
echo -e "${CYAN}║${NC} Run migrations:       ${YELLOW}docker-compose run --rm app alembic upgrade head${NC}"
echo -e "${CYAN}║${NC} Create migration:     ${YELLOW}docker-compose run --rm app alembic revision --autogenerate -m \"msg\"${NC}"
echo -e "${CYAN}║${NC} Shell into app:       ${YELLOW}docker-compose exec app bash${NC}       "
echo -e "${CYAN}║${NC} PostgreSQL shell:     ${YELLOW}docker-compose exec postgres psql -U crm_user crm_db${NC}"
echo -e "${CYAN}║${NC} Redis CLI:            ${YELLOW}docker-compose exec redis redis-cli${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Run quick health check
print_status "Running quick health check..."
if command -v python3 &> /dev/null; then
    python3 scripts/quick_health_check.py || true
else
    print_warning "Python3 not found. Skipping health check."
fi

echo ""
print_success "Enterprise CRM is ready! 🎉"
echo ""
