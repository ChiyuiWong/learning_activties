"""
COMP5241 Group 10 - Security Module Routes
Responsible: Sunny
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

security_bp = Blueprint('security', __name__)


@security_bp.route('/health', methods=['GET'])
def security_health():
    """Health check for Security module"""
    return jsonify({
        'status': 'healthy',
        'module': 'security',
        'message': 'Security module is running'
    })


@security_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint - placeholder for Sunny's implementation"""
    data = request.get_json()
    
    # TODO: Implement authentication logic here
    return jsonify({
        'message': 'Login endpoint - to be implemented by Sunny',
        'received_data': {'username': data.get('username', 'N/A')}
    }), 200


@security_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint - placeholder for Sunny's implementation"""
    data = request.get_json()
    
    # TODO: Implement user registration logic here
    return jsonify({
        'message': 'Registration endpoint - to be implemented by Sunny',
        'received_data': data
    }), 200


@security_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint - placeholder for Sunny's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement logout logic here
    return jsonify({
        'message': 'Logout endpoint - to be implemented by Sunny',
        'user': current_user
    }), 200


@security_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile - placeholder for Sunny's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement profile retrieval logic here
    return jsonify({
        'message': 'Profile endpoint - to be implemented by Sunny',
        'user': current_user
    }), 200
