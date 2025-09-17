"""
COMP5241 Group 10 - GenAI Module Services
Responsible: Ting
"""
from flask import current_app
import openai
from .models import AIGeneration, AIAnalysis


class GenAIService:
    """Service class for GenAI operations"""
    
    def __init__(self):
        self.openai_client = None
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.openai_client = openai
        else:
            current_app.logger.warning("OpenAI API key not configured")
    
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
        generation = AIGeneration(
            user_id=user_id,
            prompt=prompt,
            generated_content=content,
            generation_type=generation_type
        )
        generation.save()
        return generation
    
    def save_analysis(self, content_id, analysis_type, result, confidence=None):
        """Save AI analysis to database"""
        analysis = AIAnalysis(
            content_id=content_id,
            analysis_type=analysis_type,
            analysis_result=result,
            confidence_score=confidence
        )
        analysis.save()
        return analysis
