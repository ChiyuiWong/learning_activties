"""
COMP5241 Group 10 - GenAI Module Models
Responsible: Ting
"""
from mongoengine import Document, StringField, DateTimeField, DictField
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
