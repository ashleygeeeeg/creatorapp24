#!/usr/bin/env python3
"""
Backend API Testing for maligeeAi
Tests all endpoints as specified in the review request
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BASE_URL = "https://genesis-clone-1.preview.emergentagent.com/api"

def test_api_root():
    """Test GET /api/ - Should return message 'maligeeAi API is running'"""
    print("🧪 Testing GET /api/")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "maligeeAi API is running":
                print("   ✅ PASS: Correct message returned")
                return True
            else:
                print(f"   ❌ FAIL: Expected message 'maligeeAi API is running', got '{data.get('message')}'")
                return False
        else:
            print(f"   ❌ FAIL: Expected status 200, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_showcase_endpoint():
    """Test GET /api/showcase - Should return list of showcase items"""
    print("\n🧪 Testing GET /api/showcase")
    try:
        response = requests.get(f"{BASE_URL}/showcase")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Found {len(data)} showcase items")
            
            if isinstance(data, list) and len(data) > 0:
                # Check structure of first item
                first_item = data[0]
                required_fields = ['id', 'mobile_image', 'laptop_image', 'order']
                missing_fields = [field for field in required_fields if field not in first_item]
                
                if not missing_fields:
                    print("   ✅ PASS: Showcase items have correct structure")
                    print(f"   Sample item: {json.dumps(first_item, indent=2)}")
                    return True
                else:
                    print(f"   ❌ FAIL: Missing fields in showcase item: {missing_fields}")
                    return False
            else:
                print("   ❌ FAIL: Expected non-empty list of showcase items")
                return False
        else:
            print(f"   ❌ FAIL: Expected status 200, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_features_endpoint():
    """Test GET /api/features - Should return list of features"""
    print("\n🧪 Testing GET /api/features")
    try:
        response = requests.get(f"{BASE_URL}/features")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Found {len(data)} features")
            
            if isinstance(data, list) and len(data) > 0:
                # Check structure of first item
                first_item = data[0]
                required_fields = ['id', 'icon', 'title', 'description', 'mockup_type', 'order']
                missing_fields = [field for field in required_fields if field not in first_item]
                
                if not missing_fields:
                    print("   ✅ PASS: Features have correct structure")
                    print(f"   Sample feature: {json.dumps(first_item, indent=2)}")
                    return True
                else:
                    print(f"   ❌ FAIL: Missing fields in feature item: {missing_fields}")
                    return False
            else:
                print("   ❌ FAIL: Expected non-empty list of features")
                return False
        else:
            print(f"   ❌ FAIL: Expected status 200, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_stats_endpoint():
    """Test GET /api/stats - Should return stats object"""
    print("\n🧪 Testing GET /api/stats")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            required_fields = ['users_count', 'description']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("   ✅ PASS: Stats have correct structure")
                return True
            else:
                print(f"   ❌ FAIL: Missing fields in stats: {missing_fields}")
                return False
        else:
            print(f"   ❌ FAIL: Expected status 200, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_waitlist_creation():
    """Test POST /api/waitlist - Should create waitlist entry"""
    print("\n🧪 Testing POST /api/waitlist")
    try:
        test_data = {
            "email": "john.doe@example.com",
            "name": "John Doe"
        }
        
        response = requests.post(f"{BASE_URL}/waitlist", json=test_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            required_fields = ['id', 'email', 'name', 'created_at']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields and data['email'] == test_data['email']:
                print("   ✅ PASS: Waitlist entry created successfully")
                return True, data
            else:
                print(f"   ❌ FAIL: Missing fields or incorrect data: {missing_fields}")
                return False, None
        else:
            print(f"   ❌ FAIL: Expected status 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, None

def test_waitlist_duplicate():
    """Test POST /api/waitlist with duplicate email - Should return 409"""
    print("\n🧪 Testing POST /api/waitlist (duplicate email)")
    try:
        test_data = {
            "email": "john.doe@example.com",  # Same email as previous test
            "name": "Jane Doe"
        }
        
        response = requests.post(f"{BASE_URL}/waitlist", json=test_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 409:
            print("   ✅ PASS: Duplicate email correctly rejected with 409 status")
            return True
        else:
            print(f"   ❌ FAIL: Expected status 409 for duplicate email, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_waitlist_count():
    """Test GET /api/waitlist/count - Should return count of waitlist entries"""
    print("\n🧪 Testing GET /api/waitlist/count")
    try:
        response = requests.get(f"{BASE_URL}/waitlist/count")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            if 'count' in data and isinstance(data['count'], int):
                print(f"   ✅ PASS: Waitlist count returned: {data['count']}")
                return True
            else:
                print("   ❌ FAIL: Expected 'count' field with integer value")
                return False
        else:
            print(f"   ❌ FAIL: Expected status 200, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_seed_endpoint():
    """Test POST /api/seed - Should seed/populate the database"""
    print("\n🧪 Testing POST /api/seed")
    try:
        response = requests.post(f"{BASE_URL}/seed")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            if 'message' in data:
                print("   ✅ PASS: Seed endpoint executed successfully")
                return True
            else:
                print("   ❌ FAIL: Expected 'message' field in response")
                return False
        else:
            print(f"   ❌ FAIL: Expected status 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    """Run all backend API tests in the specified order"""
    print("🚀 Starting maligeeAi Backend API Tests")
    print(f"🔗 Testing against: {BASE_URL}")
    print("=" * 60)
    
    test_results = []
    
    # Test in the order specified in the review request
    test_results.append(("GET /api/", test_api_root()))
    test_results.append(("GET /api/showcase", test_showcase_endpoint()))
    test_results.append(("GET /api/features", test_features_endpoint()))
    test_results.append(("GET /api/stats", test_stats_endpoint()))
    
    # Test waitlist creation first, then duplicate
    waitlist_success, waitlist_data = test_waitlist_creation()
    test_results.append(("POST /api/waitlist", waitlist_success))
    
    if waitlist_success:
        test_results.append(("POST /api/waitlist (duplicate)", test_waitlist_duplicate()))
    else:
        print("\n⚠️  Skipping duplicate test due to waitlist creation failure")
        test_results.append(("POST /api/waitlist (duplicate)", False))
    
    test_results.append(("GET /api/waitlist/count", test_waitlist_count()))
    test_results.append(("POST /api/seed", test_seed_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Results: {passed} passed, {failed} failed out of {len(test_results)} tests")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())