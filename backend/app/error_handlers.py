from flask import jsonify
from werkzeug.exceptions import HTTPException
from app.utils.logger import logger

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        logger.error(f"404 Not Found: {error}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource could not be found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        logger.error(f"400 Bad Request: {error}")
        return jsonify({
            'error': 'Bad Request',
            'message': str(error)
        }), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        logger.error(f"401 Unauthorized: {error}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource'
        }), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        logger.error(f"403 Forbidden: {error}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled Exception: {error}")
        
        if isinstance(error, HTTPException):
            return jsonify({
                'error': error.name,
                'message': error.description
            }), error.code
            
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500