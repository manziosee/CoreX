#!/usr/bin/env python3
"""
Setup notifications system tables directly
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def create_notifications_tables():
    """Create notifications tables directly"""
    
    # Create database engine
    engine = create_engine(settings.database_url)
    
    # SQL to create notifications tables
    sql_commands = [
        # Create enum types
        """
        DO $$ BEGIN
            CREATE TYPE notificationtype AS ENUM ('TRANSACTION', 'KYC_UPDATE', 'LOAN_UPDATE', 'ACCOUNT_UPDATE', 'SYSTEM_ALERT');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,
        
        """
        DO $$ BEGIN
            CREATE TYPE notificationchannel AS ENUM ('EMAIL', 'SMS', 'IN_APP');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,
        
        """
        DO $$ BEGIN
            CREATE TYPE notificationstatus AS ENUM ('PENDING', 'SENT', 'FAILED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,
        
        # Create notifications table
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            customer_id UUID REFERENCES customers(id),
            user_id UUID REFERENCES users(id),
            notification_type notificationtype NOT NULL,
            channel notificationchannel NOT NULL,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            status notificationstatus DEFAULT 'PENDING',
            sent_at TIMESTAMP WITH TIME ZONE,
            read_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create notification_templates table
        """
        CREATE TABLE IF NOT EXISTS notification_templates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            template_code VARCHAR(50) UNIQUE NOT NULL,
            notification_type notificationtype NOT NULL,
            title_template VARCHAR(200) NOT NULL,
            message_template TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Insert default templates
        """
        INSERT INTO notification_templates (template_code, notification_type, title_template, message_template)
        VALUES 
            ('TRANSACTION_ALERT', 'TRANSACTION', '{type} Transaction Alert', 'Your account has been {type} with {amount}. Time: {time}'),
            ('KYC_UPDATE', 'KYC_UPDATE', 'KYC Status Update', 'Your KYC verification status has been updated to: {status}')
        ON CONFLICT (template_code) DO NOTHING;
        """
    ]
    
    try:
        with engine.connect() as conn:
            for sql in sql_commands:
                conn.execute(text(sql))
                conn.commit()
        
        print("✅ Notifications system tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating notifications tables: {e}")
        return False

if __name__ == "__main__":
    success = create_notifications_tables()
    sys.exit(0 if success else 1)