#!/usr/bin/env python3
"""
Database setup script for CoreX Banking System
Creates database and runs initial migrations
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

# Database configuration
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "2001"
DB_NAME = "coreX-DB"

def create_database():
    """Create the CoreX database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"Database '{DB_NAME}' created successfully!")
        else:
            print(f"Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        return False

def test_connection():
    """Test connection to the CoreX database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Connected to PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    print("🏦 CoreX Banking System - Database Setup")
    print("=" * 50)
    
    # Create database
    if create_database():
        # Test connection
        if test_connection():
            print("✅ Database setup completed successfully!")
            print(f"📊 Database: {DB_NAME}")
            print(f"🔗 Connection: postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        else:
            print("❌ Database connection test failed!")
            sys.exit(1)
    else:
        print("❌ Database creation failed!")
        sys.exit(1)