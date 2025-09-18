#!/usr/bin/env python3
"""
Simple health check test for the Flask server
"""
import requests
import time
import sys

def test_health():
    """Test basic server health"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy: {data}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_learning_health():
    """Test learning activities health endpoint"""
    try:
        response = requests.get("http://localhost:5000/api/learning/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Learning activities module is healthy: {data}")
            return True
        else:
            print(f"❌ Learning activities health check failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Learning activities health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing server health...")
    
    # Test basic health
    if test_health():
        # Test learning activities health
        if test_learning_health():
            print("🎉 All health checks passed!")
            sys.exit(0)
    
    print("❌ Health checks failed!")
    sys.exit(1)