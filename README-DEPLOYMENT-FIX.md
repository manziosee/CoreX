# 🚀 Fly.io Deployment Fix Guide

## 🔍 **Current Issue**
The Fly.io deployment is failing with SQLite database permission errors:
```
sqlite3.OperationalError: unable to open database file
```

## 🛠️ **Quick Fix Steps**

### **1. Install flyctl**
```bash
# Method 1: Official installer
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"

# Method 2: Direct download (if installer fails)
wget https://github.com/superfly/flyctl/releases/latest/download/flyctl_Linux_x86_64.tar.gz
tar -xzf flyctl_Linux_x86_64.tar.gz
sudo mv flyctl /usr/local/bin/
```

### **2. Login to Fly.io**
```bash
flyctl auth login
```

### **3. Fix the Deployment**
```bash
# Stop and destroy the problematic machine
flyctl machine stop -a corex-banking
flyctl machine destroy -a corex-banking --force

# Deploy fresh instance
flyctl deploy --dockerfile Dockerfile.fly -a corex-banking

# Check status
flyctl status -a corex-banking
flyctl logs -a corex-banking
```

### **4. Alternative: Use the Fix Script**
```bash
chmod +x fix_fly_deployment.sh
./fix_fly_deployment.sh
```

## 🔧 **What Was Fixed**

### **1. Dockerfile Improvements**
- Fixed directory permissions for SQLite database
- Ensured proper user ownership
- Added database file creation in startup

### **2. Startup Script Enhancements**
- Added SQLite file creation and permission setting
- Better error handling for database initialization
- Proper directory structure creation

### **3. Fly.io Configuration**
- Removed problematic volume mounts
- Using local storage for simplicity
- Enhanced health checks

## 📊 **Verify Deployment**

After deployment, check these endpoints:

```bash
# Health check
curl https://corex-banking.fly.dev/health

# API root
curl https://corex-banking.fly.dev/

# API documentation
open https://corex-banking.fly.dev/docs
```

## 🔑 **Test Authentication**

```bash
# Login with admin credentials
curl -X POST "https://corex-banking.fly.dev/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Use the returned token for API calls
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://corex-banking.fly.dev/auth/me"
```

## 🐛 **Troubleshooting**

### **If deployment still fails:**

1. **Check logs:**
   ```bash
   flyctl logs -a corex-banking
   ```

2. **SSH into machine:**
   ```bash
   flyctl ssh console -a corex-banking
   ```

3. **Manual database setup:**
   ```bash
   # Inside the machine
   mkdir -p /app/data
   touch /app/data/corex.db
   chmod 644 /app/data/corex.db
   ```

4. **Restart the app:**
   ```bash
   flyctl machine restart -a corex-banking
   ```

## 📈 **Monitoring**

- **Status**: `flyctl status -a corex-banking`
- **Logs**: `flyctl logs -a corex-banking -f`
- **Metrics**: `flyctl metrics -a corex-banking`

## 🎯 **Expected Result**

After successful deployment:
- ✅ https://corex-banking.fly.dev/health returns `{"status":"healthy"}`
- ✅ https://corex-banking.fly.dev/docs shows API documentation
- ✅ Authentication endpoints work properly
- ✅ Database operations function correctly