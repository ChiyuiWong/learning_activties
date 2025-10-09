"""
COMP5241 Group 10 - GenAI Module Routes
Responsible: Ting
"""
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from .services import GenAIService
from .models import CourseMaterial, ChatSession, ChatMessage, OllamaModel

genai_bp = Blueprint('genai', __name__)

# Initialize service
genai_service = GenAIService()

# Configure upload settings
UPLOAD_FOLDER = 'uploads/course_materials'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'pptx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@genai_bp.route('/health', methods=['GET'])
def genai_health():
    """Health check for GenAI module"""
    return jsonify({
        'status': 'healthy',
        'module': 'genai',
        'message': 'GenAI module is running'
    })


# Model Management Endpoints
@genai_bp.route('/models', methods=['GET'])
@jwt_required()
def list_models():
    """Get list of available Ollama models"""
    try:
        # Get models from Ollama
        available_models = genai_service.get_available_models()
        
        # Get model status from database
        db_models = {model.name: model for model in OllamaModel.objects()}
        
        # Combine information
        models_info = []
        for model in available_models.get('models', []):
            model_name = model['name']
            db_model = db_models.get(model_name)
            
            model_info = {
                'name': model_name,
                'size': model.get('size', ''),
                'modified_at': model.get('modified_at', ''),
                'is_downloaded': db_model.is_downloaded if db_model else False,
                'download_progress': db_model.download_progress if db_model else 0,
                'last_used': db_model.last_used.isoformat() if db_model and db_model.last_used else None
            }
            models_info.append(model_info)
        
        return jsonify({
            'success': True,
            'models': models_info
        })
    except Exception as e:
        current_app.logger.error(f"Failed to list models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/models/download', methods=['POST'])
@jwt_required()
def download_model():
    """Download an Ollama model"""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': 'Model name is required'
            }), 400
        
        success, message = genai_service.download_model(model_name)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        current_app.logger.error(f"Failed to download model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Course Materials Management Endpoints
@genai_bp.route('/materials', methods=['GET'])
@jwt_required()
def list_materials():
    """Get list of course materials"""
    try:
        user_id = get_jwt_identity()
        course_id = request.args.get('course_id')
        
        # Build query
        query = {}
        if course_id:
            query['course_id'] = course_id
        
        materials = CourseMaterial.objects(**query).order_by('-created_at')
        
        materials_data = []
        for material in materials:
            materials_data.append({
                'id': str(material.id),
                'title': material.title,
                'description': material.description,
                'file_name': material.file_name,
                'file_type': material.file_type,
                'file_size': material.file_size,
                'course_id': material.course_id,
                'uploaded_by': material.uploaded_by,
                'is_processed': material.is_processed,
                'created_at': material.created_at.isoformat(),
                'updated_at': material.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'materials': materials_data
        })
    except Exception as e:
        current_app.logger.error(f"Failed to list materials: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/materials/upload', methods=['POST'])
@jwt_required()
def upload_material():
    """Upload course material"""
    try:
        user_id = get_jwt_identity()
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description', '')
        course_id = request.form.get('course_id')
        
        if not title or not course_id:
            return jsonify({
                'success': False,
                'error': 'Title and course_id are required'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.instance_path, UPLOAD_FOLDER)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        file.save(file_path)
        
        # Save to database
        material = CourseMaterial(
            title=title,
            description=description,
            file_name=unique_filename,
            file_path=file_path,
            file_type=file_ext,
            file_size=os.path.getsize(file_path),
            course_id=course_id,
            uploaded_by=user_id
        )
        material.save()
        
        # Process the file to extract text content
        try:
            genai_service.process_course_material(file_path, str(material.id))
        except Exception as e:
            current_app.logger.warning(f"Failed to process material immediately: {e}")
        
        return jsonify({
            'success': True,
            'material': {
                'id': str(material.id),
                'title': material.title,
                'file_name': material.file_name,
                'file_type': material.file_type,
                'file_size': material.file_size,
                'is_processed': material.is_processed
            }
        })
    except Exception as e:
        current_app.logger.error(f"Failed to upload material: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/materials/<material_id>', methods=['DELETE'])
@jwt_required()
def delete_material(material_id):
    """Delete course material"""
    try:
        user_id = get_jwt_identity()
        
        material = CourseMaterial.objects.get(id=material_id)
        
        # Check if user owns this material or is admin
        if material.uploaded_by != user_id:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        # Delete file
        if os.path.exists(material.file_path):
            os.remove(material.file_path)
        
        # Delete from database
        material.delete()
        
        return jsonify({
            'success': True,
            'message': 'Material deleted successfully'
        })
    except CourseMaterial.DoesNotExist:
        return jsonify({
            'success': False,
            'error': 'Material not found'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Failed to delete material: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Chat Endpoints
@genai_bp.route('/chat/sessions', methods=['GET'])
@jwt_required()
def list_chat_sessions():
    """Get user's chat sessions"""
    try:
        user_id = get_jwt_identity()
        sessions = genai_service.get_user_sessions(user_id)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session.id),
                'session_name': session.session_name,
                'model_name': session.model_name,
                'course_id': session.course_id,
                'context_materials': session.context_materials,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions_data
        })
    except Exception as e:
        current_app.logger.error(f"Failed to list chat sessions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/chat/sessions', methods=['POST'])
@jwt_required()
def create_chat_session():
    """Create a new chat session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        model_name = data.get('model_name')
        course_id = data.get('course_id')
        context_materials = data.get('context_materials', [])
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': 'Model name is required'
            }), 400
        
        session = genai_service.save_chat_session(
            user_id=user_id,
            model_name=model_name,
            course_id=course_id,
            context_materials=context_materials
        )
        
        return jsonify({
            'success': True,
            'session': {
                'id': str(session.id),
                'model_name': session.model_name,
                'course_id': session.course_id,
                'context_materials': session.context_materials
            }
        })
    except Exception as e:
        current_app.logger.error(f"Failed to create chat session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/chat/sessions/<session_id>/messages', methods=['GET'])
@jwt_required()
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        messages = genai_service.get_chat_history(session_id)
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': str(message.id),
                'message_type': message.message_type,
                'content': message.content,
                'metadata': message.metadata,
                'created_at': message.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'messages': messages_data
        })
    except Exception as e:
        current_app.logger.error(f"Failed to get chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/chat/sessions/<session_id>/messages', methods=['POST'])
@jwt_required()
def send_chat_message(session_id):
    """Send a message in a chat session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        message = data.get('message')
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Get session
        session = ChatSession.objects.get(id=session_id)
        
        # Save user message
        user_message = genai_service.save_chat_message(
            session_id=session_id,
            user_id=user_id,
            message_type='human',
            content=message
        )
        
        # Generate AI response
        ai_response = genai_service.chat_with_model(
            model_name=session.model_name,
            prompt=message,
            context_materials=session.context_materials,
            session_id=session_id
        )
        
        # Save AI response
        ai_message = genai_service.save_chat_message(
            session_id=session_id,
            user_id=user_id,
            message_type='ai',
            content=ai_response
        )
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        session.save()
        
        return jsonify({
            'success': True,
            'user_message': {
                'id': str(user_message.id),
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'ai_response': {
                'id': str(ai_message.id),
                'content': ai_message.content,
                'created_at': ai_message.created_at.isoformat()
            }
        })
    except ChatSession.DoesNotExist:
        return jsonify({
            'success': False,
            'error': 'Chat session not found'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Failed to send chat message: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/generate', methods=['POST'])
@jwt_required(locations=["cookies"])
def generate_content():
    """Generate AI content - legacy endpoint"""
    data = request.get_json()
    
    return jsonify({
        'message': 'Please use the new chat endpoints for AI interactions',
        'received_data': data
    }), 200


@genai_bp.route('/analyze', methods=['POST'])
@jwt_required(locations=["cookies"])
def analyze_content():
    """Analyze content with AI - placeholder for future implementation"""
    data = request.get_json()
    
    return jsonify({
        'message': 'Content analysis endpoint - to be implemented',
        'received_data': data
    }), 200
