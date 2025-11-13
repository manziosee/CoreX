# CoreX Banking System - Database Documentation

## Overview

The CoreX banking system uses PostgreSQL with a comprehensive schema designed for modern banking operations, KYC compliance, and double-entry accounting.

**Database**: `coreX-DB`  
**Connection**: `postgresql://postgres:2001@localhost:5432/coreX-DB`

## Database Schema

### 📊 Tables Overview

| Table | Purpose | Records |
|-------|---------|---------|
| `customers` | Customer profiles and KYC information | Customer data |
| `users` | Staff and admin accounts | System users |
| `accounts` | Bank accounts linked to customers | Account records |
| `kyc_documents` | Identity verification documents | KYC files |
| `balances` | Real-time account balances | Balance tracking |
| `transactions` | Transaction records | Transaction history |
| `entries` | Double-entry accounting records | Journal entries |
| `audit_logs` | Complete system audit trail | Audit records |

## 🔗 Entity Relationships

```
customers (1) ──────── (*) accounts
    │                      │
    │                      │
    │                      └── (1) balances
    │
    └── (*) kyc_documents
            │
            └── verified_by ──→ users

transactions (*) ──────── (*) entries
    │                         │
    │                         └──→ accounts
    │
    ├── from_account_id ──→ accounts
    └── to_account_id ────→ accounts

users (1) ──────── (*) audit_logs
```

## 📋 Table Definitions

### 1. customers
**Purpose**: Store customer information and KYC status

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `customer_number` | VARCHAR(20) | Unique customer identifier |
| `first_name` | VARCHAR(100) | Customer first name |
| `last_name` | VARCHAR(100) | Customer last name |
| `email` | VARCHAR(255) | Email address (unique) |
| `phone` | VARCHAR(20) | Phone number |
| `date_of_birth` | DATE | Date of birth |
| `address` | TEXT | Full address |
| `city` | VARCHAR(100) | City |
| `country` | VARCHAR(100) | Country |
| `occupation` | VARCHAR(100) | Occupation |
| `income_range` | VARCHAR(50) | Income range |
| `kyc_status` | ENUM | KYC verification status |
| `status` | ENUM | Customer account status |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

**Enums**:
- `kyc_status`: PENDING, APPROVED, REJECTED
- `status`: ACTIVE, INACTIVE, SUSPENDED

**Indexes**:
- `idx_customers_number` on `customer_number`

### 2. users
**Purpose**: System users (staff, admins, auditors)

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `username` | VARCHAR(50) | Unique username |
| `email` | VARCHAR(255) | Email address (unique) |
| `password_hash` | VARCHAR(255) | Hashed password |
| `role` | ENUM | User role |
| `status` | ENUM | User status |
| `created_at` | TIMESTAMP | Account creation time |

**Enums**:
- `role`: ADMIN, TELLER, AUDITOR, API_USER
- `status`: ACTIVE, INACTIVE, SUSPENDED

### 3. accounts
**Purpose**: Bank accounts owned by customers

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `account_number` | VARCHAR(20) | Unique account number |
| `customer_id` | UUID | Foreign key to customers |
| `account_type` | ENUM | Type of account |
| `currency` | VARCHAR(3) | Currency code (USD, EUR, etc.) |
| `status` | ENUM | Account status |
| `created_at` | TIMESTAMP | Account creation time |
| `updated_at` | TIMESTAMP | Last update time |

**Enums**:
- `account_type`: SAVINGS, CURRENT, LOAN
- `status`: ACTIVE, INACTIVE, SUSPENDED, CLOSED

**Relationships**:
- `customer_id` → `customers.id`

**Indexes**:
- `idx_accounts_number` on `account_number`

### 4. kyc_documents
**Purpose**: KYC document management and verification

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `customer_id` | UUID | Foreign key to customers |
| `document_type` | ENUM | Type of document |
| `document_number` | VARCHAR(100) | Document number/ID |
| `file_path` | VARCHAR(500) | Path to uploaded file |
| `status` | ENUM | Verification status |
| `verified_by` | UUID | Foreign key to users |
| `rejection_reason` | TEXT | Reason for rejection |
| `expires_at` | TIMESTAMP | Document expiry date |
| `created_at` | TIMESTAMP | Upload time |
| `updated_at` | TIMESTAMP | Last update time |

**Enums**:
- `document_type`: NATIONAL_ID, PASSPORT, DRIVERS_LICENSE, UTILITY_BILL, BANK_STATEMENT
- `status`: PENDING, APPROVED, REJECTED, EXPIRED

**Relationships**:
- `customer_id` → `customers.id`
- `verified_by` → `users.id`

**Indexes**:
- `idx_kyc_documents_customer` on `customer_id`
- `idx_kyc_documents_status` on `status`

### 5. balances
**Purpose**: Real-time account balance tracking

| Column | Type | Description |
|--------|------|-------------|
| `account_id` | UUID | Primary key, foreign key to accounts |
| `ledger_balance` | DECIMAL(15,2) | Actual balance |
| `available_balance` | DECIMAL(15,2) | Available for transactions |
| `updated_at` | TIMESTAMP | Last balance update |

**Relationships**:
- `account_id` → `accounts.id` (1:1)

### 6. transactions
**Purpose**: Transaction records for all banking operations

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `transaction_id` | VARCHAR(50) | Unique transaction identifier |
| `from_account_id` | UUID | Source account (nullable) |
| `to_account_id` | UUID | Destination account (nullable) |
| `amount` | DECIMAL(15,2) | Transaction amount |
| `currency` | VARCHAR(3) | Currency code |
| `transaction_type` | ENUM | Type of transaction |
| `description` | TEXT | Transaction description |
| `status` | ENUM | Processing status |
| `created_at` | TIMESTAMP | Transaction creation time |
| `processed_at` | TIMESTAMP | Processing completion time |

**Enums**:
- `transaction_type`: DEPOSIT, WITHDRAWAL, TRANSFER, FEE, INTEREST
- `status`: PENDING, COMPLETED, FAILED, CANCELLED

**Relationships**:
- `from_account_id` → `accounts.id`
- `to_account_id` → `accounts.id`

**Indexes**:
- `idx_transactions_id` on `transaction_id`

### 7. entries
**Purpose**: Double-entry accounting journal entries

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `transaction_id` | UUID | Foreign key to transactions |
| `account_id` | UUID | Foreign key to accounts |
| `entry_type` | ENUM | Debit or Credit |
| `amount` | DECIMAL(15,2) | Entry amount |
| `created_at` | TIMESTAMP | Entry creation time |

**Enums**:
- `entry_type`: DEBIT, CREDIT

**Relationships**:
- `transaction_id` → `transactions.id`
- `account_id` → `accounts.id`

**Indexes**:
- `idx_entries_transaction` on `transaction_id`

### 8. audit_logs
**Purpose**: Complete audit trail for compliance

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key to users |
| `action` | VARCHAR(50) | Action performed |
| `resource_type` | VARCHAR(50) | Type of resource affected |
| `resource_id` | UUID | ID of affected resource |
| `details` | JSON | Additional details |
| `created_at` | TIMESTAMP | Action timestamp |

**Relationships**:
- `user_id` → `users.id`

**Indexes**:
- `idx_audit_logs_user` on `user_id`
- `idx_audit_logs_created` on `created_at`

## 🔄 Business Workflows

### Customer Onboarding Flow
1. **Customer Registration** → `customers` table
2. **KYC Document Upload** → `kyc_documents` table
3. **Document Verification** → Update `kyc_documents.status`
4. **KYC Status Update** → Update `customers.kyc_status`
5. **Account Creation** → `accounts` and `balances` tables

### Transaction Processing Flow
1. **Transaction Creation** → `transactions` table (status: PENDING)
2. **Double-Entry Creation** → `entries` table (DEBIT + CREDIT)
3. **Balance Updates** → `balances` table
4. **Transaction Completion** → Update `transactions.status`
5. **Audit Logging** → `audit_logs` table

### KYC Verification Flow
1. **Document Upload** → `kyc_documents` (status: PENDING)
2. **Compliance Review** → Staff verification
3. **Status Update** → `kyc_documents.status` (APPROVED/REJECTED)
4. **Customer Status** → Auto-update `customers.kyc_status`
5. **Audit Trail** → `audit_logs` entry

## 🔒 Security Features

- **UUID Primary Keys**: Prevents enumeration attacks
- **Password Hashing**: bcrypt for user passwords
- **Audit Trail**: Complete action logging
- **Role-Based Access**: User roles for authorization
- **Data Integrity**: Foreign key constraints
- **Immutable Records**: Audit logs cannot be modified

## 📈 Performance Optimizations

- **Strategic Indexes**: On frequently queried columns
- **Balance Caching**: Separate balance table for fast lookups
- **Partitioning Ready**: Audit logs can be partitioned by date
- **Connection Pooling**: SQLAlchemy connection management

## 🔧 Maintenance

### Regular Tasks
- Monitor audit log growth
- Archive old transaction data
- Update KYC document expiry status
- Balance reconciliation checks

### Backup Strategy
- Daily full database backups
- Transaction log backups every 15 minutes
- Point-in-time recovery capability
- Encrypted backup storage