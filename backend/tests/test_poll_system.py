"""
COMP5241 Group 10 - Poll System Test Script
This script tests the poll system functionality including:
- Poll creation
- Listing polls
- Voting on polls
- Getting poll results
"""
import requests
import json
import time
from pprint import pprint

# Constants
BASE_URL = 'http://localhost:5000/api'
TEACHER_CREDENTIALS = {
    'username': 'teacher1',
    'password': 'password123'
}
STUDENT_CREDENTIALS = {
    'username': 'student1',
    'password': 'password123'
}
COURSE_ID = 'COMP5241'

def login(credentials):
    """Login and get JWT token"""
    response = requests.post(
        f'{BASE_URL}/security/login',
        json=credentials
    )
    
    if response.status_code != 200:
        print(f'Login failed: {response.text}')
        return None
    
    data = response.json()
    return data.get('access_token')

def test_poll_creation(teacher_token):
    """Test creating a new poll"""
    print("\n== Testing Poll Creation ==")
    
    poll_data = {
        'question': 'What is your favorite programming language?',
        'options': ['Python', 'JavaScript', 'Java', 'C++'],
        'course_id': COURSE_ID
    }
    
    response = requests.post(
        f'{BASE_URL}/learning/polls',
        headers={'Authorization': f'Bearer {teacher_token}'},
        json=poll_data
    )
    
    print(f'Status Code: {response.status_code}')
    data = response.json()
    pprint(data)
    
    if response.status_code == 201:
        print('✅ Poll creation successful')
        return data.get('poll_id')
    else:
        print('❌ Poll creation failed')
        return None

def test_list_polls(token):
    """Test listing all polls"""
    print("\n== Testing List Polls ==")
    
    response = requests.get(
        f'{BASE_URL}/learning/polls',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f'Status Code: {response.status_code}')
    data = response.json()
    print(f'Number of polls: {len(data)}')
    
    if response.status_code == 200 and isinstance(data, list):
        print('✅ List polls successful')
        # Print first poll info if available
        if data:
            print("\nSample poll:")
            pprint(data[0])
        return data
    else:
        print('❌ List polls failed')
        return None

def test_vote_poll(student_token, poll_id):
    """Test voting on a poll"""
    print("\n== Testing Voting ==")
    
    vote_data = {
        'option_index': 0  # Vote for the first option
    }
    
    response = requests.post(
        f'{BASE_URL}/learning/polls/{poll_id}/vote',
        headers={'Authorization': f'Bearer {student_token}'},
        json=vote_data
    )
    
    print(f'Status Code: {response.status_code}')
    data = response.json()
    pprint(data)
    
    if response.status_code == 200:
        print('✅ Voting successful')
        return True
    else:
        print('❌ Voting failed')
        return False

def test_poll_results(token, poll_id):
    """Test getting poll results"""
    print("\n== Testing Poll Results ==")
    
    response = requests.get(
        f'{BASE_URL}/learning/polls/{poll_id}/results',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f'Status Code: {response.status_code}')
    data = response.json()
    pprint(data)
    
    if response.status_code == 200:
        print('✅ Get poll results successful')
        return data
    else:
        print('❌ Get poll results failed')
        return None

def test_close_poll(teacher_token, poll_id):
    """Test closing a poll"""
    print("\n== Testing Close Poll ==")
    
    response = requests.post(
        f'{BASE_URL}/learning/polls/{poll_id}/close',
        headers={'Authorization': f'Bearer {teacher_token}'}
    )
    
    print(f'Status Code: {response.status_code}')
    data = response.json()
    pprint(data)
    
    if response.status_code == 200:
        print('✅ Close poll successful')
        return True
    else:
        print('❌ Close poll failed')
        return False

def main():
    """Main test function"""
    print("===== POLL SYSTEM TEST =====")
    
    # Step 1: Login as teacher and student
    print("\nLogging in as teacher...")
    teacher_token = login(TEACHER_CREDENTIALS)
    if not teacher_token:
        print("Teacher login failed, exiting tests")
        return
    
    print("\nLogging in as student...")
    student_token = login(STUDENT_CREDENTIALS)
    if not student_token:
        print("Student login failed, exiting tests")
        return
    
    # Step 2: Create a poll as teacher
    poll_id = test_poll_creation(teacher_token)
    if not poll_id:
        print("Poll creation failed, skipping remaining tests")
        return
    
    # Step 3: List polls
    polls = test_list_polls(teacher_token)
    
    # Step 4: Student votes on the poll
    if poll_id:
        success = test_vote_poll(student_token, poll_id)
        
        # Step 5: Get poll results
        if success:
            results = test_poll_results(teacher_token, poll_id)
            
            # Step 6: Close poll
            if results:
                test_close_poll(teacher_token, poll_id)
    
    print("\n===== TEST COMPLETED =====")

if __name__ == "__main__":
    main()