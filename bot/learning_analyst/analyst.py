"""
Learning Analyst Agent Module
Main class for analyzing interview results and generating reports
"""

from ..conversation.openrouter_client import OpenRouterClient
from .data_extractor import DataExtractor
from .report_builder import ReportBuilder
from .prompt_templates import PromptTemplates


class LearningAnalystAgent:
    """Analyzes interview data and generates learning profile report"""
    
    def __init__(self, admin_id: int = 5184305178):
        """
        Initialize Learning Analyst Agent
        
        Args:
            admin_id: Telegram ID of admin to receive reports
        """
        self.client = OpenRouterClient()
        self.admin_id = admin_id
        self.data_extractor = DataExtractor()
        self.report_builder = ReportBuilder()
        self.prompt_templates = PromptTemplates()
    
    def analyze_interview(self, interview_result: dict) -> str:
        """
        Analyze interview results and generate comprehensive report
        
        Args:
            interview_result: Dictionary containing name, age, and q1-q7 answers
            
        Returns:
            Complete analysis report as formatted string
        """
        # Validate data
        is_valid, error_message = self.data_extractor.validate_data(interview_result)
        if not is_valid:
            print(f"[WARNING] Invalid interview data: {error_message}")
            return self.report_builder.build_fallback_report(interview_result)
        
        # Extract data
        data = self.data_extractor.extract_interview_data(interview_result)
        
        # Generate analysis prompt
        analysis_prompt = self.prompt_templates.get_analysis_prompt(data)
        system_prompt = self.prompt_templates.get_system_prompt()
        
        try:
            # Get AI analysis
            report = self.client.get_response(
                analysis_prompt,
                system_prompt=system_prompt
            )
            
            return report
            
        except Exception as e:
            # Fallback report if AI fails
            print(f"[ERROR] Learning analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.report_builder.build_fallback_report(interview_result)

