#!/bin/bash
set -e

echo "🚀 CoreX Banking System - Fly.io Deployment"
echo "============================================="

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io first:"
    flyctl auth login
fi

# Check if app exists
if ! flyctl apps list | grep -q "corex-banking"; then
    echo "📱 Creating new Fly.io app..."
    flyctl apps create corex-banking --org personal
fi

# Create volume if it doesn't exist
if ! flyctl volumes list -a corex-banking | grep -q "corex_data"; then
    echo "💾 Creating persistent volume..."
    flyctl volumes create corex_data --region iad --size 1 -a corex-banking
fi

# Set secrets
echo "🔐 Setting production secrets..."
flyctl secrets set \
    JWT_SECRET="$(openssl rand -base64 32)" \
    DATABASE_URL="sqlite:///app/data/corex.db" \
    ENVIRONMENT="production" \
    -a corex-banking

# Deploy the application
echo "🚀 Deploying to Fly.io..."
flyctl deploy --dockerfile Dockerfile.fly -a corex-banking

# Show deployment status
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your CoreX Banking System is now live at:"
echo "   https://corex-banking.fly.dev"
echo ""
echo "📚 API Documentation:"
echo "   https://corex-banking.fly.dev/docs"
echo ""
echo "🔍 Health Check:"
echo "   https://corex-banking.fly.dev/health"
echo ""
echo "📊 Monitor your app:"
echo "   flyctl logs -a corex-banking"
echo "   flyctl status -a corex-banking"
echo ""
echo "🔑 Default Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🎉 Happy Banking! 🏦"