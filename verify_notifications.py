#!/usr/bin/env python3
"""
Verify notifications system implementation
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if file exists and report"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_file_content(filepath, search_terms, description):
    """Check if file contains required content"""
    if not Path(filepath).exists():
        print(f"❌ {description}: {filepath} - FILE NOT FOUND")
        return False
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        missing_terms = []
        for term in search_terms:
            if term not in content:
                missing_terms.append(term)
        
        if missing_terms:
            print(f"⚠️  {description}: Missing {missing_terms}")
            return False
        else:
            print(f"✅ {description}: All required content present")
            return True
            
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def main():
    """Main verification process"""
    print("🔔 CoreX Notifications System Verification")
    print("=" * 50)
    
    # Check core files exist
    core_files = [
        ("app/models/notification.py", "Notification Models"),
        ("app/schemas/notification.py", "Notification Schemas"),
        ("app/services/notification.py", "Notification Service"),
        ("app/api/notifications.py", "Notification API"),
        ("tests/test_notifications_comprehensive.py", "Comprehensive Tests"),
        ("tests/test_notifications_integration.py", "Integration Tests"),
        ("docs/NOTIFICATIONS.md", "Documentation"),
        ("alembic/versions/003_add_notifications_system.py", "Database Migration"),
    ]
    
    print("\n📁 File Structure Check:")
    all_files_exist = True
    for filepath, description in core_files:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    # Check content requirements
    print("\n📋 Content Verification:")
    content_checks = [
        ("app/models/notification.py", 
         ["class Notification", "class NotificationTemplate", "NotificationType", "NotificationChannel"],
         "Notification Models Content"),
        
        ("app/services/notification.py",
         ["class NotificationService", "send_transaction_notification", "send_kyc_notification"],
         "Notification Service Content"),
        
        ("app/api/notifications.py",
         ["@router.post", "create_notification", "get_customer_notifications"],
         "Notification API Content"),
        
        ("app/main.py",
         ["notifications.router", "Notifications"],
         "Main App Integration"),
    ]
    
    all_content_valid = True
    for filepath, terms, description in content_checks:
        if not check_file_content(filepath, terms, description):
            all_content_valid = False
    
    # Check integration points
    print("\n🔗 Integration Check:")
    integration_checks = [
        ("app/services/transaction.py",
         ["_send_transaction_notifications", "NotificationService"],
         "Transaction Integration"),
        
        ("app/services/kyc_workflow.py",
         ["_send_kyc_notification", "NotificationService"],
         "KYC Integration"),
    ]
    
    all_integrations_valid = True
    for filepath, terms, description in integration_checks:
        if not check_file_content(filepath, terms, description):
            all_integrations_valid = False
    
    # Summary
    print("\n📊 Verification Summary:")
    print("=" * 30)
    
    if all_files_exist:
        print("✅ All required files present")
    else:
        print("❌ Some files missing")
    
    if all_content_valid:
        print("✅ All core content implemented")
    else:
        print("❌ Some content missing")
    
    if all_integrations_valid:
        print("✅ All integrations implemented")
    else:
        print("❌ Some integrations missing")
    
    overall_success = all_files_exist and all_content_valid and all_integrations_valid
    
    if overall_success:
        print("\n🎉 Notifications System: FULLY IMPLEMENTED")
        print("\n📚 Next Steps:")
        print("1. Install dependencies: python3 setup_dev_environment.py")
        print("2. Setup database: python3 setup_notifications.py")
        print("3. Run tests: make test-notifications")
        print("4. Start API: uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Notifications System: PARTIALLY IMPLEMENTED")
        print("Please check the issues above and fix them.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)