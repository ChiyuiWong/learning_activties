"""
GenAI Routes (DISABLED)
All code in this module is disabled for deployment without GenAI dependencies.
"""

genai_bp = Blueprint('genai', __name__)

# Initialize service lazily to avoid application context issues
genai_service = None

def get_genai_service():
    """Get or create GenAI service instance"""
    global genai_service
    if genai_service is None:
        genai_service = GenAIService()
    return genai_service

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
@jwt_required(locations=["cookies"])
def list_models():
    """Get list of available Ollama models"""
    try:
        # Get models from Ollama
        available_models = get_genai_service().get_available_models()
        
        current_app.logger.info(f"Ollama models response: {available_models}")
        
        # Get model status from database
        with get_db_connection() as client:
            db = client['comp5241_g10']
        db_models = {model['name']: model for model in db.ollama_models.find()}
        
        # Combine information
        models_info = []
        models_list = available_models.get('models', [])
        
        for model in models_list:
            model_name = model.get('name', '')
            if not model_name:
                continue
                
            db_model = db_models.get(model_name)
            
            model_info = {
                'name': model_name,
                'size': model.get('size', ''),
                'modified_at': model.get('modified_at', ''),
                'is_downloaded': db_model.get('is_downloaded', True) if db_model else True,  # Assume downloaded if in Ollama
                'download_progress': db_model.get('download_progress', 100) if db_model else 100,
                'last_used': db_model.get('last_used').isoformat() if db_model and db_model.get('last_used') else None
            }
            models_info.append(model_info)
        
        current_app.logger.info(f"Returning {len(models_info)} models")
        
        return jsonify({
            'success': True,
            'models': models_info
        })
    except Exception as e:
        current_app.logger.error(f"Failed to list models: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/models/download', methods=['POST'])
@jwt_required(locations=["cookies"])
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
        
        success, message = get_genai_service().download_model(model_name)
        
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
@jwt_required(locations=["cookies"])
def list_materials():
    """Get list of course materials"""
    try:
        user_id = get_jwt_identity()
        course_id = request.args.get('course_id')
        
        # Build query
        query = {}
        if course_id:
            query['course_id'] = course_id
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
        materials = list(db.course_materials.find(query).sort('created_at', -1))
        
        materials_data = []
        for material in materials:
            materials_data.append({
                'id': str(material['_id']),
                'title': material['title'],
                'description': material.get('description', ''),
                'file_name': material['file_name'],
                'file_type': material['file_type'],
                'file_size': material['file_size'],
                'course_id': material['course_id'],
                'uploaded_by': material['uploaded_by'],
                'is_processed': material.get('is_processed', False),
                'created_at': material['created_at'].isoformat(),
                'updated_at': material.get('updated_at', material['created_at']).isoformat()
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
@jwt_required(locations=["cookies"])
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
        with get_db_connection() as client:
            db = client['comp5241_g10']
        material_data = {
            'title': title,
            'description': description,
            'file_name': unique_filename,
            'file_path': file_path,
            'file_type': file_ext,
            'file_size': os.path.getsize(file_path),
            'course_id': course_id,
            'uploaded_by': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.course_materials.insert_one(material_data)
        material_id = result.inserted_id
        
        # Process the file to extract text content
        try:
            get_genai_service().process_course_material(file_path, str(material_id))
        except Exception as e:
            current_app.logger.warning(f"Failed to process material immediately: {e}")
        
        # Get the updated material
        material = db.course_materials.find_one({'_id': material_id})
        
        return jsonify({
            'success': True,
            'material': {
                'id': str(material['_id']),
                'title': material['title'],
                'file_name': material['file_name'],
                'file_type': material['file_type'],
                'file_size': material['file_size'],
                'is_processed': material.get('is_processed', False)
            }
        })
    except Exception as e:
        current_app.logger.error(f"Failed to upload material: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/materials/<material_id>', methods=['DELETE'])
@jwt_required(locations=["cookies"])
def delete_material(material_id):
    """Delete course material"""
    try:
        user_id = get_jwt_identity()
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
        material = db.course_materials.find_one({'_id': ObjectId(material_id)})
        
        if not material:
            return jsonify({
                'success': False,
                'error': 'Material not found'
            }), 404
        
        # Check if user owns this material or is admin
        if material['uploaded_by'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        # Delete file
        if os.path.exists(material['file_path']):
            os.remove(material['file_path'])
        
        # Delete from database
        db.course_materials.delete_one({'_id': ObjectId(material_id)})
        
        return jsonify({
            'success': True,
            'message': 'Material deleted successfully'
        })
    except Exception as e:
        current_app.logger.error(f"Failed to delete material: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Chat Endpoints
@genai_bp.route('/chat/sessions', methods=['GET'])
@jwt_required(locations=["cookies"])
def list_chat_sessions():
    """Get user's chat sessions"""
    try:
        user_id = get_jwt_identity()
        sessions = get_genai_service().get_user_sessions(user_id)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session['_id']),
                'session_name': session.get('session_name'),
                'model_name': session['model_name'],
                'course_id': session.get('course_id'),
                'context_materials': session.get('context_materials', []),
                'created_at': session['created_at'].isoformat(),
                'updated_at': session.get('updated_at', session['created_at']).isoformat()
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
@jwt_required(locations=["cookies"])
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
        
        session = get_genai_service().save_chat_session(
            user_id=user_id,
            model_name=model_name,
            course_id=course_id,
            context_materials=context_materials
        )
        
        return jsonify({
            'success': True,
            'session': {
                'id': str(session['_id']),
                'model_name': session['model_name'],
                'course_id': session.get('course_id'),
                'context_materials': session.get('context_materials', [])
            }
        })
    except Exception as e:
        current_app.logger.error(f"Failed to create chat session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_bp.route('/chat/sessions/<session_id>/messages', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        messages = get_genai_service().get_chat_history(session_id)
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': str(message['_id']),
                'message_type': message['message_type'],
                'content': message['content'],
                'metadata': message.get('metadata', {}),
                'created_at': message['created_at'].isoformat()
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
@jwt_required(locations=["cookies"])
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
        with get_db_connection() as client:
            db = client['comp5241_g10']
        session = db.chat_sessions.find_one({'_id': ObjectId(session_id)})
        
        if not session:
            return jsonify({
                'success': False,
                'error': 'Chat session not found'
            }), 404
        
        # Save user message
        user_message = get_genai_service().save_chat_message(
            session_id=session_id,
            user_id=user_id,
            message_type='human',
            content=message
        )
        
        # Generate AI response
        ai_response = get_genai_service().chat_with_model(
            model_name=session['model_name'],
            prompt=message,
            context_materials=session.get('context_materials', []),
            session_id=session_id
        )
        
        # Save AI response
        ai_message = get_genai_service().save_chat_message(
            session_id=session_id,
            user_id=user_id,
            message_type='ai',
            content=ai_response
        )
        
        # Update session timestamp
        db.chat_sessions.update_one({'_id': ObjectId(session_id)}, {'$set': {'updated_at': datetime.utcnow()}})
        
        return jsonify({
            'success': True,
            'user_message': {
                'id': str(user_message['_id']),
                'content': user_message['content'],
                'created_at': user_message['created_at'].isoformat()
            },
            'ai_response': {
                'id': str(ai_message['_id']),
                'content': ai_message['content'],
                'created_at': ai_message['created_at'].isoformat()
            }
        })
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
