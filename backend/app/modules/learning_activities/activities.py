"""
COMP5241 Group 10 - Learning Activity Models
Defines the models for all learning activities
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator

# Quiz Models
class QuizOption(BaseModel):
    """Option for a quiz question"""
    id: str
    text: str
    is_correct: bool = False

class QuizQuestion(BaseModel):
    """Question in a quiz"""
    id: str
    text: str
    options: List[QuizOption] = []
    explanation: Optional[str] = None
    points: int = 1
    question_type: str = "multiple_choice"  # multiple_choice, true_false, short_answer

class Quiz(BaseModel):
    """Quiz model for learning activities"""
    id: str
    title: str
    description: Optional[str] = None
    course_id: str
    questions: List[QuizQuestion] = []
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    time_limit: Optional[int] = None  # in minutes
    is_published: bool = False
    created_by: Optional[str] = None
    
    def add_question(self, question: QuizQuestion):
        """Add a question to the quiz"""
        self.questions.append(question)
        
    def get_total_points(self) -> int:
        """Calculate total points for the quiz"""
        return sum(q.points for q in self.questions)

class QuizAttempt(BaseModel):
    """Student attempt at a quiz"""
    id: str
    quiz_id: str
    student_id: str
    answers: Dict[str, Any]  # question_id -> answer
    score: Optional[float] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    time_taken: Optional[int] = None  # in seconds
    
    def calculate_score(self, quiz: Quiz) -> float:
        """Calculate the score for this attempt"""
        total_points = 0
        earned_points = 0
        
        for question in quiz.questions:
            total_points += question.points
            if question.id in self.answers:
                # Get the student's answer
                answer = self.answers[question.id]
                
                # Check if answer is correct
                if question.question_type == "multiple_choice":
                    correct_options = [opt.id for opt in question.options if opt.is_correct]
                    if isinstance(answer, list):
                        if set(answer) == set(correct_options):
                            earned_points += question.points
                    elif answer in correct_options:
                        earned_points += question.points
                elif question.question_type == "true_false":
                    correct_answer = next((opt.id for opt in question.options if opt.is_correct), None)
                    if answer == correct_answer:
                        earned_points += question.points
        
        # Save the score as a percentage
        self.score = (earned_points / total_points) * 100 if total_points > 0 else 0
        return self.score

# Word Cloud Models
class WordCloudSubmission(BaseModel):
    """Student submission for a word cloud"""
    id: str
    word_cloud_id: str
    student_id: str
    words: List[str]
    submitted_at: datetime = Field(default_factory=datetime.now)

class WordCloud(BaseModel):
    """Word Cloud model for learning activities"""
    id: str
    title: str
    description: Optional[str] = None
    course_id: str
    prompt: str
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    is_published: bool = False
    created_by: Optional[str] = None
    submissions: List[WordCloudSubmission] = []
    
    def add_submission(self, submission: WordCloudSubmission):
        """Add a submission to the word cloud"""
        self.submissions.append(submission)
    
    def get_word_frequency(self) -> Dict[str, int]:
        """Get frequency of words from all submissions"""
        word_count = {}
        for submission in self.submissions:
            for word in submission.words:
                word = word.lower().strip()
                if word:
                    word_count[word] = word_count.get(word, 0) + 1
        return word_count

# Short Answer Models
class ShortAnswerSubmission(BaseModel):
    """Student submission for a short answer question"""
    id: str
    question_id: str
    student_id: str
    answer: str
    submitted_at: datetime = Field(default_factory=datetime.now)
    feedback: Optional[str] = None
    score: Optional[float] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[str] = None

class ShortAnswerQuestion(BaseModel):
    """Short Answer Question model for learning activities"""
    id: str
    title: str
    question: str
    description: Optional[str] = None
    course_id: str
    max_points: int = 10
    sample_answer: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    is_published: bool = False
    created_by: Optional[str] = None
    submissions: List[ShortAnswerSubmission] = []
    
    def add_submission(self, submission: ShortAnswerSubmission):
        """Add a submission to the question"""
        self.submissions.append(submission)

# Mini Game Models
class MiniGameScore(BaseModel):
    """Student score for a mini game"""
    id: str
    game_id: str
    student_id: str
    score: float
    time_taken: int  # in seconds
    completed_at: datetime = Field(default_factory=datetime.now)

class MiniGame(BaseModel):
    """Mini Game model for learning activities"""
    id: str
    title: str
    description: Optional[str] = None
    course_id: str
    game_type: str  # e.g., matching, sorting, memory
    config: Dict[str, Any]  # Game specific configuration
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    is_published: bool = False
    created_by: Optional[str] = None
    scores: List[MiniGameScore] = []
    
    def add_score(self, score: MiniGameScore):
        """Add a score to the game"""
        self.scores.append(score)
    
    def get_high_scores(self, limit: int = 10) -> List[MiniGameScore]:
        """Get the top scores for this game"""
        return sorted(self.scores, key=lambda x: x.score, reverse=True)[:limit]