# 🔐 Authentication System Documentation

## Overview

CoreX Banking System implements a comprehensive authentication and authorization system using JWT tokens, role-based access control (RBAC), and security best practices.

## 🏗️ Architecture

### Components

1. **JWT Authentication**: Stateless token-based authentication
2. **Role-Based Access Control**: Four user roles with different permissions
3. **Password Security**: Bcrypt hashing with configurable complexity
4. **Rate Limiting**: API abuse prevention
5. **Audit Logging**: Complete request tracking for compliance
6. **Token Blacklisting**: Secure logout functionality

## 👥 User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **ADMIN** | System administrator | Full system access, user management |
| **TELLER** | Bank teller | Customer operations, transactions |
| **AUDITOR** | Compliance auditor | Read-only access to all data |
| **API_USER** | External API access | Limited programmatic access |

## 🔑 Authentication Endpoints

### Login
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Register User (Admin Only)
```http
POST /auth/register
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "role": "TELLER"
}
```

### Get Current User Profile
```http
GET /auth/me
Authorization: Bearer <token>
```

### Change Password
```http
PUT /auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "oldpass123",
  "new_password": "newpass123"
}
```

### Reset Password (Admin Only)
```http
POST /auth/reset-password
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "username": "targetuser",
  "new_password": "newpass123"
}
```

### List Users (Admin Only)
```http
GET /auth/users?skip=0&limit=100
Authorization: Bearer <admin-token>
```

### Update User Status (Admin Only)
```http
PUT /auth/users/{username}/status
Authorization: Bearer <admin-token>
Content-Type: application/json

"ACTIVE" | "INACTIVE" | "SUSPENDED"
```

### Logout
```http
DELETE /auth/logout
Authorization: Bearer <token>
```

## 🛡️ Security Features

### Password Requirements
- Minimum 8 characters
- Bcrypt hashing with salt
- Password change validation

### JWT Token Security
- Configurable expiration (default: 30 minutes)
- HS256 algorithm
- Token blacklisting on logout
- Role information embedded in token

### Rate Limiting
- 60 requests per minute per IP (configurable)
- Redis-based distributed limiting
- Fallback to in-memory storage

### Account Security
- Maximum login attempts tracking
- Account lockout after failed attempts
- Status-based access control

## 🔒 Role-Based Access Control

### Usage in Endpoints

```python
from app.core.auth import require_role, require_admin
from app.models.user import UserRole

# Require specific roles
@router.get("/admin-only")
async def admin_endpoint(user: User = Depends(require_admin)):
    pass

# Require multiple roles
@router.get("/teller-or-admin")
async def teller_endpoint(user: User = Depends(require_role([UserRole.ADMIN, UserRole.TELLER]))):
    pass
```

### Permission Matrix

| Endpoint | ADMIN | TELLER | AUDITOR | API_USER |
|----------|-------|--------|---------|----------|
| User Management | ✅ | ❌ | ❌ | ❌ |
| Customer Operations | ✅ | ✅ | 👁️ | ✅ |
| Transactions | ✅ | ✅ | 👁️ | ✅ |
| KYC Management | ✅ | ✅ | 👁️ | ❌ |
| Audit Logs | ✅ | ❌ | ✅ | ❌ |

*👁️ = Read-only access*

## 📊 Audit Logging

All API requests are automatically logged with:

- User ID and role
- Action type (CREATE, READ, UPDATE, DELETE, LOGIN)
- Resource type and ID
- Request details (method, path, parameters)
- Response status
- Timestamp and IP address

### Audit Log Schema
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "action_type": "CREATE|READ|UPDATE|DELETE|LOGIN|OTHER",
  "resource_type": "CUSTOMERS|ACCOUNTS|TRANSACTIONS",
  "resource_id": "string",
  "details": {
    "method": "POST",
    "path": "/customers",
    "status_code": 201,
    "ip_address": "192.168.1.1"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🚀 Setup and Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration (for rate limiting and token blacklist)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379

# Rate Limiting
RATE_LIMIT_RPM=60

# Security Settings
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=30
```

### Initialize Admin User

```bash
# Create default admin user
python create_admin.py
```

**Default Credentials:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@corex-banking.com`
- Role: `ADMIN`

## 🧪 Testing

### Authentication Tests

```bash
# Run authentication tests
pytest tests/test_auth.py -v

# Test specific scenarios
pytest tests/test_auth.py::test_login_success -v
pytest tests/test_auth.py::test_role_based_access -v
```

### Manual Testing with cURL

```bash
# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/auth/me"
```

## 🔧 Middleware Integration

### Rate Limiting Middleware
```python
from app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

### Audit Middleware
```python
from app.middleware.audit import AuditMiddleware

app.add_middleware(AuditMiddleware)
```

## 📈 Monitoring and Metrics

### Key Metrics to Monitor

1. **Authentication Metrics**
   - Login success/failure rates
   - Token expiration patterns
   - Failed authentication attempts

2. **Security Metrics**
   - Rate limit violations
   - Suspicious login patterns
   - Account lockouts

3. **Performance Metrics**
   - Authentication response times
   - Token validation performance
   - Redis connection health

## 🚨 Security Best Practices

### Production Deployment

1. **Change Default Credentials**
   ```bash
   # Update admin password immediately
   curl -X PUT "https://your-api.com/auth/change-password" \
     -H "Authorization: Bearer $ADMIN_TOKEN" \
     -d '{"current_password":"admin123","new_password":"secure-production-password"}'
   ```

2. **Environment Security**
   - Use strong JWT secrets (32+ characters)
   - Enable HTTPS in production
   - Configure proper CORS policies
   - Use environment-specific Redis instances

3. **Monitoring and Alerting**
   - Monitor failed login attempts
   - Alert on suspicious patterns
   - Track token usage patterns
   - Monitor rate limit violations

### Common Security Headers

```python
# Add security headers
app.add_middleware(
    SecurityHeadersMiddleware,
    headers={
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block"
    }
)
```

## 🔄 Token Lifecycle

1. **Token Creation**: User login generates JWT with user info and role
2. **Token Usage**: Each API request validates token and extracts user context
3. **Token Refresh**: Tokens expire after configured time (default: 30 minutes)
4. **Token Blacklist**: Logout adds token to blacklist until expiration
5. **Token Cleanup**: Expired tokens automatically removed from blacklist

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

All authentication endpoints include detailed examples and schema documentation.