from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
from config.database import get_db_connection

# Define a separate blueprint for action endpoints
action_bp = Blueprint('actions', __name__, url_prefix='/actions')


@action_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for actions module"""
    return jsonify({
        'status': 'success',
        'message': 'Actions module is healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


# Add more action-related routes here as needed
