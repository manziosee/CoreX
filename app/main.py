from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import customers, accounts, transactions, auth
from app.core.config import settings
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CoreX Banking System",
    description="Modern core banking engine for digital banks, microfinance institutions, and fintech startups",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and JWT token management"},
        {"name": "Customers", "description": "Customer registration and KYC management"},
        {"name": "Accounts", "description": "Bank account creation and balance management"},
        {"name": "Transactions", "description": "Transaction processing with double-entry accounting"}
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
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])

@app.get("/")
async def root():
    return {"message": "CoreX Banking System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "corex-api"}