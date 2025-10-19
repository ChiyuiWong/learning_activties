"""
COMP5241 Group 10 - Security Module Routes (Simplified)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

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
    """简化登录：任何用户名密码都能登录"""
    # Accept JSON payloads (used by tests) or fallback to form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    username = data.get('username', '')
    password = data.get('password', '')
    
    print(f"Login attempt: username={username}")
    
    if not username or not password:
        print("Missing username or password")
        return jsonify({'error': 'Username and password are required'}), 400
    
    # 简化登录：任何用户名+密码都能登录
    print(f"Simplified login for: {username}")
    
    # 根据用户名判断角色（简单规则）
    if any(x in username.lower() for x in ['teacher', 'prof', 'dr', 'smith', 'johnson']):
        role = 'teacher'
        user_name = '教师用户'
    else:
        role = 'student' 
        user_name = '学生用户'
    
    print(f"Login successful: {username} as {role}")
    
    # 生成JWT token
    access_token = create_access_token(
        identity=username,
        additional_claims={'username': username, 'role': role}
    )
    
    return jsonify({
        'access_token': access_token,
        'username': username,
        'role': role,
        'name': user_name
    }), 200

@security_bp.route('/register', methods=['POST'])
def register():
    """简化注册：直接成功"""
    return jsonify({'message': 'Registration successful'}), 200
