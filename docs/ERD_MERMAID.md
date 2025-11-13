# CoreX Banking System - Mermaid ERD

## Entity Relationship Diagram (Mermaid Format)

```mermaid
erDiagram
    CUSTOMERS {
        uuid id PK
        varchar customer_number UK
        varchar first_name
        varchar last_name
        varchar email UK
        varchar phone
        date date_of_birth
        text address
        varchar city
        varchar country
        varchar occupation
        varchar income_range
        enum kyc_status
        enum status
        timestamp created_at
        timestamp updated_at
    }

    USERS {
        uuid id PK
        varchar username UK
        varchar email UK
        varchar password_hash
        enum role
        enum status
        timestamp created_at
    }

    ACCOUNTS {
        uuid id PK
        varchar account_number UK
        uuid customer_id FK
        enum account_type
        varchar currency
        enum status
        timestamp created_at
        timestamp updated_at
    }

    KYC_DOCUMENTS {
        uuid id PK
        uuid customer_id FK
        enum document_type
        varchar document_number
        varchar file_path
        enum status
        uuid verified_by FK
        text rejection_reason
        timestamp expires_at
        timestamp created_at
        timestamp updated_at
    }

    BALANCES {
        uuid account_id PK_FK
        decimal ledger_balance
        decimal available_balance
        timestamp updated_at
    }

    TRANSACTIONS {
        uuid id PK
        varchar transaction_id UK
        uuid from_account_id FK
        uuid to_account_id FK
        decimal amount
        varchar currency
        enum transaction_type
        text description
        enum status
        timestamp created_at
        timestamp processed_at
    }

    ENTRIES {
        uuid id PK
        uuid transaction_id FK
        uuid account_id FK
        enum entry_type
        decimal amount
        timestamp created_at
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        varchar action
        varchar resource_type
        uuid resource_id
        json details
        timestamp created_at
    }

    %% Relationships
    CUSTOMERS ||--o{ ACCOUNTS : "owns"
    CUSTOMERS ||--o{ KYC_DOCUMENTS : "submits"
    USERS ||--o{ KYC_DOCUMENTS : "verifies"
    USERS ||--o{ AUDIT_LOGS : "creates"
    ACCOUNTS ||--|| BALANCES : "has"
    ACCOUNTS ||--o{ TRANSACTIONS : "from_account"
    ACCOUNTS ||--o{ TRANSACTIONS : "to_account"
    ACCOUNTS ||--o{ ENTRIES : "affects"
    TRANSACTIONS ||--o{ ENTRIES : "generates"
```

## Simplified Relationship View

```mermaid
graph TD
    C[CUSTOMERS] --> A[ACCOUNTS]
    C --> K[KYC_DOCUMENTS]
    U[USERS] --> K
    U --> AL[AUDIT_LOGS]
    A --> B[BALANCES]
    A --> T[TRANSACTIONS]
    A --> E[ENTRIES]
    T --> E
    
    C -.->|1:M| A
    C -.->|1:M| K
    U -.->|1:M| K
    U -.->|1:M| AL
    A -.->|1:1| B
    A -.->|1:M| T
    T -.->|1:M| E
    A -.->|1:M| E
```

## Database Flow Diagram

```mermaid
flowchart TD
    A[Customer Registration] --> B[KYC Document Upload]
    B --> C[Document Verification]
    C --> D[KYC Status Update]
    D --> E[Account Creation]
    E --> F[Balance Initialization]
    F --> G[Transaction Processing]
    G --> H[Journal Entries]
    H --> I[Balance Updates]
    I --> J[Audit Logging]
    
    subgraph "Database Tables"
        K[customers]
        L[kyc_documents]
        M[users]
        N[accounts]
        O[balances]
        P[transactions]
        Q[entries]
        R[audit_logs]
    end
    
    A --> K
    B --> L
    C --> M
    E --> N
    F --> O
    G --> P
    H --> Q
    J --> R
```