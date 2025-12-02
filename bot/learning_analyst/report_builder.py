"""
Report Builder Module
Builds and formats analysis reports
"""

from typing import Dict, Optional


class ReportBuilder:
    """Builds formatted analysis reports"""
    
    @staticmethod
    def build_fallback_report(interview_result: dict) -> str:
        """
        Build a fallback report when AI analysis fails
        
        Args:
            interview_result: Dictionary containing interview results
            
        Returns:
            Fallback report string
        """
        name = interview_result.get("name", "نامشخص")
        age = interview_result.get("age", "نامشخص")
        
        # Get question previews
        questions_preview = []
        for i in range(1, 8):
            q_key = f"q{i}"
            answer = interview_result.get(q_key, "ندارد")
            preview = answer[:100] + "..." if len(answer) > 100 else answer
            questions_preview.append(f"- سوال {i}: {preview}")
        
        return f"""🟩 1. اطلاعات اولیه

نام: {name}
سن: {age}

⚠️ متاسفانه تحلیل کامل در دسترس نیست. لطفاً داده‌های مصاحبه را به صورت دستی بررسی کنید.

پاسخ‌های مصاحبه:
{chr(10).join(questions_preview)}"""
    
    @staticmethod
    def format_report_header(name: str, age: str, user_id: int) -> str:
        """
        Format report header with user information
        
        Args:
            name: User's name
            age: User's age
            user_id: User's Telegram ID
            
        Returns:
            Formatted header string
        """
        return f"📊 گزارش تحلیل یادگیری\n\n👤 کاربر: {name} (سن: {age})\n🆔 User ID: {user_id}\n\n{'='*50}\n\n"
    
    @staticmethod
    def split_long_message(message: str, max_length: int = 4096) -> list[str]:
        """
        Split long message into chunks
        
        Args:
            message: Message to split
            max_length: Maximum length per chunk
            
        Returns:
            List of message chunks
        """
        if len(message) <= max_length:
            return [message]
        
        chunks = []
        current_chunk = ""
        
        # Try to split at section boundaries (🟩, 🟧, etc.)
        lines = message.split('\n')
        for line in lines:
            # If adding this line would exceed limit, save current chunk and start new one
            if len(current_chunk) + len(line) + 1 > max_length and current_chunk:
                chunks.append(current_chunk)
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

