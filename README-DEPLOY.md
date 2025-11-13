# Fly.io Deployment Guide

## Prerequisites

1. Install Fly.io CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Create Fly.io account:
```bash
flyctl auth signup
```

## Quick Deploy

Run the automated deployment script:
```bash
./deploy.sh
```

## Manual Deployment

1. **Login to Fly.io:**
```bash
flyctl auth login
```

2. **Initialize Fly app:**
```bash
flyctl launch --no-deploy
```

3. **Create PostgreSQL database:**
```bash
flyctl postgres create --name corex-db --region iad
flyctl postgres attach --app corex-banking corex-db
```

4. **Set secrets:**
```bash
flyctl secrets set JWT_SECRET=$(openssl rand -base64 32)
flyctl secrets set ENVIRONMENT=production
```

5. **Deploy:**
```bash
flyctl deploy --dockerfile Dockerfile.fly
```

## Access Your App

- **API**: https://corex-banking.fly.dev
- **Docs**: https://corex-banking.fly.dev/docs
- **Health**: https://corex-banking.fly.dev/health

## Useful Commands

```bash
# View logs
flyctl logs

# Scale app
flyctl scale count 2

# SSH into app
flyctl ssh console

# View app status
flyctl status
```