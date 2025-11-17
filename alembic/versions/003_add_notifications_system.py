"""Add notifications system

Revision ID: 003_add_notifications_system
Revises: 002_add_banking_features
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003_add_notifications_system'
down_revision = '002_add_banking_features'
branch_labels = None
depends_on = None

def upgrade():
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notification_type', sa.Enum('TRANSACTION', 'KYC_UPDATE', 'LOAN_UPDATE', 'ACCOUNT_UPDATE', 'SYSTEM_ALERT', name='notificationtype'), nullable=False),
        sa.Column('channel', sa.Enum('EMAIL', 'SMS', 'IN_APP', name='notificationchannel'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'FAILED', name='notificationstatus'), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notification_templates table
    op.create_table('notification_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_code', sa.String(length=50), nullable=False),
        sa.Column('notification_type', sa.Enum('TRANSACTION', 'KYC_UPDATE', 'LOAN_UPDATE', 'ACCOUNT_UPDATE', 'SYSTEM_ALERT', name='notificationtype'), nullable=False),
        sa.Column('title_template', sa.String(length=200), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_code')
    )

def downgrade():
    op.drop_table('notification_templates')
    op.drop_table('notifications')
    op.execute('DROP TYPE IF EXISTS notificationtype')
    op.execute('DROP TYPE IF EXISTS notificationchannel')
    op.execute('DROP TYPE IF EXISTS notificationstatus')