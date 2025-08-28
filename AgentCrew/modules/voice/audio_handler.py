from typing import Optional, Tuple, Any
import threading
import queue
import numpy as np
import sounddevice as sd
from AgentCrew.modules import logger
from .base import BaseAudioHandler


class AudioHandler(BaseAudioHandler):
    """Handles audio recording and playback operations."""

    def __init__(self):
        """Initialize audio handler."""
        # Initialize parent class
        super().__init__()

        # Override parent attributes and add specific implementations
        self.recording = False
        self.recording_thread = None
        self.audio_queue = queue.Queue()
        self.current_sample_rate = 44100

    def start_recording(self, sample_rate: int = 44100) -> None:
        """
        Start recording audio in a separate thread.

        Args:
            sample_rate: Sample rate for recording
        """
        if self.recording:
            logger.warning("Recording already in progress")
            return

        self.recording = True
        self.current_sample_rate = sample_rate
        self.audio_queue.queue.clear()  # Clear any previous data

        self.recording_thread = threading.Thread(
            target=self._recording_worker, args=(sample_rate,), daemon=True
        )
        self.recording_thread.start()
        logger.info("Recording started")

    def stop_recording(self) -> Tuple[Optional[Any], int]:
        """
        Stop recording and return the recorded audio.

        Returns:
            Tuple of (audio_data, sample_rate) or (None, 0) if no data
        """
        if not self.recording:
            logger.warning("No recording in progress")
            return None, 0

        self.recording = False

        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)

        # Collect all recorded frames
        frames = []
        while not self.audio_queue.empty():
            try:
                frames.append(self.audio_queue.get_nowait())
            except queue.Empty:
                break

        if frames:
            audio_data = np.concatenate(frames, axis=0).flatten()
            logger.info(
                f"Recording stopped. Captured {len(audio_data) / self.current_sample_rate:.2f} seconds"
            )
            return audio_data, self.current_sample_rate
        else:
            logger.warning("No audio data captured")
            return None, 0

    def _recording_worker(self, sample_rate: int):
        """Worker thread for continuous recording."""
        try:

            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Recording status: {status}")
                if self.recording:
                    self.audio_queue.put(indata.copy())

            with sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                callback=callback,
                dtype="float32",
                blocksize=1024,
            ):
                while self.recording:
                    sd.sleep(100)  # Sleep for 100ms chunks

        except Exception as e:
            logger.error(f"Recording error: {str(e)}")
            self.recording = False

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.recording

    def __del__(self):
        """Cleanup PyAudio."""
        try:
            if self.recording:
                self.stop_recording()
        except Exception:
            pass
