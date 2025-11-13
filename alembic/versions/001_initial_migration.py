"""Initial migration with all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customers table
    op.create_table('customers',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('customer_number', sa.String(length=20), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('occupation', sa.String(length=100), nullable=True),
    sa.Column('income_range', sa.String(length=50), nullable=True),
    sa.Column('kyc_status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='kycstatus'), nullable=True),
    sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', name='customerstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('customer_number'),
    sa.UniqueConstraint('email')
    )
    
    # Create users table
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'TELLER', 'AUDITOR', 'API_USER', name='userrole'), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', name='userstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    
    # Create accounts table
    op.create_table('accounts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('account_number', sa.String(length=20), nullable=False),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('account_type', sa.Enum('SAVINGS', 'CURRENT', 'LOAN', name='accounttype'), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'CLOSED', name='accountstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('account_number')
    )
    
    # Create kyc_documents table
    op.create_table('kyc_documents',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('document_type', sa.Enum('NATIONAL_ID', 'PASSPORT', 'DRIVERS_LICENSE', 'UTILITY_BILL', 'BANK_STATEMENT', name='documenttype'), nullable=False),
    sa.Column('document_number', sa.String(length=100), nullable=True),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED', name='documentstatus'), nullable=True),
    sa.Column('verified_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create balances table
    op.create_table('balances',
    sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('ledger_balance', sa.DECIMAL(precision=15, scale=2), nullable=True),
    sa.Column('available_balance', sa.DECIMAL(precision=15, scale=2), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('account_id')
    )
    
    # Create transactions table
    op.create_table('transactions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('transaction_id', sa.String(length=50), nullable=False),
    sa.Column('from_account_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('to_account_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('transaction_type', sa.Enum('DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'FEE', 'INTEREST', name='transactiontype'), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED', name='transactionstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['from_account_id'], ['accounts.id'], ),
    sa.ForeignKeyConstraint(['to_account_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('transaction_id')
    )
    
    # Create entries table
    op.create_table('entries',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('entry_type', sa.Enum('DEBIT', 'CREDIT', name='entrytype'), nullable=False),
    sa.Column('amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create audit_logs table
    op.create_table('audit_logs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('action', sa.String(length=50), nullable=False),
    sa.Column('resource_type', sa.String(length=50), nullable=True),
    sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_customers_number', 'customers', ['customer_number'])
    op.create_index('idx_accounts_number', 'accounts', ['account_number'])
    op.create_index('idx_transactions_id', 'transactions', ['transaction_id'])
    op.create_index('idx_entries_transaction', 'entries', ['transaction_id'])
    op.create_index('idx_kyc_documents_customer', 'kyc_documents', ['customer_id'])
    op.create_index('idx_kyc_documents_status', 'kyc_documents', ['status'])
    op.create_index('idx_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_created', 'audit_logs', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_audit_logs_created')
    op.drop_index('idx_audit_logs_user')
    op.drop_index('idx_kyc_documents_status')
    op.drop_index('idx_kyc_documents_customer')
    op.drop_index('idx_entries_transaction')
    op.drop_index('idx_transactions_id')
    op.drop_index('idx_accounts_number')
    op.drop_index('idx_customers_number')
    
    # Drop tables
    op.drop_table('audit_logs')
    op.drop_table('entries')
    op.drop_table('transactions')
    op.drop_table('balances')
    op.drop_table('kyc_documents')
    op.drop_table('accounts')
    op.drop_table('users')
    op.drop_table('customers')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS entrytype')
    op.execute('DROP TYPE IF EXISTS transactionstatus')
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS accountstatus')
    op.execute('DROP TYPE IF EXISTS accounttype')
    op.execute('DROP TYPE IF EXISTS documentstatus')
    op.execute('DROP TYPE IF EXISTS documenttype')
    op.execute('DROP TYPE IF EXISTS userstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS customerstatus')
    op.execute('DROP TYPE IF EXISTS kycstatus')