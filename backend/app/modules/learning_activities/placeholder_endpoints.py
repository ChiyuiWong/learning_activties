"""
COMP5241 Group 10 - Mock Learning Activities API Endpoints
Adds placeholders for missing GET routes to fix 500 errors
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

# Get logger
logger = logging.getLogger(__name__)

# Create blueprints for each activity type
placeholder_api = Blueprint('placeholder_api', __name__)

def register_placeholder_endpoints(app):
    """Register placeholder GET endpoints for all activity types"""
    logger.info("Registering placeholder endpoints for learning activities")
    
    # Define activity types with their route prefixes and sample data
    activity_types = [
        {
            'name': 'quizzes',
            'prefix': '/api/learning/quizzes',
            'sample_data': [
                {
                    'id': 'quiz1',
                    'title': 'Sample Quiz 1',
                    'description': 'This is a sample quiz',
                    'course_id': 'COMP5241',
                    'created_at': '2025-10-11T10:00:00Z'
                }
            ]
        },
        {
            'name': 'wordclouds',
            'prefix': '/api/learning/wordclouds',
            'sample_data': [
                {
                    'id': 'wc1',
                    'title': 'Sample Word Cloud',
                    'description': 'This is a sample word cloud',
                    'course_id': 'COMP5241',
                    'created_at': '2025-10-11T10:00:00Z'
                }
            ]
        },
        {
            'name': 'shortanswers',
            'prefix': '/api/learning/shortanswers',
            'sample_data': [
                {
                    'id': 'sa1',
                    'title': 'Sample Short Answer',
                    'question': 'This is a sample question',
                    'course_id': 'COMP5241',
                    'created_at': '2025-10-11T10:00:00Z'
                }
            ]
        },
        {
            'name': 'minigames',
            'prefix': '/api/learning/minigames',
            'sample_data': [
                {
                    'id': 'mg1',
                    'title': 'Sample Minigame',
                    'description': 'This is a sample minigame',
                    'course_id': 'COMP5241',
                    'created_at': '2025-10-11T10:00:00Z'
                }
            ]
        },
        {
            'name': 'polls',
            'prefix': '/api/learning/polls',
            'sample_data': [
                {
                    'id': 'poll1',
                    'title': 'Sample Poll',
                    'question': 'This is a sample poll question',
                    'options': [
                        {'text': 'Option A', 'votes': 0},
                        {'text': 'Option B', 'votes': 0}
                    ],
                    'course_id': 'COMP5241',
                    'created_at': '2025-10-11T10:00:00Z'
                }
            ]
        }
    ]
    
    # Register GET endpoints for each activity type
    for activity in activity_types:
        route = activity['prefix']
        name = activity['name']
        sample_data = activity['sample_data']
        
        # Create a closure to capture the activity name and sample data
        def create_handler(activity_name, activity_data):
            @jwt_required(locations=["cookies", "headers"], optional=True)
            def handler():
                try:
                    # Get query parameters
                    course_id = request.args.get('course_id')
                    user_id = get_jwt_identity()
                    
                    # Log the request
                    logger.info(f"GET {activity_name} request: course_id={course_id}, user_id={user_id}")
                    
                    # Return sample data
                    return jsonify(activity_data)
                except Exception as e:
                    logger.error(f"Error handling GET {activity_name}: {e}")
                    return jsonify({"error": str(e)}), 500
            
            # Set the function name
            handler.__name__ = f"get_{activity_name}"
            return handler
        
        # Register the route
        handler = create_handler(name, sample_data)
        app.add_url_rule(f"{route}/", 
                        endpoint=f"get_{name}",
                        view_func=handler,
                        methods=['GET'])
        
        logger.info(f"Registered placeholder endpoint: GET {route}/")
    
    logger.info("Placeholder endpoints registered successfully")