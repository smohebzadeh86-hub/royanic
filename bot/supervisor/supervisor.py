"""
Supervisor Agent Module
Main supervisor agent that coordinates between interview and analysis agents
"""

from typing import Dict, Optional
from .workflow_manager import WorkflowManager
from .data_validator import DataValidator


class SupervisorAgent:
    """
    Supervisor Agent that manages workflow between interview and analysis agents
    
    Responsibilities:
    - Monitor that interview agent completes all 7 questions
    - Ensure responses are complete (based on interview agent signals)
    - When all data is ready: send to learning analyst
    - Deliver final report
    """
    
    def __init__(self):
        """Initialize Supervisor Agent"""
        self.workflow_manager = WorkflowManager()
        self.data_validator = DataValidator()
    
    def handle_user_message(self, user_id: int, user_message: str) -> Dict:
        """
        Handle user message and coordinate workflow
        
        Args:
            user_id: User's Telegram ID
            user_message: User's message
            
        Returns:
            Dictionary with:
                - message: str - Message to send to user
                - state: str - Current state
                - is_complete: bool - Whether interview is complete
                - should_trigger_analysis: bool - Whether to trigger analysis
                - interview_data: dict - Interview data if complete
        """
        # Process interview step
        workflow_result = self.workflow_manager.process_interview_step(user_id, user_message)
        
        interview_result = workflow_result["interview_result"]
        is_complete = workflow_result["is_interview_complete"]
        interview_data = workflow_result["interview_data"]
        
        # If interview is complete, validate data
        should_trigger_analysis = False
        validation_message = None
        
        if is_complete and interview_data:
            # Validate completion
            is_valid, error_message = self.data_validator.validate_interview_completion(interview_data)
            
            if is_valid:
                # Check data quality (warnings don't prevent processing)
                is_acceptable, warnings = self.data_validator.validate_data_quality(interview_data)
                
                if warnings:
                    print(f"[WARNING] Data quality warnings: {warnings}")
                
                should_trigger_analysis = True
                validation_message = "✅ مصاحبه کامل و معتبر است"
            else:
                validation_message = f"⚠️ خطا در اعتبارسنجی: {error_message}"
                print(f"[ERROR] Validation failed: {error_message}")
        
        return {
            "message": interview_result.get("message", ""),
            "state": interview_result.get("state").value if interview_result.get("state") else None,
            "is_complete": is_complete,
            "should_trigger_analysis": should_trigger_analysis,
            "interview_data": interview_data if should_trigger_analysis else None,
            "validation_message": validation_message
        }
    
    def trigger_analysis_and_get_report(self, interview_data: dict) -> str:
        """
        Trigger analysis and get final report
        
        Args:
            interview_data: Complete interview data dictionary
            
        Returns:
            Analysis report string
        """
        # Validate before analysis
        is_valid, error_message = self.data_validator.validate_interview_completion(interview_data)
        
        if not is_valid:
            return f"⚠️ خطا در اعتبارسنجی داده‌ها: {error_message}"
        
        # Trigger analysis
        report = self.workflow_manager.trigger_analysis(interview_data)
        
        return report
    
    def get_progress(self, user_id: int) -> Optional[Dict]:
        """
        Get interview progress for a user
        
        Args:
            user_id: User's Telegram ID
            
        Returns:
            Progress dictionary or None
        """
        return self.workflow_manager.get_interview_progress(user_id)
    
    def start_interview(self, user_id: int) -> str:
        """
        Start a new interview for a user
        
        Args:
            user_id: User's Telegram ID
            
        Returns:
            Introduction message
        """
        return self.workflow_manager.interview_agent.start_interview(user_id)
    
    def reset_interview(self, user_id: int):
        """
        Reset interview for a user
        
        Args:
            user_id: User's Telegram ID
        """
        self.workflow_manager.interview_agent.reset_interview(user_id)

