#!/usr/bin/env python3
"""
Install dependencies and setup development environment
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main installation process"""
    commands = [
        ("pip install --user alembic sqlalchemy psycopg2-binary fastapi uvicorn", "Installing core dependencies"),
        ("pip install --user -r requirements.txt", "Installing all requirements"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"Failed to execute: {cmd}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)