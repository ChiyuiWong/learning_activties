#!/usr/bin/env python3
"""
Simple GenAI API Test Runner
Run this to quickly test all GenAI endpoints
"""
import requests
import json
from datetime import datetime
from colorama import init, Fore, Style
import sys

# Initialize colorama
init(autoreset=True)

BASE_URL = "http://localhost:5001/api"

def print_success(msg):
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_info(msg):
    print(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")

def print_header(msg):
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{Style.RESET_ALL}\n")


class GenAIAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {"passed": 0, "failed": 0, "total": 0}
    
    def test(self, name, func):
        """Run a test and track results"""
        self.results["total"] += 1
        try:
            func()
            self.results["passed"] += 1
            print_success(name)
            return True
        except AssertionError as e:
            self.results["failed"] += 1
            print_error(f"{name}: {str(e)}")
            return False
        except Exception as e:
            self.results["failed"] += 1
            print_error(f"{name}: Unexpected error - {str(e)}")
            return False
    
    # Models API Tests
    def test_list_models(self):
        """Test GET /api/genai/models"""
        response = self.session.get(f"{BASE_URL}/genai/models")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'success' in data, "Response missing 'success' field"
        assert 'models' in data, "Response missing 'models' field"
        
        print_info(f"  Found {len(data['models'])} models")
        
        if data['models']:
            model = data['models'][0]
            print_info(f"  Sample model: {model.get('name', 'unknown')}")
    
    def test_download_model_validation(self):
        """Test model download validation"""
        response = self.session.post(
            f"{BASE_URL}/genai/models/download",
            json={}
        )
        assert response.status_code == 400, "Should reject missing model_name"
        
        data = response.json()
        assert data['success'] is False, "Should return success=False"
    
    # Chat API Tests
    def test_list_chat_sessions(self):
        """Test GET /api/genai/chat/sessions"""
        response = self.session.get(f"{BASE_URL}/genai/chat/sessions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'success' in data, "Response missing 'success' field"
        assert 'sessions' in data, "Response missing 'sessions' field"
        
        print_info(f"  Found {len(data['sessions'])} chat sessions")
    
    def test_create_session_validation(self):
        """Test chat session creation validation"""
        response = self.session.post(
            f"{BASE_URL}/genai/chat/sessions",
            json={}
        )
        assert response.status_code == 400, "Should reject missing model_name"
    
    def test_send_message_validation(self):
        """Test message sending validation"""
        response = self.session.post(
            f"{BASE_URL}/genai/chat/sessions/test_session/messages",
            json={}
        )
        assert response.status_code == 400, "Should reject missing message"
    
    # Materials API Tests
    def test_list_materials(self):
        """Test GET /api/genai/materials"""
        response = self.session.get(f"{BASE_URL}/genai/materials")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'success' in data, "Response missing 'success' field"
        assert 'materials' in data, "Response missing 'materials' field"
        
        print_info(f"  Found {len(data['materials'])} materials")
    
    def test_upload_material_validation(self):
        """Test material upload validation"""
        response = self.session.post(
            f"{BASE_URL}/genai/materials/upload",
            data={}
        )
        assert response.status_code == 400, "Should reject missing file"
    
    def test_delete_invalid_material(self):
        """Test deleting non-existent material"""
        response = self.session.delete(
            f"{BASE_URL}/genai/materials/invalid_id_12345"
        )
        assert response.status_code in [404, 500], "Should return error for invalid ID"
    
    # Health Check Tests
    def test_health_check(self):
        """Test main health endpoint"""
        response = self.session.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        data = response.json()
        print_info(f"  Status: {data.get('status', 'unknown')}")
    
    def test_genai_health(self):
        """Test GenAI module health"""
        response = self.session.get(f"{BASE_URL}/genai/health")
        assert response.status_code == 200, f"GenAI health check failed"
        
        data = response.json()
        print_info(f"  GenAI Module: {data.get('status', 'unknown')}")
    
    # Integration Tests
    def test_end_to_end_workflow(self):
        """Test complete workflow if Ollama is available"""
        # Get models
        models_response = self.session.get(f"{BASE_URL}/genai/models")
        if models_response.status_code != 200:
            print_info("  Skipping: Models API not available")
            return
        
        models_data = models_response.json()
        if not models_data.get('models'):
            print_info("  Skipping: No models available")
            return
        
        print_info("  Testing end-to-end workflow with available models")
    
    def run_all_tests(self):
        """Run all tests"""
        print_header("GenAI API Test Suite")
        
        # Health Checks
        print_header("Health Checks")
        self.test("API Health Check", self.test_health_check)
        self.test("GenAI Module Health", self.test_genai_health)
        
        # Models API
        print_header("Models API")
        self.test("List Models", self.test_list_models)
        self.test("Download Model Validation", self.test_download_model_validation)
        
        # Chat API
        print_header("Chat API")
        self.test("List Chat Sessions", self.test_list_chat_sessions)
        self.test("Create Session Validation", self.test_create_session_validation)
        self.test("Send Message Validation", self.test_send_message_validation)
        
        # Materials API
        print_header("Materials API")
        self.test("List Materials", self.test_list_materials)
        self.test("Upload Material Validation", self.test_upload_material_validation)
        self.test("Delete Invalid Material", self.test_delete_invalid_material)
        
        # Integration
        print_header("Integration Tests")
        self.test("End-to-End Workflow", self.test_end_to_end_workflow)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print_header("Test Results Summary")
        
        total = self.results["total"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        
        print(f"Total Tests:  {total}")
        print(f"{Fore.GREEN}Passed:       {passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed:       {failed}{Style.RESET_ALL}")
        
        if failed == 0:
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"  ✓ ALL TESTS PASSED!")
            print(f"{'='*60}{Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"  ✗ {failed} TEST(S) FAILED")
            print(f"{'='*60}{Style.RESET_ALL}\n")
        
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    print(f"{Fore.CYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         COMP5241 Group 10 - GenAI API Test Suite         ║")
    print("║                                                           ║")
    print("║  Make sure your Flask server is running on port 5001     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}\n")
    
    try:
        tester = GenAIAPITester()
        exit_code = tester.run_all_tests()
        sys.exit(exit_code)
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server at http://localhost:5001")
        print_info("Make sure your Flask server is running: python start_system.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print_info("\nTests interrupted by user")
        sys.exit(1)

