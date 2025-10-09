"""
COMP5241 Group 10 - GenAI Module Models
Responsible: Ting
"""
from mongoengine import Document, StringField, DateTimeField, DictField, BooleanField, IntField, ListField
from datetime import datetime


class AIGeneration(Document):
    """Model for storing AI generation requests and results"""
    user_id = StringField(required=True)
    prompt = StringField(required=True)
    generated_content = StringField()
    generation_type = StringField(choices=['text', 'image', 'audio'], default='text')
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'ai_generations',
        'indexes': ['user_id', 'created_at', 'generation_type']
    }


class AIAnalysis(Document):
    """Model for storing AI analysis results"""
    content_id = StringField(required=True)
    analysis_type = StringField(required=True)
    analysis_result = DictField()
    confidence_score = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'ai_analyses',
        'indexes': ['content_id', 'analysis_type', 'created_at']
    }


class CourseMaterial(Document):
    """Model for storing course materials uploaded by teachers"""
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    file_name = StringField(required=True)
    file_path = StringField(required=True)
    file_type = StringField(required=True, choices=['pdf', 'docx', 'txt', 'pptx'])
    file_size = IntField(required=True)  # in bytes
    course_id = StringField(required=True)
    uploaded_by = StringField(required=True)  # teacher user_id
    content_text = StringField()  # extracted text content for RAG
    is_processed = BooleanField(default=False)  # whether content has been processed for RAG
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'course_materials',
        'indexes': ['course_id', 'uploaded_by', 'created_at', 'is_processed']
    }


class ChatSession(Document):
    """Model for storing chat sessions with AI"""
    user_id = StringField(required=True)
    course_id = StringField()  # optional, for course-specific chats
    session_name = StringField(max_length=100)
    model_name = StringField(required=True)  # Ollama model being used
    context_materials = ListField(StringField())  # list of CourseMaterial IDs used as context
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'chat_sessions',
        'indexes': ['user_id', 'course_id', 'created_at']
    }


class ChatMessage(Document):
    """Model for storing individual chat messages"""
    session_id = StringField(required=True)  # reference to ChatSession
    user_id = StringField(required=True)
    message_type = StringField(required=True, choices=['human', 'ai'])
    content = StringField(required=True)
    metadata = DictField()  # can store model parameters, response time, etc.
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'chat_messages',
        'indexes': ['session_id', 'user_id', 'created_at']
    }


class OllamaModel(Document):
    """Model for tracking available Ollama models"""
    name = StringField(required=True, unique=True)
    description = StringField()
    size = StringField()  # model size (e.g., "7B", "13B")
    family = StringField()  # model family (e.g., "llama", "mistral")
    is_downloaded = BooleanField(default=False)
    download_progress = IntField(default=0)  # percentage
    last_used = DateTimeField()
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'ollama_models',
        'indexes': ['name', 'is_downloaded', 'last_used']
    }
