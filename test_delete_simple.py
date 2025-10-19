#!/usr/bin/env python3
"""
Simple test to check if delete endpoints are available
"""
import requests
import json

def test_delete_endpoints():
    """Test if delete endpoints are accessible"""
    base_url = "http://localhost:5000"
    
    print("Testing delete endpoints...")
    
    # Test delete endpoints (should return 405 Method Not Allowed for GET)
    endpoints = [
        "/api/learning/delete/polls/test_id",
        "/api/learning/delete/shortanswers/test_id", 
        "/api/learning/delete/quizzes/test_id",
        "/api/learning/delete/wordclouds/test_id"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 405:  # Method Not Allowed is expected for GET
                print(f"✓ {endpoint} - endpoint exists (405 Method Not Allowed)")
            elif response.status_code == 404:
                print(f"✗ {endpoint} - endpoint not found (404)")
            else:
                print(f"? {endpoint} - unexpected response ({response.status_code})")
        except Exception as e:
            print(f"✗ {endpoint} - error: {e}")

if __name__ == "__main__":
    test_delete_endpoints()
