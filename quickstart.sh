#!/bin/bash
# Quickstart script for Networking Demo Platform

set -e

echo "================================================================"
echo "  Networking Demo Platform - Quickstart"
echo "================================================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker found"

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✓ Docker Compose found"

# Check Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker first."
    exit 1
fi
echo "✓ Docker daemon is running"

echo ""
echo "Prerequisites check passed!"
echo ""

# Build and start services
echo "Building and starting services..."
echo "This may take a few minutes on first run..."
echo ""

docker-compose up --build -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check Redis
if docker-compose ps redis | grep -q "Up"; then
    echo "✓ Redis is running"
else
    echo "⚠️  Redis may not be ready yet"
fi

# Check API
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✓ API is running"
else
    echo "⚠️  API may not be ready yet"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ Frontend is running"
else
    echo "⚠️  Frontend may not be ready yet"
fi

echo ""
echo "================================================================"
echo "  🎉 Platform is starting up!"
echo "================================================================"
echo ""
echo "Access the platform:"
echo "  • Frontend:        http://localhost:3000"
echo "  • API Docs:        http://localhost:8000/api/docs"
echo "  • Health Check:    http://localhost:8000/api/health"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
echo "For detailed instructions, see README-PRODUCTION.md"
echo ""
