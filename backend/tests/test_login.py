"""
Test script for login functionality
"""
import requests
import json
import os
import socket

# Get hostname for codespace URL
hostname = socket.gethostname()
# Use the public URL if in codespace environment
if '.codespaces.' in hostname:
    BASE_URL = f"https://{os.environ.get('CODESPACE_NAME')}-5000.{os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN')}"
else:
    BASE_URL = 'http://localhost:5000'

print(f"Using base URL: {BASE_URL}")

def test_login(username, password):
    """Test login with given credentials"""
    print(f"Testing login with username='{username}', password='{password}'")
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/security/login',
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.ok:
            print("✓ Login successful!")
            return data.get('access_token')
        else:
            print("✗ Login failed")
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    """Main test function"""
    print("==== Testing Teacher Login ====")
    teacher_token = test_login('teacher1', 'password123')
    
    print("\n==== Testing Student Login ====")
    student_token = test_login('student1', 'password123')
    
    print("\n==== Testing Invalid Username ====")
    test_login('invalid_user', 'password123')
    
    print("\n==== Testing Invalid Password ====")
    test_login('teacher1', 'wrong_password')

if __name__ == "__main__":
    main()