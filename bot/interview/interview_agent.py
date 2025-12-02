"""
Interview Agent Module
Manages the interview flow and state
"""

from enum import Enum
import json
from .interview_questions import INTRODUCTION, QUESTIONS, COMPLETION_MESSAGE, get_motivational_message
from .question_analyzer import QuestionAnalyzer
from ..conversation.danua_identity import (
    is_about_danua_question,
    is_who_are_you_question,
    WHO_ARE_YOU_RESPONSE,
    ABOUT_DANUA_RESPONSE
)


class InterviewState(Enum):
    """Interview states"""
    WAITING_FOR_START = "waiting_for_start"
    GETTING_NAME_AGE = "getting_name_age"
    ASKING_QUESTION = "asking_question"
    FOLLOWING_UP = "following_up"
    COMPLETED = "completed"


class InterviewAgent:
    """Manages interview flow"""
    
    def __init__(self):
        self.analyzer = QuestionAnalyzer()
        self.interviews = {}  # user_id -> interview_data
    
    def start_interview(self, user_id: int):
        """Start a new interview for a user"""
        self.interviews[user_id] = {
            "state": InterviewState.GETTING_NAME_AGE,
            "current_question_index": 0,
            "name": None,
            "age": None,
            "answers": {},
            "follow_up_counts": {}  # question_id -> count of follow-ups
        }
        return INTRODUCTION
    
    def process_response(self, user_id: int, user_message: str) -> dict:
        """
        Process user response and return next message
        
        Returns:
            dict with keys:
                - message: str - Message to send to user
                - state: InterviewState - Current state
                - is_complete: bool - Whether interview is complete
                - result: dict - Final result if complete
        """
        # Check for questions about Danua first (before interview flow)
        if is_who_are_you_question(user_message):
            return {
                "message": WHO_ARE_YOU_RESPONSE,
                "state": InterviewState.WAITING_FOR_START if user_id not in self.interviews else self.interviews[user_id]["state"],
                "is_complete": False,
                "result": None
            }
        
        if is_about_danua_question(user_message):
            return {
                "message": ABOUT_DANUA_RESPONSE,
                "state": InterviewState.WAITING_FOR_START if user_id not in self.interviews else self.interviews[user_id]["state"],
                "is_complete": False,
                "result": None
            }
        
        if user_id not in self.interviews:
            # Start interview if not started
            return {
                "message": self.start_interview(user_id),
                "state": InterviewState.GETTING_NAME_AGE,
                "is_complete": False,
                "result": None
            }
        
        interview = self.interviews[user_id]
        
        # Handle different states
        if interview["state"] == InterviewState.GETTING_NAME_AGE:
            return self._handle_name_age(user_id, user_message)
        
        elif interview["state"] == InterviewState.ASKING_QUESTION:
            return self._handle_question_response(user_id, user_message)
        
        elif interview["state"] == InterviewState.FOLLOWING_UP:
            return self._handle_follow_up(user_id, user_message)
        
        elif interview["state"] == InterviewState.COMPLETED:
            # Even after completion, check for Danua questions
            if is_who_are_you_question(user_message):
                return {
                    "message": WHO_ARE_YOU_RESPONSE,
                    "state": InterviewState.COMPLETED,
                    "is_complete": True,
                    "result": self._get_result(user_id)
                }
            
            if is_about_danua_question(user_message):
                return {
                    "message": ABOUT_DANUA_RESPONSE,
                    "state": InterviewState.COMPLETED,
                    "is_complete": True,
                    "result": self._get_result(user_id)
                }
            
            return {
                "message": "مصاحبه قبلاً تمام شده. برای شروع مصاحبه جدید، /start رو بزن. اگر سوال دیگه‌ای داری، می‌تونی بپرسی! 😊",
                "state": InterviewState.COMPLETED,
                "is_complete": True,
                "result": self._get_result(user_id)
            }
    
    def _handle_name_age(self, user_id: int, user_message: str) -> dict:
        """Extract name and age from user message"""
        interview = self.interviews[user_id]
        
        # Try to extract name and age
        message_lower = user_message.lower()
        
        # Look for patterns
        name = None
        age = None
        
        # Try to find name and age patterns
        lines = user_message.split('\n')
        for line in lines:
            if 'نام' in line or 'اسم' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    name = parts[1].strip()
            elif 'سن' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    try:
                        age = int(parts[1].strip())
                    except:
                        pass
        
        # If not found in structured format, try to extract from natural text
        if not name or not age:
            words = user_message.split()
            for i, word in enumerate(words):
                if word.isdigit() and 3 <= int(word) <= 20:  # Reasonable age range
                    age = int(word)
                    # Name might be before or after age
                    if i > 0 and len(words[i-1]) > 2:
                        name = words[i-1]
                    elif i < len(words) - 1 and len(words[i+1]) > 2:
                        name = words[i+1]
        
        # If still not found, use AI to extract
        if not name or not age:
            from ..conversation.danua_identity import get_danua_system_prompt
            extraction_prompt = f"""این پیام یک کاربر است که می‌خواهد نام و سن خود را بگوید:

{user_message}

لطفاً نام و سن را استخراج کن و به این فرمت JSON پاسخ بده:
{{
    "name": "نام",
    "age": عدد
}}

اگر پیدا نکردی، null بگذار. فقط JSON را برگردان."""
            
            try:
                from ..conversation.openrouter_client import OpenRouterClient
                client = OpenRouterClient()
                result_text = client.get_response(
                    extraction_prompt,
                    system_prompt=get_danua_system_prompt()
                )
                
                import re
                json_match = re.search(r'\{[^}]+\}', result_text, re.DOTALL)
                if json_match:
                    extracted = json.loads(json_match.group())
                    if extracted.get("name"):
                        name = extracted["name"]
                    if extracted.get("age"):
                        age = extracted["age"]
            except:
                pass
        
        # Check if we have both
        if name and age:
            interview["name"] = name
            interview["age"] = age
            interview["state"] = InterviewState.ASKING_QUESTION
            
            question_data = QUESTIONS[0]
            return {
                "message": f"عالی {name}! 😊 حالا بذار سوالات رو شروع کنیم.\n\n{question_data['question']}",
                "state": InterviewState.ASKING_QUESTION,
                "is_complete": False,
                "result": None
            }
        else:
            missing = []
            if not name:
                missing.append("نام")
            if not age:
                missing.append("سن")
            
            return {
                "message": f"لطفاً {', '.join(missing)} خودت رو بهم بده.\nمثلاً: «من [نام] هستم و [سن] سال دارم»",
                "state": InterviewState.GETTING_NAME_AGE,
                "is_complete": False,
                "result": None
            }
    
    def _handle_question_response(self, user_id: int, user_message: str) -> dict:
        """Handle response to a question"""
        interview = self.interviews[user_id]
        question_index = interview["current_question_index"]
        question_data = QUESTIONS[question_index]
        
        # Save the answer first (even if incomplete, we need it for follow-up)
        if question_data["id"] not in interview["answers"]:
            interview["answers"][question_data["id"]] = user_message
        else:
            # If there's already an answer, combine them
            interview["answers"][question_data["id"]] = f"{interview['answers'][question_data['id']]}\n\n{user_message}"
        
        # Analyze response (use combined answer if exists)
        answer_to_analyze = interview["answers"][question_data["id"]]
        follow_up_count = interview.get("follow_up_counts", {}).get(question_data["id"], 0)
        analysis = self.analyzer.analyze_response(
            question_data["id"],
            question_data["question"],
            answer_to_analyze,
            question_data["required_elements"],
            follow_up_count=follow_up_count
        )
        
        if analysis["is_complete"]:
            # Save answer and move to next question
            # Reset follow-up count for this question
            if "follow_up_counts" not in interview:
                interview["follow_up_counts"] = {}
            interview["follow_up_counts"][question_data["id"]] = 0
            interview["current_question_index"] += 1
            
            # Check if all questions are done
            if interview["current_question_index"] >= len(QUESTIONS):
                interview["state"] = InterviewState.COMPLETED
                return {
                    "message": COMPLETION_MESSAGE,
                    "state": InterviewState.COMPLETED,
                    "is_complete": True,
                    "result": self._get_result(user_id)
                }
            else:
                # Ask next question with motivational message
                motivational_msg = get_motivational_message()
                next_question = QUESTIONS[interview["current_question_index"]]
                return {
                    "message": f"{motivational_msg}\n\n{next_question['question']}",
                    "state": InterviewState.ASKING_QUESTION,
                    "is_complete": False,
                    "result": None
                }
        else:
            # Need follow-up - increment counter
            if "follow_up_counts" not in interview:
                interview["follow_up_counts"] = {}
            interview["follow_up_counts"][question_data["id"]] = interview["follow_up_counts"].get(question_data["id"], 0) + 1
            interview["state"] = InterviewState.FOLLOWING_UP
            # Don't show follow_up questions again - feedback should be complete and ask only missing elements
            return {
                "message": analysis['feedback'],
                "state": InterviewState.FOLLOWING_UP,
                "is_complete": False,
                "result": None
            }
    
    def _handle_follow_up(self, user_id: int, user_message: str) -> dict:
        """Handle follow-up response"""
        interview = self.interviews[user_id]
        question_index = interview["current_question_index"]
        question_data = QUESTIONS[question_index]
        
        # Combine original answer with follow-up (append to existing answer)
        if question_data["id"] in interview["answers"]:
            combined_answer = f"{interview['answers'][question_data['id']]}\n\n{user_message}"
        else:
            combined_answer = user_message
        
        # Update stored answer
        interview["answers"][question_data["id"]] = combined_answer
        
        # Increment follow-up count (this is a new follow-up response)
        if "follow_up_counts" not in interview:
            interview["follow_up_counts"] = {}
        follow_up_count = interview["follow_up_counts"].get(question_data["id"], 0) + 1
        interview["follow_up_counts"][question_data["id"]] = follow_up_count
        
        # Analyze again with combined answer
        analysis = self.analyzer.analyze_response(
            question_data["id"],
            question_data["question"],
            combined_answer,
            question_data["required_elements"],
            follow_up_count=follow_up_count
        )
        
        if analysis["is_complete"]:
            # Save combined answer and move to next
            interview["answers"][question_data["id"]] = combined_answer
            # Reset follow-up count for this question
            if "follow_up_counts" not in interview:
                interview["follow_up_counts"] = {}
            interview["follow_up_counts"][question_data["id"]] = 0
            interview["current_question_index"] += 1
            interview["state"] = InterviewState.ASKING_QUESTION
            
            # Check if done
            if interview["current_question_index"] >= len(QUESTIONS):
                interview["state"] = InterviewState.COMPLETED
                return {
                    "message": COMPLETION_MESSAGE,
                    "state": InterviewState.COMPLETED,
                    "is_complete": True,
                    "result": self._get_result(user_id)
                }
            else:
                # Ask next question with motivational message
                motivational_msg = get_motivational_message()
                next_question = QUESTIONS[interview["current_question_index"]]
                return {
                    "message": f"{motivational_msg}\n\n{next_question['question']}",
                    "state": InterviewState.ASKING_QUESTION,
                    "is_complete": False,
                    "result": None
                }
        else:
            # Still need more info - follow_up_count already incremented above
            # Only show feedback (it should contain questions about missing elements)
            return {
                "message": analysis['feedback'],
                "state": InterviewState.FOLLOWING_UP,
                "is_complete": False,
                "result": None
            }
    
    def _get_result(self, user_id: int) -> dict:
        """Get final interview result as JSON"""
        interview = self.interviews[user_id]
        result = {
            "name": interview["name"],
            "age": interview["age"],
            "q1": interview["answers"].get("q1", ""),
            "q2": interview["answers"].get("q2", ""),
            "q3": interview["answers"].get("q3", ""),
            "q4": interview["answers"].get("q4", ""),
            "q5": interview["answers"].get("q5", ""),
            "q6": interview["answers"].get("q6", ""),
            "q7": interview["answers"].get("q7", "")
        }
        return result
    
    def reset_interview(self, user_id: int):
        """Reset interview for a user"""
        if user_id in self.interviews:
            del self.interviews[user_id]
    
    def get_interview_state(self, user_id: int) -> InterviewState:
        """Get current interview state for a user"""
        if user_id not in self.interviews:
            return InterviewState.WAITING_FOR_START
        return self.interviews[user_id]["state"]

