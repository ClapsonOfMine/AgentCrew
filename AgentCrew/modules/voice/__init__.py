"""Voice module for AgentCrew with multiple voice service integrations.

This module provides speech-to-text and text-to-speech capabilities
using various APIs including ElevenLabs and DeepInfra (STT only),
built on a flexible abstract base class architecture.
"""

from .elevenlabs_service import ElevenLabsVoiceService
from .deepinfra_service import DeepInfraVoiceService
from .base import BaseVoiceService
from .text_cleaner import TextCleaner
from .audio_handler import AudioHandler

__all__ = [
    "BaseVoiceService",
    "ElevenLabsVoiceService",
    "DeepInfraVoiceService",
    "TextCleaner",
    "AudioHandler",
]
