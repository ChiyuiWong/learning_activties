"""
COMP5241 Group 10 - Learning Activities Models
Contains data models for quizzes, word clouds, short-answer questions, and mini-games
"""
from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField, IntField, BooleanField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField, DictField, FloatField, URLField
from datetime import datetime

# =========== Quiz Models ===========

class QuizOption(EmbeddedDocument):
    """Option for a quiz question"""
    text = StringField(required=True)
    is_correct = BooleanField(default=False)
    explanation = StringField()  # Optional explanation for this option

class QuizQuestion(EmbeddedDocument):
    """Question in a quiz"""
    text = StringField(required=True, max_length=500)
    options = ListField(EmbeddedDocumentField(QuizOption), required=True)
    points = IntField(default=1)
    question_type = StringField(default='multiple_choice', choices=[
        'multiple_choice',  # Single correct answer
        'multiple_select',  # Multiple correct answers
        'true_false'        # True/False question
    ])

class Quiz(Document):
    """Quiz model containing multiple questions"""
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=500)
    questions = ListField(EmbeddedDocumentField(QuizQuestion), required=True)
    created_by = StringField(required=True)  # teacher user_id
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    time_limit = IntField()  # Time limit in minutes, null for no limit
    course_id = StringField(required=True)
    
    meta = {
        'collection': 'quizzes',
        'indexes': ['course_id', 'created_by', 'is_active', 'expires_at']
    }

class QuizAttempt(Document):
    """Record of a student's quiz attempt"""
    quiz = ReferenceField(Quiz, required=True, reverse_delete_rule=2)  # CASCADE
    student_id = StringField(required=True)
    started_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    answers = ListField(DictField())  # List of {question_index: option_indices}
    score = FloatField()  # Calculated score after submission
    
    meta = {
        'collection': 'quiz_attempts',
        'indexes': [
            'quiz', 
            'student_id', 
            {'fields': ['quiz', 'student_id']}
        ]
    }

# =========== Word Cloud Models ===========

class WordCloudSubmission(EmbeddedDocument):
    """Individual word submission for a word cloud"""
    word = StringField(required=True, max_length=50)
    submitted_by = StringField(required=True)  # student user_id
    submitted_at = DateTimeField(default=datetime.utcnow)

class WordCloud(Document):
    """Word cloud model for collecting words from students"""
    title = StringField(required=True, max_length=200)
    prompt = StringField(required=True, max_length=500)
    submissions = ListField(EmbeddedDocumentField(WordCloudSubmission), default=[])
    max_submissions_per_user = IntField(default=3)  # Max words per student
    created_by = StringField(required=True)  # teacher user_id
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    course_id = StringField(required=True)
    
    meta = {
        'collection': 'word_clouds',
        'indexes': ['course_id', 'created_by', 'is_active', 'expires_at']
    }

# =========== Short Answer Models ===========

class ShortAnswerSubmission(EmbeddedDocument):
    """Individual answer submission for a short answer question"""
    text = StringField(required=True)
    submitted_by = StringField(required=True)  # student user_id
    submitted_at = DateTimeField(default=datetime.utcnow)
    feedback = StringField()  # Teacher feedback
    score = FloatField()  # Optional score if graded

class ShortAnswerQuestion(Document):
    """Short answer question model"""
    question = StringField(required=True, max_length=500)
    answer_hint = StringField()  # Optional hint for students
    example_answer = StringField()  # Model answer (only visible to teacher)
    submissions = ListField(EmbeddedDocumentField(ShortAnswerSubmission), default=[])
    max_length = IntField(default=1000)  # Maximum answer length
    created_by = StringField(required=True)  # teacher user_id
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    course_id = StringField(required=True)
    
    meta = {
        'collection': 'short_answer_questions',
        'indexes': ['course_id', 'created_by', 'is_active', 'expires_at']
    }

# =========== Mini-Game Models ===========

class MiniGameScore(EmbeddedDocument):
    """Score record for a mini-game"""
    student_id = StringField(required=True)
    score = IntField(required=True)
    time_taken = FloatField()  # Time in seconds
    achieved_at = DateTimeField(default=datetime.utcnow)

class MiniGame(Document):
    """Mini-game model"""
    title = StringField(required=True, max_length=200)
    game_type = StringField(required=True, choices=[
        'matching',      # Matching pairs game
        'sorting',       # Sorting/categorization game
        'sequence',      # Arrange items in correct sequence
        'memory',        # Memory game
        'custom'         # Custom game with specific configuration
    ])
    description = StringField(max_length=500)
    instructions = StringField()
    game_config = DictField()  # Configuration specific to the game type
    scores = ListField(EmbeddedDocumentField(MiniGameScore), default=[])
    created_by = StringField(required=True)  # teacher user_id
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    course_id = StringField(required=True)
    
    meta = {
        'collection': 'mini_games',
        'indexes': ['course_id', 'created_by', 'is_active', 'expires_at', 'game_type']
    }