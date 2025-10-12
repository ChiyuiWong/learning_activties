"""
COMP5241 Group 10 - Health Check Tests
Basic tests to verify system setup
"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_health_endpoint(client):
    """Test main health endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'message' in data


def test_genai_health_endpoint(client):
    """Test GenAI module health endpoint"""
    response = client.get('/api/genai/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['module'] == 'genai'


def test_security_health_endpoint(client):
    """Test Security module health endpoint"""
    response = client.get('/api/security/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['module'] == 'security'


def test_courses_health_endpoint(client):
    """Test Courses module health endpoint"""
    response = client.get('/api/courses/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['module'] == 'courses'


def test_learning_health_endpoint(client):
    """Test Learning Activities module health endpoint"""
    response = client.get('/api/learning/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['module'] == 'learning_activities'


def test_admin_health_endpoint(client):
    """Test Admin module health endpoint"""
    response = client.get('/api/admin/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['module'] == 'admin'
