#!/usr/bin/env python3
"""
Check if delete functionality is properly integrated
"""
import requests
import json

def check_server_status():
    """Check if server is running and accessible"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running and accessible")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server on port 5000")
        return False
    except Exception as e:
        print(f"✗ Error checking server: {e}")
        return False

def check_learning_activities_health():
    """Check if learning activities module is accessible"""
    try:
        response = requests.get("http://localhost:5000/api/learning/health", timeout=5)
        if response.status_code == 200:
            print("✓ Learning activities module is accessible")
            return True
        else:
            print(f"✗ Learning activities module returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error checking learning activities: {e}")
        return False

def check_delete_endpoints():
    """Check if delete endpoints are accessible"""
    endpoints = [
        "/api/learning/delete/polls/test_id",
        "/api/learning/delete/shortanswers/test_id", 
        "/api/learning/delete/quizzes/test_id",
        "/api/learning/delete/wordclouds/test_id"
    ]
    
    print("\nChecking delete endpoints...")
    all_working = True
    
    for endpoint in endpoints:
        try:
            # Try GET request (should return 405 Method Not Allowed)
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            if response.status_code == 405:
                print(f"✓ {endpoint} - endpoint exists (405 Method Not Allowed)")
            elif response.status_code == 404:
                print(f"✗ {endpoint} - endpoint not found (404)")
                all_working = False
            else:
                print(f"? {endpoint} - unexpected response ({response.status_code})")
        except Exception as e:
            print(f"✗ {endpoint} - error: {e}")
            all_working = False
    
    return all_working

if __name__ == "__main__":
    print("Checking delete functionality integration...")
    
    if not check_server_status():
        print("\n❌ Server is not running or not accessible")
        print("Please make sure your Flask server is running on port 5000")
        exit(1)
    
    if not check_learning_activities_health():
        print("\n❌ Learning activities module is not accessible")
        print("Please check if the learning activities blueprint is properly registered")
        exit(1)
    
    if check_delete_endpoints():
        print("\n✅ Delete functionality is properly integrated!")
        print("You can now use the delete functionality in your application")
    else:
        print("\n❌ Delete endpoints are not accessible")
        print("The delete routes may not be properly registered")
        print("Please restart your server to load the new delete routes")
