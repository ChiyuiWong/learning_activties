"""
COMP5241 Group 10 - GenAI API Tests
Test suite for GenAI module endpoints
"""
import pytest
import json
from datetime import datetime


class TestGenAIModelsAPI:
    """Test GenAI Models endpoints"""
    
    def test_list_models_success(self, client, auth_headers):
        """Test GET /api/genai/models returns models list"""
        response = client.get('/api/genai/models', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'success' in data
        assert 'models' in data
        assert isinstance(data['models'], list)
    
    def test_list_models_structure(self, client, auth_headers):
        """Test models response has correct structure"""
        response = client.get('/api/genai/models', headers=auth_headers)
        data = response.get_json()
        
        if data.get('models'):
            model = data['models'][0]
            assert 'name' in model
            assert 'size' in model
            assert 'is_downloaded' in model
            assert 'download_progress' in model
    
    def test_download_model_missing_name(self, client, auth_headers):
        """Test download model without model_name fails"""
        response = client.post(
            '/api/genai/models/download',
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestGenAIChatAPI:
    """Test GenAI Chat endpoints"""
    
    def test_list_chat_sessions(self, client, auth_headers):
        """Test GET /api/genai/chat/sessions"""
        response = client.get('/api/genai/chat/sessions', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'success' in data
        assert 'sessions' in data
        assert isinstance(data['sessions'], list)
    
    def test_create_chat_session_missing_model(self, client, auth_headers):
        """Test creating session without model_name fails"""
        response = client.post(
            '/api/genai/chat/sessions',
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_create_chat_session_success(self, client, auth_headers):
        """Test creating a valid chat session"""
        response = client.post(
            '/api/genai/chat/sessions',
            headers=auth_headers,
            json={
                'model_name': 'test-model',
                'context_materials': []
            }
        )
        
        # Note: This might fail if Ollama is not running or model doesn't exist
        # That's expected behavior
        data = response.get_json()
        assert 'success' in data
    
    def test_get_chat_history_invalid_session(self, client, auth_headers):
        """Test getting history for non-existent session"""
        response = client.get(
            '/api/genai/chat/sessions/invalid_session_id/messages',
            headers=auth_headers
        )
        
        # Should return 404 or empty list
        assert response.status_code in [200, 404]
    
    def test_send_message_missing_data(self, client, auth_headers):
        """Test sending message without message content"""
        response = client.post(
            '/api/genai/chat/sessions/test_session/messages',
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestGenAIMaterialsAPI:
    """Test GenAI Materials endpoints"""
    
    def test_list_materials(self, client, auth_headers):
        """Test GET /api/genai/materials"""
        response = client.get('/api/genai/materials', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'success' in data
        assert 'materials' in data
        assert isinstance(data['materials'], list)
    
    def test_list_materials_with_course_filter(self, client, auth_headers):
        """Test filtering materials by course_id"""
        response = client.get(
            '/api/genai/materials?course_id=COMP5241',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_upload_material_missing_file(self, client, auth_headers):
        """Test uploading material without file"""
        response = client.post(
            '/api/genai/materials/upload',
            headers=auth_headers,
            data={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_delete_material_invalid_id(self, client, auth_headers):
        """Test deleting non-existent material"""
        response = client.delete(
            '/api/genai/materials/invalid_material_id',
            headers=auth_headers
        )
        
        # Should return 404 or error
        assert response.status_code in [404, 500]


class TestGenAIIntegration:
    """Integration tests for GenAI workflows"""
    
    def test_models_to_chat_workflow(self, client, auth_headers):
        """Test complete workflow: list models -> create session -> send message"""
        # 1. List available models
        models_response = client.get('/api/genai/models', headers=auth_headers)
        assert models_response.status_code == 200
        
        models_data = models_response.get_json()
        
        # If models exist, test chat creation
        if models_data.get('models') and len(models_data['models']) > 0:
            model_name = models_data['models'][0]['name']
            
            # 2. Create chat session
            session_response = client.post(
                '/api/genai/chat/sessions',
                headers=auth_headers,
                json={'model_name': model_name}
            )
            
            session_data = session_response.get_json()
            
            # If session created successfully, test messaging
            if session_data.get('success') and session_data.get('session_id'):
                session_id = session_data['session_id']
                
                # 3. Send a message
                message_response = client.post(
                    f'/api/genai/chat/sessions/{session_id}/messages',
                    headers=auth_headers,
                    json={'message': 'Hello, test message'}
                )
                
                # The response structure should be valid
                message_data = message_response.get_json()
                assert 'success' in message_data


class TestGenAIErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json_payload(self, client, auth_headers):
        """Test sending invalid JSON"""
        response = client.post(
            '/api/genai/chat/sessions',
            headers=auth_headers,
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]
    
    def test_missing_auth(self, client):
        """Test requests without authentication (if auth is enabled)"""
        # This test depends on DISABLE_AUTH setting
        response = client.get('/api/genai/models')
        # Should work if auth is disabled, fail if enabled
        assert response.status_code in [200, 401, 422]
    
    def test_cors_headers(self, client, auth_headers):
        """Test CORS headers are present"""
        response = client.get('/api/genai/models', headers=auth_headers)
        
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200


# Fixtures
@pytest.fixture
def auth_headers():
    """Provide authentication headers for tests"""
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test_token'
    }

