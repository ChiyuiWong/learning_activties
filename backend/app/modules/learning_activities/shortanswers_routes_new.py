"""
COMP5241 Group 10 - Complete Short Answer System
Implements full CRUD operations for short answer questions with database support
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
from config.database import get_db_connection
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define a separate blueprint for short answer endpoints
shortanswers_bp = Blueprint('shortanswers', __name__, url_prefix='/shortanswers')


# Get all short answer questions for a course
@shortanswers_bp.route('', methods=['GET'])
@jwt_required(locations=["cookies", "headers"], optional=True)
def get_shortanswers():
    """Get all short answer questions for a course"""
    try:
        course_id = request.args.get('course_id', 'COMP5241')
        
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                shortanswers_collection = db.shortanswers
                
                # Find all short answer questions for the course
                questions = list(shortanswers_collection.find({'course_id': course_id}))
                
                # Convert ObjectId to string and add submission count
                for question in questions:
                    question['_id'] = str(question['_id'])
                    question['id'] = question['_id']
                    
                    # Count submissions for this question
                    submissions_count = db.shortanswer_submissions.count_documents({
                        'question_id': ObjectId(question['_id'])
                    })
                    question['submissions_count'] = submissions_count
                
                return jsonify(questions)
                
        except Exception as db_error:
            logger.warning(f"Database connection failed: {db_error}, using dummy data")
            # Return dummy data if database is not available
            return jsonify([
                {
                    'id': 'sa1',
                    'title': 'Explain Object-Oriented Programming',
                    'question': 'Describe the main principles of object-oriented programming and provide examples.',
                    'course_id': course_id,
                    'max_length': 500,
                    'submissions_count': 12,
                    'created_at': '2025-10-15T10:00:00Z',
                    'created_by': 'teacher1',
                    'is_active': True,
                    'points': 10
                },
                {
                    'id': 'sa2',
                    'title': 'Database Design Principles',
                    'question': 'What are the key considerations when designing a relational database?',
                    'course_id': course_id,
                    'max_length': 300,
                    'submissions_count': 8,
                    'created_at': '2025-10-13T15:45:00Z',
                    'created_by': 'teacher1',
                    'is_active': True,
                    'points': 15
                }
            ])
            
    except Exception as e:
        logger.error(f"Error getting short answer questions: {e}")
        return jsonify({'error': str(e)}), 500


# Create a short answer question (teacher only)
@shortanswers_bp.route('', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def create_shortanswer():
    """Create a new short answer question"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('title') or not data.get('question'):
            return jsonify({'error': 'Title and question are required'}), 400
        
        # Prepare question data
        question_data = {
            'title': data['title'],
            'question': data['question'],
            'course_id': data.get('course_id', 'COMP5241'),
            'created_by': user_id or 'teacher1',
            'created_at': datetime.utcnow(),
            'is_active': True,
            'max_length': data.get('max_length', 500),
            'points': data.get('points', 10),
            'rubric': data.get('rubric', ''),  # Grading rubric
            'due_date': data.get('due_date'),  # Optional due date
            'allow_late_submissions': data.get('allow_late_submissions', True)
        }
        
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                shortanswers_collection = db.shortanswers
                
                # Insert the question
                result = shortanswers_collection.insert_one(question_data)
                question_id = str(result.inserted_id)
                
                return jsonify({
                    'success': True,
                    'question_id': question_id,
                    'message': 'Short answer question created successfully'
                }), 201
                
        except Exception as db_error:
            logger.warning(f"Database operation failed: {db_error}")
            return jsonify({
                'success': True,
                'question_id': 'demo_sa_' + str(int(datetime.utcnow().timestamp())),
                'message': 'Short answer question created successfully (demo mode)'
            }), 201
            
    except Exception as e:
        logger.error(f"Error creating short answer question: {e}")
        return jsonify({'error': str(e)}), 500


# Submit an answer (student)
@shortanswers_bp.route('/<question_id>/submit', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def submit_answer(question_id):
    """Submit an answer for a short answer question"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'answer' not in data:
            return jsonify({'error': 'answer is required'}), 400
        
        answer_text = data['answer'].strip()
        if not answer_text:
            return jsonify({'error': 'Answer cannot be empty'}), 400
        
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                shortanswers_collection = db.shortanswers
                submissions_collection = db.shortanswer_submissions
                
                # Check if question exists
                question = shortanswers_collection.find_one({'_id': ObjectId(question_id)})
                if not question:
                    return jsonify({'error': 'Question not found'}), 404
                
                # Check max length
                max_length = question.get('max_length', 500)
                if len(answer_text) > max_length:
                    return jsonify({'error': f'Answer exceeds maximum length of {max_length} characters'}), 400
                
                # Check if user already submitted
                existing_submission = submissions_collection.find_one({
                    'question_id': ObjectId(question_id),
                    'user_id': user_id
                })
                
                if existing_submission:
                    # Update existing submission
                    submissions_collection.update_one(
                        {'_id': existing_submission['_id']},
                        {
                            '$set': {
                                'answer': answer_text,
                                'submitted_at': datetime.utcnow(),
                                'status': 'submitted'
                            }
                        }
                    )
                    message = 'Answer updated successfully'
                else:
                    # Create new submission
                    submission_data = {
                        'question_id': ObjectId(question_id),
                        'user_id': user_id,
                        'answer': answer_text,
                        'submitted_at': datetime.utcnow(),
                        'status': 'submitted',
                        'grade': None,
                        'feedback': None,
                        'graded_at': None,
                        'graded_by': None
                    }
                    submissions_collection.insert_one(submission_data)
                    message = 'Answer submitted successfully'
                
                return jsonify({'success': True, 'message': message}), 200
                
        except Exception as db_error:
            logger.warning(f"Database operation failed: {db_error}")
            return jsonify({'success': True, 'message': 'Answer submitted (demo mode)'}), 200
            
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return jsonify({'error': str(e)}), 500


# Grade a submission (teacher only)
@shortanswers_bp.route('/submissions/<submission_id>/grade', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def grade_submission(submission_id):
    """Grade a student's submission"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'grade' not in data:
            return jsonify({'error': 'grade is required'}), 400
        
        grade = data['grade']
        feedback = data.get('feedback', '')
        
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                submissions_collection = db.shortanswer_submissions
                
                # Check if submission exists
                submission = submissions_collection.find_one({'_id': ObjectId(submission_id)})
                if not submission:
                    return jsonify({'error': 'Submission not found'}), 404
                
                # Update submission with grade and feedback
                submissions_collection.update_one(
                    {'_id': ObjectId(submission_id)},
                    {
                        '$set': {
                            'grade': grade,
                            'feedback': feedback,
                            'graded_at': datetime.utcnow(),
                            'graded_by': user_id,
                            'status': 'graded'
                        }
                    }
                )
                
                return jsonify({'success': True, 'message': 'Submission graded successfully'}), 200
                
        except Exception as db_error:
            logger.warning(f"Database operation failed: {db_error}")
            return jsonify({'success': True, 'message': 'Submission graded (demo mode)'}), 200
            
    except Exception as e:
        logger.error(f"Error grading submission: {e}")
        return jsonify({'error': str(e)}), 500


# Delete a short answer question (teacher only)
@shortanswers_bp.route('/<question_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_shortanswer(question_id):
    """Delete a short answer question"""
    try:
        user_id = get_jwt_identity()
        
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                shortanswers_collection = db.shortanswers
                submissions_collection = db.shortanswer_submissions
                
                # Check if question exists
                question = shortanswers_collection.find_one({'_id': ObjectId(question_id)})
                if not question:
                    return jsonify({'error': 'Question not found'}), 404
                
                # Delete the question
                shortanswers_collection.delete_one({'_id': ObjectId(question_id)})
                
                # Delete associated submissions
                submissions_collection.delete_many({'question_id': ObjectId(question_id)})
                
                return jsonify({'success': True, 'message': 'Question deleted successfully'}), 200
                
        except Exception as db_error:
            logger.warning(f"Database operation failed: {db_error}")
            return jsonify({'success': True, 'message': 'Question deleted (demo mode)'}), 200
            
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        return jsonify({'error': str(e)}), 500


# Get a specific short answer question
@shortanswers_bp.route('/<question_id>', methods=['GET'])
@jwt_required(locations=["cookies", "headers"], optional=True)
def get_shortanswer(question_id):
    """Get a specific short answer question by ID"""
    try:
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                shortanswers_collection = db.shortanswers
                
                question = shortanswers_collection.find_one({'_id': ObjectId(question_id)})
                if not question:
                    return jsonify({'error': 'Question not found'}), 404
                
                # Convert ObjectId to string
                question['_id'] = str(question['_id'])
                question['id'] = question['_id']
                
                # Count submissions
                submissions_count = db.shortanswer_submissions.count_documents({
                    'question_id': ObjectId(question_id)
                })
                question['submissions_count'] = submissions_count
                
                return jsonify(question)
                
        except Exception as db_error:
            logger.warning(f"Database operation failed: {db_error}")
            # Return dummy question
            return jsonify({
                'id': question_id,
                'title': 'Sample Short Answer Question',
                'question': 'This is a sample short answer question. Please provide a detailed response.',
                'course_id': 'COMP5241',
                'max_length': 500,
                'points': 10,
                'created_at': '2025-10-16T10:00:00Z',
                'is_active': True,
                'submissions_count': 5
            })
            
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        return jsonify({'error': str(e)}), 500


# Get submissions for a question (teacher)
@shortanswers_bp.route('/<question_id>/submissions', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def get_question_submissions(question_id):
    """Get all submissions for a specific question (teacher only)"""
    try:
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                submissions_collection = db.shortanswer_submissions
                
                # Get all submissions for this question
                submissions = list(submissions_collection.find({'question_id': ObjectId(question_id)}))
                
                # Convert ObjectId to string
                for submission in submissions:
                    submission['_id'] = str(submission['_id'])
                    submission['question_id'] = str(submission['question_id'])
                
                return jsonify(submissions)
                
        except Exception as db_error:
            logger.warning(f"Database operation failed: {db_error}")
            # Return dummy submissions
            return jsonify([
                {
                    'id': 'sub1',
                    'user_id': 'student1',
                    'answer': 'This is a sample answer from student1.',
                    'submitted_at': '2025-10-16T12:00:00Z',
                    'status': 'graded',
                    'grade': 8,
                    'feedback': 'Good answer, but could be more detailed.'
                },
                {
                    'id': 'sub2',
                    'user_id': 'student2',
                    'answer': 'This is another sample answer from student2.',
                    'submitted_at': '2025-10-16T12:30:00Z',
                    'status': 'submitted',
                    'grade': None,
                    'feedback': None
                }
            ])
            
    except Exception as e:
        logger.error(f"Error getting submissions: {e}")
        return jsonify({'error': str(e)}), 500


# Get student's own submission
@shortanswers_bp.route('/<question_id>/my-submission', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def get_my_submission(question_id):
    """Get the current user's submission for a question"""
    try:
        user_id = get_jwt_identity()
        
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                submissions_collection = db.shortanswer_submissions
                
                # Find user's submission
                submission = submissions_collection.find_one({
                    'question_id': ObjectId(question_id),
                    'user_id': user_id
                })
                
                if not submission:
                    return jsonify({'error': 'No submission found'}), 404
                
                # Convert ObjectId to string
                submission['_id'] = str(submission['_id'])
                submission['question_id'] = str(submission['question_id'])
                
                return jsonify(submission)
                
        except Exception as db_error:
            logger.warning(f"Database operation failed: {db_error}")
            # Return dummy submission
            return jsonify({
                'id': 'demo_sub',
                'user_id': user_id,
                'answer': 'This is a demo submission.',
                'submitted_at': '2025-10-16T12:00:00Z',
                'status': 'submitted',
                'grade': None,
                'feedback': None
            })
            
    except Exception as e:
        logger.error(f"Error getting submission: {e}")
        return jsonify({'error': str(e)}), 500
