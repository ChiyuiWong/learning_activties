"""
COMP5241 Group 10 - Courses Module Routes
Responsible: Keith
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/health', methods=['GET'])
def courses_health():
    """Health check for Courses module"""
    return jsonify({
        'status': 'healthy',
        'module': 'courses',
        'message': 'Courses module is running'
    })


@courses_bp.route('/', methods=['GET'])
@jwt_required()
def get_courses():
    """Get courses - placeholder for Keith's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement course retrieval logic
    return jsonify({
        'message': 'Get courses endpoint - to be implemented by Keith',
        'user': current_user
    }), 200


@courses_bp.route('/', methods=['POST'])
@jwt_required()
def create_course():
    """Create course - placeholder for Keith's implementation"""
    data = request.get_json()
    current_user = get_jwt_identity()
    
    # TODO: Implement course creation logic
    return jsonify({
        'message': 'Create course endpoint - to be implemented by Keith',
        'received_data': data,
        'user': current_user
    }), 201


@courses_bp.route('/<course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """Get specific course - placeholder for Keith's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement specific course retrieval
    return jsonify({
        'message': 'Get specific course endpoint - to be implemented by Keith',
        'course_id': course_id,
        'user': current_user
    }), 200


@courses_bp.route('/<course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_in_course(course_id):
    """Enroll in course - placeholder for Keith's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement course enrollment logic
    return jsonify({
        'message': 'Course enrollment endpoint - to be implemented by Keith',
        'course_id': course_id,
        'user': current_user
    }), 200


@courses_bp.route('/<course_id>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    """Get students enrolled in course - placeholder for Keith's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement student list retrieval
    return jsonify({
        'message': 'Get course students endpoint - to be implemented by Keith',
        'course_id': course_id,
        'user': current_user
    }), 200
