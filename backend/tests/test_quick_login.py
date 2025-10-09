"""
Quick test script for direct login testing
"""
import requests
import pytest


def test_teacher_login_manual():
    """
    Manual test for teacher login - requires running server
    Note: This test is skipped by default as it requires a running server
    """
    pytest.skip("Manual test - requires running server at localhost:5000")
    
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
    
    assert response.status_code in [200, 401]  # Either success or auth failure is expected


def test_student_login_manual():
    """
    Manual test for student login - requires running server
    Note: This test is skipped by default as it requires a running server
    """
    pytest.skip("Manual test - requires running server at localhost:5000")
    
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
    
    assert response.status_code in [200, 401]  # Either success or auth failure is expected