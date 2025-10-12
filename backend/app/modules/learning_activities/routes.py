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
from .activity_routes import activities_bp

from .services import LearningActivityService
from bson import ObjectId

learning_bp = Blueprint('learning', __name__)

# Register sub-blueprints
learning_bp.register_blueprint(polls_bp)
learning_bp.register_blueprint(quizzes_bp)
learning_bp.register_blueprint(wordclouds_bp)
learning_bp.register_blueprint(shortanswers_bp)
learning_bp.register_blueprint(minigames_bp)
learning_bp.register_blueprint(activities_bp)

@learning_bp.route('/health', methods=['GET'])
def learning_health():
    """Health check for Learning Activities module"""
    return jsonify({
        'status': 'healthy',
        'module': 'learning_activities',
        'message': 'Learning Activities module is running'
    })


@learning_bp.route('/activities', methods=['GET'])
@jwt_required(locations=["cookies"])
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
                'icon': '📊',
                'enabled': True
            },
            {
                'type': 'quizzes',
                'name': 'Quizzes',
                'description': 'Multiple-choice assessments',
                'icon': '📝',
                'enabled': True
            },
            {
                'type': 'wordclouds',
                'name': 'Word Clouds',
                'description': 'Collaborative word visualizations',
                'icon': '☁️',
                'enabled': True
            },
            {
                'type': 'shortanswers',
                'name': 'Short Answers',
                'description': 'Text response questions',
                'icon': '📄',
                'enabled': True
            }
        ]
    }
    
    return jsonify(response)