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
@jwt_required(locations=["cookies", "headers"])
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

@quizzes_bp.route('/<quiz_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_quiz(quiz_id):
    """Delete a quiz"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            quizzes_collection = db.quizzes
            
            # Delete quiz by ObjectId
            result = quizzes_collection.delete_one({'_id': ObjectId(quiz_id)})
            
            if result.deleted_count == 0:
                return jsonify({'error': 'Quiz not found'}), 404
            
            return jsonify({'message': 'Quiz deleted successfully'}), 200
            
    except Exception as e:
        logger.error(f"Error deleting quiz: {e}")
        return jsonify({'error': str(e)}), 500

