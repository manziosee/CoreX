#!/usr/bin/env python3
"""
Check database structure and relationships
"""

import psycopg2

def check_database():
    conn = psycopg2.connect('postgresql://postgres:2001@localhost:5432/coreX-DB')
    cursor = conn.cursor()
    
    print("📊 TABLES CREATED:")
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  ✅ {table[0]}")
    
    print("\n🔗 FOREIGN KEY RELATIONSHIPS:")
    cursor.execute("""
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        ORDER BY tc.table_name;
    """)
    relationships = cursor.fetchall()
    for rel in relationships:
        print(f"  🔗 {rel[0]}.{rel[1]} → {rel[2]}.{rel[3]}")
    
    print("\n📋 TABLE DETAILS:")
    for table in tables:
        if table[0] != 'alembic_version':
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table[0]}' ORDER BY ordinal_position;")
            columns = cursor.fetchall()
            print(f"\n  📄 {table[0]}:")
            for col in columns:
                print(f"    - {col[0]} ({col[1]})")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_database()