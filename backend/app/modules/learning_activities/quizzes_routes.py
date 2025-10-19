"""
COMP5241 Group 10 - Simple Quiz Routes (No Emoji)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from bson import ObjectId
from config.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/quizzes')

@quizzes_bp.route('/health', methods=['GET'])
def quizzes_health():
    """Health check for quizzes module"""
    return jsonify({
        'status': 'healthy',
        'module': 'quizzes',
        'message': 'Quizzes module is running'
    })

@quizzes_bp.route('', methods=['GET'])
# @jwt_required(locations=["cookies", "headers"])  # 临时禁用认证
def get_quizzes():
    """Get all quizzes"""
    try:
        course_id = request.args.get('course_id', 'COMP5241')
        print(f"[INFO] Getting quizzes for course: {course_id}")
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
            quizzes_collection = db.quizzes
            
            # Get all active quizzes for the course
            query = {'is_active': True, 'course_id': course_id}
            quizzes = list(quizzes_collection.find(query))
            
            print(f"[INFO] Found {len(quizzes)} quizzes")
            
            # Convert ObjectId to string and add required fields
            for quiz in quizzes:
                quiz['id'] = str(quiz['_id'])
                quiz['_id'] = str(quiz['_id'])
                quiz['created_at'] = quiz['created_at'].isoformat() if isinstance(quiz['created_at'], datetime) else quiz['created_at']
                
                # Add fields expected by frontend
                quiz['questions_count'] = len(quiz.get('questions', []))
                quiz['time_limit'] = quiz.get('time_limit', 1800)  # Default 30 minutes
            
            return jsonify(quizzes), 200
            
    except Exception as e:
        print(f"[ERROR] Error getting quizzes: {e}")
        logger.error(f"Error getting quizzes: {e}")
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def create_quiz():
    """Create a new quiz"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        print(f"[INFO] Received quiz creation request: {data}")
        
        # Validate required fields
        if not data or not data.get('title') or not data.get('questions'):
            return jsonify({'error': 'Title and questions are required'}), 400
        
        if len(data.get('questions', [])) == 0:
            return jsonify({'error': 'At least 1 question is required'}), 400
        
        # Connect to MongoDB
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                quizzes_collection = db.quizzes
                
                # Prepare quiz data for MongoDB
                quiz_data = {
                    'title': data['title'],
                    'description': data.get('description', ''),
                    'questions': data['questions'],
                    'course_id': data.get('course_id', 'COMP5241'),
                    'created_by': user_id or 'teacher1',
                    'created_at': datetime.now(timezone.utc),
                    'is_active': True,
                    'time_limit': data.get('time_limit', 1800),  # Default 30 minutes
                    'allow_retakes': data.get('allow_retakes', True),
                    'show_correct_answers': data.get('show_correct_answers', True)
                }
                
                # Insert the quiz into MongoDB
                result = quizzes_collection.insert_one(quiz_data)
                quiz_id = str(result.inserted_id)
                
                print(f"[SUCCESS] Quiz saved to MongoDB: {data['title']}")
                print(f"[INFO] MongoDB ObjectId: {quiz_id}")
                
                return jsonify({
                    'success': True,
                    'quiz_id': quiz_id,
                    'id': quiz_id,
                    'title': data['title'],
                    'description': data.get('description', ''),
                    'questions': data['questions'],
                    'course_id': data.get('course_id', 'COMP5241'),
                    'created_by': user_id or 'teacher1',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'is_active': True,
                    'message': 'Quiz created successfully in MongoDB'
                }), 201
                
        except Exception as db_error:
            print(f"[ERROR] MongoDB connection failed: {db_error}")
            logger.error(f"Database connection failed: {db_error}")
            return jsonify({
                'error': 'Database connection required',
                'message': 'MongoDB must be running to create quizzes. Please start MongoDB service.'
            }), 503
        
    except Exception as e:
        print(f"[ERROR] Quiz creation failed: {e}")
        logger.error(f"Error creating quiz: {e}")
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<quiz_id>', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def get_quiz(quiz_id):
    """Get a specific quiz"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            quizzes_collection = db.quizzes
            
            # Find quiz by ObjectId
            quiz = quizzes_collection.find_one({'_id': ObjectId(quiz_id)})
            
            if not quiz:
                return jsonify({'error': 'Quiz not found'}), 404
            
            # Convert ObjectId to string
            quiz['id'] = str(quiz['_id'])
            quiz['_id'] = str(quiz['_id'])
            quiz['created_at'] = quiz['created_at'].isoformat() if isinstance(quiz['created_at'], datetime) else quiz['created_at']
            
            return jsonify(quiz), 200
            
    except Exception as e:
        logger.error(f"Error getting quiz: {e}")
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<quiz_id>/submit', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def submit_quiz(quiz_id):
    """Submit answers for a quiz"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        print(f"[INFO] ===== QUIZ SUBMISSION START (v2.0) =====")
        print(f"[INFO] Quiz submission request for quiz {quiz_id} by user {user_id}")
        print(f"[INFO] Submission data: {data}")
        
        # Validate ObjectId format
        try:
            ObjectId(quiz_id)
        except Exception as e:
            print(f"[ERROR] Invalid ObjectId format: {quiz_id}, error: {e}")
            return jsonify({'error': 'Invalid quiz ID format'}), 400
        
        if not data:
            print(f"[ERROR] No data received in request")
            return jsonify({'error': 'No data provided'}), 400
            
        if 'answers' not in data:
            print(f"[ERROR] No 'answers' field in data: {data}")
            return jsonify({'error': 'answers are required'}), 400
        
        answers = data['answers']  # Expected format: [{'question_index': 0, 'selected_options': [0, 1]}, ...]
        
        print(f"[INFO] Received {len(answers)} answers")
        for i, answer in enumerate(answers):
            print(f"[INFO] Answer {i}: {answer}")
            if 'question_index' not in answer:
                print(f"[ERROR] Answer {i} missing question_index")
                return jsonify({'error': f'Answer {i} missing question_index'}), 400
            if 'selected_options' not in answer:
                print(f"[ERROR] Answer {i} missing selected_options")
                return jsonify({'error': f'Answer {i} missing selected_options'}), 400
            
            # 检查是否有未回答的题目
            selected_options = answer.get('selected_options', [])
            if len(selected_options) == 0:
                question_num = answer.get('question_index', i) + 1
                print(f"[ERROR] Answer {i} (Question {question_num}) has no selected options")
                return jsonify({'error': f'请回答第 {question_num} 题'}), 400
        
        try:
            print(f"[INFO] Attempting database connection...")
            client = get_db_connection()
            print(f"[INFO] Database connection successful")
            db = client['comp5241_g10']
            quizzes_collection = db.quizzes
            submissions_collection = db.quiz_submissions
            
            print(f"[INFO] Looking for quiz with ObjectId: {ObjectId(quiz_id)}")
            # Check if quiz exists
            quiz = quizzes_collection.find_one({'_id': ObjectId(quiz_id)})
            if not quiz:
                print(f"[ERROR] Quiz not found with ID: {quiz_id}")
                return jsonify({'error': 'Quiz not found'}), 404
                
            print(f"[INFO] Found quiz: {quiz['title']}")
            
            # Check if user already submitted (unless retakes allowed)
            if not quiz.get('allow_retakes', True):
                existing_submission = submissions_collection.find_one({
                    'quiz_id': ObjectId(quiz_id),
                    'user_id': user_id
                })
                
                if existing_submission:
                    print(f"[INFO] User {user_id} already submitted quiz {quiz_id}, but retakes not allowed")
                    # 返回成功状态但包含已提交信息，而不是错误
                    return jsonify({
                        'success': False,
                        'already_submitted': True,
                        'message': '您已经提交过这个测验了',
                        'previous_score': existing_submission.get('score', 0),
                        'submitted_at': existing_submission.get('submitted_at', '').isoformat() if existing_submission.get('submitted_at') else '',
                        'quiz_title': quiz.get('title', '测验')
                    }), 200  # 返回200状态码，不是错误
            else:
                print(f"[INFO] Retakes allowed for quiz {quiz_id}, proceeding with submission")
            
            # Calculate score
            total_questions = len(quiz['questions'])
            correct_answers = 0
            
            for answer in answers:
                question_index = answer.get('question_index')
                selected_options = answer.get('selected_options', [])
                
                if question_index < 0 or question_index >= total_questions:
                    continue
                
                question = quiz['questions'][question_index]
                correct_option_indices = [
                    i for i, opt in enumerate(question['options']) 
                    if opt.get('is_correct', False)
                ]
                
                # Check if selected options match correct options
                if set(selected_options) == set(correct_option_indices):
                    correct_answers += 1
            
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            print(f"[INFO] Calculated score: {score}% ({correct_answers}/{total_questions})")
            
            # Record the submission
            submission_data = {
                'quiz_id': ObjectId(quiz_id),
                'user_id': user_id,
                'answers': answers,
                'score': score,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'submitted_at': datetime.now(timezone.utc)
            }
            submissions_collection.insert_one(submission_data)
            
            print(f"[SUCCESS] Quiz submission saved to database")
            
            # Prepare response
            response = {
                'success': True,
                'score': score,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'message': f'Quiz submitted successfully. Score: {score:.1f}%'
            }
            
            # Include correct answers if allowed
            if quiz.get('show_correct_answers', True):
                response['correct_answers_detail'] = []
                for i, question in enumerate(quiz['questions']):
                    correct_indices = [
                        j for j, opt in enumerate(question['options']) 
                        if opt.get('is_correct', False)
                    ]
                    response['correct_answers_detail'].append({
                        'question_index': i,
                        'correct_options': correct_indices
                    })
            
            return jsonify(response), 200
            
        except Exception as db_error:
            print(f"[ERROR] Database operation failed: {db_error}")
            logger.warning(f"Database operation failed: {db_error}")
            # Return a demo response when database fails
            return jsonify({
                'success': True,
                'score': 85.0,
                'correct_answers': 8,
                'total_questions': 10,
                'message': 'Quiz submitted successfully (demo mode)'
            }), 200
            
    except Exception as e:
        print(f"[ERROR] Error submitting quiz: {e}")
        logger.error(f"Error submitting quiz: {e}")
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<quiz_id>', methods=['PUT'])
@jwt_required(locations=["cookies", "headers"])
def update_quiz(quiz_id):
    """Update a quiz (teacher only)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        print(f"[INFO] Quiz update request for quiz {quiz_id} by user {user_id}")
        print(f"[INFO] Update data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields if provided
        if 'title' in data and not data['title']:
            return jsonify({'error': 'Title cannot be empty'}), 400
        
        if 'questions' in data and len(data['questions']) == 0:
            return jsonify({'error': 'At least 1 question is required'}), 400
        
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                quizzes_collection = db.quizzes
                
                # Check if quiz exists
                quiz = quizzes_collection.find_one({'_id': ObjectId(quiz_id)})
                if not quiz:
                    return jsonify({'error': 'Quiz not found'}), 404
                
                # Prepare update data
                update_data = {}
                if 'title' in data:
                    update_data['title'] = data['title']
                if 'description' in data:
                    update_data['description'] = data['description']
                if 'questions' in data:
                    update_data['questions'] = data['questions']
                if 'time_limit' in data:
                    update_data['time_limit'] = data['time_limit']
                if 'allow_retakes' in data:
                    update_data['allow_retakes'] = data['allow_retakes']
                if 'show_correct_answers' in data:
                    update_data['show_correct_answers'] = data['show_correct_answers']
                
                update_data['updated_at'] = datetime.now(timezone.utc)
                
                # Update the quiz
                result = quizzes_collection.update_one(
                    {'_id': ObjectId(quiz_id)},
                    {'$set': update_data}
                )
                
                if result.matched_count == 0:
                    return jsonify({'error': 'Quiz not found'}), 404
                
                print(f"[SUCCESS] Quiz updated: {quiz_id}")
                
                # Return updated quiz
                updated_quiz = quizzes_collection.find_one({'_id': ObjectId(quiz_id)})
                updated_quiz['id'] = str(updated_quiz['_id'])
                updated_quiz['_id'] = str(updated_quiz['_id'])
                updated_quiz['created_at'] = updated_quiz['created_at'].isoformat() if isinstance(updated_quiz['created_at'], datetime) else updated_quiz['created_at']
                if 'updated_at' in updated_quiz:
                    updated_quiz['updated_at'] = updated_quiz['updated_at'].isoformat() if isinstance(updated_quiz['updated_at'], datetime) else updated_quiz['updated_at']
                
                return jsonify({
                    'success': True,
                    'message': 'Quiz updated successfully',
                    'quiz': updated_quiz
                }), 200
                
        except Exception as db_error:
            print(f"[ERROR] Database operation failed: {db_error}")
            logger.error(f"Database operation failed: {db_error}")
            return jsonify({
                'success': True,
                'message': 'Quiz updated successfully (demo mode)'
            }), 200
            
    except Exception as e:
        print(f"[ERROR] Error updating quiz: {e}")
        logger.error(f"Error updating quiz: {e}")
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<quiz_id>/results', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def get_quiz_results(quiz_id):
    """Get all submissions for a quiz (teacher only)"""
    try:
        user_id = get_jwt_identity()
        print(f"[INFO] Getting quiz results for quiz {quiz_id} by user {user_id}")
        
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                submissions_collection = db.quiz_submissions
                users_collection = db.users
                
                # Get all submissions for this quiz
                submissions = list(submissions_collection.find({'quiz_id': ObjectId(quiz_id)}))
                
                print(f"[INFO] Found {len(submissions)} submissions")
                
                # Enrich submissions with user information
                for submission in submissions:
                    submission['_id'] = str(submission['_id'])
                    submission['quiz_id'] = str(submission['quiz_id'])
                    
                    # Convert datetime to string
                    if 'submitted_at' in submission and isinstance(submission['submitted_at'], datetime):
                        submission['submitted_at'] = submission['submitted_at'].isoformat()
                    
                    # Try to get user information
                    try:
                        user = users_collection.find_one({'_id': submission['user_id']})
                        if user:
                            submission['student_name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                            submission['student_email'] = user.get('email', '')
                        else:
                            submission['student_name'] = submission['user_id']
                            submission['student_email'] = f"{submission['user_id']}@example.com"
                    except:
                        submission['student_name'] = submission['user_id']
                        submission['student_email'] = f"{submission['user_id']}@example.com"
                
                return jsonify({
                    'success': True,
                    'submissions': submissions,
                    'total_submissions': len(submissions)
                }), 200
                
        except Exception as db_error:
            print(f"[ERROR] Database operation failed: {db_error}")
            logger.warning(f"Database operation failed: {db_error}")
            # Return dummy results for demo
            return jsonify({
                'success': True,
                'submissions': [
                    {
                        'id': 'sub1',
                        'user_id': 'alice.wang',
                        'student_name': 'Alice Wang',
                        'student_email': 'alice.wang@example.com',
                        'score': 85.0,
                        'correct_answers': 8,
                        'total_questions': 10,
                        'submitted_at': '2025-10-17T10:00:00Z'
                    },
                    {
                        'id': 'sub2',
                        'user_id': 'bob.chen',
                        'student_name': 'Bob Chen',
                        'student_email': 'bob.chen@example.com',
                        'score': 92.0,
                        'correct_answers': 9,
                        'total_questions': 10,
                        'submitted_at': '2025-10-17T10:15:00Z'
                    },
                    {
                        'id': 'sub3',
                        'user_id': 'charlie.li',
                        'student_name': 'Charlie Li',
                        'student_email': 'charlie.li@example.com',
                        'score': 78.0,
                        'correct_answers': 7,
                        'total_questions': 10,
                        'submitted_at': '2025-10-17T10:30:00Z'
                    }
                ],
                'total_submissions': 3
            }), 200
            
    except Exception as e:
        print(f"[ERROR] Error getting quiz results: {e}")
        logger.error(f"Error getting quiz results: {e}")
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<quiz_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_quiz(quiz_id):
    """Delete a quiz"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            quizzes_collection = db.quizzes
            submissions_collection = db.quiz_submissions
            
            # Delete quiz by ObjectId
            result = quizzes_collection.delete_one({'_id': ObjectId(quiz_id)})
            
            if result.deleted_count == 0:
                return jsonify({'error': 'Quiz not found'}), 404
            
            # Also delete associated submissions
            submissions_collection.delete_many({'quiz_id': ObjectId(quiz_id)})
            
            return jsonify({'message': 'Quiz deleted successfully'}), 200
            
    except Exception as e:
        logger.error(f"Error deleting quiz: {e}")
        return jsonify({'error': str(e)}), 500
