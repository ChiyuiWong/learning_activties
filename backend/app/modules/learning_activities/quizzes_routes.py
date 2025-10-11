"""
COMP5241 Group 10 - Quiz Routes
API endpoints for quiz functionality
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define a separate blueprint for quiz endpoints
quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/quizzes')

def validate_quiz_data(data):
    """Validate quiz creation data"""
    errors = []
    
    if not data:
        return ['No data provided']
    
    # Required fields
    if not data.get('title') or not str(data.get('title')).strip():
        errors.append('Title is required and cannot be empty')
    
    if not data.get('course_id') or not str(data.get('course_id')).strip():
        errors.append('Course ID is required and cannot be empty')
    
    if not data.get('questions') or not isinstance(data.get('questions'), list) or len(data.get('questions')) == 0:
        errors.append('At least one question is required')
    
    # Validate questions
    for i, q_data in enumerate(data.get('questions', [])):
        if not q_data.get('text') or not str(q_data.get('text')).strip():
            errors.append(f'Question {i+1}: text is required and cannot be empty')
        
        if not q_data.get('options') or not isinstance(q_data.get('options'), list) or len(q_data.get('options')) < 2:
            errors.append(f'Question {i+1}: at least 2 options are required')
        
        # Validate options
        has_correct_option = False
        for j, opt_data in enumerate(q_data.get('options', [])):
            if not opt_data.get('text') or not str(opt_data.get('text')).strip():
                errors.append(f'Question {i+1}, Option {j+1}: text is required and cannot be empty')
            
            if opt_data.get('is_correct'):
                has_correct_option = True
        
        if not has_correct_option:
            errors.append(f'Question {i+1}: must have at least one correct option')
        
        # Validate points
        points = q_data.get('points', 1)
        if not isinstance(points, int) or points < 1 or points > 100:
            errors.append(f'Question {i+1}: points must be an integer between 1 and 100')
    
    # Validate time limit
    time_limit = data.get('time_limit')
    if time_limit is not None and (not isinstance(time_limit, int) or time_limit < 1 or time_limit > 300):
        errors.append('Time limit must be an integer between 1 and 300 minutes')
    
    # Validate expiration date
    if data.get('expires_at'):
        try:
            expires_at = datetime.fromisoformat(data['expires_at'])
            if expires_at <= datetime.utcnow():
                errors.append('Expiration date must be in the future')
        except ValueError:
            errors.append('Invalid expiration date format')
    
    return errors

# Create a quiz (teacher only)
@quizzes_bp.route('/', methods=['POST'])
@jwt_required(locations=["cookies"])
def create_quiz():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        validation_errors = validate_quiz_data(data)
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Create quiz questions from the provided data
        questions = []
        for q_data in data.get('questions', []):
            options = []
            for opt_data in q_data.get('options', []):
                option = {
                    'text': str(opt_data.get('text')).strip(),
                    'is_correct': bool(opt_data.get('is_correct', False)),
                    'explanation': str(opt_data.get('explanation', '')).strip()
                }
                options.append(option)

            question = {
                'text': str(q_data.get('text')).strip(),
                'options': options,
                'points': int(q_data.get('points', 1)),
                'question_type': q_data.get('question_type', 'multiple_choice')
            }
            questions.append(question)

        # Create and save quiz
        quiz_data = {
            'title': str(data['title']).strip(),
            'description': str(data.get('description', '')).strip(),
            'questions': questions,
            'created_by': user_id,
            'course_id': str(data['course_id']).strip(),
            'time_limit': data.get('time_limit'),
            'expires_at': datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            'is_active': True,
            'created_at': datetime.utcnow()
        }

        result = current_app.db.quizzes.insert_one(quiz_data)
        quiz_data['_id'] = result.inserted_id

        # Calculate total points
        total_points = sum(q['points'] for q in questions)

        logger.info(f"Quiz created successfully by user {user_id}: {quiz_data['_id']}")
        return jsonify({
            'message': 'Quiz created successfully',
            'quiz_id': str(quiz_data['_id']),
            'total_points': total_points
        }), 201
        
    except Exception as e:
        logger.error(f"Quiz creation error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# List quizzes (optionally filter by course)
@quizzes_bp.route('/', methods=['GET'])
@jwt_required(locations=["cookies"])
def list_quizzes():
    try:
        user_id = get_jwt_identity()
        course_id = request.args.get('course_id')
        include_expired = request.args.get('include_expired', 'false').lower() == 'true'
        
        # Build query
        query = {'is_active': True}
        if course_id:
            query['course_id'] = course_id

        # Filter expired quizzes unless specifically requested
        if not include_expired:
            now = datetime.utcnow()
            query['$or'] = [
                {'expires_at': None},
                {'expires_at': {'$gt': now}}
            ]

        # Sort by creation date (newest first)
        quizzes = list(current_app.db.quizzes.find(query).sort('created_at', -1))
        result = []

        for quiz in quizzes:
            # Get user's attempt info
            user_attempts = list(current_app.db.quiz_attempts.find({
                'quiz_id': str(quiz['_id']),
                'student_id': user_id
            }))

            completed_attempts = [a for a in user_attempts if a.get('is_submitted', False)]

            # Calculate total points
            total_points = sum(q['points'] for q in quiz['questions'])

            quiz_data = {
                'id': str(quiz['_id']),
                'title': quiz['title'],
                'description': quiz['description'],
                'question_count': len(quiz['questions']),
                'total_points': total_points,
                'created_by': quiz['created_by'],
                'is_active': quiz['is_active'],
                'created_at': quiz['created_at'].isoformat(),
                'expires_at': quiz['expires_at'].isoformat() if quiz.get('expires_at') else None,
                'course_id': quiz['course_id'],
                'time_limit': quiz['time_limit'],
                'is_expired': quiz.get('expires_at') and quiz['expires_at'] < datetime.utcnow(),
                'user_stats': {
                    'attempts_count': len(user_attempts),
                    'completed_attempts': len(completed_attempts),
                    'best_score': max([a.get('score', 0) for a in completed_attempts], default=0),
                    'has_active_attempt': len([a for a in user_attempts if not a.get('is_submitted', False)]) > 0
                }
            }
            result.append(quiz_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error listing quizzes: {str(e)}")
        return jsonify({'error': 'Failed to retrieve quizzes', 'details': str(e)}), 500

# Get a specific quiz
@quizzes_bp.route('/<quiz_id>', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_quiz(quiz_id):
    try:
        quiz = current_app.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        # Different response structure for students vs teachers
        user_id = get_jwt_identity()
        is_creator = quiz['created_by'] == user_id

        # Basic quiz data
        result = {
            'id': str(quiz['_id']),
            'title': quiz['title'],
            'description': quiz['description'],
            'created_by': quiz['created_by'],
            'is_active': quiz['is_active'],
            'created_at': quiz['created_at'].isoformat(),
            'expires_at': quiz['expires_at'].isoformat() if quiz.get('expires_at') else None,
            'course_id': quiz['course_id'],
            'time_limit': quiz['time_limit'],
            'questions': []
        }

        # Add questions with appropriate level of detail
        for i, question in enumerate(quiz['questions']):
            q_data = {
                'text': question['text'],
                'question_type': question['question_type'],
                'points': question['points'],
                'options': []
            }

            for j, option in enumerate(question['options']):
                opt_data = {
                    'text': option['text'],
                }

                # Only include correct answers and explanations for teachers
                if is_creator:
                    opt_data['is_correct'] = option['is_correct']
                    if option.get('explanation'):
                        opt_data['explanation'] = option['explanation']

                q_data['options'].append(opt_data)

            result['questions'].append(q_data)

        return jsonify(result), 200
    except Exception:
        return jsonify({'error': 'Quiz not found'}), 404

# Start a quiz attempt
@quizzes_bp.route('/<quiz_id>/attempt', methods=['POST'])
@jwt_required(locations=["cookies"])
def start_quiz_attempt(quiz_id):
    try:
        user_id = get_jwt_identity()

        # Validate quiz exists and is available
        quiz = current_app.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        if not quiz.get('is_active', True):
            return jsonify({'error': 'Quiz is no longer active'}), 400

        if quiz.get('expires_at') and quiz['expires_at'] < datetime.utcnow():
            return jsonify({'error': 'Quiz has expired'}), 400

        # Check for existing incomplete attempts
        existing_attempt = current_app.db.quiz_attempts.find_one({
            'quiz_id': quiz_id,
            'student_id': user_id,
            'is_submitted': False
        })

        if existing_attempt:
            # Check if time limit exceeded
            started_at = existing_attempt['started_at']
            time_limit = quiz.get('time_limit')
            if time_limit and (datetime.utcnow() - started_at).total_seconds() / 60 > time_limit:
                current_app.db.quiz_attempts.update_one(
                    {'_id': existing_attempt['_id']},
                    {'$set': {
                        'is_submitted': True,
                        'completed_at': datetime.utcnow()
                    }}
                )
                return jsonify({'error': 'Previous attempt has expired due to time limit'}), 400

            time_remaining = None
            if time_limit:
                elapsed = (datetime.utcnow() - started_at).total_seconds()
                time_remaining = time_limit * 60 - elapsed

            return jsonify({
                'message': 'Existing attempt found',
                'attempt_id': str(existing_attempt['_id']),
                'started_at': existing_attempt['started_at'].isoformat(),
                'time_remaining': time_remaining
            }), 200

        # Check for completed attempts (some quizzes might allow multiple attempts)
        completed_attempts_count = current_app.db.quiz_attempts.count_documents({
            'quiz_id': quiz_id,
            'student_id': user_id,
            'is_submitted': True
        })

        # For now, allow only one attempt per quiz
        if completed_attempts_count > 0:
            return jsonify({'error': 'You have already completed this quiz'}), 400

        # Create new attempt
        attempt_data = {
            'quiz_id': quiz_id,
            'student_id': user_id,
            'started_at': datetime.utcnow(),
            'answers': [],
            'is_submitted': False
        }
        result = current_app.db.quiz_attempts.insert_one(attempt_data)
        attempt_data['_id'] = result.inserted_id

        # Calculate total points
        total_points = sum(q['points'] for q in quiz['questions'])

        return jsonify({
            'message': 'Quiz attempt started successfully',
            'attempt_id': str(attempt_data['_id']),
            'started_at': attempt_data['started_at'].isoformat(),
            'time_limit_minutes': quiz.get('time_limit'),
            'total_questions': len(quiz['questions']),
            'total_points': total_points
        }), 201
        
    except Exception as e:
        logger.error(f"Error starting quiz attempt: {str(e)}")
        return jsonify({'error': 'Failed to start quiz attempt', 'details': str(e)}), 500

# Submit a quiz attempt with improved scoring
@quizzes_bp.route('/<quiz_id>/submit', methods=['POST'])
@jwt_required(locations=["cookies"])
def submit_quiz(quiz_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'answers' not in data:
            return jsonify({'error': 'Missing answers in submission'}), 400

        quiz = current_app.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        # Find the active attempt
        attempt = current_app.db.quiz_attempts.find_one({
            'quiz_id': quiz_id,
            'student_id': user_id,
            'is_submitted': False
        })

        if not attempt:
            return jsonify({'error': 'No active quiz attempt found. Please start the quiz first.'}), 400

        # Check time limit
        started_at = attempt['started_at']
        time_limit = quiz.get('time_limit')
        if time_limit and (datetime.utcnow() - started_at).total_seconds() / 60 > time_limit:
            current_app.db.quiz_attempts.update_one(
                {'_id': attempt['_id']},
                {'$set': {
                    'is_submitted': True,
                    'completed_at': datetime.utcnow()
                }}
            )
            return jsonify({'error': 'Quiz time limit exceeded'}), 400

        # Validate answers format
        answers = data.get('answers', [])
        if not isinstance(answers, list):
            return jsonify({'error': 'Answers must be provided as a list'}), 400

        # Calculate score with detailed feedback
        total_points = 0
        earned_points = 0
        question_results = []

        for q_idx, question in enumerate(quiz['questions']):
            total_points += question['points']

            # Find the answer for this question
            answer_data = None
            for answer in answers:
                if answer.get('question_index') == q_idx:
                    answer_data = answer
                    break

            if not answer_data:
                # No answer provided for this question
                question_results.append({
                    'question_index': q_idx,
                    'correct': False,
                    'points_earned': 0,
                    'points_possible': question['points']
                })
                continue

            selected_options = answer_data.get('selected_options', [])

            # Determine correct answer based on question type
            is_correct = False

            if question['question_type'] in ['multiple_choice', 'true_false']:
                # Single selection questions
                correct_options = [i for i, opt in enumerate(question['options']) if opt['is_correct']]
                is_correct = (len(selected_options) == 1 and
                            selected_options[0] in correct_options and
                            len(correct_options) == 1)

            elif question['question_type'] == 'multiple_select':
                # Multiple selection questions
                correct_options = [i for i, opt in enumerate(question['options']) if opt['is_correct']]
                is_correct = set(selected_options) == set(correct_options)

            points_earned = question['points'] if is_correct else 0
            earned_points += points_earned

            question_results.append({
                'question_index': q_idx,
                'correct': is_correct,
                'points_earned': points_earned,
                'points_possible': question['points'],
                'selected_options': selected_options
            })

        # Update attempt
        completed_at = datetime.utcnow()
        score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0

        current_app.db.quiz_attempts.update_one(
            {'_id': attempt['_id']},
            {'$set': {
                'completed_at': completed_at,
                'answers': answers,
                'score': score_percentage,
                'is_submitted': True
            }}
        )

        logger.info(f"Quiz {quiz_id} submitted by user {user_id}, score: {score_percentage}%")

        return jsonify({
            'message': 'Quiz submitted successfully',
            'attempt_id': str(attempt['_id']),
            'score_percentage': round(score_percentage, 1),
            'points_earned': earned_points,
            'total_points': total_points,
            'time_taken_seconds': (completed_at - started_at).total_seconds(),
            'completed_at': completed_at.isoformat(),
            'question_results': question_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting quiz: {str(e)}")
        return jsonify({'error': 'Failed to submit quiz', 'details': str(e)}), 500

# Get quiz results (teacher only)
@quizzes_bp.route('/<quiz_id>/results', methods=['GET'])
@jwt_required(locations=["cookies"])
def quiz_results(quiz_id):
    user_id = get_jwt_identity()
    
    try:
        quiz = current_app.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        # Ensure the user is the creator of the quiz
        if quiz['created_by'] != user_id:
            return jsonify({'error': 'You are not authorized to view these results'}), 403

        # Get all attempts for this quiz
        attempts = list(current_app.db.quiz_attempts.find({
            'quiz_id': quiz_id,
            'completed_at': {'$ne': None}
        }))

        results = []
        for attempt in attempts:
            results.append({
                'student_id': attempt['student_id'],
                'started_at': attempt['started_at'].isoformat(),
                'completed_at': attempt['completed_at'].isoformat() if attempt.get('completed_at') else None,
                'score': attempt['score'],
                'percentage': round(attempt['score'], 1)
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
            'title': quiz['title'],
            'total_attempts': len(results),
            'average_score': round(avg_score, 1),
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'attempts': results
        }), 200
    except Exception:
        return jsonify({'error': 'Quiz not found'}), 404

# Get student's own quiz results
@quizzes_bp.route('/<quiz_id>/my-result', methods=['GET'])
@jwt_required(locations=["cookies"])
def my_quiz_result(quiz_id):
    user_id = get_jwt_identity()
    
    try:
        quiz = current_app.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        attempt = current_app.db.quiz_attempts.find_one({
            'quiz_id': quiz_id,
            'student_id': user_id,
            'completed_at': {'$ne': None}
        })

        if not attempt:
            return jsonify({'error': 'You have not completed this quiz yet'}), 404

        max_score = sum(q['points'] for q in quiz['questions'])
        percentage = (attempt['score'] / max_score * 100) if max_score > 0 else 0

        return jsonify({
            'quiz_id': quiz_id,
            'title': quiz['title'],
            'score': attempt['score'],
            'max_score': max_score,
            'percentage': round(percentage, 1),
            'completed_at': attempt['completed_at'].isoformat() if attempt.get('completed_at') else None
        }), 200
    except Exception:
        return jsonify({'error': 'Quiz or attempt not found'}), 404

# Close/deactivate a quiz (teacher only)
@quizzes_bp.route('/<quiz_id>/close', methods=['POST'])
@jwt_required(locations=["cookies"])
def close_quiz(quiz_id):
    user_id = get_jwt_identity()
    
    try:
        quiz = current_app.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        # Only the creator can close the quiz
        if quiz['created_by'] != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can close this quiz'}), 403

        current_app.db.quizzes.update_one(
            {'_id': ObjectId(quiz_id)},
            {'$set': {'is_active': False}}
        )
        return jsonify({'message': 'Quiz closed successfully'}), 200
    except Exception:
        return jsonify({'error': 'Quiz not found'}), 404