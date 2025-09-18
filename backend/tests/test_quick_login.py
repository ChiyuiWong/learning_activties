"""
Quick test script for direct login testing
"""
import requests

# Test teacher login
print("Testing teacher login...")
response = requests.post(
    'http://localhost:5000/api/security/login',
    json={
        'username': 'teacher1',
        'password': 'password123'
    }
)

print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")

# Test student login
print("\nTesting student login...")
response = requests.post(
    'http://localhost:5000/api/security/login',
    json={
        'username': 'student1',
        'password': 'password123'
    }
)

print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")