"""
GenAI Services (DISABLED)
All code in this module is disabled for deployment without GenAI dependencies.
"""
from langchain_community.embeddings import OpenAIEmbeddings
from bson import ObjectId


class GenAIService:
    """Service class for GenAI operations"""
    
    def __init__(self):
        self.openai_client = None
        self.chroma_client = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize AI services"""
        try:
            # Initialize OpenAI client
            api_key = current_app.config.get('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                self.openai_client = openai
            else:
                current_app.logger.warning("OpenAI API key not configured")
        except RuntimeError:
            # Application context not available during initialization
            # This is expected and will be handled when the service is first used
            pass
        
        # Initialize ChromaDB client
        try:
            self.chroma_client = chromadb.Client()
            if hasattr(current_app, 'logger'):
                current_app.logger.info("ChromaDB initialized successfully")
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Failed to initialize ChromaDB: {e}")
            else:
                print(f"Failed to initialize ChromaDB: {e}")
    
    def get_available_models(self):
        """Get list of available Ollama models"""
        try:
            models = ollama.list()
            # Ensure we always return a dict with 'models' key
            if isinstance(models, dict):
                return models
            else:
                return {'models': []}
        except Exception as e:
            current_app.logger.error(f"Failed to get Ollama models: {e}")
            return {'models': []}
    
    def download_model(self, model_name):
        """Download an Ollama model"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            # Check if model already exists
            model_doc = db.ollama_models.find_one({'name': model_name})
            if not model_doc:
                # Create model document
                model_doc = {
                    'name': model_name,
                    'is_downloaded': False,
                    'download_progress': 0,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                result = db.ollama_models.insert_one(model_doc)
                model_doc['_id'] = result.inserted_id
            
            # Start download
            response = ollama.pull(model_name)
            
            # Update model status
            db.ollama_models.update_one(
                {'_id': model_doc['_id']},
                {'$set': {
                    'is_downloaded': True,
                    'download_progress': 100,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            return True, "Model downloaded successfully"
        except Exception as e:
            current_app.logger.error(f"Failed to download model {model_name}: {e}")
            return False, str(e)
    
    def chat_with_model(self, model_name, prompt, context_materials=None, session_id=None):
        """Chat with an Ollama model with optional RAG context"""
        try:
            # Prepare context from course materials if provided
            context = ""
            if context_materials:
                context = self._get_context_from_materials(context_materials)
            
            # Prepare the full prompt with context
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nPlease answer based on the provided context."
            else:
                full_prompt = prompt
            
            # Generate response using Ollama
            response = ollama.chat(model=model_name, messages=[
                {
                    'role': 'user',
                    'content': full_prompt
                }
            ])
            
            return response['message']['content']
        except Exception as e:
            current_app.logger.error(f"Failed to chat with model {model_name}: {e}")
            raise e
    
    def _get_context_from_materials(self, material_ids):
        """Retrieve and combine content from course materials"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
        context_texts = []
        for material_id in material_ids:
            try:
                material = db.course_materials.find_one({'_id': ObjectId(material_id)})
                if material and material.get('content_text'):
                    context_texts.append(f"From {material['title']}: {material['content_text']}")
            except Exception:
                current_app.logger.warning(f"Course material {material_id} not found")
        
        return "\n\n".join(context_texts)
    
    def process_course_material(self, file_path, material_id):
        """Extract text content from uploaded course material"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            material = db.course_materials.find_one({'_id': ObjectId(material_id)})
            
            if not material:
                raise ValueError(f"Material {material_id} not found")
            
            if material['file_type'] == 'pdf':
                text = self._extract_text_from_pdf(file_path)
            elif material['file_type'] == 'docx':
                text = self._extract_text_from_docx(file_path)
            elif material['file_type'] == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file type: {material['file_type']}")
            
            # Store extracted text
            db.course_materials.update_one(
                {'_id': ObjectId(material_id)},
                {'$set': {
                    'content_text': text,
                    'is_processed': True,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            # Optionally, store in vector database for better RAG
            self._store_in_vector_db(text, material_id)
            
            return text
        except Exception as e:
            current_app.logger.error(f"Failed to process course material {material_id}: {e}")
            raise e
    
    def _extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            current_app.logger.error(f"Failed to extract text from PDF: {e}")
            raise e
        return text
    
    def _extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            current_app.logger.error(f"Failed to extract text from DOCX: {e}")
            raise e
        return text
    
    def _store_in_vector_db(self, text, material_id):
        """Store text chunks in ChromaDB for better retrieval"""
        if not self.chroma_client:
            return
        
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create collection if it doesn't exist
            collection_name = f"course_material_{material_id}"
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name
            )
            
            # Add chunks to collection
            for i, chunk in enumerate(chunks):
                collection.add(
                    documents=[chunk],
                    ids=[f"{material_id}_chunk_{i}"]
                )
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Failed to store in vector DB: {e}")
            else:
                print(f"Failed to store in vector DB: {e}")
    
    def save_chat_session(self, user_id, model_name, course_id=None, context_materials=None):
        """Save a new chat session"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
        session_data = {
            'user_id': user_id,
            'course_id': course_id,
            'model_name': model_name,
            'context_materials': context_materials or [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.chat_sessions.insert_one(session_data)
        session_data['_id'] = result.inserted_id
        return session_data
    
    def save_chat_message(self, session_id, user_id, message_type, content, metadata=None):
        """Save a chat message"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
        message_data = {
            'session_id': session_id,
            'user_id': user_id,
            'message_type': message_type,
            'content': content,
            'metadata': metadata or {},
            'created_at': datetime.utcnow()
        }
        result = db.chat_messages.insert_one(message_data)
        message_data['_id'] = result.inserted_id
        return message_data
    
    def get_chat_history(self, session_id):
        """Get chat history for a session"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
        return list(db.chat_messages.find({'session_id': session_id}).sort('created_at', 1))
    
    def get_user_sessions(self, user_id):
        """Get all chat sessions for a user"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
        return list(db.chat_sessions.find({'user_id': user_id}).sort('created_at', -1))
    
    def generate_text(self, prompt, user_id):
        """Generate text using AI - to be implemented by Ting"""
        # TODO: Implement text generation logic
        pass
    
    def analyze_content(self, content, analysis_type):
        """Analyze content using AI - to be implemented by Ting"""
        # TODO: Implement content analysis logic
        pass
    
    def save_generation(self, user_id, prompt, content, generation_type='text'):
        """Save AI generation to database"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
        generation_data = {
            'user_id': user_id,
            'prompt': prompt,
            'generated_content': content,
            'generation_type': generation_type,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.ai_generations.insert_one(generation_data)
        generation_data['_id'] = result.inserted_id
        return generation_data
    
    def save_analysis(self, content_id, analysis_type, result, confidence=None):
        """Save AI analysis to database"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
        analysis_data = {
            'content_id': content_id,
            'analysis_type': analysis_type,
            'analysis_result': result,
            'confidence_score': confidence,
            'created_at': datetime.utcnow()
        }
        result = db.ai_analyses.insert_one(analysis_data)
        analysis_data['_id'] = result.inserted_id
        return analysis_data
