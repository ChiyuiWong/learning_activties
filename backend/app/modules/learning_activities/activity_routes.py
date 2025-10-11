"""
COMP5241 Group 10 - Generic Learning Activities Routes
API endpoints for creating and managing generic learning activities
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
from config.database import get_db_connection
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define a separate blueprint for activity endpoints
activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def create_activity():
    """Generic endpoint to create any type of learning activity"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Basic validation
        required_fields = ['title', 'activity_type', 'course_id']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields', 
                'details': f"Missing: {', '.join(missing_fields)}"
            }), 400
            
        # Validate activity type
        valid_types = ['quiz', 'poll', 'wordcloud', 'shortanswer', 'minigame']
        if data['activity_type'] not in valid_types:
            return jsonify({
                'error': 'Invalid activity type',
                'details': f"Must be one of: {', '.join(valid_types)}"
            }), 400
        
        # Create base activity record
        activity_data = {
            'title': str(data['title']).strip(),
            'description': str(data.get('description', '')).strip(),
            'activity_type': data['activity_type'],
            'course_id': str(data['course_id']).strip(),
            'created_by': user_id,
            'instructions': str(data.get('instructions', '')).strip(),
            'max_score': int(data.get('max_score', 100)),
            'time_limit': int(data.get('time_limit')) if data.get('time_limit') else None,
            'metadata': data.get('metadata', {}),
            'is_active': data.get('status', 'draft') == 'published',
            'created_at': datetime.utcnow()
        }
        
        # Handle dates if provided
        if data.get('start_date'):
            try:
                activity_data['start_date'] = datetime.fromisoformat(data['start_date'])
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
                
        if data.get('due_date'):
            try:
                activity_data['due_date'] = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({'error': 'Invalid due_date format'}), 400
                
        if data.get('end_date'):
            try:
                activity_data['end_date'] = datetime.fromisoformat(data['end_date'])
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        # Route to the specific activity type creation function
        # This provides a unified API but still delegates to specialized handlers
        activity_type = data['activity_type']
        
        # Connect to DB once
        with get_db_connection() as client:
            db = client['comp5241_g10']
            
            # Create the base activity first
            activities_collection = db.learning_activities
            activity_result = activities_collection.insert_one(activity_data)
            activity_id = activity_result.inserted_id
            
            # For specific types, create type-specific records and link them
            response = None
            
            if activity_type == 'quiz':
                response = _create_quiz(db, activity_data, activity_id, data)
            elif activity_type == 'poll':
                response = _create_poll(db, activity_data, activity_id, data)
            elif activity_type == 'wordcloud':
                response = _create_wordcloud(db, activity_data, activity_id, data)
            elif activity_type == 'shortanswer':
                response = _create_shortanswer(db, activity_data, activity_id, data)
            elif activity_type == 'minigame':
                response = _create_minigame(db, activity_data, activity_id, data)
            
            # If there was an error in the specialized creation, delete the base activity
            if response and 'error' in response:
                activities_collection.delete_one({'_id': activity_id})
                return jsonify(response), 400
            
            return jsonify({
                'success': True,
                'message': f'{activity_type.capitalize()} created successfully',
                'activity': {
                    'id': str(activity_id),
                    'type': activity_type,
                    'title': activity_data['title']
                }
            }), 201
                
    except Exception as e:
        logger.exception(f"Error creating activity: {e}")
        return jsonify({'error': str(e)}), 500

# Helper functions for each activity type
def _create_quiz(db, activity_data, activity_id, data):
    """Create a quiz record"""
    metadata = data.get('metadata', {})
    questions = metadata.get('questions', [])
    
    if not questions:
        return {'error': 'Quiz must have at least one question'}
    
    # Validate questions
    for i, question in enumerate(questions):
        if not question.get('text'):
            return {'error': f'Question {i+1} is missing text'}
            
        options = question.get('options', [])
        if len(options) < 2:
            return {'error': f'Question {i+1} must have at least 2 options'}
            
        has_correct_option = any(opt.get('is_correct') for opt in options)
        if not has_correct_option:
            return {'error': f'Question {i+1} must have at least one correct option'}
    
    # Create quiz record
    quiz_data = {
        'activity_id': activity_id,
        'questions': questions,
        'shuffle_questions': metadata.get('shuffle_questions', False),
        'shuffle_options': metadata.get('shuffle_options', False),
        'passing_score': metadata.get('passing_score', 70),
        'attempts': [] # Will store student attempts
    }
    
    db.quizzes.insert_one(quiz_data)
    return None  # No error

def _create_poll(db, activity_data, activity_id, data):
    """Create a poll record"""
    metadata = data.get('metadata', {})
    question = metadata.get('question')
    options = metadata.get('options', [])
    
    if not question:
        return {'error': 'Poll must have a question'}
        
    if len(options) < 2:
        return {'error': 'Poll must have at least 2 options'}
    
    # Normalize options
    normalized_options = []
    for opt in options:
        if isinstance(opt, str):
            normalized_options.append({'text': opt, 'votes': 0})
        elif isinstance(opt, dict) and 'text' in opt:
            normalized_options.append({'text': opt['text'], 'votes': 0})
    
    if len(normalized_options) < 2:
        return {'error': 'Poll must have at least 2 valid options'}
    
    # Create poll record
    poll_data = {
        'activity_id': activity_id,
        'question': question,
        'options': normalized_options,
        'is_anonymous': metadata.get('is_anonymous', False),
        'allow_multiple_votes': metadata.get('allow_multiple_votes', False),
        'voters': []  # Will track who has voted
    }
    
    db.polls.insert_one(poll_data)
    return None  # No error

def _create_wordcloud(db, activity_data, activity_id, data):
    """Create a word cloud record"""
    metadata = data.get('metadata', {})
    prompt = metadata.get('prompt')
    
    if not prompt:
        return {'error': 'Word cloud must have a prompt'}
    
    # Create word cloud record
    wordcloud_data = {
        'activity_id': activity_id,
        'prompt': prompt,
        'max_submissions_per_user': metadata.get('max_submissions_per_user', 3),
        'min_word_length': metadata.get('min_word_length', 3),
        'filter_profanity': metadata.get('filter_profanity', True),
        'words': [],  # Will store submitted words
        'submissions': {}  # Will track submissions per user
    }
    
    db.wordclouds.insert_one(wordcloud_data)
    return None  # No error

def _create_shortanswer(db, activity_data, activity_id, data):
    """Create a short answer record"""
    metadata = data.get('metadata', {})
    question = metadata.get('question')
    
    if not question:
        return {'error': 'Short answer must have a question'}
    
    # Create short answer record
    shortanswer_data = {
        'activity_id': activity_id,
        'question': question,
        'answer_guidelines': metadata.get('answer_guidelines', ''),
        'max_length': metadata.get('max_length', 1000),
        'rubric': metadata.get('rubric', ''),
        'responses': []  # Will store student responses
    }
    
    db.shortanswers.insert_one(shortanswer_data)
    return None  # No error

def _create_minigame(db, activity_data, activity_id, data):
    """Create a mini-game record"""
    metadata = data.get('metadata', {})
    game_type = metadata.get('game_type')
    
    if not game_type:
        return {'error': 'Mini-game must have a game type'}
        
    valid_game_types = ['matching', 'sorting', 'sequence', 'memory', 'custom']
    if game_type not in valid_game_types:
        return {'error': f'Invalid game type. Must be one of: {", ".join(valid_game_types)}'}
    
    # Create mini-game record
    minigame_data = {
        'activity_id': activity_id,
        'game_type': game_type,
        'game_config': metadata.get('game_config', {}),
        'scores': []  # Will store player scores
    }
    
    db.minigames.insert_one(minigame_data)
    return None  # No error