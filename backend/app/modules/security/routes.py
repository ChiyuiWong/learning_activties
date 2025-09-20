"""
COMP5241 Group 10 - Security Module Routes
Responsible: Sunny
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app.modules.security.services import SecurityService

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
    """User login endpoint with simple mock authentication for testing"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    print(f"Login attempt: username={username}")

    
    if not username or not password:
        print("Missing username or password")
        return jsonify({'error': 'Username and password are required'}), 400
    role = SecurityService.get_role(username, password)
    if role is None:
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Create access token with user info
    token_data = {
        'username': username,
        'role': role
    }
    access_token = create_access_token(identity=username, additional_claims=token_data)
    
    return jsonify({
        'access_token': access_token,
        'username': username,
        'role': role
    }), 200


@security_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint - placeholder for Sunny's implementation
    NOTE: Registration SHALL only be permitted to be carry out by trusted identities
    """
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
