# CoreX Banking System

A modern, modular core banking engine for digital banks, microfinance institutions, and fintech startups.

## Features

- **Customer Management**: Register and manage customer profiles with KYC
- **Account Management**: Support for savings, current, and loan accounts
- **Double-Entry Accounting**: Ensures all transactions are balanced
- **Transaction Processing**: Deposits, withdrawals, and transfers
- **Audit Trail**: Complete immutable transaction history
- **Multi-Currency Support**: Handle multiple currencies safely
- **Role-Based Access**: Admin, Teller, Auditor, and API user roles
- **Security**: OAuth2 + JWT authentication

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Setup with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd CoreX
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker-compose up -d
```

4. The API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/admin123)
- RabbitMQ Management: http://localhost:15672 (guest/guest)
- Metabase: http://localhost:3001

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start PostgreSQL, Redis, and RabbitMQ:
```bash
docker-compose up -d postgres redis rabbitmq
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

### Testing

Run tests with pytest:
```bash
pytest
```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Authentication

1. Get access token:
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

2. Use token in subsequent requests:
```bash
curl -H "Authorization: Bearer <your-token>" \
  "http://localhost:8000/customers/"
```

## Architecture

- **API Layer**: FastAPI with automatic OpenAPI documentation
- **Service Layer**: Business logic and validation
- **Data Layer**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for fast balance lookups
- **Queue**: RabbitMQ for async processing
- **Monitoring**: Grafana + Loki for observability
- **Reporting**: Metabase for business intelligence

## Database Schema

Key tables:
- `customers`: Customer information and KYC status
- `accounts`: Bank accounts linked to customers
- `balances`: Cached account balances
- `transactions`: Transaction records
- `entries`: Double-entry journal entries
- `audit_logs`: Complete audit trail

## Deployment

### Fly.io Deployment

Deploy to Fly.io with one command:
```bash
./deploy.sh
```

See [README-DEPLOY.md](README-DEPLOY.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request