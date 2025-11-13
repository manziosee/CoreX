#!/usr/bin/env python3
"""
Database management script for CoreX Banking System
"""

import subprocess
import sys
import argparse

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

def setup_database():
    """Setup database and run migrations"""
    print("🏦 Setting up CoreX Database...")
    
    # Create database
    if not run_command("python3 setup_db.py", "Creating database"):
        return False
    
    # Run migrations
    if not run_command("alembic upgrade head", "Running migrations"):
        return False
    
    print("✅ Database setup completed!")
    return True

def create_migration(message):
    """Create a new migration"""
    command = f"alembic revision --autogenerate -m '{message}'"
    return run_command(command, f"Creating migration: {message}")

def upgrade_database():
    """Upgrade database to latest migration"""
    return run_command("alembic upgrade head", "Upgrading database")

def downgrade_database(revision="base"):
    """Downgrade database to specific revision"""
    command = f"alembic downgrade {revision}"
    return run_command(command, f"Downgrading database to {revision}")

def show_history():
    """Show migration history"""
    return run_command("alembic history", "Showing migration history")

def show_current():
    """Show current migration"""
    return run_command("alembic current", "Showing current migration")

def main():
    parser = argparse.ArgumentParser(description="CoreX Database Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    subparsers.add_parser("setup", help="Setup database and run initial migrations")
    
    # Migration commands
    migrate_parser = subparsers.add_parser("migrate", help="Create new migration")
    migrate_parser.add_argument("message", help="Migration message")
    
    # Upgrade command
    subparsers.add_parser("upgrade", help="Upgrade database to latest migration")
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("--revision", default="base", help="Revision to downgrade to")
    
    # History commands
    subparsers.add_parser("history", help="Show migration history")
    subparsers.add_parser("current", help="Show current migration")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_database()
    elif args.command == "migrate":
        create_migration(args.message)
    elif args.command == "upgrade":
        upgrade_database()
    elif args.command == "downgrade":
        downgrade_database(args.revision)
    elif args.command == "history":
        show_history()
    elif args.command == "current":
        show_current()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()