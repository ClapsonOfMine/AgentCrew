import os
import tempfile
import threading
from typing import Dict, Any, Optional
import queue
import soundfile as sf
from openai import OpenAI
from .text_cleaner import TextCleaner
from .audio_handler import AudioHandler
from .base import BaseVoiceService

from AgentCrew.modules import logger


class DeepInfraVoiceService(BaseVoiceService):
    """Service for DeepInfra voice interactions using OpenAI-compatible API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the voice service with DeepInfra API."""
        # Initialize parent class
        super().__init__()

        # Set the API key
        self.api_key = api_key or os.getenv("DEEPINFRA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepInfra API key not found. Set DEEPINFRA_API_KEY environment variable."
            )

        # Initialize OpenAI client with DeepInfra endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )

        self.audio_handler = AudioHandler()
        self.text_cleaner = TextCleaner()

        # STT settings - Using the specified model for DeepInfra
        self.stt_model = "openai/whisper-large-v3-turbo"

        # TTS settings - Note: DeepInfra primarily provides STT, not TTS
        # We'll implement STT functionality and leave TTS as placeholder

        # TTS streaming thread management
        self._start_tts_thread()

    def start_voice_recording(self, sample_rate: int = 44100) -> Dict[str, Any]:
        """
        Start recording voice input.

        Args:
            sample_rate: Audio sample rate

        Returns:
            Status dictionary
        """
        try:
            self.audio_handler.start_recording(sample_rate)
            return {
                "success": True,
                "message": "Recording started.",
            }
        except Exception as e:
            logger.error(f"Failed to start recording: {str(e)}")
            return {"success": False, "error": f"Failed to start recording: {str(e)}"}

    def stop_voice_recording(self) -> Dict[str, Any]:
        """
        Stop recording and return status.

        Returns:
            Status dictionary with recording info
        """
        try:
            audio_data, sample_rate = self.audio_handler.stop_recording()

            if audio_data is None:
                return {"success": False, "error": "No audio data captured"}

            duration = len(audio_data) / sample_rate
            return {
                "success": True,
                "audio_data": audio_data,
                "sample_rate": sample_rate,
                "duration": duration,
                "message": f"Recording stopped. Duration: {duration:.2f} seconds",
            }

        except Exception as e:
            logger.error(f"Failed to stop recording: {str(e)}")
            return {"success": False, "error": f"Failed to stop recording: {str(e)}"}

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.audio_handler.is_recording()

    async def speech_to_text(self, audio_data: Any, sample_rate: int) -> Dict[str, Any]:
        """
        Convert speech to text using DeepInfra's OpenAI-compatible STT.

        Args:
            audio_data: NumPy array of audio data
            sample_rate: Sample rate of the audio

        Returns:
            Dict containing transcription results
        """
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                sf.write(tmp_file.name, audio_data, sample_rate)
                tmp_file_path = tmp_file.name

            # Perform speech-to-text using OpenAI-compatible API
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.stt_model,
                    file=audio_file,
                    language="en",  # Can be made configurable, supports ISO-639-1 format
                    response_format="verbose_json",  # Get detailed response with timestamps
                    temperature=0.2,  # Lower temperature for more focused output
                    timestamp_granularities=["segment"],  # Get segment-level timestamps
                )

            # Clean up temp file
            os.unlink(tmp_file_path)

            # Extract information from the response
            text = transcript.text if hasattr(transcript, "text") else ""
            language = transcript.language if hasattr(transcript, "language") else "en"

            return {
                "success": True,
                "text": text,
                "language": language,
                "confidence": 1.0,  # DeepInfra doesn't provide confidence scores in this format
                "words": [],
            }

        except Exception as e:
            logger.error(f"Speech-to-text failed: {str(e)}")
            return {"success": False, "error": f"Failed to transcribe audio: {str(e)}"}

    def translate_to_english(self, audio_data: Any, sample_rate: int) -> Dict[str, Any]:
        """
        Translate audio to English using DeepInfra's translation endpoint.

        Args:
            audio_data: NumPy array of audio data
            sample_rate: Sample rate of the audio

        Returns:
            Dict containing translation results
        """
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                sf.write(tmp_file.name, audio_data, sample_rate)
                tmp_file_path = tmp_file.name

            # Perform translation using OpenAI-compatible API
            with open(tmp_file_path, "rb") as audio_file:
                translation = self.client.audio.translations.create(
                    model=self.stt_model,
                    file=audio_file,
                    response_format="verbose_json",
                    temperature=0.2,
                    prompt="",  # Optional prompt in English to guide translation
                )

            # Clean up temp file
            os.unlink(tmp_file_path)

            # Extract information from the response
            text = translation.text if hasattr(translation, "text") else ""

            return {
                "success": True,
                "text": text,
                "language": "en",  # Always English for translations
                "confidence": 1.0,
                "is_translation": True,
            }

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return {"success": False, "error": f"Failed to translate audio: {str(e)}"}

    def clean_text_for_speech(self, text: str) -> str:
        """
        Clean assistant response text for natural speech.

        Args:
            text: Raw assistant response text

        Returns:
            Cleaned text suitable for TTS
        """
        return self.text_cleaner.clean_for_speech(text)

    def _start_tts_thread(self):
        """Start the TTS worker thread if not already running."""
        with self.tts_lock:
            if not self.tts_thread_running:
                self.tts_thread_running = True
                self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
                self.tts_thread.start()
                logger.debug("TTS worker thread started (DeepInfra - STT only)")

    def _tts_worker(self):
        """Worker thread for processing TTS requests."""
        # Note: DeepInfra primarily provides STT, not TTS
        # This is a placeholder implementation
        while self.tts_thread_running:
            try:
                # Wait for TTS request with timeout
                tts_request = self.tts_queue.get(timeout=1.0)
                if tts_request is None:  # Shutdown signal
                    break

                text, voice_id, model_id = tts_request
                logger.warning(
                    f"TTS not available with DeepInfra service. Text: {text[:50]}..."
                )

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"TTS worker error: {str(e)}")

        logger.debug("TTS worker thread stopped")

    def _process_tts_request(
        self, text: str, voice_id: Optional[str], model_id: Optional[str]
    ):
        """
        Process a single TTS request synchronously in the worker thread.

        Note: DeepInfra doesn't provide TTS functionality, only STT.
        This is a placeholder implementation.

        Args:
            text: Text to convert to speech
            voice_id: Not used in DeepInfra
            model_id: Not used in DeepInfra
        """
        logger.warning(
            f"TTS not available with DeepInfra service. Text: {text[:50]}..."
        )

    def text_to_speech_stream(
        self, text: str, voice_id: Optional[str] = None, model_id: Optional[str] = None
    ):
        """
        Queue text-to-speech audio for streaming in a separate thread.

        Note: DeepInfra doesn't provide TTS functionality.
        This method logs a warning and returns immediately.

        Args:
            text: Text to convert to speech
            voice_id: Not used in DeepInfra
            model_id: Not used in DeepInfra
        """
        logger.warning(
            f"TTS not available with DeepInfra service. Use STT functionality instead."
        )

    def text_to_speech_stream_sync(
        self, text: str, voice_id: Optional[str] = None, model_id: Optional[str] = None
    ):
        """
        Synchronous version of text-to-speech streaming.

        Note: DeepInfra doesn't provide TTS functionality.

        Args:
            text: Text to convert to speech
            voice_id: Not used in DeepInfra
            model_id: Not used in DeepInfra

        Returns:
            None - TTS not supported
        """
        logger.warning(f"TTS not available with DeepInfra service.")
        return None

    def list_voices(self) -> Dict[str, Any]:
        """
        List available voices.

        Note: DeepInfra doesn't provide TTS, so no voices available.
        """
        return {
            "success": False,
            "error": "TTS voices not available with DeepInfra service. Service provides STT only.",
            "voices": [],
        }

    def set_voice(self, voice_id: str):
        """
        Set the default voice for TTS.

        Note: Not applicable for DeepInfra as it doesn't provide TTS.
        """
        logger.warning("Voice setting not available with DeepInfra service (STT only).")

    def get_configured_voice_id(self) -> str:
        """
        Get the voice ID from configuration.

        Note: Not applicable for DeepInfra as it doesn't provide TTS.
        """
        return ""

    def set_voice_settings(self, **kwargs):
        """
        Update voice settings.

        Note: Not applicable for DeepInfra as it doesn't provide TTS.
        """
        logger.warning(
            "Voice settings not available with DeepInfra service (STT only)."
        )

    def stop_tts_thread(self):
        """Stop the TTS worker thread gracefully."""
        with self.tts_lock:
            if self.tts_thread_running:
                self.tts_thread_running = False

                # Clear the queue and add shutdown signal
                try:
                    while not self.tts_queue.empty():
                        self.tts_queue.get_nowait()
                except queue.Empty:
                    pass

                self.tts_queue.put(None)  # Shutdown signal

                # Wait for thread to finish
                if self.tts_thread and self.tts_thread.is_alive():
                    self.tts_thread.join(timeout=2.0)

                logger.debug("TTS thread stopped")

    def clear_tts_queue(self):
        """Clear any pending TTS requests."""
        try:
            while not self.tts_queue.empty():
                self.tts_queue.get_nowait()
            logger.debug("TTS queue cleared")
        except queue.Empty:
            pass

    def __del__(self):
        """Cleanup when service is destroyed."""
        try:
            self.stop_tts_thread()
        except Exception:
            pass

