"""
COMP5241 Group 10 - Quiz Routes
API endpoints for quiz functionality
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from .activities import Quiz, QuizQuestion, QuizOption, QuizAttempt
from datetime import datetime

# Define a separate blueprint for quiz endpoints
quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/quizzes')

# Create a quiz (teacher only)
@quizzes_bp.route('/', methods=['POST'])
@jwt_required()
def create_quiz():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title') or not data.get('questions') or not data.get('course_id'):
        return jsonify({'error': 'Missing required fields (title, questions, or course_id)'}), 400
    
    # Create quiz questions from the provided data
    questions = []
    for q_data in data.get('questions', []):
        if not q_data.get('text') or not q_data.get('options'):
            return jsonify({'error': 'Each question must have text and options'}), 400
            
        options = []
        has_correct_option = False
        for opt_data in q_data.get('options', []):
            if not isinstance(opt_data, dict) or not opt_data.get('text'):
                return jsonify({'error': 'Each option must have text'}), 400
                
            option = QuizOption(
                text=opt_data.get('text'),
                is_correct=opt_data.get('is_correct', False),
                explanation=opt_data.get('explanation', '')
            )
            options.append(option)
            if opt_data.get('is_correct'):
                has_correct_option = True
                
        # Ensure at least one correct option for each question
        if not has_correct_option:
            return jsonify({'error': 'Each question must have at least one correct option'}), 400
            
        question = QuizQuestion(
            text=q_data.get('text'),
            options=options,
            points=q_data.get('points', 1),
            question_type=q_data.get('question_type', 'multiple_choice')
        )
        questions.append(question)
    
    try:
        quiz = Quiz(
            title=data['title'],
            description=data.get('description', ''),
            questions=questions,
            created_by=user_id,
            course_id=data['course_id'],
            time_limit=data.get('time_limit'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        quiz.save()
        return jsonify({'message': 'Quiz created successfully', 'quiz_id': str(quiz.id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# List quizzes (optionally filter by course)
@quizzes_bp.route('/', methods=['GET'])
@jwt_required()
def list_quizzes():
    course_id = request.args.get('course_id')
    query = Quiz.objects(is_active=True)
    if course_id:
        query = query.filter(course_id=course_id)
    
    # Sort by creation date (newest first)
    quizzes = query.order_by('-created_at')
    result = []
    
    for quiz in quizzes:
        result.append({
            'id': str(quiz.id),
            'title': quiz.title,
            'description': quiz.description,
            'question_count': len(quiz.questions),
            'created_by': quiz.created_by,
            'is_active': quiz.is_active,
            'created_at': quiz.created_at.isoformat(),
            'expires_at': quiz.expires_at.isoformat() if quiz.expires_at else None,
            'course_id': quiz.course_id,
            'time_limit': quiz.time_limit
        })
    return jsonify(result), 200

# Get a specific quiz
@quizzes_bp.route('/<quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        
        # Different response structure for students vs teachers
        user_id = get_jwt_identity()
        is_creator = quiz.created_by == user_id
        
        # Basic quiz data
        result = {
            'id': str(quiz.id),
            'title': quiz.title,
            'description': quiz.description,
            'created_by': quiz.created_by,
            'is_active': quiz.is_active,
            'created_at': quiz.created_at.isoformat(),
            'expires_at': quiz.expires_at.isoformat() if quiz.expires_at else None,
            'course_id': quiz.course_id,
            'time_limit': quiz.time_limit,
            'questions': []
        }
        
        # Add questions with appropriate level of detail
        for i, question in enumerate(quiz.questions):
            q_data = {
                'text': question.text,
                'question_type': question.question_type,
                'points': question.points,
                'options': []
            }
            
            for j, option in enumerate(question.options):
                opt_data = {
                    'text': option.text,
                }
                
                # Only include correct answers and explanations for teachers
                if is_creator:
                    opt_data['is_correct'] = option.is_correct
                    if option.explanation:
                        opt_data['explanation'] = option.explanation
                        
                q_data['options'].append(opt_data)
                
            result['questions'].append(q_data)
            
        return jsonify(result), 200
    except DoesNotExist:
        return jsonify({'error': 'Quiz not found'}), 404

# Submit a quiz attempt
@quizzes_bp.route('/<quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('answers'):
        return jsonify({'error': 'Missing answers in submission'}), 400
        
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        
        # Check if the quiz is still active
        if not quiz.is_active:
            return jsonify({'error': 'Quiz is no longer active'}), 400
            
        # Check if the quiz has expired
        if quiz.expires_at and quiz.expires_at < datetime.utcnow():
            return jsonify({'error': 'Quiz has expired'}), 400
            
        # Check for existing attempt
        existing_attempt = QuizAttempt.objects(quiz=quiz_id, student_id=user_id, completed_at__ne=None).first()
        if existing_attempt:
            return jsonify({'error': 'You have already completed this quiz'}), 400
            
        # Calculate score
        total_score = 0
        max_score = 0
        answers = data.get('answers', [])
        
        # Process each answer
        for q_idx, answer in enumerate(answers):
            # Skip if question index is out of range
            if q_idx >= len(quiz.questions):
                continue
                
            question = quiz.questions[q_idx]
            max_score += question.points
            
            # Get selected option indices
            selected_indices = answer.get('selected_options', [])
            
            # Check if all correct options are selected and no incorrect options are selected
            all_correct = True
            for opt_idx, option in enumerate(question.options):
                is_selected = opt_idx in selected_indices
                
                # If correct option not selected or incorrect option selected
                if (option.is_correct and not is_selected) or (not option.is_correct and is_selected):
                    all_correct = False
                    break
                    
            if all_correct:
                total_score += question.points
        
        # Create or update attempt
        attempt = QuizAttempt.objects(quiz=quiz_id, student_id=user_id).first()
        if attempt:
            attempt.completed_at = datetime.utcnow()
            attempt.answers = answers
            attempt.score = total_score
        else:
            attempt = QuizAttempt(
                quiz=quiz,
                student_id=user_id,
                completed_at=datetime.utcnow(),
                answers=answers,
                score=total_score
            )
            
        attempt.save()
        
        # Calculate percentage
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'score': total_score,
            'max_score': max_score,
            'percentage': round(percentage, 1)
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Quiz not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get quiz results (teacher only)
@quizzes_bp.route('/<quiz_id>/results', methods=['GET'])
@jwt_required()
def quiz_results(quiz_id):
    user_id = get_jwt_identity()
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        
        # Ensure the user is the creator of the quiz
        if quiz.created_by != user_id:
            return jsonify({'error': 'You are not authorized to view these results'}), 403
            
        # Get all attempts for this quiz
        attempts = QuizAttempt.objects(quiz=quiz_id, completed_at__ne=None)
        
        results = []
        for attempt in attempts:
            results.append({
                'student_id': attempt.student_id,
                'started_at': attempt.started_at.isoformat(),
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                'score': attempt.score,
                'percentage': round(attempt.score / sum(q.points for q in quiz.questions) * 100, 1)
            })
            
        # Calculate stats
        if results:
            avg_score = sum(r['score'] for r in results) / len(results)
            highest_score = max(r['score'] for r in results)
            lowest_score = min(r['score'] for r in results)
        else:
            avg_score = highest_score = lowest_score = 0
            
        return jsonify({
            'quiz_id': quiz_id,
            'title': quiz.title,
            'total_attempts': len(results),
            'average_score': round(avg_score, 1),
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'attempts': results
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Quiz not found'}), 404

# Get student's own quiz results
@quizzes_bp.route('/<quiz_id>/my-result', methods=['GET'])
@jwt_required()
def my_quiz_result(quiz_id):
    user_id = get_jwt_identity()
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        attempt = QuizAttempt.objects(quiz=quiz_id, student_id=user_id, completed_at__ne=None).first()
        
        if not attempt:
            return jsonify({'error': 'You have not completed this quiz yet'}), 404
            
        max_score = sum(q.points for q in quiz.questions)
        percentage = (attempt.score / max_score * 100) if max_score > 0 else 0
        
        return jsonify({
            'quiz_id': quiz_id,
            'title': quiz.title,
            'score': attempt.score,
            'max_score': max_score,
            'percentage': round(percentage, 1),
            'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Quiz or attempt not found'}), 404

# Close/deactivate a quiz (teacher only)
@quizzes_bp.route('/<quiz_id>/close', methods=['POST'])
@jwt_required()
def close_quiz(quiz_id):
    user_id = get_jwt_identity()
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        # Only the creator can close the quiz
        if quiz.created_by != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can close this quiz'}), 403
            
        quiz.is_active = False
        quiz.save()
        return jsonify({'message': 'Quiz closed successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'Quiz not found'}), 404