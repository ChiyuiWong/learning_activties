"""
COMP5241 Group 10 - Poll Models
Defines the models for polls
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PollOption(BaseModel):
    """Option for a poll"""
    id: str
    text: str
    votes: int = 0
    
    def add_vote(self):
        """Increment the vote count for this option"""
        self.votes += 1

class Poll(BaseModel):
    """Poll model for learning activities"""
    id: str
    title: str
    question: str
    description: Optional[str] = None
    course_id: str
    options: List[PollOption] = []
    created_at: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    is_published: bool = False
    created_by: Optional[str] = None
    
    def add_option(self, option: PollOption):
        """Add an option to the poll"""
        self.options.append(option)
    
    def get_total_votes(self) -> int:
        """Calculate the total number of votes"""
        return sum(option.votes for option in self.options)
    
    def get_results(self) -> Dict[str, Any]:
        """Get poll results with percentage for each option"""
        total_votes = self.get_total_votes()
        results = {
            'total_votes': total_votes,
            'options': []
        }
        
        for option in self.options:
            percentage = (option.votes / total_votes * 100) if total_votes > 0 else 0
            results['options'].append({
                'id': option.id,
                'text': option.text,
                'votes': option.votes,
                'percentage': round(percentage, 2)
            })
        
        return results