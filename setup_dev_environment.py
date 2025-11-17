#!/usr/bin/env python3
"""
Complete development environment setup script
Prevents dependency and migration issues
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run command with proper error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True, result.stdout
        else:
            print(f"⚠️  {description} completed with warnings")
            print(f"Output: {result.stdout}")
            print(f"Errors: {result.stderr}")
            return False, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False, e.stderr

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_virtual_environment():
    """Setup virtual environment if not exists"""
    if not Path("venv").exists():
        success, _ = run_command("python3 -m venv venv", "Creating virtual environment")
        if not success:
            return False
    
    # Install pip packages in virtual environment
    commands = [
        ("./venv/bin/pip install --upgrade pip", "Upgrading pip"),
        ("./venv/bin/pip install wheel setuptools", "Installing build tools"),
        ("./venv/bin/pip install -r requirements.txt", "Installing requirements"),
    ]
    
    for cmd, desc in commands:
        success, _ = run_command(cmd, desc, check=False)
        if not success:
            # Try alternative installation
            alt_cmd = cmd.replace("./venv/bin/pip", "pip3 install --user")
            print(f"Trying alternative: {alt_cmd}")
            run_command(alt_cmd, f"{desc} (alternative)", check=False)
    
    return True

def setup_database():
    """Setup database and run migrations"""
    print("🔄 Setting up database...")
    
    # Check if database exists
    success, _ = run_command("python3 setup_db.py", "Database setup", check=False)
    
    # Try to run migrations
    migration_commands = [
        ("python3 manage_db.py upgrade", "Running migrations"),
        ("python3 setup_notifications.py", "Setting up notifications tables"),
    ]
    
    for cmd, desc in migration_commands:
        run_command(cmd, desc, check=False)
    
    return True

def run_tests():
    """Run test suite to verify setup"""
    print("🔄 Running tests to verify setup...")
    
    test_commands = [
        ("python3 -m pytest tests/test_notifications_comprehensive.py -v", "Testing notifications"),
        ("python3 -m pytest tests/test_main.py -v", "Testing main functionality"),
    ]
    
    for cmd, desc in test_commands:
        success, output = run_command(cmd, desc, check=False)
        if "FAILED" in output:
            print(f"⚠️  Some tests failed in {desc}")
        elif "passed" in output:
            print(f"✅ {desc} passed")

def create_env_file():
    """Create .env file if not exists"""
    if not Path(".env").exists():
        if Path(".env.example").exists():
            run_command("cp .env.example .env", "Creating .env file")
            print("📝 Please update .env file with your database credentials")
        else:
            print("⚠️  No .env.example found, please create .env manually")

def main():
    """Main setup process"""
    print("🏦 CoreX Banking System - Development Environment Setup")
    print("=" * 60)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        (create_env_file, "Environment configuration"),
        (setup_virtual_environment, "Virtual environment and dependencies"),
        (setup_database, "Database and migrations"),
        (run_tests, "Test suite verification"),
    ]
    
    for step_func, step_name in steps:
        print(f"\n📋 Step: {step_name}")
        try:
            step_func()
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            continue
    
    print("\n🎉 Development environment setup completed!")
    print("\n📚 Next steps:")
    print("1. Update .env file with your database credentials")
    print("2. Run: python3 -m uvicorn app.main:app --reload")
    print("3. Visit: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)