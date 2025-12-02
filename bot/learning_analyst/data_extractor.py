"""
Data Extractor Module
Extracts and validates data from interview results
"""

from typing import Dict, Optional


class DataExtractor:
    """Extracts and validates interview data"""
    
    @staticmethod
    def extract_interview_data(interview_result: dict) -> Dict[str, str]:
        """
        Extract interview data from result dictionary
        
        Args:
            interview_result: Dictionary containing interview results
            
        Returns:
            Dictionary with extracted data (name, age, q1-q7)
        """
        return {
            "name": interview_result.get("name", "نامشخص"),
            "age": str(interview_result.get("age", "نامشخص")),
            "q1": interview_result.get("q1", ""),
            "q2": interview_result.get("q2", ""),
            "q3": interview_result.get("q3", ""),
            "q4": interview_result.get("q4", ""),
            "q5": interview_result.get("q5", ""),
            "q6": interview_result.get("q6", ""),
            "q7": interview_result.get("q7", "")
        }
    
    @staticmethod
    def validate_data(interview_result: dict) -> tuple[bool, Optional[str]]:
        """
        Validate that interview result has required fields
        
        Args:
            interview_result: Dictionary containing interview results
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["name", "age", "q1", "q2", "q3", "q4", "q5", "q6", "q7"]
        
        missing_fields = []
        for field in required_fields:
            if field not in interview_result or not interview_result[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    @staticmethod
    def get_question_labels() -> Dict[str, str]:
        """
        Get labels for each question
        
        Returns:
            Dictionary mapping question IDs to labels
        """
        return {
            "q1": "یادگیری معتادکننده",
            "q2": "بازی‌ها و فعالیت‌های مورد علاقه",
            "q3": "خسته‌کننده‌ها",
            "q4": "ترجیح روش یادگیری",
            "q5": "بهترین یادگیری",
            "q6": "یادگیری تیمی/شخصی",
            "q7": "بازخورد"
        }

