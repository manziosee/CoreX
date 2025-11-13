#!/usr/bin/env python3
"""
Run CoreX locally with your PostgreSQL database
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("🏦 CoreX Banking System - Local Setup")
    print("=" * 50)
    print("📊 Using local PostgreSQL database: coreX-DB")
    print("🔗 Connection: postgresql://postgres:2001@localhost:5432/coreX-DB")
    print()
    
    # Setup database
    if not run_command("python3 setup_db.py", "Setting up database"):
        return False
    
    # Run migrations
    if not run_command("python3 manage_db.py upgrade", "Running migrations"):
        return False
    
    # Start the application
    print("🚀 Starting CoreX API server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print()
    
    try:
        subprocess.run("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000", shell=True)
    except KeyboardInterrupt:
        print("\n👋 CoreX API server stopped")

if __name__ == "__main__":
    main()