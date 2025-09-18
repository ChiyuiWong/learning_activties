"""
COMP5241 Group 10 - Learning Activities Module Routes
Responsible: Charlie
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

learning_bp = Blueprint('learning', __name__)


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
    """Get learning activities - placeholder for Charlie's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement activity retrieval logic
    return jsonify({
        'message': 'Get activities endpoint - to be implemented by Charlie',
        'user': current_user
    }), 200


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
