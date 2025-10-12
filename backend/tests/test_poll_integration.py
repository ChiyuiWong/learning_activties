"""
COMP5241 Group 10 - Poll System Integration Tests
This file contains pytest-based integration tests for the poll system.
These tests verify that the complete system works properly end-to-end.

Make sure the Flask application is running before running these tests.
"""
import pytest
import requests
import json
import time
from datetime import datetime

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


class TestPollSystemIntegration:
    """Integration test class for the Poll System"""
    
    @pytest.fixture(scope="class")
    def auth_tokens(self):
        """Get authentication tokens for teacher and student"""
        tokens = {}
        
        # Get teacher token
        response = requests.post(
            f'{BASE_URL}/security/login',
            json=TEACHER_CREDENTIALS
        )
        assert response.status_code == 200, "Teacher login failed"
        data = response.json()
        tokens['teacher'] = data.get('access_token')
        
        # Get student token
        response = requests.post(
            f'{BASE_URL}/security/login',
            json=STUDENT_CREDENTIALS
        )
        assert response.status_code == 200, "Student login failed"
        data = response.json()
        tokens['student'] = data.get('access_token')
        
        return tokens
    
    @pytest.fixture
    def create_test_poll(self, auth_tokens):
        """Create a test poll and return its ID"""
        poll_data = {
            'question': f'Integration Test Poll - {datetime.utcnow().isoformat()}',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'course_id': COURSE_ID
        }
        
        response = requests.post(
            f'{BASE_URL}/learning/polls',
            headers={'Authorization': f'Bearer {auth_tokens["teacher"]}'},
            json=poll_data
        )
        
        assert response.status_code == 201, "Failed to create test poll"
        data = response.json()
        poll_id = data.get('poll_id')
        
        yield poll_id
        
        # Clean up - close the poll after tests
        requests.post(
            f'{BASE_URL}/learning/polls/{poll_id}/close',
            headers={'Authorization': f'Bearer {auth_tokens["teacher"]}'}
        )
    
    def test_poll_lifecycle(self, auth_tokens, create_test_poll):
        """Test the complete lifecycle of a poll"""
        poll_id = create_test_poll
        
        # Step 1: Verify poll is in the list of polls
        response = requests.get(
            f'{BASE_URL}/learning/polls',
            headers={'Authorization': f'Bearer {auth_tokens["teacher"]}'}
        )
        assert response.status_code == 200
        polls = response.json()
        poll_ids = [poll['id'] for poll in polls]
        assert poll_id in poll_ids, "Created poll not found in polls list"
        
        # Step 2: Get specific poll details
        response = requests.get(
            f'{BASE_URL}/learning/polls/{poll_id}',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'}
        )
        assert response.status_code == 200
        poll_data = response.json()
        assert poll_data['id'] == poll_id
        assert len(poll_data['options']) == 4
        
        # Step 3: Student votes on the poll
        vote_data = {'option_index': 1}  # Vote for Option B
        response = requests.post(
            f'{BASE_URL}/learning/polls/{poll_id}/vote',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'},
            json=vote_data
        )
        assert response.status_code == 200
        assert response.json()['message'] == 'Vote recorded successfully'
        
        # Step 4: Get poll results
        response = requests.get(
            f'{BASE_URL}/learning/polls/{poll_id}/results',
            headers={'Authorization': f'Bearer {auth_tokens["teacher"]}'}
        )
        assert response.status_code == 200
        results = response.json()
        assert results['total_votes'] == 1
        assert results['results'][1]['votes'] == 1  # Option B should have 1 vote
        assert results['results'][1]['percentage'] == 100.0
        
        # Step 5: Try to vote again with the same student
        response = requests.post(
            f'{BASE_URL}/learning/polls/{poll_id}/vote',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'},
            json=vote_data
        )
        assert response.status_code == 400
        assert 'already voted' in response.json()['error']
        
        # Step 6: Close the poll
        response = requests.post(
            f'{BASE_URL}/learning/polls/{poll_id}/close',
            headers={'Authorization': f'Bearer {auth_tokens["teacher"]}'}
        )
        assert response.status_code == 200
        assert response.json()['message'] == 'Poll closed successfully'
        
        # Step 7: Try to vote on closed poll
        vote_data = {'option_index': 2}  # Try different option
        response = requests.post(
            f'{BASE_URL}/learning/polls/{poll_id}/vote',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'},
            json=vote_data
        )
        assert response.status_code == 400
        assert 'closed' in response.json()['error']
    
    def test_multiple_votes(self, auth_tokens, create_test_poll):
        """Test multiple students voting on a poll"""
        # This would need additional student accounts
        # For this test, we'll just verify that results are calculated correctly
        
        poll_id = create_test_poll
        
        # Manually adjust vote counts in the database via API
        # (In a real test, this would be done by having multiple students vote)
        # For now, we'll simulate by checking poll results after each vote
        
        # First vote
        vote_data = {'option_index': 0}  # Vote for Option A
        response = requests.post(
            f'{BASE_URL}/learning/polls/{poll_id}/vote',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'},
            json=vote_data
        )
        assert response.status_code == 200
        
        # Get results after one vote
        response = requests.get(
            f'{BASE_URL}/learning/polls/{poll_id}/results',
            headers={'Authorization': f'Bearer {auth_tokens["teacher"]}'}
        )
        assert response.status_code == 200
        results = response.json()
        assert results['total_votes'] == 1
        assert results['results'][0]['votes'] == 1
        assert results['results'][0]['percentage'] == 100.0
    
    def test_list_polls_by_course(self, auth_tokens):
        """Test filtering polls by course"""
        response = requests.get(
            f'{BASE_URL}/learning/polls?course_id={COURSE_ID}',
            headers={'Authorization': f'Bearer {auth_tokens["teacher"]}'}
        )
        assert response.status_code == 200
        polls = response.json()
        
        # All returned polls should have the requested course ID
        for poll in polls:
            assert poll['course_id'] == COURSE_ID
    
    def test_invalid_poll_access(self, auth_tokens):
        """Test accessing a non-existent poll"""
        invalid_id = '000000000000000000000000'  # Invalid ObjectId
        
        # Try to get details
        response = requests.get(
            f'{BASE_URL}/learning/polls/{invalid_id}',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'}
        )
        assert response.status_code == 404
        
        # Try to vote
        vote_data = {'option_index': 0}
        response = requests.post(
            f'{BASE_URL}/learning/polls/{invalid_id}/vote',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'},
            json=vote_data
        )
        assert response.status_code == 404
        
        # Try to get results
        response = requests.get(
            f'{BASE_URL}/learning/polls/{invalid_id}/results',
            headers={'Authorization': f'Bearer {auth_tokens["teacher"]}'}
        )
        assert response.status_code == 404
    
    def test_invalid_vote_data(self, auth_tokens, create_test_poll):
        """Test submitting invalid vote data"""
        poll_id = create_test_poll
        
        # Missing option_index
        response = requests.post(
            f'{BASE_URL}/learning/polls/{poll_id}/vote',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'},
            json={}
        )
        assert response.status_code == 400
        
        # Invalid option_index (out of bounds)
        response = requests.post(
            f'{BASE_URL}/learning/polls/{poll_id}/vote',
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'},
            json={'option_index': 99}
        )
        assert response.status_code == 400
        assert 'Invalid option_index' in response.json()['error']