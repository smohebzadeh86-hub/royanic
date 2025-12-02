"""
Conversation Module
Handles general conversation and AI communication
"""

from .openrouter_client import OpenRouterClient
from .danua_identity import (
    DANUA_STORY,
    DANUA_INTRODUCTION,
    WHO_ARE_YOU_RESPONSE,
    ABOUT_DANUA_RESPONSE,
    get_danua_system_prompt,
    is_about_danua_question,
    is_who_are_you_question
)

__all__ = [
    'OpenRouterClient',
    'DANUA_STORY',
    'DANUA_INTRODUCTION',
    'WHO_ARE_YOU_RESPONSE',
    'ABOUT_DANUA_RESPONSE',
    'get_danua_system_prompt',
    'is_about_danua_question',
    'is_who_are_you_question'
]

