#!/usr/bin/env python3
"""
Test script for the FastAPI User Login System
This script helps verify the application setup and BigQuery integration.
"""

import requests
import json
import bcrypt
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False

def test_login_with_invalid_credentials():
    """Test login with invalid credentials"""
    print("\n🔍 Testing login with invalid credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": "nonexistent", "password": "wrongpassword"}
        )
        if response.status_code == 401:
            print("✅ Invalid credentials properly rejected")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")
        return False

def test_login_with_valid_credentials():
    """Test login with valid credentials (if user exists)"""
    print("\n🔍 Testing login with valid credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful")
            print(f"   User ID: {data['user_id']}")
            print(f"   Username: {data['username']}")
            print(f"   Role: {data['role']}")
            print(f"   Token: {data['access_token'][:50]}...")
            return data['access_token']
        elif response.status_code == 401:
            print("⚠️  Login failed - user may not exist in database")
            print("   This is expected if the test user hasn't been created")
            return None
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")
        return None

def test_me_endpoint(token):
    """Test the /me endpoint with authentication"""
    if not token:
        print("\n⚠️  Skipping /me endpoint test (no valid token)")
        return False
    
    print("\n🔍 Testing /me endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ /me endpoint working")
            print(f"   User ID: {data['user_id']}")
            print(f"   Username: {data['username']}")
            print(f"   Email: {data['email']}")
            print(f"   Role: {data['role']}")
            print(f"   Is Active: {data['is_active']}")
            return True
        else:
            print(f"❌ /me endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ /me endpoint error: {str(e)}")
        return False

def test_invalid_token():
    """Test /me endpoint with invalid token"""
    print("\n🔍 Testing /me endpoint with invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        
        if response.status_code == 401:
            print("✅ Invalid token properly rejected")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid token test error: {str(e)}")
        return False

def generate_bcrypt_hash(password):
    """Generate bcrypt hash for a password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return password_hash.decode('utf-8')

def print_bigquery_setup_instructions():
    """Print instructions for setting up BigQuery"""
    print("\n" + "="*60)
    print("📋 BIGQUERY SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. Create the BigQuery table with this schema:")
    print("""
CREATE TABLE `practise-bi.user.users` (
  user_id STRING,
  username STRING,
  email STRING,
  password_hash STRING,
  role STRING,
  is_active BOOLEAN,
  created_at TIMESTAMP,
  last_login TIMESTAMP
);
    """)
    
    print("\n2. Insert a test user with bcrypt hashed password:")
    test_hash = generate_bcrypt_hash(TEST_PASSWORD)
    print(f"""
INSERT INTO `practise-bi.user.users` (
  user_id, username, email, password_hash, role, is_active, created_at
) VALUES (
  'test_user_001',
  '{TEST_USERNAME}',
  'test@example.com',
  '{test_hash}',
  'user',
  true,
  CURRENT_TIMESTAMP(),
  NULL
);
    """)
    
    print("\n3. Verify the service account has BigQuery permissions:")
    print("   - BigQuery Data Editor")
    print("   - BigQuery Job User")
    print("   - BigQuery User")
    
    print("\n4. Ensure the service account JSON file is present:")
    print("   - practise-bi-88d1549575a4.json")

def main():
    """Main test function"""
    print("🚀 FastAPI User Login System - Test Suite")
    print("="*50)
    
    # Check if service account file exists
    if not os.path.exists("practise-bi-88d1549575a4.json"):
        print("❌ Service account JSON file not found!")
        print("   Please ensure 'practise-bi-88d1549575a4.json' is in the current directory")
        return
    
    print("✅ Service account JSON file found")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_health_endpoint():
        tests_passed += 1
    
    if test_login_with_invalid_credentials():
        tests_passed += 1
    
    token = test_login_with_valid_credentials()
    if token is not None:
        tests_passed += 1
    
    if test_me_endpoint(token):
        tests_passed += 1
    
    if test_invalid_token():
        tests_passed += 1
        total_tests += 1
    
    # Print results
    print("\n" + "="*50)
    print(f"📊 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The application is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the setup instructions below.")
        print_bigquery_setup_instructions()

if __name__ == "__main__":
    main() 