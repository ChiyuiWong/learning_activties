
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
from .services import LearningActivityService
from bson import ObjectId

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


@learning_bp.route('/activities/to-grade', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_submissions_to_grade():
    """Teacher: get submissions needing grading (optionally filter by course)"""
    user_id = get_jwt_identity()
    course_id = request.args.get('course_id')

    try:
        subs = LearningActivityService.get_submissions_for_grading(user_id, course_id=course_id)
        result = []
        for s in subs:
            result.append({
                'submission_id': str(s['_id']),
                'activity_id': s['activity_id'],
                'student_id': s['student_id'],
                'submitted_at': s['submitted_at'].isoformat() if s.get('submitted_at') else None,
                'status': s['status']
            })
        return jsonify(result), 200
    except ValueError as ve:
        return jsonify({'error': 'Invalid input', 'details': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to get submissions', 'details': str(e)}), 500


@learning_bp.route('/activities/submissions/<submission_id>/grade', methods=['POST'])
@jwt_required(locations=["cookies"])
def grade_submission(submission_id):
    """Teacher grades a specific submission"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    try:
        score = data.get('score')
        feedback = data.get('feedback')
        updated = LearningActivityService.grade_submission(submission_id=submission_id, score=score, feedback=feedback, graded_by=user_id)
        return jsonify({'message': 'Submission graded', 'submission_id': str(updated['_id']), 'score': updated.get('score')}), 200
    except ValueError as ve:
        return jsonify({'error': 'Invalid score', 'details': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to grade submission', 'details': str(e)}), 500


@learning_bp.route('/activities/<activity_id>/submissions', methods=['GET'])
@jwt_required(locations=["cookies"])
def list_activity_submissions(activity_id):
    """List all submissions for an activity (teacher view)"""
    user_id = get_jwt_identity()
    try:
        # Optionally enforce teacher is the owner in production
        subs = LearningActivityService.get_submissions_for_activity(activity_id)
        result = []
        for s in subs:
            result.append({
                'submission_id': str(s['_id']),
                'student_id': s['student_id'],
                'submitted_at': s['submitted_at'].isoformat() if s.get('submitted_at') else None,
                'status': s['status'],
                'score': s.get('score')
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Failed to list submissions', 'details': str(e)}), 500


@learning_bp.route('/students/<student_id>/progress', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_student_progress(student_id):
    """Get student's progress across activities (optionally filter by course)"""
    course_id = request.args.get('course_id')
    try:
        progresses = LearningActivityService.get_student_progress(student_id, course_id=course_id)
        result = []
        for p in progresses:
            result.append({
                'activity_id': p['activity_id'],
                'progress_percentage': p['progress_percentage'],
                'time_spent': p['time_spent'],
                'is_completed': p['is_completed'],
                'last_accessed': p['last_accessed'].isoformat() if p.get('last_accessed') else None
            })
        return jsonify(result), 200
    except ValueError as ve:
        return jsonify({'error': 'Invalid input', 'details': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to get progress', 'details': str(e)}), 500


@learning_bp.route('/activities', methods=['POST'])
@jwt_required(locations=["cookies"])
def create_activity():
    """Create learning activity - placeholder for Charlie's implementation"""
    data = request.get_json() or {}
    current_user = get_jwt_identity()

    try:
        activity = LearningActivityService.create_activity(
            title=data.get('title'),
            description=data.get('description'),
            activity_type=data.get('activity_type'),
            course_id=data.get('course_id'),
            created_by=current_user,
            instructions=data.get('instructions'),
            max_score=data.get('max_score'),
            time_limit=data.get('time_limit'),
            due_date=data.get('due_date'),
            is_active=data.get('is_active', True)
        )

        return jsonify({
            'message': 'Activity created successfully',
            'activity_id': str(activity['_id'])
        }), 201
    except ValueError as ve:
        return jsonify({'error': 'Invalid input', 'details': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create activity', 'details': str(e)}), 500


@learning_bp.route('/activities/<activity_id>', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_activity(activity_id):
    """Get specific learning activity - placeholder for Charlie's implementation"""
    current_user = get_jwt_identity()
    try:
        activity = LearningActivityService.get_activity_by_id(activity_id)
        # Basic serialization
        result = {
            'id': str(activity['_id']),
            'title': activity['title'],
            'description': activity['description'],
            'activity_type': activity['activity_type'],
            'course_id': activity['course_id'],
            'created_by': activity['created_by'],
            'instructions': activity['instructions'],
            'max_score': activity['max_score'],
            'time_limit': activity['time_limit'],
            'due_date': activity['due_date'].isoformat() if activity.get('due_date') else None,
            'is_active': activity['is_active'],
            'created_at': activity['created_at'].isoformat() if activity.get('created_at') else None
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve activity', 'details': str(e)}), 500


@learning_bp.route('/activities/<activity_id>/submit', methods=['POST'])
@jwt_required(locations=["cookies"])
def submit_activity():
    """Submit activity completion using LearningActivityService"""
    data = request.get_json() or {}
    current_user = get_jwt_identity()
    try:
        submission = LearningActivityService.submit_activity(
            activity_id=request.view_args.get('activity_id'),
            student_id=current_user,
            submission_data=data.get('submission_data', data)
        )

        return jsonify({
            'message': 'Submission received',
            'submission_id': str(submission['_id']),
            'status': submission['status']
        }), 200
    except ValueError as ve:
        return jsonify({'error': 'Invalid input', 'details': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to submit activity', 'details': str(e)}), 500
