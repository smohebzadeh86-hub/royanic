"""
Workflow Manager Module
Manages the workflow between interview agent and learning analyst
"""

from typing import Dict, Optional
from ..interview import InterviewAgent
from ..learning_analyst import LearningAnalystAgent


class WorkflowManager:
    """Manages workflow between agents"""
    
    def __init__(self):
        """Initialize workflow manager"""
        self.interview_agent = InterviewAgent()
        self.learning_analyst = LearningAnalystAgent()
    
    def process_interview_step(self, user_id: int, user_message: str) -> Dict:
        """
        Process a single step in the interview workflow
        
        Args:
            user_id: User's Telegram ID
            user_message: User's message
            
        Returns:
            Dictionary with workflow result
        """
        # Process with interview agent
        result = self.interview_agent.process_response(user_id, user_message)
        
        return {
            "interview_result": result,
            "is_interview_complete": result.get("is_complete", False),
            "interview_data": result.get("result")
        }
    
    def trigger_analysis(self, interview_data: dict) -> str:
        """
        Trigger learning analysis on completed interview
        
        Args:
            interview_data: Complete interview data dictionary
            
        Returns:
            Analysis report string
        """
        if not interview_data:
            return "⚠️ داده‌های مصاحبه موجود نیست"
        
        try:
            report = self.learning_analyst.analyze_interview(interview_data)
            return report
        except Exception as e:
            print(f"[ERROR] Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"⚠️ خطا در تحلیل: {str(e)}"
    
    def get_interview_progress(self, user_id: int) -> Optional[Dict]:
        """
        Get current interview progress for a user
        
        Args:
            user_id: User's Telegram ID
            
        Returns:
            Dictionary with progress information or None
        """
        if user_id not in self.interview_agent.interviews:
            return None
        
        interview = self.interview_agent.interviews[user_id]
        current_index = interview.get("current_question_index", 0)
        total_questions = 7
        
        return {
            "current_question": current_index + 1,
            "total_questions": total_questions,
            "progress_percentage": int((current_index / total_questions) * 100),
            "answers_count": len(interview.get("answers", {})),
            "state": interview.get("state").value if interview.get("state") else None
        }

