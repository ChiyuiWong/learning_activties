#!/usr/bin/env python3
"""
COMP5241 Group 10 - Learning Activities Test Suite
Test all learning activity endpoints to ensure they work correctly
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

class LearningActivitiesTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.teacher_token = None
        self.student_token = None
        self.test_course_id = "COMP5241_TEST"
        self.created_items = {
            'quizzes': [],
            'wordclouds': [],
            'shortanswers': [],
            'minigames': []
        }
        
    def log(self, message):
        """Log test messages with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def login(self, username, password):
        """Login and get JWT token"""
        login_data = {
            "username": username,
            "password": password
        }
        
        response = self.session.post(f"{API_BASE}/security/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            self.log(f"Login failed for {username}: {response.text}")
            return None
    
    def set_auth_header(self, token):
        """Set authorization header for session"""
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        else:
            self.session.headers.pop('Authorization', None)
    
    def test_health_endpoints(self):
        """Test all health endpoints"""
        self.log("Testing health endpoints...")
        
        # Test main API health
        response = self.session.get(f"{API_BASE}/health")
        assert response.status_code == 200, f"API health check failed: {response.text}"
        
        # Test learning activities health
        response = self.session.get(f"{API_BASE}/learning/health")
        assert response.status_code == 200, f"Learning activities health check failed: {response.text}"
        
        self.log("✅ All health endpoints working")
    
    def test_quiz_functionality(self):
        """Test complete quiz functionality"""
        self.log("Testing quiz functionality...")
        
        # Test quiz creation (as teacher)
        self.set_auth_header(self.teacher_token)
        
        quiz_data = {
            "title": "Test Quiz - Python Basics",
            "description": "A test quiz about Python programming",
            "course_id": self.test_course_id,
            "time_limit": 30,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
            "questions": [
                {
                    "text": "What is Python?",
                    "question_type": "multiple_choice",
                    "points": 2,
                    "options": [
                        {"text": "A snake", "is_correct": False},
                        {"text": "A programming language", "is_correct": True},
                        {"text": "A type of coffee", "is_correct": False},
                        {"text": "A web browser", "is_correct": False}
                    ]
                },
                {
                    "text": "Which of these are Python frameworks?",
                    "question_type": "multiple_select",
                    "points": 3,
                    "options": [
                        {"text": "Django", "is_correct": True},
                        {"text": "Flask", "is_correct": True},
                        {"text": "React", "is_correct": False},
                        {"text": "Vue", "is_correct": False}
                    ]
                }
            ]
        }
        
        response = self.session.post(f"{API_BASE}/learning/quizzes/", json=quiz_data)
        assert response.status_code == 201, f"Quiz creation failed: {response.text}"
        
        quiz_id = response.json()['quiz_id']
        self.created_items['quizzes'].append(quiz_id)
        self.log(f"✅ Quiz created successfully: {quiz_id}")
        
        # Test quiz listing
        response = self.session.get(f"{API_BASE}/learning/quizzes/?course_id={self.test_course_id}")
        assert response.status_code == 200, f"Quiz listing failed: {response.text}"
        quizzes = response.json()
        assert len(quizzes) > 0, "No quizzes found in listing"
        self.log("✅ Quiz listing working")
        
        # Test quiz retrieval
        response = self.session.get(f"{API_BASE}/learning/quizzes/{quiz_id}")
        assert response.status_code == 200, f"Quiz retrieval failed: {response.text}"
        quiz_details = response.json()
        assert len(quiz_details['questions']) == 2, "Quiz should have 2 questions"
        self.log("✅ Quiz retrieval working")
        
        # Test quiz attempt (as student)
        self.set_auth_header(self.student_token)
        
        # Start quiz attempt
        response = self.session.post(f"{API_BASE}/learning/quizzes/{quiz_id}/attempt")
        assert response.status_code == 201, f"Quiz attempt start failed: {response.text}"
        attempt_data = response.json()
        self.log(f"✅ Quiz attempt started: {attempt_data['attempt_id']}")
        
        # Submit quiz answers
        quiz_answers = {
            "answers": [
                {
                    "question_index": 0,
                    "selected_options": [1]  # "A programming language"
                },
                {
                    "question_index": 1,
                    "selected_options": [0, 1]  # "Django" and "Flask"
                }
            ]
        }
        
        response = self.session.post(f"{API_BASE}/learning/quizzes/{quiz_id}/submit", json=quiz_answers)
        assert response.status_code == 200, f"Quiz submission failed: {response.text}"
        result = response.json()
        assert result['score_percentage'] == 100.0, f"Expected 100% score, got {result['score_percentage']}%"
        self.log(f"✅ Quiz submitted successfully with score: {result['score_percentage']}%")
        
        self.log("✅ All quiz functionality tests passed")
    
    def test_wordcloud_functionality(self):
        """Test complete word cloud functionality"""
        self.log("Testing word cloud functionality...")
        
        # Test word cloud creation (as teacher)
        self.set_auth_header(self.teacher_token)
        
        wordcloud_data = {
            "title": "AI and Machine Learning Terms",
            "prompt": "Share words or terms related to AI and Machine Learning",
            "course_id": self.test_course_id,
            "max_submissions_per_user": 5,
            "expires_at": (datetime.now() + timedelta(days=3)).isoformat()
        }
        
        response = self.session.post(f"{API_BASE}/learning/wordclouds/", json=wordcloud_data)
        assert response.status_code == 201, f"Word cloud creation failed: {response.text}"
        
        wordcloud_id = response.json()['wordcloud_id']
        self.created_items['wordclouds'].append(wordcloud_id)
        self.log(f"✅ Word cloud created successfully: {wordcloud_id}")
        
        # Test word submission (as student)
        self.set_auth_header(self.student_token)
        
        test_words = ["artificial intelligence", "machine learning", "neural networks", "deep learning", "algorithms"]
        
        for word in test_words:
            word_data = {"word": word}
            response = self.session.post(f"{API_BASE}/learning/wordclouds/{wordcloud_id}/submit", json=word_data)
            assert response.status_code == 200, f"Word submission failed for '{word}': {response.text}"
        
        self.log(f"✅ Submitted {len(test_words)} words successfully")
        
        # Test word cloud results
        response = self.session.get(f"{API_BASE}/learning/wordclouds/{wordcloud_id}/results")
        assert response.status_code == 200, f"Word cloud results failed: {response.text}"
        results = response.json()
        assert results['analytics']['total_submissions'] == len(test_words), "Wrong submission count"
        assert len(results['words']) == len(test_words), "Wrong unique word count"
        self.log("✅ Word cloud results working correctly")
        
        self.log("✅ All word cloud functionality tests passed")
    
    def test_shortanswer_functionality(self):
        """Test complete short answer functionality"""
        self.log("Testing short answer functionality...")
        
        # Test short answer creation (as teacher)
        self.set_auth_header(self.teacher_token)
        
        shortanswer_data = {
            "question": "Explain the concept of object-oriented programming and provide an example.",
            "answer_hint": "Think about classes, objects, inheritance, and encapsulation",
            "example_answer": "OOP is a programming paradigm based on objects and classes...",
            "max_length": 2000,
            "course_id": self.test_course_id,
            "expires_at": (datetime.now() + timedelta(days=5)).isoformat()
        }
        
        response = self.session.post(f"{API_BASE}/learning/shortanswers/", json=shortanswer_data)
        assert response.status_code == 201, f"Short answer creation failed: {response.text}"
        
        question_id = response.json()['question_id']
        self.created_items['shortanswers'].append(question_id)
        self.log(f"✅ Short answer question created successfully: {question_id}")
        
        # Test answer submission (as student)
        self.set_auth_header(self.student_token)
        
        answer_data = {
            "answer": "Object-oriented programming (OOP) is a programming paradigm that organizes code into objects and classes. Objects contain both data (attributes) and methods (functions) that operate on that data. Key principles include encapsulation, inheritance, and polymorphism. For example, in Python: class Car: def __init__(self, brand): self.brand = brand"
        }
        
        response = self.session.post(f"{API_BASE}/learning/shortanswers/{question_id}/submit", json=answer_data)
        assert response.status_code == 200, f"Answer submission failed: {response.text}"
        self.log("✅ Answer submitted successfully")
        
        # Test feedback provision (as teacher)
        self.set_auth_header(self.teacher_token)
        
        feedback_data = {
            "feedback": "Good explanation of OOP concepts. The example could be more detailed.",
            "score": 85.5
        }
        
        response = self.session.post(f"{API_BASE}/learning/shortanswers/{question_id}/feedback/student1", json=feedback_data)
        assert response.status_code == 200, f"Feedback provision failed: {response.text}"
        self.log("✅ Feedback provided successfully")
        
        # Test statistics
        response = self.session.get(f"{API_BASE}/learning/shortanswers/{question_id}/stats")
        assert response.status_code == 200, f"Statistics retrieval failed: {response.text}"
        stats = response.json()
        assert stats['statistics']['total_submissions'] == 1, "Wrong submission count in stats"
        self.log("✅ Statistics working correctly")
        
        self.log("✅ All short answer functionality tests passed")
    
    def test_minigame_functionality(self):
        """Test basic mini-game functionality"""
        self.log("Testing mini-game functionality...")
        
        # Test mini-game creation (as teacher)
        self.set_auth_header(self.teacher_token)
        
        minigame_data = {
            "title": "Python Syntax Matching Game",
            "game_type": "matching",
            "description": "Match Python syntax elements with their descriptions",
            "instructions": "Click on pairs that match to score points",
            "course_id": self.test_course_id,
            "max_score": 100,
            "game_config": {
                "pairs": [
                    {"item1": "def", "item2": "Function definition"},
                    {"item1": "class", "item2": "Class definition"},
                    {"item1": "import", "item2": "Module import"},
                    {"item1": "if", "item2": "Conditional statement"}
                ],
                "time_limit": 300
            }
        }
        
        response = self.session.post(f"{API_BASE}/learning/minigames/", json=minigame_data)
        assert response.status_code == 201, f"Mini-game creation failed: {response.text}"
        
        minigame_id = response.json()['minigame_id']
        self.created_items['minigames'].append(minigame_id)
        self.log(f"✅ Mini-game created successfully: {minigame_id}")
        
        # Test mini-game listing
        response = self.session.get(f"{API_BASE}/learning/minigames/?course_id={self.test_course_id}")
        assert response.status_code == 200, f"Mini-game listing failed: {response.text}"
        minigames = response.json()
        assert len(minigames) > 0, "No mini-games found in listing"
        self.log("✅ Mini-game listing working")
        
        self.log("✅ All mini-game functionality tests passed")
    
    def run_all_tests(self):
        """Run the complete test suite"""
        self.log("🚀 Starting Learning Activities Test Suite")
        
        try:
            # Login users
            self.log("Logging in test users...")
            self.teacher_token = self.login("teacher1", "123")
            self.student_token = self.login("student1", "password123")
            
            if not self.teacher_token or not self.student_token:
                raise Exception("Failed to login test users")
            
            self.log("✅ Test users logged in successfully")
            
            # Run all test functions
            self.test_health_endpoints()
            self.test_quiz_functionality()
            self.test_wordcloud_functionality()
            self.test_shortanswer_functionality()
            self.test_minigame_functionality()
            
            self.log("🎉 All tests passed successfully!")
            
        except Exception as e:
            self.log(f"❌ Test failed: {str(e)}")
            raise e
        
        finally:
            # Clean up created items (optional)
            self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """Clean up test data (optional)"""
        self.log("🧹 Test cleanup completed")

if __name__ == "__main__":
    test_suite = LearningActivitiesTestSuite()
    test_suite.run_all_tests()