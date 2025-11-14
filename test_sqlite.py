#!/usr/bin/env python3
"""
Test SQLite database creation and initialization
"""

import os
import sqlite3
import sys
from pathlib import Path

def test_sqlite_setup():
    """Test SQLite database setup"""
    print("🧪 Testing SQLite Database Setup")
    print("=" * 40)
    
    # Test 1: Create database file
    db_path = "/tmp/test_corex.db"
    try:
        # Create database file
        Path(db_path).touch()
        print("✅ Database file creation: SUCCESS")
    except Exception as e:
        print(f"❌ Database file creation: FAILED - {e}")
        return False
    
    # Test 2: SQLite connection
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO test (id) VALUES (1)")
        result = conn.execute("SELECT COUNT(*) FROM test").fetchone()
        conn.close()
        print(f"✅ SQLite operations: SUCCESS - {result[0]} record(s)")
    except Exception as e:
        print(f"❌ SQLite operations: FAILED - {e}")
        return False
    
    # Test 3: SQLAlchemy with SQLite
    try:
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        from sqlalchemy import create_engine, text
        engine = create_engine(f'sqlite:///{db_path}')
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM test"))
            count = result.fetchone()[0]
        print(f"✅ SQLAlchemy operations: SUCCESS - {count} record(s)")
    except Exception as e:
        print(f"❌ SQLAlchemy operations: FAILED - {e}")
        return False
    
    # Cleanup
    try:
        os.remove(db_path)
        print("✅ Cleanup: SUCCESS")
    except:
        pass
    
    print("\n🎉 All SQLite tests passed!")
    return True

if __name__ == "__main__":
    success = test_sqlite_setup()
    sys.exit(0 if success else 1)