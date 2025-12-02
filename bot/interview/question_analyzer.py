"""
Question Analyzer Module
Analyzes user responses to determine if they contain enough information
"""

from ..conversation.openrouter_client import OpenRouterClient
from ..conversation.danua_identity import get_danua_system_prompt


class QuestionAnalyzer:
    """Analyzes user responses to interview questions"""
    
    def __init__(self):
        self.client = OpenRouterClient()
    
    def analyze_response(self, question_id: str, question_text: str, user_response: str, required_elements: list, follow_up_count: int = 0) -> dict:
        """
        Analyze if user response contains enough information
        
        Args:
            question_id: ID of the question (q1, q2, etc.)
            question_text: The question text
            user_response: User's response
            required_elements: List of required elements to check
            follow_up_count: Number of follow-up responses user has given (0 = first response)
        
        Returns:
            dict with keys:
                - is_complete: bool
                - missing_elements: list
                - feedback: str
        """
        # Create analysis prompt with Danua's personality
        danua_prompt = get_danua_system_prompt()
        
        # Add leniency instruction if user has given multiple responses
        leniency_note = ""
        if follow_up_count >= 3:
            leniency_note = "\n\n⚠️ توجه: کاربر تا الان 3 بار یا بیشتر پاسخ داده. اگر حداقل 60% از عناصر مورد نیاز رو پوشش داده، می‌تونی is_complete رو true کنی.\n"
        elif follow_up_count >= 2:
            leniency_note = "\n\n⚠️ توجه: کاربر تا الان 2 بار پاسخ داده. اگر حداقل 80% از عناصر مورد نیاز رو پوشش داده، is_complete رو true کن.\n"
        else:
            leniency_note = "\n\n⚠️ مهم: کاربر اولین یا دومین باره که پاسخ میده. باید دقیق باشی و همه عناصر مورد نیاز رو چک کنی. فقط اگر واقعاً همه یا اکثر عناصر رو پوشش داده، is_complete رو true کن.\n"
        
        analysis_prompt = f"""{danua_prompt}

⚠️ هشدار مهم: هرگز از "شما" یا "پاسخ شما" استفاده نکن! همیشه "تو" بگو و لحن صمیمی داشته باش!

تو دانوا هستی - یک دوست صمیمی که می‌خوای به کاربر (که یک بچه است) کمک کنی تا پاسخش رو کامل کنه. این یک مکالمه ادامه‌داره، پس نباید سلام کنی یا شروع جدیدی بکنی. همیشه لحن صمیمی و دوستانه داشته باش، مثل یک دوست نزدیک که با بچه حرف می‌زنه.

🚫 ممنوع: "پاسخ شما..."، "لطفاً..."، "شما باید..."، کلمات سخت، سوالات پیچیده
✅ مجاز: "چه باحال گفتی که..."، "می‌بینم که..."، "عالی!..."، کلمات ساده، سوالات ساده و قابل فهم

قوانین مهم برای سوالات (بر اساس تست مامان):
- سوالات باید خیلی ساده و قابل فهم باشه برای بچه‌ها
- از کلمات ساده استفاده کن، نه کلمات سخت
- سوالات کوتاه باشه و واضح
- مثال بزن تا بچه بفهمه چی می‌خوای
- سوالات رو به زبان ساده بپرس
- اما لحن باید مثل دانوا باشه (صمیمی و دوستانه)، نه مثل مادر

سوال:
{question_text}

پاسخ کاربر (شامل همه پاسخ‌های قبلی در این سوال):
{user_response}

عناصر مورد نیاز در پاسخ (باید همه اینها در پاسخ باشه):
{chr(10).join(f'- {element}' for element in required_elements)}

{leniency_note}

حالا باید دقیقاً و با جزئیات تحلیل کنی:
1. کاربر چه چیزهایی گفته؟ (جزئیات کامل - همه چیزهایی که تا الان گفته)
2. **مهم**: برای هر عنصر از required_elements، بررسی کن که آیا کاربر اون رو پوشش داده یا نه:
   - اگر گفته → تایید کن و در missing_elements نذار
   - اگر نگفته یا ناقص گفته → در missing_elements بذار
3. آیا پاسخ کلی و مبهمه یا جزئیات کافی داره؟
4. دقیقاً چه اطلاعاتی کمه؟ (فقط چیزهایی که واقعاً نگفته)
5. **بسیار مهم**: دنبال نکات و عناصر مهم باش - باید همه عناصر کلیدی رو چک کنی، نه اینکه خیلی سریع ول کنی

قوانین مهم:
- فقط چیزهایی که کاربر نگفته رو بپرس، نه چیزهایی که قبلاً گفته
- اگر کاربر چیزی رو گفته، اون رو تایید کن و نگو دوباره
- اگر کاربر گفته "یادم نمیاد" یا "نمیدونم"، بپذیر و فقط چیزهای دیگه رو بپرس

⚠️⚠️⚠️ قانون بسیار مهم برای تشخیص کافی بودن اطلاعات ⚠️⚠️⚠️:
- **اولویت اول**: باید همه عناصر مورد نیاز (required_elements) رو چک کنی و ببینی آیا کاربر همه رو پوشش داده یا نه
- **قانون اصلی**: فقط وقتی is_complete رو true کن که کاربر حداقل 80% از عناصر مورد نیاز رو پوشش داده باشه
- **قانون سهل‌گیری (فقط در موارد خاص)**: 
  * اگر follow_up_count >= 3 (یعنی کاربر 3 بار یا بیشتر پاسخ داده) و حداقل 60% از عناصر رو پوشش داده، می‌تونی is_complete رو true کنی
  * اگر follow_up_count >= 2 و کاربر 80%+ از عناصر رو پوشش داده، is_complete رو true کن
- **هرگز** اگر کاربر فقط 1 عنصر از 3 عنصر رو گفته (مثلاً فقط "موضوع یادگیری" رو گفته)، is_complete رو false کن و بقیه عناصر رو بپرس
- **مهم**: دنبال نکات و عناصر مهم باش - باید همه عناصر کلیدی رو بپرسی، نه اینکه خیلی سریع ول کنی

مثال تحلیل خوب و درست (این لحن رو باید همیشه استفاده کنی):
اگر کاربر گفته: "آزادی انتخاب داشتم، می‌تونستم ببینم، می‌تونستم پازل کنم، خیلی هیجان داشتم"

تحلیل درست (لحن صمیمی و دوستانه دانوا، سوالات ساده بر اساس تست مامان):
"چه باحال گفتی که آزادی انتخاب داشتی و هیجان‌زده بودی! ✨ این خیلی خوبه! می‌خوام بیشتر بدونم: دقیقا چی یاد می‌گرفتی؟ مثلاً زبان انگلیسی؟ یا نقاشی؟ یا ریاضی؟ و اینکه وقتی می‌تونستی خودت انتخاب کنی که چی یاد بگیری، چه احساسی داشتی؟ مثلاً خوشحال بودی؟ یا هیجان‌زده بودی؟ 🌟"

تحلیل اشتباه (هرگز این لحن رو استفاده نکن):
"پاسخ شما موضوع یادگیری را پوشش می‌دهد، اما محرک انگیزشی و احساس یا هیجان را مشخص نکرده‌اید. لطفاً دقیق‌تر توضیح بده که موضوع یادگیری و محرک انگیزشی چه بود."

چرا اشتباهه:
- از "شما" استفاده کرده (باید "تو" باشه)
- لحن رسمی و خشکه (باید صمیمی باشه)
- نگفته چه چیزهایی کاربر گفته (باید تایید کنه)
- از "لطفاً" استفاده کرده (باید طبیعی باشه)

⚠️⚠️⚠️ قبل از اینکه is_complete رو true کنی، حتماً چک کن:
1. آیا کاربر همه یا اکثر (80%+) عناصر مورد نیاز رو پوشش داده؟
2. آیا پاسخ واقعاً کامل و مفیده یا فقط یک چیز رو گفته؟
3. اگر فقط 1 عنصر از 3 عنصر رو گفته، حتماً is_complete = false کن و بقیه رو بپرس

لطفاً تحلیل دقیق و جزئیات‌دار کن و به این فرمت JSON پاسخ بده:
{{
    "is_complete": true/false,
    "missing_elements": ["عنصر1", "عنصر2"],
    "feedback": "تحلیل دقیق، جزئیات‌دار و انسان‌گونه از زبان دانوا"
}}

⚠️⚠️⚠️ قوانین بسیار مهم برای feedback (حتماً رعایت کن - این قوانین غیرقابل تغییر هستند) ⚠️⚠️⚠️:

1. هرگز از "شما" استفاده نکن - همیشه "تو" بگو
2. هرگز نگو "پاسخ شما..." - این ممنوعه! بگو "می‌بینم که..." یا "چه باحال گفتی که..."
3. هرگز نگو "لطفاً..." - این لحن رسمیه و ممنوعه
4. همیشه اول چیزهایی که کاربر گفته رو تایید کن با عبارات مثل:
   * "چه باحال گفتی که..."
   * "عالی! می‌بینم که..."
   * "خوبه که گفتی..."
   * "جالب بود که..."
5. بعد فقط چیزهایی که واقعاً کمه رو بپرس (نه چیزهایی که قبلاً گفته)
6. به صورت سوالات دوستانه و مکالمه‌ای بپرس (مثل "می‌خوام بیشتر بفهمم..." یا "می‌تونی بیشتر بگی درباره...")
 7. باید سوالات مشخص و دقیق بپرسی درباره missing elements (نه کلی)
 8. سوالات باید خیلی ساده باشه که بچه بفهمه - بر اساس تست مامان (سوالات ساده و قابل فهم)
 9. از کلمات ساده استفاده کن - نه کلمات سخت یا پیچیده
 10. سوالات کوتاه باشه و واضح - هر سوال یک چیز رو بپرس
 11. مثال بزن تا بچه بفهمه چی می‌خوای (مثلاً "مثلاً زبان انگلیسی؟ یا نقاشی؟")
 12. لحن مثل دانوا باشه (صمیمی و دوستانه مثل یک دوست)، نه مثل مادر، نه یک ربات
 13. طبیعی و انسان‌گونه باشه - مثل صحبت با یک دوست نزدیک
 14. حداقل 3-4 جمله باشه و شامل سوالات ساده و مشخص باشه
 15. از کلمات مکالمه‌ای ساده استفاده کن مثل "می‌خوام بفهمم"، "می‌تونی بگی"، "جالب بود"، "خوبه"، "چه باحال"
 16. از ایموجی استفاده کن (✨، 🌟، 😊) ولی نه زیاد
 17. اگر کاربر چیزی رو گفته، اون رو تکرار نکن و نگو "لطفاً دقیق‌تر توضیح بده" - فقط چیزهای جدید رو بپرس
 18. feedback باید کامل باشه و شامل سوالات ساده و مشخص درباره missing elements باشه
 19. هرگز سلام نکن یا شروع جدید نکن (این مکالمه ادامه‌داره)

مثال‌های لحن خوب (همیشه از این لحن استفاده کن - لحن دانوا، سوالات ساده):
- "چه باحال گفتی که [چیزی که کاربر گفته]! ✨ می‌خوام بیشتر بدونم [فقط چیزهای ناقص]. مثلاً [مثال ساده]؟ یا [مثال دیگر]؟ 🌟"
- "عالی! می‌بینم که گفتی [چیزی که کاربر گفته]. این خیلی خوبه! ولی می‌خوام بیشتر بفهمم [فقط چیزهای ناقص]. مثلاً [مثال ساده]؟"
- "خوبه که گفتی [چیزی که کاربر گفته]! حالا می‌خوام بفهمم [فقط چیزهای ناقص]. مثلاً [مثال ساده]؟ یا [مثال دیگر]؟ 😊"
- "می‌بینم که [چیزی که کاربر گفته] رو گفتی. جالب بود! ✨ ولی یه چیز دیگه هم می‌خوام بفهمم [فقط چیزهای ناقص]. مثلاً [مثال ساده]؟ 🌟"

مثال‌های لحن خوب (همیشه از این لحن استفاده کن):
- "چه باحال گفتی که [چیزی که کاربر گفته]! این خیلی خوبه که [تایید]. ✨ می‌خوام بیشتر بدونم [فقط چیزهای ناقص]... 🌟"
- "عالی! می‌بینم که گفتی [چیزی که کاربر گفته]. این خیلی خوبه! ولی می‌خوام بیشتر بفهمم [فقط چیزهای ناقص]..."
- "خوبه که گفتی [چیزی که کاربر گفته]. جالب بود! حالا می‌خوام دقیق‌تر بفهمم که [فقط چیزهای ناقص]..."
- "می‌بینم که [چیزی که کاربر گفته] رو گفتی. این خیلی خوبه! ✨ ولی یه چیز دیگه هم می‌خوام بفهمم [فقط چیزهای ناقص]... 🌟"

فقط JSON را برگردان، هیچ متن اضافی نباشه."""

        try:
            # Get AI analysis
            # Use Danua's personality in the conversation
            analysis_text = self.client.get_response(
                analysis_prompt,
                system_prompt=get_danua_system_prompt()
            )
            
            # Try to extract JSON from response
            import json
            import re
            
            # Try multiple patterns to find JSON
            # Pattern 1: Find JSON object with balanced braces (handles nested objects and arrays)
            brace_count = 0
            start_idx = -1
            json_match = None
            
            for i, char in enumerate(analysis_text):
                if char == '{':
                    if brace_count == 0:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx != -1:
                        json_match = analysis_text[start_idx:i+1]
                        break
            
            # Pattern 2: Fallback - try simple regex
            if not json_match:
                json_match_obj = re.search(r'\{[^{}]*"is_complete"[^{}]*\}', analysis_text, re.DOTALL)
                if json_match_obj:
                    json_match = json_match_obj.group()
            
            # Pattern 3: Last resort - find any JSON-like structure
            if not json_match:
                json_match_obj = re.search(r'\{[^}]*\}', analysis_text, re.DOTALL)
                if json_match_obj:
                    json_match = json_match_obj.group()
            
            if json_match:
                try:
                    # Clean up the JSON string (remove markdown code blocks if present)
                    json_str = json_match
                    if json_str.startswith('```'):
                        json_str = re.sub(r'```json\s*', '', json_str)
                        json_str = re.sub(r'```\s*', '', json_str)
                    
                    analysis_json = json.loads(json_str)
                    
                    # Validate that we have the required fields
                    if "is_complete" in analysis_json and "feedback" in analysis_json:
                        feedback = analysis_json.get("feedback", "")
                        # Post-process feedback to ensure friendly tone
                        feedback = self._fix_feedback_tone(feedback, user_response)
                        return {
                            "is_complete": analysis_json.get("is_complete", False),
                            "missing_elements": analysis_json.get("missing_elements", []),
                            "feedback": feedback
                        }
                except json.JSONDecodeError as e:
                    # If JSON parsing fails, try to extract manually
                    print(f"[WARNING] JSON parsing failed: {str(e)}")
                    print(f"[DEBUG] AI Response: {analysis_text[:200]}")
            
            # If we couldn't parse JSON, try to extract feedback from text
            # Look for feedback-like patterns
            feedback_patterns = [
                r'feedback["\']?\s*:\s*["\']([^"\']+)["\']',
                r'feedback["\']?\s*:\s*([^\n,}]+)',
            ]
            
            for pattern in feedback_patterns:
                feedback_match = re.search(pattern, analysis_text, re.IGNORECASE)
                if feedback_match:
                    feedback = feedback_match.group(1).strip()
                    # Try to determine if complete by looking for keywords
                    is_complete = "کامل" in analysis_text.lower() or "تمام" in analysis_text.lower()
                    return {
                        "is_complete": is_complete,
                        "missing_elements": [] if is_complete else required_elements,
                        "feedback": feedback if feedback else "لطفاً بیشتر برام توضیح بده."
                    }
            
            # Fallback: basic analysis
            print(f"[WARNING] Could not parse AI response, using fallback")
            print(f"[DEBUG] AI Response: {analysis_text[:500]}")
            return self._basic_analysis(user_response, required_elements, question_text, follow_up_count)
            
        except Exception as e:
            # Fallback to basic analysis if AI fails
            print(f"[ERROR] AI analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._basic_analysis(user_response, required_elements, question_text, follow_up_count)
    
    def _fix_feedback_tone(self, feedback: str, user_response: str) -> str:
        """
        Fix feedback tone to ensure it's friendly, simple, and uses 'تو' instead of 'شما'
        Makes questions simple and understandable for children
        """
        # Replace formal language with friendly language
        feedback = feedback.replace("پاسخ شما", "می‌بینم که")
        feedback = feedback.replace("شما باید", "می‌تونی")
        feedback = feedback.replace("شما", "تو")
        feedback = feedback.replace("لطفاً", "")
        feedback = feedback.replace("لطفا", "")
        feedback = feedback.replace("مشخص نکرده‌اید", "نگفتی")
        feedback = feedback.replace("مشخص نکرده اید", "نگفتی")
        feedback = feedback.replace("پوشش می‌دهد", "گفتی")
        feedback = feedback.replace("پوشش می دهد", "گفتی")
        
        # Remove formal phrases
        feedback = feedback.replace("لطفاً دقیق‌تر توضیح بده", "")
        feedback = feedback.replace("لطفا دقیق تر توضیح بده", "")
        
        # Simplify complex words for children
        feedback = feedback.replace("مهارت هنری", "نقاشی یا کاردستی")
        feedback = feedback.replace("موضوع علمی", "ریاضی یا علوم")
        feedback = feedback.replace("زبان جدید", "زبان انگلیسی یا زبان دیگه")
        feedback = feedback.replace("مباحث", "درس‌ها")
        feedback = feedback.replace("روش یادگیری", "طریقه یاد گرفتن")
        
        # If feedback doesn't start with a friendly phrase, add one
        friendly_starters = ["چه باحال", "عالی", "خوبه", "جالب", "می‌بینم"]
        feedback_lower = feedback.lower()
        
        if not any(feedback_lower.startswith(starter) for starter in friendly_starters):
            # Try to extract what user said and create friendly start
            if "زبان" in user_response.lower() or "یاد" in user_response.lower():
                if "داستان" in user_response.lower():
                    feedback = f"چه باحال گفتی که داشتی زبان می‌خوندی و به شکل داستان بود! ✨ {feedback}"
                else:
                    feedback = f"عالی! می‌بینم که {feedback}"
            else:
                feedback = f"خوبه که گفتی! {feedback}"
        
        # Clean up any remaining formal language
        feedback = feedback.strip()
        if feedback.startswith("می‌بینم که") and "گفتی" not in feedback:
            # Add what user said
            if "زبان" in user_response.lower():
                feedback = feedback.replace("می‌بینم که", "چه باحال گفتی که داشتی زبان می‌خوندی! ✨ می‌بینم که")
        
        # Ensure questions are simple - add examples if missing
        if "؟" in feedback and "مثلاً" not in feedback and "یا" not in feedback:
            # Try to add simple examples
            if "چی یاد" in feedback.lower() or "چیزی یاد" in feedback.lower():
                feedback = feedback.replace("؟", "؟ مثلاً زبان انگلیسی؟ یا نقاشی؟ یا ریاضی؟")
            elif "احساس" in feedback.lower():
                feedback = feedback.replace("؟", "؟ مثلاً خوشحال بودی؟ یا هیجان‌زده بودی؟")
        
        return feedback
    
    def _basic_analysis(self, user_response: str, required_elements: list, question_text: str = "", follow_up_count: int = 0) -> dict:
        """
        Basic analysis fallback when AI is not available
        Checks response length and basic keywords with smarter feedback
        """
        response_lower = user_response.lower()
        missing = []
        
        # Check which required elements might be missing based on keywords
        element_keywords = {
            "موضوع یادگیری": ["یاد", "آموخت", "یادگیری", "مهارت", "موضوع"],
            "محرک انگیزشی": ["رقابت", "بردن", "ساختن", "کشف", "انتخاب"],
            "احساس یا هیجان": ["احساس", "هیجان", "خوشحال", "ذوق", "لذت"],
            "بازی یا فعالیت": ["بازی", "فعالیت", "ورزش", "نقاشی"],
            "لحظه خاص": ["لحظه", "زمان", "وقتی", "اون موقع"],
            "دلیل خسته‌شدن": ["خسته", "حوصله", "کسل", "طولانی"],
            "ترجیح روش": ["ترجیح", "دوست دارم", "ترجیح می‌دم"],
            "روش یادگیری": ["یاد گرفتم", "یاد داد", "دیدن", "انجام دادن"],
            "ترجیح تیمی/شخصی": ["تنهایی", "تیمی", "با دوست", "خودم"],
            "نوع بازخورد": ["بازخورد", "تحسین", "تشویق", "نظر"]
        }
        
        # Check which elements are likely missing
        found_elements = []
        for element in required_elements:
            keywords = element_keywords.get(element, [])
            found = any(keyword in response_lower for keyword in keywords)
            if not found:
                missing.append(element)
            else:
                found_elements.append(element)
        
        # Simple length check
        if len(user_response.strip()) < 30:
            # Simplify element names for children
            missing_simple = []
            for elem in required_elements[:2]:
                if "یادگیری" in elem:
                    missing_simple.append("چی یاد می‌گرفتی")
                elif "محرک" in elem:
                    missing_simple.append("چی باعث شد جذاب بشه")
                elif "احساس" in elem:
                    missing_simple.append("چه احساسی داشتی")
                else:
                    missing_simple.append(elem)
            missing_str = " و ".join(missing_simple)
            feedback = f"پاسخت کوتاهه! 😊 می‌خوام بیشتر بفهمم درباره {missing_str}. می‌تونی بیشتر برام بگی؟"
            return {
                "is_complete": False,
                "missing_elements": required_elements,
                "feedback": feedback
            }
        
        # Calculate coverage percentage
        coverage_percentage = len(found_elements) / len(required_elements) if required_elements else 0
        
        # If user has given multiple responses, be lenient but still check coverage
        if follow_up_count >= 3 and coverage_percentage >= 0.6:
            # User has answered 3+ times and covered at least 60% - accept it
            return {
                "is_complete": True,
                "missing_elements": [],
                "feedback": "عالی! پاسخت کامل بود ✨"
            }
        
        if follow_up_count >= 2 and coverage_percentage >= 0.8:
            # User has answered 2+ times and covered at least 80% - accept it
            return {
                "is_complete": True,
                "missing_elements": [],
                "feedback": "عالی! پاسخت کامل بود ✨"
            }
        
        # If we found missing elements, give specific feedback with simple language
        if missing:
            # Only be lenient if user has given multiple follow-ups AND covered most elements
            if follow_up_count >= 2 and coverage_percentage >= 0.7:
                # User covered 70%+ after 2+ follow-ups - accept it
                return {
                    "is_complete": True,
                    "missing_elements": [],
                    "feedback": "عالی! پاسخت کامل بود ✨"
                }
            
            # Simplify element names for children
            missing_simple = []
            for elem in missing[:2]:
                if "یادگیری" in elem:
                    missing_simple.append("چی یاد می‌گرفتی")
                elif "محرک" in elem:
                    missing_simple.append("چی باعث شد جذاب بشه")
                elif "احساس" in elem:
                    missing_simple.append("چه احساسی داشتی")
                else:
                    missing_simple.append(elem)
            missing_str = " و ".join(missing_simple)
            found_str = "چیزهایی" if found_elements else "چیزهایی"
            feedback = f"چه باحال گفتی که {found_str}! ✨ ولی می‌خوام بیشتر بفهمم: {missing_str}. مثلاً چی بود؟ 🌟"
            return {
                "is_complete": False,
                "missing_elements": missing,
                "feedback": feedback
            }
        
        # Check for question marks (might indicate user is confused)
        if user_response.count('?') > 2:
            return {
                "is_complete": False,
                "missing_elements": ["اطلاعات بیشتر"],
                "feedback": "به نظر می‌رسه سوال داری. اگر چیزی واضح نیست بپرس و جوابت رو کامل کن."
            }
        
        # If response is reasonably long and seems complete (all elements covered)
        if len(user_response.strip()) > 50 and len(missing) == 0 and coverage_percentage >= 0.8:
            return {
                "is_complete": True,
                "missing_elements": [],
                "feedback": "عالی! پاسخت کامل بود ✨"
            }
        
        # Simplify element name for children
        missing_element = required_elements[0] if required_elements else "چیزهای دیگه"
        if "یادگیری" in missing_element:
            missing_element = "چی یاد می‌گرفتی"
        elif "محرک" in missing_element:
            missing_element = "چی باعث شد جذاب بشه"
        elif "احساس" in missing_element:
            missing_element = "چه احساسی داشتی"
        
        feedback = f"می‌خوام بیشتر بفهمم: {missing_element}. مثلاً چی بود؟ 😊"
        return {
            "is_complete": False,
            "missing_elements": required_elements[:1] if not missing else missing,
            "feedback": feedback
        }

