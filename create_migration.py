#!/usr/bin/env python3
"""
Create initial migration for CoreX Banking System
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("🏦 CoreX Banking System - Migration Setup")
    print("=" * 50)
    
    # Initialize Alembic
    if not run_command("alembic init alembic", "Initializing Alembic"):
        return False
    
    # Create initial migration
    if not run_command("alembic revision --autogenerate -m 'Initial migration with all tables'", "Creating initial migration"):
        return False
    
    print("✅ Migration setup completed!")
    print("📝 Next steps:")
    print("   1. Review the generated migration file")
    print("   2. Run: alembic upgrade head")
    
    return True

if __name__ == "__main__":
    main()