"""
COMP5241 Group 10 - Learning Activity Base Models
Defines the base models for learning activities
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class LearningActivity(BaseModel):
    """Base model for all learning activities"""
    id: str
    title: str
    description: Optional[str] = None
    course_id: str
    activity_type: str  # quiz, poll, wordcloud, shortanswer, minigame
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    is_published: bool = False
    created_by: Optional[str] = None
    
    def get_status(self) -> str:
        """Get the current status of this activity"""
        now = datetime.now()
        if not self.is_published:
            return "draft"
        elif self.due_date and now > self.due_date:
            return "expired"
        else:
            return "active"