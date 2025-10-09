#!/usr/bin/env python3
"""
Complete API Test Suite for COMP5241 Group 10
Tests all modules: Security, Courses, GenAI, Learning Activities
Run with: uv run python test_all_apis.py
"""
import requests
import json
from colorama import init, Fore, Style
import sys

init(autoreset=True)

BASE_URL = "http://localhost:5001/api"

def print_success(msg):
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_info(msg):
    print(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")

def print_header(msg):
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"  {msg}")
    print(f"{'='*70}{Style.RESET_ALL}\n")


class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {"passed": 0, "failed": 0, "skipped": 0}
    
    def test_endpoint(self, name, method, endpoint, expected_status=200, json_data=None):
        """Generic endpoint tester"""
        try:
            if method == 'GET':
                response = self.session.get(f"{BASE_URL}{endpoint}")
            elif method == 'POST':
                response = self.session.post(f"{BASE_URL}{endpoint}", json=json_data or {})
            elif method == 'PUT':
                response = self.session.put(f"{BASE_URL}{endpoint}", json=json_data or {})
            elif method == 'DELETE':
                response = self.session.delete(f"{BASE_URL}{endpoint}")
            
            if response.status_code == expected_status:
                self.results["passed"] += 1
                print_success(f"{name} - {method} {endpoint}")
                return response
            else:
                self.results["failed"] += 1
                print_error(f"{name} - Expected {expected_status}, got {response.status_code}")
                return response
        except Exception as e:
            self.results["failed"] += 1
            print_error(f"{name} - {str(e)}")
            return None
    
    def test_health_endpoints(self):
        """Test all health check endpoints"""
        print_header("Health Check Endpoints")
        
        self.test_endpoint("Main Health", "GET", "/health")
        self.test_endpoint("Security Health", "GET", "/security/health")
        self.test_endpoint("GenAI Health", "GET", "/genai/health")
        self.test_endpoint("Courses Health", "GET", "/courses/health")
        self.test_endpoint("Learning Activities Health", "GET", "/learning/health")
    
    def test_genai_endpoints(self):
        """Test GenAI module endpoints"""
        print_header("GenAI Module Endpoints")
        
        # Models
        response = self.test_endpoint("List Models", "GET", "/genai/models")
        if response:
            data = response.json()
            print_info(f"  Found {len(data.get('models', []))} models")
        
        self.test_endpoint("Download Model (validation)", "POST", "/genai/models/download", 
                          expected_status=400, json_data={})
        
        # Chat
        self.test_endpoint("List Chat Sessions", "GET", "/genai/chat/sessions")
        self.test_endpoint("Create Session (validation)", "POST", "/genai/chat/sessions", 
                          expected_status=400, json_data={})
        
        # Materials
        response = self.test_endpoint("List Materials", "GET", "/genai/materials")
        if response:
            data = response.json()
            print_info(f"  Found {len(data.get('materials', []))} materials")
    
    def test_courses_endpoints(self):
        """Test Courses module endpoints"""
        print_header("Courses Module Endpoints")
        
        response = self.test_endpoint("List Courses", "GET", "/courses/")
        if response:
            data = response.json()
            print_info(f"  Found {len(data.get('courses', []))} courses")
    
    def test_learning_endpoints(self):
        """Test Learning Activities endpoints"""
        print_header("Learning Activities Endpoints")
        
        # Quizzes
        response = self.test_endpoint("List Quizzes", "GET", "/learning/quizzes/")
        if response:
            data = response.json()
            print_info(f"  Found {len(data)} quizzes")
        
        # Word Clouds
        response = self.test_endpoint("List Word Clouds", "GET", "/learning/wordclouds/")
        if response:
            data = response.json()
            print_info(f"  Found {len(data)} word clouds")
        
        # Short Answers
        response = self.test_endpoint("List Short Answers", "GET", "/learning/shortanswers/")
        if response:
            data = response.json()
            print_info(f"  Found {len(data)} short answers")
        
        # Mini Games
        response = self.test_endpoint("List Mini Games", "GET", "/learning/minigames/")
        if response:
            data = response.json()
            print_info(f"  Found {len(data)} mini games")
        
        # Polls
        response = self.test_endpoint("List Polls", "GET", "/learning/polls/")
        if response:
            data = response.json()
            print_info(f"  Found {len(data)} polls")
    
    def test_security_endpoints(self):
        """Test Security module endpoints (basic checks only)"""
        print_header("Security Module Endpoints")
        
        # These will fail without proper auth, but we're just checking they're reachable
        self.test_endpoint("Get Profile (no auth)", "GET", "/security/profile", 
                          expected_status=401)
    
    def run_all_tests(self):
        """Run all API tests"""
        print(f"{Fore.CYAN}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║     COMP5241 Group 10 - Complete API Test Suite (UV)              ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Style.RESET_ALL}\n")
        
        self.test_health_endpoints()
        self.test_genai_endpoints()
        self.test_courses_endpoints()
        self.test_learning_endpoints()
        self.test_security_endpoints()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print_header("Test Results Summary")
        
        total = self.results["passed"] + self.results["failed"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        
        print(f"Total Tests:  {total}")
        print(f"{Fore.GREEN}Passed:       {passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed:       {failed}{Style.RESET_ALL}")
        
        if failed == 0:
            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"  ✓ ALL TESTS PASSED!")
            print(f"{'='*70}{Style.RESET_ALL}\n")
            return 0
        else:
            print(f"\n{Fore.RED}{'='*70}")
            print(f"  ✗ {failed} TEST(S) FAILED")
            print(f"{'='*70}{Style.RESET_ALL}\n")
            return 1


if __name__ == "__main__":
    try:
        tester = APITester()
        exit_code = tester.run_all_tests()
        sys.exit(exit_code)
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server at http://localhost:5001")
        print_info("Make sure your Flask server is running: uv run python start_system.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print_info("\nTests interrupted by user")
        sys.exit(1)

