#!/bin/bash

# CoreX Banking System - Fly.io Deployment Script

echo "🚀 Deploying CoreX Banking System to Fly.io..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Login to Fly.io (if not already logged in)
echo "🔐 Checking Fly.io authentication..."
flyctl auth whoami || flyctl auth login

# Create PostgreSQL database
echo "🗄️ Creating PostgreSQL database..."
flyctl postgres create --name corex-db --region iad --vm-size shared-cpu-1x --volume-size 10

# Get database connection string
echo "📝 Getting database connection string..."
flyctl postgres attach --app corex-banking corex-db

# Set environment variables
echo "⚙️ Setting environment variables..."
flyctl secrets set \
  JWT_SECRET=$(openssl rand -base64 32) \
  ENVIRONMENT=production

# Deploy the application
echo "🚀 Deploying application..."
flyctl deploy --dockerfile Dockerfile.fly

echo "✅ Deployment complete!"
echo "🌐 Your CoreX Banking System is available at: https://corex-banking.fly.dev"
echo "📚 API Documentation: https://corex-banking.fly.dev/docs"