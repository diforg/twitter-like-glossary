#!/bin/bash
# Development helper script for Twitter Likes Archive

set -e

case "${1:-help}" in
  up)
    echo "🚀 Starting the application..."
    docker-compose up -d
    echo "✅ Application started at http://localhost:5000"
    ;;
  down)
    echo "🛑 Stopping the application..."
    docker-compose down
    echo "✅ Application stopped"
    ;;
  logs)
    echo "📋 Showing application logs..."
    docker-compose logs -f app
    ;;
  build)
    echo "🔨 Building the Docker image..."
    docker-compose build
    echo "✅ Build complete"
    ;;
  restart)
    echo "🔄 Restarting the application..."
    docker-compose restart app
    echo "✅ Application restarted"
    ;;
  clean)
    echo "🧹 Cleaning up..."
    docker-compose down -v
    rm -f data/likes_data.json
    echo "✅ Cleaned up all data and containers"
    ;;
  shell)
    echo "🐚 Opening shell in app container..."
    docker-compose exec app /bin/bash
    ;;
  pip-install)
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
    ;;
  local)
    echo "🏃 Running locally (requires Python 3.11+)..."
    source venv/bin/activate 2>/dev/null || python3.11 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python run.py
    ;;
  *)
    echo "Twitter Likes Archive - Development Helper"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  up          - Start the application with Docker Compose"
    echo "  down        - Stop the application"
    echo "  logs        - Show application logs"
    echo "  build       - Build the Docker image"
    echo "  restart     - Restart the application"
    echo "  clean       - Remove all containers, volumes, and data"
    echo "  shell       - Open a bash shell in the app container"
    echo "  pip-install - Install Python dependencies locally"
    echo "  local       - Run the app locally (without Docker)"
    echo "  help        - Show this help message"
    echo ""
    ;;
esac
