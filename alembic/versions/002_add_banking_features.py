"""Add banking features - loans, interest, payments

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create loans table
    op.create_table('loans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loan_number', sa.String(length=20), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loan_type', sa.Enum('PERSONAL', 'BUSINESS', 'MORTGAGE', 'AUTO', name='loantype'), nullable=False),
        sa.Column('principal_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('interest_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('term_months', sa.String(length=3), nullable=False),
        sa.Column('monthly_payment', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'ACTIVE', 'CLOSED', 'DEFAULTED', name='loanstatus'), nullable=True),
        sa.Column('disbursed_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('outstanding_balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('application_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('disbursement_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('maturity_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('purpose', sa.Text(), nullable=True),
        sa.Column('collateral_description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('loan_number')
    )

    # Create loan_payments table
    op.create_table('loan_payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_number', sa.String(length=10), nullable=False),
        sa.Column('payment_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('amount_paid', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('principal_paid', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('interest_paid', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('balance_after_payment', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['loan_id'], ['loans.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create interest_rates table
    op.create_table('interest_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rate_code', sa.String(length=20), nullable=False),
        sa.Column('interest_type', sa.Enum('SAVINGS', 'LOAN', 'OVERDRAFT', name='interesttype'), nullable=False),
        sa.Column('base_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('effective_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('min_balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('max_balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('frequency', sa.Enum('DAILY', 'MONTHLY', 'QUARTERLY', 'ANNUALLY', name='interestfrequency'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rate_code')
    )

    # Create interest_postings table
    op.create_table('interest_postings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('posting_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('calculation_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('calculation_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('average_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('interest_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('interest_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['rate_id'], ['interest_rates.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create bill_payments table
    op.create_table('bill_payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_reference', sa.String(length=50), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('biller_code', sa.String(length=20), nullable=False),
        sa.Column('biller_name', sa.String(length=100), nullable=False),
        sa.Column('bill_account_number', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('payment_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED', name='paymentstatus'), nullable=True),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_reference')
    )

    # Create standing_orders table
    op.create_table('standing_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_reference', sa.String(length=50), nullable=False),
        sa.Column('from_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_execution_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['from_account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['to_account_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_reference')
    )

    # Create standing_order_executions table
    op.create_table('standing_order_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('standing_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('execution_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED', name='paymentstatus'), nullable=True),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['standing_order_id'], ['standing_orders.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('standing_order_executions')
    op.drop_table('standing_orders')
    op.drop_table('bill_payments')
    op.drop_table('interest_postings')
    op.drop_table('interest_rates')
    op.drop_table('loan_payments')
    op.drop_table('loans')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS interestfrequency')
    op.execute('DROP TYPE IF EXISTS interesttype')
    op.execute('DROP TYPE IF EXISTS loanstatus')
    op.execute('DROP TYPE IF EXISTS loantype')