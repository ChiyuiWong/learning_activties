#!/usr/bin/env python3
"""
Advanced test script for learning activities models - testing helper methods and complex functionality
"""
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_advanced_functionality():
    """Test the advanced functionality of learning activities models"""
    try:
        print("🔄 Testing advanced model functionality...")
        
        from app.modules.learning_activities.activities import (
            Quiz, QuizQuestion, QuizOption, QuizAttempt,
            WordCloud, WordCloudSubmission,
            ShortAnswerQuestion, ShortAnswerSubmission,
            MiniGame, MiniGameScore
        )
        
        # Test Quiz helper methods
        print("\n📝 Testing Quiz functionality...")
        
        quiz_data = Quiz(
            title="Python Basics Quiz",
            description="Test your Python knowledge",
            questions=[
                QuizQuestion(
                    text="What is Python?",
                    options=[
                        QuizOption(text="A snake", is_correct=False),
                        QuizOption(text="A programming language", is_correct=True)
                    ],
                    points=2
                ),
                QuizQuestion(
                    text="Python is interpreted",
                    options=[
                        QuizOption(text="True", is_correct=True),
                        QuizOption(text="False", is_correct=False)
                    ],
                    points=3
                )
            ],
            created_by="teacher1",
            course_id="COMP5241",
            time_limit=30,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        total_points = quiz_data.get_total_points()
        print(f"✅ Quiz total points: {total_points}")
        
        is_expired = quiz_data.is_expired()
        print(f"✅ Quiz expired check: {is_expired}")
        
        # Test WordCloud functionality
        print("\n☁️ Testing WordCloud functionality...")
        
        word_cloud = WordCloud(
            title="AI Terms",
            prompt="Share AI-related terms",
            created_by="teacher1",
            course_id="COMP5241",
            max_submissions_per_user=3,
            expires_at=datetime.utcnow() + timedelta(days=3)
        )
        
        # Add some submissions
        submissions = [
            WordCloudSubmission(word="machine learning", submitted_by="student1"),
            WordCloudSubmission(word="neural networks", submitted_by="student1"),
            WordCloudSubmission(word="machine learning", submitted_by="student2"),
            WordCloudSubmission(word="deep learning", submitted_by="student2")
        ]
        
        for sub in submissions:
            sub.clean()  # Clean the words
            word_cloud.submissions.append(sub)
        
        user_count = word_cloud.get_user_submissions_count("student1")
        print(f"✅ Student1 submissions: {user_count}")
        
        word_frequency = word_cloud.get_word_frequency()
        print(f"✅ Word frequency: {word_frequency}")
        
        # Test ShortAnswerQuestion functionality
        print("\n📄 Testing ShortAnswer functionality...")
        
        short_answer = ShortAnswerQuestion(
            question="Explain object-oriented programming",
            answer_hint="Think about classes and objects",
            created_by="teacher1",
            course_id="COMP5241",
            max_length=1000,
            expires_at=datetime.utcnow() + timedelta(days=5)
        )
        
        # Add submissions
        submissions = [
            ShortAnswerSubmission(text="OOP is about classes and objects...", submitted_by="student1", score=85.5, is_graded=True),
            ShortAnswerSubmission(text="Object oriented programming...", submitted_by="student2", is_graded=False)
        ]
        
        for sub in submissions:
            short_answer.submissions.append(sub)
        
        user_submission = short_answer.get_user_submission("student1")
        print(f"✅ Student1 submission found: {user_submission.text[:30]}...")
        
        graded_count = short_answer.get_graded_submissions_count()
        print(f"✅ Graded submissions: {graded_count}")
        
        # Test MiniGame functionality
        print("\n🎮 Testing MiniGame functionality...")
        
        mini_game = MiniGame(
            title="Python Matching Game",
            game_type="matching",
            description="Match Python terms with definitions",
            created_by="teacher1",
            course_id="COMP5241",
            max_score=100,
            game_config={
                "pairs": [
                    {"term": "def", "definition": "Function definition"},
                    {"term": "class", "definition": "Class definition"}
                ]
            },
            expires_at=datetime.utcnow() + timedelta(days=10)
        )
        
        # Add some scores
        scores = [
            MiniGameScore(student_id="student1", score=85, time_taken=120.5),
            MiniGameScore(student_id="student1", score=92, time_taken=105.2),
            MiniGameScore(student_id="student2", score=78, time_taken=140.0),
            MiniGameScore(student_id="student2", score=88, time_taken=130.5)
        ]
        
        for score in scores:
            mini_game.scores.append(score)
        
        best_score = mini_game.get_user_best_score("student1")
        print(f"✅ Student1 best score: {best_score}")
        
        attempts_count = mini_game.get_user_attempts_count("student1")
        print(f"✅ Student1 attempts: {attempts_count}")
        
        leaderboard = mini_game.get_leaderboard(limit=3)
        print(f"✅ Leaderboard: {[(entry['student_id'], entry['score']) for entry in leaderboard]}")
        
        # Test QuizAttempt functionality
        print("\n⏱️ Testing QuizAttempt functionality...")
        
        attempt = QuizAttempt(
            quiz=None,  # Would be a reference in real usage
            student_id="student1",
            started_at=datetime.utcnow() - timedelta(minutes=15),
            completed_at=datetime.utcnow(),
            score=85.5,
            is_submitted=True
        )
        
        time_taken = attempt.get_time_taken()
        print(f"✅ Time taken: {time_taken} seconds")
        
        print("\n🎯 All advanced functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_advanced_functionality()
    if success:
        print("\n🎉 All learning activities advanced functionality is working correctly!")
        exit(0)
    else:
        print("\n❌ Some advanced functionality has issues!")
        exit(1)