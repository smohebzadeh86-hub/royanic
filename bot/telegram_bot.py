"""
Telegram Bot Module
Handles Telegram bot interactions and message processing
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from .config import TELEGRAM_BOT_TOKEN, MAX_MESSAGE_LENGTH, PROXY_URL
from .supervisor import SupervisorAgent
from .learning_analyst import ReportBuilder


class TelegramBot:
    """Telegram Bot Handler"""
    
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.supervisor = SupervisorAgent()
        self.report_builder = ReportBuilder()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Start interview"""
        user_id = update.effective_user.id
        
        # Reset any existing interview
        self.supervisor.reset_interview(user_id)
        
        # Start new interview through supervisor
        welcome_message = self.supervisor.start_interview(user_id)
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "📚 راهنمای استفاده:\n\n"
            "/start - شروع مجدد ربات\n"
            "/help - نمایش این راهنما\n"
            "/clear - پاک کردن تاریخچه گفتگو\n\n"
            "فقط پیام خود را ارسال کنید تا پاسخ دریافت کنید!"
        )
        await update.message.reply_text(help_message)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command to reset conversation history"""
        user_id = update.effective_user.id
        if user_id in self.user_conversations:
            del self.user_conversations[user_id]
        await update.message.reply_text("✅ تاریخچه گفتگو پاک شد!")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages - Interview flow"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        try:
            # Show typing indicator
            try:
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id,
                    action="typing"
                )
            except Exception as e:
                # If typing indicator fails, continue anyway
                print(f"[WARNING] Could not send typing indicator: {str(e)}")
            
            # Process with supervisor agent (manages workflow)
            supervisor_result = self.supervisor.handle_user_message(user_id, user_message)
            
            # Send response to user
            bot_message = supervisor_result["message"]
            
            # Split long messages if necessary
            if len(bot_message) > MAX_MESSAGE_LENGTH:
                chunks = [
                    bot_message[i:i + MAX_MESSAGE_LENGTH]
                    for i in range(0, len(bot_message), MAX_MESSAGE_LENGTH)
                ]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(bot_message)
            
            # If interview is complete and validated, trigger analysis
            if supervisor_result["should_trigger_analysis"] and supervisor_result["interview_data"]:
                # Save result to console
                import json
                interview_data = supervisor_result["interview_data"]
                result_json = json.dumps(interview_data, ensure_ascii=False, indent=2)
                print(f"\n[SUPERVISOR] Interview complete and validated for user {user_id}")
                print(result_json)
                
                if supervisor_result.get("validation_message"):
                    print(f"[SUPERVISOR] {supervisor_result['validation_message']}")
                
                # Generate analysis report and send to admin (async, non-blocking)
                import asyncio
                asyncio.create_task(self._send_analysis_to_admin(context, interview_data, user_id))
        
        except Exception as e:
            # Handle errors gracefully
            error_msg = f"⚠️ متاسفم، مشکلی پیش اومد. لطفاً دوباره تلاش کنید."
            try:
                await update.message.reply_text(error_msg)
            except:
                pass
            print(f"[ERROR] Error handling message: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def _send_analysis_to_admin(self, context: ContextTypes.DEFAULT_TYPE, interview_result: dict, user_id: int):
        """
        Generate learning analysis report and send to admin
        
        Args:
            context: Bot context for sending messages
            interview_result: Interview result dictionary
            user_id: User ID who completed the interview
        """
        try:
            print(f"[SUPERVISOR] Triggering analysis for user {user_id}...")
            
            # Trigger analysis through supervisor
            report = self.supervisor.trigger_analysis_and_get_report(interview_result)
            
            # Get admin ID from learning analyst
            admin_id = self.supervisor.workflow_manager.learning_analyst.admin_id
            
            # Prepare header message using ReportBuilder
            name = interview_result.get("name", "نامشخص")
            age = str(interview_result.get("age", "نامشخص"))
            header = self.report_builder.format_report_header(name, age, user_id)
            
            # Combine header and report
            full_report = header + report
            
            # Split long messages using ReportBuilder
            chunks = self.report_builder.split_long_message(full_report, MAX_MESSAGE_LENGTH)
            
            # Send all chunks
            for i, chunk in enumerate(chunks):
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=chunk,
                        parse_mode=None
                    )
                    # Small delay between messages
                    if i < len(chunks) - 1:  # Don't delay after last message
                        import asyncio
                        await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"[ERROR] Failed to send chunk {i+1} to admin: {str(e)}")
            
            print(f"[ANALYSIS] Report sent successfully to admin {admin_id} ({len(chunks)} chunks)")
                    
        except Exception as e:
            print(f"[ERROR] Error in analysis generation: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Try to send error notification to admin
            try:
                admin_id = self.supervisor.workflow_manager.learning_analyst.admin_id
                error_msg = f"⚠️ خطا در تولید گزارش تحلیل برای کاربر {user_id}\n\nخطا: {str(e)}"
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=error_msg
                )
            except:
                pass
    
    def run(self):
        """Start the Telegram bot"""
        try:
            # Create application with optional proxy
            print("[BOT] Initializing bot...")
            
            # Configure request with optional proxy
            request = None
            if PROXY_URL:
                print(f"[BOT] Using proxy: {PROXY_URL}")
                request = HTTPXRequest(proxy=PROXY_URL, connect_timeout=30.0, read_timeout=30.0)
            else:
                request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
            
            application = Application.builder().token(self.token).request(request).build()
            
            # Add command handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("clear", self.clear_command))
            
            # Add message handler (must be last)
            application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
            )
            
            # Add error handler
            async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
                """Handle errors"""
                error = context.error
                print(f"[ERROR] Update {update} caused error {error}")
                
                # Check if it's a network error
                from telegram.error import NetworkError
                if isinstance(error, NetworkError):
                    print("[ERROR] Network error - Check VPN/Internet connection")
                    print("[ERROR] If VPN is disconnected, please reconnect and restart the bot")
            
            application.add_error_handler(error_handler)
            
            # Start the bot
            print("[BOT] Bot is running...")
            print("[BOT] Waiting for messages...")
            print("[BOT] Multi-user support enabled - can handle multiple users simultaneously")
            print("[BOT] You can send /start to the bot now!")
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False,
                stop_signals=None,  # Prevent signal handling issues
                pool_timeout=30  # Timeout for getting updates
            )
        except Exception as e:
            print(f"[ERROR] Failed to start bot: {str(e)}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise

