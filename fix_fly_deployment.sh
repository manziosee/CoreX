#!/bin/bash
set -e

echo "🔧 Fixing Fly.io Deployment Issues"
echo "=================================="

# Install flyctl if not present
if ! command -v flyctl &> /dev/null; then
    echo "📦 Installing flyctl..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io:"
    flyctl auth login
fi

# Stop the current machine
echo "🛑 Stopping current machine..."
flyctl machine stop -a corex-banking || true

# Remove the problematic machine
echo "🗑️ Removing problematic machine..."
flyctl machine destroy -a corex-banking --force || true

# Deploy fresh
echo "🚀 Deploying fresh instance..."
flyctl deploy --dockerfile Dockerfile.fly -a corex-banking

# Check status
echo "📊 Checking deployment status..."
flyctl status -a corex-banking

echo "✅ Deployment fix complete!"
echo "🌐 Check: https://corex-banking.fly.dev/health"