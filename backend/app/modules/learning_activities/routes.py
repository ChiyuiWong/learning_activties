
# --- Poll Endpoints (after blueprint definition) ---
from .poll import Poll, Option, Vote
from mongoengine.errors import ValidationError, NotUniqueError, DoesNotExist
from datetime import datetime

# Place poll endpoints here, after blueprint and imports
"""
COMP5241 Group 10 - Learning Activities Module Routes
Responsible: Charlie
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .polls_routes import polls_bp
from .quizzes_routes import quizzes_bp
from .wordclouds_routes import wordclouds_bp
from .shortanswers_routes import shortanswers_bp
from .minigames_routes import minigames_bp

learning_bp = Blueprint('learning', __name__)

# Register sub-blueprints
learning_bp.register_blueprint(polls_bp)
learning_bp.register_blueprint(quizzes_bp)
learning_bp.register_blueprint(wordclouds_bp)
learning_bp.register_blueprint(shortanswers_bp)
learning_bp.register_blueprint(minigames_bp)

@learning_bp.route('/health', methods=['GET'])
def learning_health():
    """Health check for Learning Activities module"""
    return jsonify({
        'status': 'healthy',
        'module': 'learning_activities',
        'message': 'Learning Activities module is running'
    })


@learning_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_activities():
    """Get all available learning activities"""
    current_user = get_jwt_identity()
    course_id = request.args.get('course_id')
    
    response = {
        'user_id': current_user,
        'available_activities': [
            {
                'type': 'polls',
                'name': 'Interactive Polls',
                'description': 'Quick polls with instant results',
                'endpoint': '/api/learning/polls'
            },
            {
                'type': 'quizzes',
                'name': 'Quizzes',
                'description': 'Multiple-choice quizzes with automatic scoring',
                'endpoint': '/api/learning/quizzes'
            },
            {
                'type': 'wordclouds',
                'name': 'Word Clouds',
                'description': 'Collaborative word clouds for group brainstorming',
                'endpoint': '/api/learning/wordclouds'
            },
            {
                'type': 'shortanswers',
                'name': 'Short Answer Questions',
                'description': 'Free-text responses with teacher feedback',
                'endpoint': '/api/learning/shortanswers'
            },
            {
                'type': 'minigames',
                'name': 'Mini-Games',
                'description': 'Interactive games for learning reinforcement',
                'endpoint': '/api/learning/minigames'
            }
        ]
    }
    
    return jsonify(response), 200


@learning_bp.route('/activities', methods=['POST'])
@jwt_required()
def create_activity():
    """Create learning activity - placeholder for Charlie's implementation"""
    data = request.get_json()
    current_user = get_jwt_identity()
    
    # TODO: Implement activity creation logic
    return jsonify({
        'message': 'Create activity endpoint - to be implemented by Charlie',
        'received_data': data,
        'user': current_user
    }), 201


@learning_bp.route('/activities/<activity_id>', methods=['GET'])
@jwt_required()
def get_activity(activity_id):
    """Get specific learning activity - placeholder for Charlie's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement specific activity retrieval
    return jsonify({
        'message': 'Get specific activity endpoint - to be implemented by Charlie',
        'activity_id': activity_id,
        'user': current_user
    }), 200


@learning_bp.route('/activities/<activity_id>/submit', methods=['POST'])
@jwt_required()
def submit_activity():
    """Submit activity completion - placeholder for Charlie's implementation"""
    data = request.get_json()
    current_user = get_jwt_identity()
    
    # TODO: Implement activity submission logic
    return jsonify({
        'message': 'Submit activity endpoint - to be implemented by Charlie',
        'received_data': data,
        'user': current_user
    }), 200
