"""
COMP5241 Group 10 - Learning Activities Routes
Main blueprint that registers sub-blueprints for different activity types
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
<<<<<<< Updated upstream
from .polls_routes import polls_bp
from .quizzes_routes import quizzes_bp
from .wordclouds_routes import wordclouds_bp
from .shortanswers_routes import shortanswers_bp
from .minigames_routes import minigames_bp
from .activity_routes import activities_bp

from .services import LearningActivityService
from bson import ObjectId
=======
>>>>>>> Stashed changes

# Import sub-blueprints
from .quizzes_routes import quizzes_bp
from .polls_routes import polls_bp
from .wordclouds_routes import wordclouds_bp
from .wordclouds_routes_no_auth import wordclouds_no_auth_bp  # 临时无认证版本
from .shortanswers_routes import shortanswers_bp

# Create main learning activities blueprint
learning_bp = Blueprint('learning', __name__, url_prefix='/learning')

# Register sub-blueprints
learning_bp.register_blueprint(quizzes_bp)
learning_bp.register_blueprint(polls_bp)
learning_bp.register_blueprint(wordclouds_bp)
learning_bp.register_blueprint(wordclouds_no_auth_bp)  # 临时无认证版本
learning_bp.register_blueprint(shortanswers_bp)
<<<<<<< Updated upstream
learning_bp.register_blueprint(minigames_bp)
learning_bp.register_blueprint(activities_bp)
=======
>>>>>>> Stashed changes

@learning_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for learning activities module"""
    from flask import current_app
    return jsonify({
        'status': 'healthy',
        'module': 'learning_activities',
        'message': 'Learning activities module is running',
        'auth_disabled': current_app.config.get('DISABLE_AUTH', False),
        'sub_modules': {
            'quizzes': 'registered',
            'polls': 'registered', 
            'wordclouds': 'registered',
            'shortanswers': 'registered'
        }
    })

@learning_bp.route('/', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def get_all_activities():
    """Get all learning activities for a course"""
    try:
        user_id = get_jwt_identity()
        course_id = request.args.get('course_id', 'COMP5241')
        
        # This endpoint requires authentication
        # Individual activity endpoints are handled by their respective blueprints
        
        response = {
            'message': 'Learning activities module',
            'user_id': user_id,
            'course_id': course_id,
            'available_endpoints': {
                'quizzes': '/api/learning/quizzes/',
                'polls': '/api/learning/polls/',
                'wordclouds': '/api/learning/wordclouds/',
                'shortanswers': '/api/learning/shortanswers/'
            }
        }
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify(response)

# Note: Individual activity endpoints are now handled by their respective blueprints:
# - /quizzes/* -> quizzes_bp (quizzes_routes.py)
# - /polls/* -> polls_bp (polls_routes.py)  
# - /wordclouds/* -> wordclouds_bp (wordclouds_routes.py)
# - /shortanswers/* -> shortanswers_bp (shortanswers_routes.py)
#
# All these endpoints now require authentication (no optional=True)