from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api import customers, accounts, transactions, auth, kyc
from app.core.config import settings
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CoreX Banking System",
    description="""# 🏦 CoreX Banking System API
    
**Modern, modular core banking engine for digital banks, microfinance institutions, and fintech startups**

## 🚀 Features
- **JWT Authentication** with role-based access control
- **Customer Management** with KYC compliance
- **Account Management** with multi-currency support
- **Transaction Processing** with double-entry accounting
- **Document Management** for KYC verification
- **Audit Logging** for compliance and security

## 🔐 Authentication
1. **Login** with username/password to get JWT token
2. **Use Bearer token** in Authorization header for protected endpoints
3. **Role-based access**: ADMIN, TELLER, AUDITOR, API_USER

## 📚 Getting Started
1. Use the **Login** endpoint with default credentials: `admin` / `admin123`
2. Copy the `access_token` from the response
3. Click **Authorize** button and enter: `Bearer <your-token>`
4. Now you can access all protected endpoints

## 🔗 Links
- **Live Demo**: [https://corex-banking.fly.dev](https://corex-banking.fly.dev)
- **GitHub**: [https://github.com/manziosee/CoreX](https://github.com/manziosee/CoreX)
- **Documentation**: [Database Schema](https://github.com/manziosee/CoreX/blob/main/docs/DATABASE.md)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication", 
            "description": "🔐 User authentication, JWT token management, and role-based access control"
        },
        {
            "name": "Customers", 
            "description": "👥 Customer registration, onboarding, and profile management"
        },
        {
            "name": "KYC", 
            "description": "📋 Know Your Customer document upload, verification, and compliance tracking"
        },
        {
            "name": "Accounts", 
            "description": "💳 Bank account creation, balance management, and multi-currency support"
        },
        {
            "name": "Transactions", 
            "description": "💸 Transaction processing with double-entry accounting and audit trails"
        }
    ],
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://corex-banking.fly.dev",
            "description": "Production server on Fly.io"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(kyc.router, prefix="/kyc", tags=["KYC"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])

# Custom OpenAPI schema with security
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token obtained from /auth/token endpoint"
        }
    }
    
    # Add security to protected endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if path != "/auth/token" and path != "/health" and path != "/":
                openapi_schema["paths"][path][method]["security"] = [
                    {"BearerAuth": []}
                ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
async def root():
    return {"message": "CoreX Banking System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "corex-api"}