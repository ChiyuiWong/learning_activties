"""
COMP5241 Group 10 - Learning Activities Models
Contains data models for quizzes, word clouds, short-answer questions, and mini-games
"""
from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField, IntField, BooleanField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField, DictField, FloatField, URLField, ValidationError
from datetime import datetime
import re

# =========== Quiz Models ===========

class QuizOption(EmbeddedDocument):
    """Option for a quiz question"""
    text = StringField(required=True, min_length=1, max_length=300)
    is_correct = BooleanField(default=False)
    explanation = StringField(max_length=500)  # Optional explanation for this option
    
    def clean(self):
        """Validate quiz option"""
        if not self.text or not self.text.strip():
            raise ValidationError('Option text cannot be empty')
        self.text = self.text.strip()

class QuizQuestion(EmbeddedDocument):
    """Question in a quiz"""
    text = StringField(required=True, max_length=1000)
    options = ListField(EmbeddedDocumentField(QuizOption), required=True)
    points = IntField(default=1, min_value=1, max_value=100)
    question_type = StringField(default='multiple_choice', choices=[
        'multiple_choice',  # Single correct answer
        'multiple_select',  # Multiple correct answers
        'true_false'        # True/False question
    ])
    
    def clean(self):
        """Validate quiz question"""
        if not self.text or not self.text.strip():
            raise ValidationError('Question text cannot be empty')
        self.text = self.text.strip()
        
        if not self.options or len(self.options) < 2:
            raise ValidationError('Question must have at least 2 options')
        
        # Check if at least one option is correct
        has_correct_option = any(opt.is_correct for opt in self.options)
        if not has_correct_option:
            raise ValidationError('Question must have at least one correct option')

class Quiz(Document):
    """Quiz model containing multiple questions"""
    title = StringField(required=True, max_length=200, min_length=1)
    description = StringField(max_length=1000)
    questions = ListField(EmbeddedDocumentField(QuizQuestion), required=True)
    created_by = StringField(required=True)  # teacher user_id
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    time_limit = IntField(min_value=1, max_value=300)  # Time limit in minutes, 1-300 min
    course_id = StringField(required=True)
    
    meta = {
        'collection': 'quizzes',
        'indexes': ['course_id', 'created_by', 'is_active', 'expires_at']
    }
    
    def clean(self):
        """Validate quiz"""
        if not self.title or not self.title.strip():
            raise ValidationError('Quiz title cannot be empty')
        self.title = self.title.strip()
        
        if not self.questions or len(self.questions) < 1:
            raise ValidationError('Quiz must have at least one question')
        
        if self.expires_at and self.expires_at <= datetime.utcnow():
            raise ValidationError('Expiration date must be in the future')
    
    def get_total_points(self):
        """Calculate total points for the quiz"""
        return sum(q.points for q in self.questions)
    
    def is_expired(self):
        """Check if quiz has expired"""
        return self.expires_at and self.expires_at <= datetime.utcnow()

class QuizAttempt(Document):
    """Record of a student's quiz attempt"""
    quiz = ReferenceField(Quiz, required=True, reverse_delete_rule=2)  # CASCADE
    student_id = StringField(required=True)
    started_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    answers = ListField(DictField())  # List of {question_index: selected_options, submitted_at: datetime}
    score = FloatField(min_value=0, max_value=100)  # Score as percentage
    is_submitted = BooleanField(default=False)
    
    meta = {
        'collection': 'quiz_attempts',
        'indexes': [
            'quiz', 
            'student_id', 
            {'fields': ['quiz', 'student_id']},
            'is_submitted'
        ]
    }
    
    def clean(self):
        """Validate quiz attempt"""
        if self.completed_at and self.completed_at < self.started_at:
            raise ValidationError('Completion time cannot be before start time')
    
    def get_time_taken(self):
        """Get time taken for the attempt in seconds"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def is_time_expired(self):
        """Check if attempt has exceeded time limit"""
        if not self.quiz.time_limit or self.completed_at:
            return False
        
        time_elapsed = (datetime.utcnow() - self.started_at).total_seconds() / 60  # Convert to minutes
        return time_elapsed > self.quiz.time_limit

class WordCloudSubmission(EmbeddedDocument):
    """Individual word submission for a word cloud"""
    word = StringField(required=True, max_length=50, min_length=1)
    submitted_by = StringField(required=True)  # student user_id
    submitted_at = DateTimeField(default=datetime.utcnow)
    
    def clean(self):
        """Validate word submission"""
        if not self.word or not self.word.strip():
            raise ValidationError('Word cannot be empty')
        
        # Clean and validate the word
        self.word = re.sub(r'[^\w\s-]', '', self.word.strip().lower())
        if not self.word:
            raise ValidationError('Word contains only invalid characters')

class WordCloud(Document):
    """Word cloud model for collecting words from students"""
    title = StringField(required=True, max_length=200, min_length=1)
    prompt = StringField(required=True, max_length=1000, min_length=1)
    submissions = ListField(EmbeddedDocumentField(WordCloudSubmission), default=[])
    max_submissions_per_user = IntField(default=3, min_value=1, max_value=10)  # Max words per student
    created_by = StringField(required=True)  # teacher user_id
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    course_id = StringField(required=True)
    
    meta = {
        'collection': 'word_clouds',
        'indexes': ['course_id', 'created_by', 'is_active', 'expires_at']
    }
    
    def clean(self):
        """Validate word cloud"""
        if not self.title or not self.title.strip():
            raise ValidationError('Title cannot be empty')
        if not self.prompt or not self.prompt.strip():
            raise ValidationError('Prompt cannot be empty')
        
        self.title = self.title.strip()
        self.prompt = self.prompt.strip()
        
        if self.expires_at and self.expires_at <= datetime.utcnow():
            raise ValidationError('Expiration date must be in the future')
    
    def get_user_submissions_count(self, user_id):
        """Get number of submissions by a specific user"""
        return len([s for s in self.submissions if s.submitted_by == user_id])
    
    def get_word_frequency(self):
        """Get word frequency dictionary"""
        word_freq = {}
        for submission in self.submissions:
            word = submission.word.lower()
            word_freq[word] = word_freq.get(word, 0) + 1
        return word_freq
    
    def is_expired(self):
        """Check if word cloud has expired"""
        return self.expires_at and self.expires_at <= datetime.utcnow()

class ShortAnswerSubmission(EmbeddedDocument):
    """Individual answer submission for a short answer question"""
    text = StringField(required=True, max_length=2000)
    submitted_by = StringField(required=True)  # student user_id
    submitted_at = DateTimeField(default=datetime.utcnow)
    feedback = StringField(max_length=1000)  # Teacher feedback
    score = FloatField(min_value=0, max_value=100)  # Score as percentage
    is_graded = BooleanField(default=False)
    
    def clean(self):
        """Validate submission"""
        if not self.text or not self.text.strip():
            raise ValidationError('Answer text cannot be empty')
        self.text = self.text.strip()

class ShortAnswerQuestion(Document):
    """Short answer question model"""
    question = StringField(required=True, max_length=1000, min_length=1)
    answer_hint = StringField(max_length=500)  # Optional hint for students
    example_answer = StringField(max_length=2000)  # Model answer (only visible to teacher)
    submissions = ListField(EmbeddedDocumentField(ShortAnswerSubmission), default=[])
    max_length = IntField(default=1000, min_value=100, max_value=5000)  # Maximum answer length
    created_by = StringField(required=True)  # teacher user_id
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    course_id = StringField(required=True)
    
    meta = {
        'collection': 'short_answer_questions',
        'indexes': ['course_id', 'created_by', 'is_active', 'expires_at']
    }
    
    def clean(self):
        """Validate short answer question"""
        if not self.question or not self.question.strip():
            raise ValidationError('Question cannot be empty')
        self.question = self.question.strip()
        
        if self.expires_at and self.expires_at <= datetime.utcnow():
            raise ValidationError('Expiration date must be in the future')
    
    def get_user_submission(self, user_id):
        """Get submission by a specific user"""
        for submission in self.submissions:
            if submission.submitted_by == user_id:
                return submission
        return None
    
    def get_graded_submissions_count(self):
        """Get count of graded submissions"""
        return len([s for s in self.submissions if s.is_graded])
    
    def is_expired(self):
        """Check if question has expired"""
        return self.expires_at and self.expires_at <= datetime.utcnow()

class MiniGameScore(EmbeddedDocument):
    """Score record for a mini-game"""
    student_id = StringField(required=True)
    score = IntField(required=True, min_value=0)
    time_taken = FloatField(min_value=0)  # Time in seconds
    achieved_at = DateTimeField(default=datetime.utcnow)
    game_data = DictField()  # Additional game-specific data
    
    def clean(self):
        """Validate score record"""
        if self.score < 0:
            raise ValidationError('Score cannot be negative')

class MiniGame(Document):
    """Mini-game model"""
    title = StringField(required=True, max_length=200, min_length=1)
    game_type = StringField(required=True, choices=[
        'matching',      # Matching pairs game
        'sorting',       # Sorting/categorization game
        'sequence',      # Arrange items in correct sequence
        'memory',        # Memory game
        'custom'         # Custom game with specific configuration
    ])
    description = StringField(max_length=1000)
    instructions = StringField(max_length=2000)
    game_config = DictField()  # Configuration specific to the game type
    scores = ListField(EmbeddedDocumentField(MiniGameScore), default=[])
    max_score = IntField(default=100, min_value=1)  # Maximum possible score
    created_by = StringField(required=True)  # teacher user_id
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    course_id = StringField(required=True)
    
    meta = {
        'collection': 'mini_games',
        'indexes': ['course_id', 'created_by', 'is_active', 'expires_at', 'game_type']
    }
    
    def clean(self):
        """Validate mini-game"""
        if not self.title or not self.title.strip():
            raise ValidationError('Title cannot be empty')
        self.title = self.title.strip()
        
        if self.expires_at and self.expires_at <= datetime.utcnow():
            raise ValidationError('Expiration date must be in the future')
    
    def get_user_best_score(self, user_id):
        """Get user's best score"""
        user_scores = [s.score for s in self.scores if s.student_id == user_id]
        return max(user_scores) if user_scores else 0
    
    def get_user_attempts_count(self, user_id):
        """Get number of attempts by a user"""
        return len([s for s in self.scores if s.student_id == user_id])
    
    def get_leaderboard(self, limit=10):
        """Get top scores leaderboard"""
        # Group by student and get their best score
        user_best_scores = {}
        for score_record in self.scores:
            student_id = score_record.student_id
            if student_id not in user_best_scores or score_record.score > user_best_scores[student_id]['score']:
                user_best_scores[student_id] = {
                    'student_id': student_id,
                    'score': score_record.score,
                    'time_taken': score_record.time_taken,
                    'achieved_at': score_record.achieved_at
                }
        
        # Sort by score (descending) and time taken (ascending for tie-breaking)
        leaderboard = sorted(
            user_best_scores.values(), 
            key=lambda x: (-x['score'], x['time_taken'] or float('inf'))
        )
        
        return leaderboard[:limit]
    
    def is_expired(self):
        """Check if mini-game has expired"""
        return self.expires_at and self.expires_at <= datetime.utcnow()