"""
Data Validator Module
Validates interview completion and data quality
"""

from typing import Dict, Tuple, Optional


class DataValidator:
    """Validates interview data completeness and quality"""
    
    REQUIRED_QUESTIONS = 7
    REQUIRED_FIELDS = ["name", "age", "q1", "q2", "q3", "q4", "q5", "q6", "q7"]
    
    @staticmethod
    def validate_interview_completion(interview_result: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate that interview is complete with all required data
        
        Args:
            interview_result: Dictionary containing interview results
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if all required fields exist
        missing_fields = []
        for field in DataValidator.REQUIRED_FIELDS:
            if field not in interview_result:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Check if answers are not empty
        empty_answers = []
        for i in range(1, 8):
            q_key = f"q{i}"
            if not interview_result.get(q_key, "").strip():
                empty_answers.append(f"سوال {i}")
        
        if empty_answers:
            return False, f"Empty answers for: {', '.join(empty_answers)}"
        
        # Check name and age
        if not interview_result.get("name", "").strip():
            return False, "Name is missing or empty"
        
        if not interview_result.get("age"):
            return False, "Age is missing"
        
        return True, None
    
    @staticmethod
    def check_question_count(answers: dict) -> Tuple[bool, int, int]:
        """
        Check how many questions have been answered
        
        Args:
            answers: Dictionary of answers (q1, q2, etc.)
            
        Returns:
            Tuple of (is_complete, answered_count, required_count)
        """
        answered = 0
        for i in range(1, 8):
            q_key = f"q{i}"
            if q_key in answers and answers[q_key].strip():
                answered += 1
        
        is_complete = answered >= DataValidator.REQUIRED_QUESTIONS
        return is_complete, answered, DataValidator.REQUIRED_QUESTIONS
    
    @staticmethod
    def get_missing_questions(answers: dict) -> list[str]:
        """
        Get list of missing question IDs
        
        Args:
            answers: Dictionary of answers
            
        Returns:
            List of missing question IDs (e.g., ["q3", "q5"])
        """
        missing = []
        for i in range(1, 8):
            q_key = f"q{i}"
            if q_key not in answers or not answers[q_key].strip():
                missing.append(q_key)
        
        return missing
    
    @staticmethod
    def validate_data_quality(interview_result: dict) -> Tuple[bool, list[str]]:
        """
        Validate data quality (not just completeness)
        
        Args:
            interview_result: Dictionary containing interview results
            
        Returns:
            Tuple of (is_acceptable, warnings)
        """
        warnings = []
        
        # Check for very short answers
        for i in range(1, 8):
            q_key = f"q{i}"
            answer = interview_result.get(q_key, "")
            if answer and len(answer.strip()) < 10:
                warnings.append(f"سوال {i} پاسخ خیلی کوتاهی دارد")
        
        # Check name format
        name = interview_result.get("name", "")
        if name and len(name.strip()) < 2:
            warnings.append("نام خیلی کوتاه است")
        
        # Check age range
        age = interview_result.get("age")
        if age:
            try:
                age_int = int(age) if isinstance(age, str) else age
                if age_int < 3 or age_int > 20:
                    warnings.append(f"سن ({age}) خارج از محدوده معمول است")
            except (ValueError, TypeError):
                warnings.append("سن نامعتبر است")
        
        # Warnings don't prevent processing, just inform
        return True, warnings

