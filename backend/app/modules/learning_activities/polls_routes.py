"""
COMP5241 Group 10 - Clean Polls Routes (No Emoji)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from bson import ObjectId
from config.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

polls_bp = Blueprint('polls', __name__, url_prefix='/polls')

@polls_bp.route('/health', methods=['GET'])
def polls_health():
    """Health check for polls module"""
    return jsonify({
        'status': 'healthy',
        'module': 'polls',
        'message': 'Polls module is running'
    })

@polls_bp.route('', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def create_poll():
    """Create a new poll"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        print(f"[INFO] Received poll creation request: {data}")
        
        # Validate required fields
        if not data or not data.get('question') or not data.get('options'):
            return jsonify({'error': 'Question and options are required'}), 400
        
        if len(data.get('options', [])) < 2:
            return jsonify({'error': 'At least 2 options are required'}), 400
        
        # Connect to MongoDB
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                polls_collection = db.polls
                
                # Prepare poll data for MongoDB
                poll_data = {
                    'question': data['question'],
                    'options': [{'text': opt, 'votes': 0} for opt in data['options']],
                    'course_id': data.get('course_id', 'COMP5241'),
                    'created_by': user_id or 'teacher1',
                    'created_at': datetime.now(timezone.utc),
                    'is_active': True,
                    'allow_multiple_votes': data.get('allow_multiple_votes', False)
                }
                
                # Insert the poll into MongoDB
                result = polls_collection.insert_one(poll_data)
                poll_id = str(result.inserted_id)
                
                print(f"[SUCCESS] Poll saved to MongoDB: {data['question']}")
                print(f"[INFO] MongoDB ObjectId: {poll_id}")
                print(f"[INFO] Options: {[opt for opt in data['options']]}")
                
                return jsonify({
                    'success': True,
                    'poll_id': poll_id,
                    'id': poll_id,
                    'question': data['question'],
                    'options': [{'text': opt, 'votes': 0} for opt in data['options']],
                    'course_id': data.get('course_id', 'COMP5241'),
                    'created_by': user_id or 'teacher1',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'is_active': True,
                    'total_votes': 0,
                    'message': 'Poll created successfully in MongoDB'
                }), 201
                
        except Exception as db_error:
            print(f"[ERROR] MongoDB connection failed: {db_error}")
            logger.error(f"Database connection failed: {db_error}")
            return jsonify({
                'error': 'Database connection required',
                'message': 'MongoDB must be running to create polls. Please start MongoDB service.'
            }), 503
        
    except Exception as e:
        print(f"[ERROR] Poll creation failed: {e}")
        logger.error(f"Error creating poll: {e}")
        return jsonify({'error': str(e)}), 500

@polls_bp.route('', methods=['GET'])
# @jwt_required(locations=["cookies", "headers"])  # 临时禁用认证
def get_polls():
    """Get all polls for a course"""
    try:
        course_id = request.args.get('course_id', 'COMP5241')
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
            polls_collection = db.polls
            
            # Get all active polls for the course
            query = {'is_active': True, 'course_id': course_id}
            polls = list(polls_collection.find(query))
            
            # Convert ObjectId to string and calculate total votes
            for poll in polls:
                poll['id'] = str(poll['_id'])
                poll['_id'] = str(poll['_id'])
                poll['created_at'] = poll['created_at'].isoformat() if isinstance(poll['created_at'], datetime) else poll['created_at']
                poll['total_votes'] = sum(option['votes'] for option in poll['options'])
            
            return jsonify(polls), 200
            
    except Exception as e:
        logger.error(f"Error getting polls: {e}")
        return jsonify({'error': str(e)}), 500

@polls_bp.route('/<poll_id>', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def get_poll(poll_id):
    """Get a specific poll by ID"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            polls_collection = db.polls
            
            # Find poll by ObjectId
            poll = polls_collection.find_one({'_id': ObjectId(poll_id)})
            
            if not poll:
                return jsonify({'error': 'Poll not found'}), 404
            
            # Convert ObjectId to string and calculate total votes
            poll['id'] = str(poll['_id'])
            poll['_id'] = str(poll['_id'])
            poll['created_at'] = poll['created_at'].isoformat() if isinstance(poll['created_at'], datetime) else poll['created_at']
            poll['total_votes'] = sum(option['votes'] for option in poll['options'])
            
            return jsonify(poll), 200
            
    except Exception as e:
        logger.error(f"Error getting poll: {e}")
        return jsonify({'error': str(e)}), 500

@polls_bp.route('/<poll_id>/vote', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def vote_on_poll(poll_id):
    """Submit a vote for a poll"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'option_index' not in data:
            return jsonify({'error': 'option_index is required'}), 400
        
        option_index = data['option_index']
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
            polls_collection = db.polls
            votes_collection = db.poll_votes
            
            # Check if poll exists
            poll = polls_collection.find_one({'_id': ObjectId(poll_id)})
            if not poll:
                return jsonify({'error': 'Poll not found'}), 404
            
            # Check if user already voted (unless multiple votes allowed)
            if not poll.get('allow_multiple_votes', False):
                existing_vote = votes_collection.find_one({
                    'poll_id': ObjectId(poll_id),
                    'user_id': user_id
                })
                
                if existing_vote:
                    return jsonify({'error': 'You have already voted on this poll'}), 400
            
            # Validate option index
            if option_index < 0 or option_index >= len(poll['options']):
                return jsonify({'error': 'Invalid option index'}), 400
            
            # Record the vote
            vote_data = {
                'poll_id': ObjectId(poll_id),
                'user_id': user_id,
                'option_index': option_index,
                'voted_at': datetime.now(timezone.utc)
            }
            votes_collection.insert_one(vote_data)
            
            # Update vote count in poll
            polls_collection.update_one(
                {'_id': ObjectId(poll_id)},
                {'$inc': {f'options.{option_index}.votes': 1}}
            )
            
            return jsonify({'success': True, 'message': 'Vote recorded successfully'}), 200
            
    except Exception as e:
        logger.error(f"Error voting on poll: {e}")
        return jsonify({'error': str(e)}), 500

@polls_bp.route('/<poll_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_poll(poll_id):
    """Delete a poll"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            polls_collection = db.polls
            
            # Delete poll by ObjectId
            result = polls_collection.delete_one({'_id': ObjectId(poll_id)})
            
            if result.deleted_count == 0:
                return jsonify({'error': 'Poll not found'}), 404
            
            return jsonify({'message': 'Poll deleted successfully'}), 200
            
    except Exception as e:
        logger.error(f"Error deleting poll: {e}")
        return jsonify({'error': str(e)}), 500
