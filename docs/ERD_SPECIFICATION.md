# CoreX Banking System - ERD Specification

## Database: coreX-DB

### Tables and Relationships

## 1. CUSTOMERS Table
```
customers
├── id (UUID, PK)
├── customer_number (VARCHAR(20), UNIQUE)
├── first_name (VARCHAR(100))
├── last_name (VARCHAR(100))
├── email (VARCHAR(255), UNIQUE)
├── phone (VARCHAR(20))
├── date_of_birth (DATE)
├── address (TEXT)
├── city (VARCHAR(100))
├── country (VARCHAR(100))
├── occupation (VARCHAR(100))
├── income_range (VARCHAR(50))
├── kyc_status (ENUM: PENDING, APPROVED, REJECTED)
├── status (ENUM: ACTIVE, INACTIVE, SUSPENDED)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

## 2. USERS Table
```
users
├── id (UUID, PK)
├── username (VARCHAR(50), UNIQUE)
├── email (VARCHAR(255), UNIQUE)
├── password_hash (VARCHAR(255))
├── role (ENUM: ADMIN, TELLER, AUDITOR, API_USER)
├── status (ENUM: ACTIVE, INACTIVE, SUSPENDED)
└── created_at (TIMESTAMP)
```

## 3. ACCOUNTS Table
```
accounts
├── id (UUID, PK)
├── account_number (VARCHAR(20), UNIQUE)
├── customer_id (UUID, FK → customers.id)
├── account_type (ENUM: SAVINGS, CURRENT, LOAN)
├── currency (VARCHAR(3))
├── status (ENUM: ACTIVE, INACTIVE, SUSPENDED, CLOSED)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

## 4. KYC_DOCUMENTS Table
```
kyc_documents
├── id (UUID, PK)
├── customer_id (UUID, FK → customers.id)
├── document_type (ENUM: NATIONAL_ID, PASSPORT, DRIVERS_LICENSE, UTILITY_BILL, BANK_STATEMENT)
├── document_number (VARCHAR(100))
├── file_path (VARCHAR(500))
├── status (ENUM: PENDING, APPROVED, REJECTED, EXPIRED)
├── verified_by (UUID, FK → users.id)
├── rejection_reason (TEXT)
├── expires_at (TIMESTAMP)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

## 5. BALANCES Table
```
balances
├── account_id (UUID, PK, FK → accounts.id)
├── ledger_balance (DECIMAL(15,2))
├── available_balance (DECIMAL(15,2))
└── updated_at (TIMESTAMP)
```

## 6. TRANSACTIONS Table
```
transactions
├── id (UUID, PK)
├── transaction_id (VARCHAR(50), UNIQUE)
├── from_account_id (UUID, FK → accounts.id, NULLABLE)
├── to_account_id (UUID, FK → accounts.id, NULLABLE)
├── amount (DECIMAL(15,2))
├── currency (VARCHAR(3))
├── transaction_type (ENUM: DEPOSIT, WITHDRAWAL, TRANSFER, FEE, INTEREST)
├── description (TEXT)
├── status (ENUM: PENDING, COMPLETED, FAILED, CANCELLED)
├── created_at (TIMESTAMP)
└── processed_at (TIMESTAMP)
```

## 7. ENTRIES Table
```
entries
├── id (UUID, PK)
├── transaction_id (UUID, FK → transactions.id)
├── account_id (UUID, FK → accounts.id)
├── entry_type (ENUM: DEBIT, CREDIT)
├── amount (DECIMAL(15,2))
└── created_at (TIMESTAMP)
```

## 8. AUDIT_LOGS Table
```
audit_logs
├── id (UUID, PK)
├── user_id (UUID, FK → users.id)
├── action (VARCHAR(50))
├── resource_type (VARCHAR(50))
├── resource_id (UUID)
├── details (JSON)
└── created_at (TIMESTAMP)
```

## Relationships

### One-to-Many Relationships
1. **customers (1) → accounts (M)**
   - `accounts.customer_id` → `customers.id`
   - One customer can have multiple accounts

2. **customers (1) → kyc_documents (M)**
   - `kyc_documents.customer_id` → `customers.id`
   - One customer can have multiple KYC documents

3. **users (1) → kyc_documents (M)**
   - `kyc_documents.verified_by` → `users.id`
   - One user can verify multiple documents

4. **users (1) → audit_logs (M)**
   - `audit_logs.user_id` → `users.id`
   - One user can have multiple audit log entries

5. **accounts (1) → transactions (M) [from_account]**
   - `transactions.from_account_id` → `accounts.id`
   - One account can be source for multiple transactions

6. **accounts (1) → transactions (M) [to_account]**
   - `transactions.to_account_id` → `accounts.id`
   - One account can be destination for multiple transactions

7. **transactions (1) → entries (M)**
   - `entries.transaction_id` → `transactions.id`
   - One transaction can have multiple journal entries

8. **accounts (1) → entries (M)**
   - `entries.account_id` → `accounts.id`
   - One account can have multiple journal entries

### One-to-One Relationships
1. **accounts (1) → balances (1)**
   - `balances.account_id` → `accounts.id`
   - Each account has exactly one balance record

## ERD Diagram Structure

```
┌─────────────┐    1:M    ┌─────────────┐    1:1    ┌─────────────┐
│  customers  │◄─────────►│   accounts  │◄─────────►│   balances  │
└─────────────┘           └─────────────┘           └─────────────┘
       │                         │
       │ 1:M                     │ 1:M
       ▼                         ▼
┌─────────────┐           ┌─────────────┐
│kyc_documents│           │transactions │
└─────────────┘           └─────────────┘
       │                         │
       │ M:1                     │ 1:M
       ▼                         ▼
┌─────────────┐           ┌─────────────┐
│    users    │           │   entries   │
└─────────────┘           └─────────────┘
       │                         │
       │ 1:M                     │ M:1
       ▼                         ▼
┌─────────────┐           ┌─────────────┐
│ audit_logs  │           │   accounts  │
└─────────────┘           └─────────────┘
```

## Indexes

```sql
-- Performance indexes
CREATE INDEX idx_customers_number ON customers(customer_number);
CREATE INDEX idx_accounts_number ON accounts(account_number);
CREATE INDEX idx_transactions_id ON transactions(transaction_id);
CREATE INDEX idx_entries_transaction ON entries(transaction_id);
CREATE INDEX idx_kyc_documents_customer ON kyc_documents(customer_id);
CREATE INDEX idx_kyc_documents_status ON kyc_documents(status);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

## Constraints

### Primary Keys
- All tables use UUID primary keys
- `balances` table uses `account_id` as primary key (also foreign key)

### Foreign Keys
- `accounts.customer_id` → `customers.id`
- `kyc_documents.customer_id` → `customers.id`
- `kyc_documents.verified_by` → `users.id`
- `balances.account_id` → `accounts.id`
- `transactions.from_account_id` → `accounts.id`
- `transactions.to_account_id` → `accounts.id`
- `entries.transaction_id` → `transactions.id`
- `entries.account_id` → `accounts.id`
- `audit_logs.user_id` → `users.id`

### Unique Constraints
- `customers.customer_number`
- `customers.email`
- `users.username`
- `users.email`
- `accounts.account_number`
- `transactions.transaction_id`

## Business Rules

1. **Double-Entry Accounting**: Every transaction must have matching debit and credit entries
2. **Balance Integrity**: Account balances must equal sum of all entries for that account
3. **KYC Compliance**: Customers must have approved KYC documents before account activation
4. **Audit Trail**: All system actions must be logged in audit_logs
5. **Transaction Atomicity**: All transaction processing must be atomic (all or nothing)

## Data Types Summary

- **UUID**: All primary keys and foreign key references
- **VARCHAR**: Text fields with length limits
- **TEXT**: Unlimited text fields (addresses, descriptions, reasons)
- **DECIMAL(15,2)**: Monetary amounts with 2 decimal precision
- **TIMESTAMP**: All date/time fields with timezone support
- **ENUM**: Predefined value sets for status fields
- **JSON**: Flexible data storage for audit details