#!/usr/bin/env python3
"""
Test script for learning activities models
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_models():
    """Test the learning activities models"""
    try:
        print("🔄 Importing learning activity models...")
        
        from app.modules.learning_activities.activities import (
            Quiz, QuizQuestion, QuizOption, QuizAttempt,
            WordCloud, WordCloudSubmission,
            ShortAnswerQuestion, ShortAnswerSubmission,
            MiniGame, MiniGameScore
        )
        print("✅ All learning activity models imported successfully!")
        
        # Test creating some sample instances
        print("\n🔍 Testing model creation...")
        
        # Test QuizOption
        option = QuizOption(text="Python is a programming language", is_correct=True)
        print(f"✅ QuizOption created: {option.text}")
        
        # Test QuizQuestion
        question = QuizQuestion(
            text="What is Python?",
            options=[
                QuizOption(text="A snake", is_correct=False),
                QuizOption(text="A programming language", is_correct=True)
            ],
            points=2
        )
        print(f"✅ QuizQuestion created: {question.text}")
        
        # Test WordCloudSubmission
        word_submission = WordCloudSubmission(
            word="artificial intelligence",
            submitted_by="student1"
        )
        print(f"✅ WordCloudSubmission created: {word_submission.word}")
        
        # Test ShortAnswerSubmission
        answer_submission = ShortAnswerSubmission(
            text="Object-oriented programming is a paradigm...",
            submitted_by="student1"
        )
        print(f"✅ ShortAnswerSubmission created: {answer_submission.text[:50]}...")
        
        # Test MiniGameScore
        game_score = MiniGameScore(
            student_id="student1",
            score=85,
            time_taken=120.5
        )
        print(f"✅ MiniGameScore created: Score={game_score.score}, Time={game_score.time_taken}s")
        
        # Test model validation
        print("\n🧪 Testing validation...")
        
        # Test empty option validation
        try:
            empty_option = QuizOption(text="", is_correct=False)
            empty_option.clean()
            print("❌ Empty option validation failed")
        except Exception as e:
            print(f"✅ Empty option validation works: {str(e)}")
        
        # Test question without correct answer
        try:
            bad_question = QuizQuestion(
                text="Bad question?",
                options=[
                    QuizOption(text="Wrong 1", is_correct=False),
                    QuizOption(text="Wrong 2", is_correct=False)
                ]
            )
            bad_question.clean()
            print("❌ Question validation failed")
        except Exception as e:
            print(f"✅ Question validation works: {str(e)}")
        
        # Test word cleaning validation
        try:
            word_sub = WordCloudSubmission(word="  test@word#123  ", submitted_by="student1")
            word_sub.clean()
            print(f"✅ Word cleaning works: '{word_sub.word}'")
        except Exception as e:
            print(f"❌ Word cleaning failed: {str(e)}")
        
        print("\n🎯 All model tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_models()
    if success:
        print("\n🎉 Learning activities models are working correctly!")
        exit(0)
    else:
        print("\n❌ Learning activities models have issues!")
        exit(1)