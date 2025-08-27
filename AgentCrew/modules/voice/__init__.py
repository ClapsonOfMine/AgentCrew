"""Voice module for AgentCrew with ElevenLabs integration.

This module provides speech-to-text and text-to-speech capabilities
using the ElevenLabs API, built on a flexible abstract base class architecture.
"""

from .elevenlabs_service import ElevenLabsVoiceService
from .base import BaseVoiceService
from .text_cleaner import TextCleaner
from .audio_handler import AudioHandler

__all__ = [
    "BaseVoiceService",
    "ElevenLabsVoiceService",
    "TextCleaner",
    "AudioHandler",
]
