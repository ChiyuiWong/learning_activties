"""
COMP5241 Group 10 - Admin Module Routes
Responsible: Sunny
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.modules.admin.services import AdminService

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/health', methods=['GET'])
def admin_health():
    """Health check for Admin module"""
    return jsonify({
        'status': 'healthy',
        'module': 'admin',
        'message': 'Admin module is running'
    })


@admin_bp.route('/users', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_all_users():
    """Get all users - placeholder for Sunny's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement user management logic with admin permissions check
    return jsonify({
        'message': 'Get all users endpoint - to be implemented by Sunny',
        'user': current_user
    }), 200


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required(locations=["cookies"])
def update_user(user_id):
    """Update user - placeholder for Sunny's implementation"""
    data = request.get_json()
    current_user = get_jwt_identity()
    # TODO: Implement user update logic with admin permissions check
    return jsonify({
        'message': 'Update user endpoint - to be implemented by Sunny',
        'user_id': user_id,
        'received_data': data,
        'admin': current_user
    }), 200


@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
@jwt_required(locations=["cookies"])
def activate_user(user_id):
    """Activate/deactivate user - placeholder for Sunny's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement user activation/deactivation logic
    return jsonify({
        'message': 'User activation endpoint - to be implemented by Sunny',
        'user_id': user_id,
        'admin': current_user
    }), 200


@admin_bp.route('/new_users', methods=['POST'])
@jwt_required(locations=["cookies"])
def new_users():
    """Initialize a batch of new users and return activation URLs"""
    claims = get_jwt()
    if "role" not in claims or claims["role"] != "admin":
        return jsonify({'message': 'No permission'}), 401
    ret = AdminService.new_users(request.get_json(), claims["username"], request.headers.get('X-Forwarded-For', request.remote_addr))
    print(ret)
    return jsonify(ret), 200


@admin_bp.route('/profile', methods=['POST'])
@jwt_required(locations=["cookies"])
def get_profile():
    """Get user profile - placeholder for Sunny's implementation"""
    claims = get_jwt()

    # TODO: Implement profile retrieval logic here
    return jsonify({
        'message': 'Profile endpoint - to be implemented by Sunny',
        'info': claims
    }), 200


@admin_bp.route('/system/stats', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_system_stats():
    """Get system statistics - placeholder for Sunny's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement system statistics logic
    return jsonify({
        'message': 'System stats endpoint - to be implemented by Sunny',
        'admin': current_user
    }), 200


@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_audit_logs():
    """Get audit logs - placeholder for Sunny's implementation"""
    current_user = get_jwt_identity()
    
    # TODO: Implement audit log retrieval logic
    return jsonify({
        'message': 'Audit logs endpoint - to be implemented by Sunny',
        'admin': current_user
    }), 200
