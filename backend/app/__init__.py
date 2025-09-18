"""
COMP5241 Group 10 - Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config.database import init_db
from app.config.config import Config
import os


def create_app(config_class=Config):
    """Create and configure Flask application"""
    # Get frontend directory path
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')
    
    # Initialize Flask app with static files from frontend directory
    app = Flask(__name__,
                static_folder=os.path.join(frontend_dir, 'static'),
                static_url_path='/static')
                
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from app.modules.genai.routes import genai_bp
    from app.modules.security.routes import security_bp
    from app.modules.admin.routes import admin_bp
    from app.modules.learning_activities.routes import learning_bp
    from app.modules.courses.routes import courses_bp
    
    app.register_blueprint(genai_bp, url_prefix='/api/genai')
    app.register_blueprint(security_bp, url_prefix='/api/security')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'COMP5241 Group 10 API is running'}
    
    # Serve frontend HTML files
    from flask import send_from_directory
    
    @app.route('/')
    def index():
        return send_from_directory(frontend_dir, 'index.html')
    
    @app.route('/polls')
    def polls():
        return send_from_directory(frontend_dir, 'polls.html')
        
    @app.route('/login-test')
    def login_test():
        return send_from_directory(frontend_dir, 'login_test.html')
    
    return app
