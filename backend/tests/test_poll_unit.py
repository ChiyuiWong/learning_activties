"""
COMP5241 Group 10 - Poll System Unit Tests
This file contains comprehensive pytest-based unit tests for the poll system functionality.
"""
import pytest
from app import create_app
from app.modules.learning_activities.poll import Poll, Vote, Option
from mongoengine.errors import NotUniqueError, ValidationError
from datetime import datetime, timedelta
import json

# Test data
TEST_COURSE_ID = 'TEST_COURSE'
TEST_QUESTION = 'Test Poll Question?'
TEST_OPTIONS = ['Option A', 'Option B', 'Option C']


@pytest.fixture
def app():
    """Create and configure test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Authentication headers fixture"""
    # Mock teacher token
    teacher_token = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZWFjaGVyMSIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoxODAwMDAwMDAwfQ.mock_signature_for_testing'
    }
    
    # Mock student token
    student_token = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzdHVkZW50MSIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoxODAwMDAwMDAwfQ.mock_signature_for_testing'
    }
    
    return {
        'teacher': teacher_token,
        'student': student_token
    }


@pytest.fixture
def mock_polls():
    """Create test polls in database and clean up after tests"""
    # Clear any existing test polls
    Poll.objects(course_id=TEST_COURSE_ID).delete()
    Vote.objects().delete()
    
    # Create test polls
    options = [Option(text=opt) for opt in TEST_OPTIONS]
    poll = Poll(
        question=TEST_QUESTION,
        options=options,
        created_by='teacher1',
        course_id=TEST_COURSE_ID
    )
    poll.save()
    
    # Create a second poll that's closed
    closed_poll = Poll(
        question='Closed Poll Question',
        options=[Option(text='Option X'), Option(text='Option Y')],
        created_by='teacher1',
        course_id=TEST_COURSE_ID,
        is_active=False
    )
    closed_poll.save()
    
    # Create a third poll with an expiration date
    expired_poll = Poll(
        question='Expired Poll Question',
        options=[Option(text='Option 1'), Option(text='Option 2')],
        created_by='teacher1',
        course_id=TEST_COURSE_ID,
        expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
    )
    expired_poll.save()
    
    yield {
        'active_poll': poll,
        'closed_poll': closed_poll,
        'expired_poll': expired_poll
    }
    
    # Clean up
    Poll.objects(course_id=TEST_COURSE_ID).delete()
    Vote.objects().delete()


class TestPollAPI:
    """Test class for Poll API endpoints"""
    
    def test_create_poll(self, client, auth_headers):
        """Test creating a new poll"""
        # Prepare test data
        poll_data = {
            'question': 'What is your favorite programming language?',
            'options': ['Python', 'JavaScript', 'Java', 'C++'],
            'course_id': TEST_COURSE_ID
        }
        
        # Make request
        response = client.post(
            '/api/learning/polls',
            headers=auth_headers['teacher'],
            data=json.dumps(poll_data),
            content_type='application/json'
        )
        
        # Assert response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'poll_id' in data
        assert data['message'] == 'Poll created successfully'
        
        # Verify poll was created in database
        poll = Poll.objects.get(id=data['poll_id'])
        assert poll.question == poll_data['question']
        assert len(poll.options) == len(poll_data['options'])
        assert poll.course_id == TEST_COURSE_ID
        
        # Clean up
        poll.delete()
    
    def test_create_poll_missing_fields(self, client, auth_headers):
        """Test creating a poll with missing required fields"""
        # Missing options
        poll_data = {
            'question': 'Incomplete poll?',
            'course_id': TEST_COURSE_ID
        }
        
        response = client.post(
            '/api/learning/polls',
            headers=auth_headers['teacher'],
            data=json.dumps(poll_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_list_polls(self, client, auth_headers, mock_polls):
        """Test listing active polls"""
        response = client.get(
            '/api/learning/polls',
            headers=auth_headers['teacher']
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        
        # Should include at least our active and expired polls (but not closed)
        assert len(data) >= 2
        
        # Verify filter by course
        response = client.get(
            f'/api/learning/polls?course_id={TEST_COURSE_ID}',
            headers=auth_headers['teacher']
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        for poll in data:
            assert poll['course_id'] == TEST_COURSE_ID
    
    def test_get_poll_by_id(self, client, auth_headers, mock_polls):
        """Test getting a specific poll by ID"""
        poll_id = str(mock_polls['active_poll'].id)
        
        response = client.get(
            f'/api/learning/polls/{poll_id}',
            headers=auth_headers['student']
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == poll_id
        assert data['question'] == TEST_QUESTION
        assert len(data['options']) == len(TEST_OPTIONS)
    
    def test_get_nonexistent_poll(self, client, auth_headers):
        """Test getting a poll that doesn't exist"""
        response = client.get(
            '/api/learning/polls/000000000000000000000000',
            headers=auth_headers['student']
        )
        
        assert response.status_code == 404
    
    def test_vote_on_poll(self, client, auth_headers, mock_polls):
        """Test voting on an active poll"""
        poll_id = str(mock_polls['active_poll'].id)
        vote_data = {'option_index': 1}  # Vote for second option
        
        response = client.post(
            f'/api/learning/polls/{poll_id}/vote',
            headers=auth_headers['student'],
            data=json.dumps(vote_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Vote recorded successfully'
        
        # Verify vote was recorded
        poll = Poll.objects.get(id=poll_id)
        assert poll.options[1].votes == 1
        
        # Verify vote record exists
        vote = Vote.objects(poll=poll_id, student_id='student1').first()
        assert vote is not None
        assert vote.option_index == 1
    
    def test_vote_twice(self, client, auth_headers, mock_polls):
        """Test that a student cannot vote twice on the same poll"""
        poll_id = str(mock_polls['active_poll'].id)
        vote_data = {'option_index': 0}
        
        # First vote should succeed
        response = client.post(
            f'/api/learning/polls/{poll_id}/vote',
            headers=auth_headers['student'],
            data=json.dumps(vote_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Second vote should fail
        response = client.post(
            f'/api/learning/polls/{poll_id}/vote',
            headers=auth_headers['student'],
            data=json.dumps(vote_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already voted' in data['error']
    
    def test_vote_closed_poll(self, client, auth_headers, mock_polls):
        """Test voting on a closed poll"""
        poll_id = str(mock_polls['closed_poll'].id)
        vote_data = {'option_index': 0}
        
        response = client.post(
            f'/api/learning/polls/{poll_id}/vote',
            headers=auth_headers['student'],
            data=json.dumps(vote_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'closed' in data['error']
    
    def test_vote_expired_poll(self, client, auth_headers, mock_polls):
        """Test voting on an expired poll"""
        poll_id = str(mock_polls['expired_poll'].id)
        vote_data = {'option_index': 0}
        
        response = client.post(
            f'/api/learning/polls/{poll_id}/vote',
            headers=auth_headers['student'],
            data=json.dumps(vote_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'expired' in data['error']
    
    def test_poll_results(self, client, auth_headers, mock_polls):
        """Test getting poll results"""
        poll = mock_polls['active_poll']
        poll_id = str(poll.id)
        
        # Add some votes first
        poll.options[0].votes = 5
        poll.options[1].votes = 3
        poll.options[2].votes = 2
        poll.save()
        
        response = client.get(
            f'/api/learning/polls/{poll_id}/results',
            headers=auth_headers['teacher']
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['poll_id'] == poll_id
        assert data['total_votes'] == 10
        assert len(data['results']) == 3
        
        # Verify percentages
        assert data['results'][0]['percentage'] == 50.0  # 5/10 = 50%
        assert data['results'][1]['percentage'] == 30.0  # 3/10 = 30%
        assert data['results'][2]['percentage'] == 20.0  # 2/10 = 20%
    
    def test_close_poll(self, client, auth_headers, mock_polls):
        """Test closing an active poll"""
        poll_id = str(mock_polls['active_poll'].id)
        
        response = client.post(
            f'/api/learning/polls/{poll_id}/close',
            headers=auth_headers['teacher']
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Poll closed successfully'
        
        # Verify poll is now closed
        poll = Poll.objects.get(id=poll_id)
        assert poll.is_active is False
    
    def test_unauthorized_close(self, client, auth_headers, mock_polls):
        """Test that only the creator can close a poll"""
        poll_id = str(mock_polls['active_poll'].id)
        
        # Try to close with student token
        response = client.post(
            f'/api/learning/polls/{poll_id}/close',
            headers=auth_headers['student']
        )
        
        # Should fail because student didn't create the poll
        assert response.status_code == 403