"""
Configuration module for Telegram bot
Contains all API keys and configuration settings
"""

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "8277682636:AAECGOsy9rhJHLTaPlQIgX2gdJbZZxrSGic"

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "google/gemini-2.0-flash-exp:free"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Bot Settings
MAX_MESSAGE_LENGTH = 4096  # Telegram's maximum message length
REQUEST_TIMEOUT = 30  # Timeout for API requests in seconds

# Proxy Settings (optional - set if needed)
# For example in Iran where Telegram might be blocked
# PROXY_URL = "http://proxy.example.com:8080"  # Uncomment and set if needed
PROXY_URL = None  # Set to None if no proxy needed

