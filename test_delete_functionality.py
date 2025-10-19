#!/usr/bin/env python3
"""
Test script for delete functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_delete_functionality():
    """Test the delete functionality for all activity types"""
    print("Testing delete functionality...")
    
    # Test data
    test_data = {
        'polls': {
            'question': 'Test poll for deletion',
            'options': ['Option 1', 'Option 2', 'Option 3'],
            'course_id': 'COMP5241',
            'created_by': 'test_teacher'
        },
        'shortanswers': {
            'question': 'Test short answer for deletion',
            'course_id': 'COMP5241',
            'created_by': 'test_teacher'
        },
        'quizzes': {
            'title': 'Test quiz for deletion',
            'description': 'A test quiz',
            'course_id': 'COMP5241',
            'created_by': 'test_teacher',
            'questions': [
                {
                    'text': 'What is 2+2?',
                    'options': [
                        {'text': '3', 'is_correct': False},
                        {'text': '4', 'is_correct': True},
                        {'text': '5', 'is_correct': False}
                    ],
                    'question_type': 'multiple_choice'
                }
            ]
        }
    }
    
    created_items = {}
    
    try:
        # Create test items
        print("\n1. Creating test items...")
        
        # Create poll
        poll_response = requests.post(f"{BASE_URL}/api/learning/polls", json=test_data['polls'])
        if poll_response.status_code == 201:
            poll_data = poll_response.json()
            created_items['poll_id'] = poll_data.get('poll_id')
            print(f"✓ Poll created: {created_items['poll_id']}")
        else:
            print(f"✗ Failed to create poll: {poll_response.text}")
            
        # Create short answer
        shortanswer_response = requests.post(f"{BASE_URL}/api/learning/shortanswers", json=test_data['shortanswers'])
        if shortanswer_response.status_code == 201:
            shortanswer_data = shortanswer_response.json()
            created_items['shortanswer_id'] = shortanswer_data.get('question_id')
            print(f"✓ Short answer created: {created_items['shortanswer_id']}")
        else:
            print(f"✗ Failed to create short answer: {shortanswer_response.text}")
            
        # Create quiz
        quiz_response = requests.post(f"{BASE_URL}/api/learning/quizzes", json=test_data['quizzes'])
        if quiz_response.status_code == 201:
            quiz_data = quiz_response.json()
            created_items['quiz_id'] = quiz_data.get('quiz_id')
            print(f"✓ Quiz created: {created_items['quiz_id']}")
        else:
            print(f"✗ Failed to create quiz: {quiz_response.text}")
        
        # Test delete functionality
        print("\n2. Testing delete functionality...")
        
        # Delete poll
        if 'poll_id' in created_items:
            delete_response = requests.delete(f"{BASE_URL}/api/learning/delete/polls/{created_items['poll_id']}")
            if delete_response.status_code == 200:
                print("✓ Poll deleted successfully")
            else:
                print(f"✗ Failed to delete poll: {delete_response.text}")
        
        # Delete short answer
        if 'shortanswer_id' in created_items:
            delete_response = requests.delete(f"{BASE_URL}/api/learning/delete/shortanswers/{created_items['shortanswer_id']}")
            if delete_response.status_code == 200:
                print("✓ Short answer deleted successfully")
            else:
                print(f"✗ Failed to delete short answer: {delete_response.text}")
        
        # Delete quiz
        if 'quiz_id' in created_items:
            delete_response = requests.delete(f"{BASE_URL}/api/learning/delete/quizzes/{created_items['quiz_id']}")
            if delete_response.status_code == 200:
                print("✓ Quiz deleted successfully")
            else:
                print(f"✗ Failed to delete quiz: {delete_response.text}")
        
        print("\n3. Verifying deletion...")
        
        # Verify poll deletion
        if 'poll_id' in created_items:
            get_response = requests.get(f"{BASE_URL}/api/learning/polls/{created_items['poll_id']}")
            if get_response.status_code == 404:
                print("✓ Poll successfully deleted (not found)")
            else:
                print("✗ Poll still exists after deletion")
        
        # Verify short answer deletion
        if 'shortanswer_id' in created_items:
            get_response = requests.get(f"{BASE_URL}/api/learning/shortanswers/{created_items['shortanswer_id']}")
            if get_response.status_code == 404:
                print("✓ Short answer successfully deleted (not found)")
            else:
                print("✗ Short answer still exists after deletion")
        
        # Verify quiz deletion
        if 'quiz_id' in created_items:
            get_response = requests.get(f"{BASE_URL}/api/learning/quizzes/{created_items['quiz_id']}")
            if get_response.status_code == 404:
                print("✓ Quiz successfully deleted (not found)")
            else:
                print("✗ Quiz still exists after deletion")
        
        print("\n✅ Delete functionality test completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://localhost:5001")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_delete_functionality()
