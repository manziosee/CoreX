#!/usr/bin/env python3
"""
Authentication Endpoints Test Script for CoreX Banking System
"""

import requests
import json
import sys
from typing import Optional

class AuthTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token: Optional[str] = None
        
    def test_health_check(self):
        """Test if the API is running"""
        print("🔍 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_login(self, username: str = "admin", password: str = "admin123"):
        """Test login endpoint"""
        print(f"🔐 Testing login with {username}...")
        try:
            response = self.session.post(
                f"{self.base_url}/auth/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                print("✅ Login successful")
                print(f"   Token: {self.admin_token[:50]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def test_get_profile(self):
        """Test get current user profile"""
        print("👤 Testing get current user profile...")
        if not self.admin_token:
            print("❌ No token available")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/auth/me",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Profile retrieved successfully")
                print(f"   Username: {data.get('username')}")
                print(f"   Role: {data.get('role')}")
                print(f"   Email: {data.get('email')}")
                return True
            else:
                print(f"❌ Profile retrieval failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Profile retrieval failed: {e}")
            return False
    
    def test_register_user(self):
        """Test user registration (admin only)"""
        print("📝 Testing user registration...")
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        user_data = {
            "username": "test_teller",
            "email": "test.teller@corex-banking.com",
            "password": "teller123",
            "role": "TELLER"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=user_data,
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User registration successful")
                print(f"   Username: {data.get('username')}")
                print(f"   Role: {data.get('role')}")
                return True
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User registration failed: {e}")
            return False
    
    def test_list_users(self):
        """Test list users (admin only)"""
        print("📋 Testing list users...")
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/auth/users?skip=0&limit=10",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )\n            \n            if response.status_code == 200:\n                data = response.json()\n                print(\"✅ Users list retrieved successfully\")\n                print(f\"   Found {len(data)} users\")\n                for user in data:\n                    print(f\"   - {user.get('username')} ({user.get('role')})\")\n                return True\n            else:\n                print(f\"❌ List users failed: {response.status_code}\")\n                print(f\"   Response: {response.text}\")\n                return False\n        except Exception as e:\n            print(f\"❌ List users failed: {e}\")\n            return False\n    \n    def test_change_password(self):\n        \"\"\"Test change password\"\"\"\n        print(\"🔑 Testing change password...\")\n        if not self.admin_token:\n            print(\"❌ No token available\")\n            return False\n            \n        password_data = {\n            \"current_password\": \"admin123\",\n            \"new_password\": \"newadmin123\"\n        }\n        \n        try:\n            response = self.session.put(\n                f\"{self.base_url}/auth/change-password\",\n                json=password_data,\n                headers={\"Authorization\": f\"Bearer {self.admin_token}\"}\n            )\n            \n            if response.status_code == 200:\n                print(\"✅ Password change successful\")\n                # Change it back\n                password_data = {\n                    \"current_password\": \"newadmin123\",\n                    \"new_password\": \"admin123\"\n                }\n                self.session.put(\n                    f\"{self.base_url}/auth/change-password\",\n                    json=password_data,\n                    headers={\"Authorization\": f\"Bearer {self.admin_token}\"}\n                )\n                return True\n            else:\n                print(f\"❌ Password change failed: {response.status_code}\")\n                print(f\"   Response: {response.text}\")\n                return False\n        except Exception as e:\n            print(f\"❌ Password change failed: {e}\")\n            return False\n    \n    def test_unauthorized_access(self):\n        \"\"\"Test accessing protected endpoint without token\"\"\"\n        print(\"🚫 Testing unauthorized access...\")\n        try:\n            response = self.session.get(f\"{self.base_url}/auth/me\")\n            \n            if response.status_code == 401:\n                print(\"✅ Unauthorized access properly blocked\")\n                return True\n            else:\n                print(f\"❌ Unauthorized access not blocked: {response.status_code}\")\n                return False\n        except Exception as e:\n            print(f\"❌ Unauthorized access test failed: {e}\")\n            return False\n    \n    def test_logout(self):\n        \"\"\"Test logout endpoint\"\"\"\n        print(\"🚪 Testing logout...\")\n        if not self.admin_token:\n            print(\"❌ No token available\")\n            return False\n            \n        try:\n            response = self.session.delete(\n                f\"{self.base_url}/auth/logout\",\n                headers={\"Authorization\": f\"Bearer {self.admin_token}\"}\n            )\n            \n            if response.status_code == 200:\n                print(\"✅ Logout successful\")\n                return True\n            else:\n                print(f\"❌ Logout failed: {response.status_code}\")\n                print(f\"   Response: {response.text}\")\n                return False\n        except Exception as e:\n            print(f\"❌ Logout failed: {e}\")\n            return False\n    \n    def run_all_tests(self):\n        \"\"\"Run all authentication tests\"\"\"\n        print(\"🏦 CoreX Banking System - Authentication Tests\")\n        print(\"=\" * 50)\n        \n        tests = [\n            self.test_health_check,\n            self.test_unauthorized_access,\n            self.test_login,\n            self.test_get_profile,\n            self.test_register_user,\n            self.test_list_users,\n            self.test_change_password,\n            self.test_logout\n        ]\n        \n        passed = 0\n        total = len(tests)\n        \n        for test in tests:\n            try:\n                if test():\n                    passed += 1\n                print()  # Empty line for readability\n            except Exception as e:\n                print(f\"❌ Test failed with exception: {e}\")\n                print()\n        \n        print(\"=\" * 50)\n        print(f\"📊 Test Results: {passed}/{total} tests passed\")\n        \n        if passed == total:\n            print(\"🎉 All authentication tests passed!\")\n            return True\n        else:\n            print(\"⚠️  Some tests failed. Check the output above.\")\n            return False\n\ndef main():\n    import argparse\n    \n    parser = argparse.ArgumentParser(description=\"Test CoreX Banking System Authentication\")\n    parser.add_argument(\"--url\", default=\"http://localhost:8000\", help=\"Base URL of the API\")\n    args = parser.parse_args()\n    \n    tester = AuthTester(args.url)\n    success = tester.run_all_tests()\n    \n    sys.exit(0 if success else 1)\n\nif __name__ == \"__main__\":\n    main()"