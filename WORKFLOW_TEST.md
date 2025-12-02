# تست جریان کار کامل - از کاربر تا ادمین

## 📋 جریان کار (Workflow)

### مرحله 1: شروع مصاحبه
```
کاربر → /start
    ↓
TelegramBot.start_command()
    ↓
SupervisorAgent.start_interview()
    ↓
WorkflowManager.interview_agent.start_interview()
    ↓
InterviewAgent.start_interview()
    ↓
بازگشت: پیام خوش‌آمدگویی + درخواست نام و سن
```

### مرحله 2: دریافت نام و سن
```
کاربر → "من احمد هستم و 10 سال دارم"
    ↓
TelegramBot.handle_message()
    ↓
SupervisorAgent.handle_user_message()
    ↓
WorkflowManager.process_interview_step()
    ↓
InterviewAgent.process_response()
    ↓
InterviewAgent._handle_name_age()
    ↓
بازگشت: سوال اول
```

### مرحله 3: پرسیدن سوالات (1 تا 7)
```
کاربر → پاسخ سوال
    ↓
SupervisorAgent.handle_user_message()
    ↓
WorkflowManager.process_interview_step()
    ↓
InterviewAgent.process_response()
    ↓
InterviewAgent._handle_question_response() یا _handle_follow_up()
    ↓
QuestionAnalyzer.analyze_response()
    ↓
اگر کامل نبود → سوال کمکی
اگر کامل بود → سوال بعدی
```

### مرحله 4: تکمیل مصاحبه
```
کاربر → پاسخ سوال 7 (کامل)
    ↓
InterviewAgent → is_complete = True
    ↓
SupervisorAgent.handle_user_message()
    ↓
DataValidator.validate_interview_completion()
    ↓
اگر معتبر بود:
    should_trigger_analysis = True
    interview_data = {...}
```

### مرحله 5: تحلیل و گزارش
```
TelegramBot.handle_message()
    ↓
اگر should_trigger_analysis == True:
    ↓
asyncio.create_task(_send_analysis_to_admin())
    ↓
SupervisorAgent.trigger_analysis_and_get_report()
    ↓
WorkflowManager.trigger_analysis()
    ↓
LearningAnalystAgent.analyze_interview()
    ↓
DataExtractor.extract_interview_data()
    ↓
PromptTemplates.get_analysis_prompt()
    ↓
OpenRouterClient.get_response() → AI تحلیل
    ↓
ReportBuilder.format_report_header()
    ↓
ReportBuilder.split_long_message()
    ↓
ارسال به ادمین (ID: 5184305178)
```

## ✅ بررسی نقاط کلیدی

### 1. Import ها
- ✅ `telegram_bot.py` → `SupervisorAgent`
- ✅ `supervisor.py` → `WorkflowManager`, `DataValidator`
- ✅ `workflow_manager.py` → `InterviewAgent`, `LearningAnalystAgent`
- ✅ `learning_analyst/analyst.py` → همه ماژول‌های داخلی

### 2. جریان داده
- ✅ کاربر → Supervisor → Interview Agent
- ✅ Interview Agent → Supervisor → Data Validator
- ✅ Supervisor → Learning Analyst
- ✅ Learning Analyst → Report Builder → Admin

### 3. مدیریت خطا
- ✅ Try-catch در همه سطوح
- ✅ Fallback report در صورت خطا
- ✅ لاگ‌گذاری مناسب

### 4. اعتبارسنجی
- ✅ DataValidator چک می‌کنه همه فیلدها موجود باشن
- ✅ چک می‌کنه پاسخ‌ها خالی نباشن
- ✅ چک کیفیت داده‌ها (اختیاری)

## 🔍 نقاط نیازمند بررسی

1. **Admin ID**: باید مطمئن بشیم که ID درست است (5184305178)
2. **Message Length**: باید مطمئن بشیم که پیام‌های طولانی درست split می‌شن
3. **Async Tasks**: باید مطمئن بشیم که asyncio.create_task درست کار می‌کنه

## 📝 تست دستی

برای تست کامل، باید:
1. ربات رو اجرا کنی
2. /start بزنی
3. نام و سن بدی
4. به 7 سوال پاسخ بدی
5. بررسی کنی که گزارش به ادمین ارسال شده

