"""
Chrome browser process management for browser automation.

Adapted from the PoC implementation to manage Chrome browser instances
with DevTools Protocol support.
"""

import os
import signal
import atexit
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ChromeManager:
    """Manages Chrome browser process lifecycle for automation."""

    def __init__(self, debug_port: int = 9222, user_data_dir: Optional[str] = None):
        """
        Initialize Chrome manager.

        Args:
            debug_port: Port for Chrome DevTools Protocol
            user_data_dir: Directory for Chrome user data storage
        """
        self.debug_port = debug_port
        self.user_data_dir = user_data_dir or Path.cwd() / "chrome_user_data"
        self.chrome_process: Optional[subprocess.Popen] = None
        self.chrome_thread: Optional[threading.Thread] = None
        self._shutdown = False

        # Register cleanup on exit
        atexit.register(self.cleanup)

    def _find_chrome_executable(self) -> str:
        """
        Find Chrome/Chromium executable path.

        Returns:
            Path to Chrome executable

        Raises:
            FileNotFoundError: If Chrome executable not found
        """
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "/opt/google/chrome/chrome",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Try to find via which command
        try:
            result = subprocess.run(
                ["which", "google-chrome"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

        try:
            result = subprocess.run(
                ["which", "chromium"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

        raise FileNotFoundError("Chrome/Chromium executable not found")

    def _start_chrome_process(self):
        """Start Chrome with remote debugging in a separate process."""
        try:
            chrome_executable = self._find_chrome_executable()


            chrome_args = [
                chrome_executable,
                f"--remote-debugging-port={self.debug_port}",
                "--no-first-run",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--allow-file-access-from-files",
                "--disable-web-security",
                "--allow-running-insecure-content",
            ]

            self.chrome_process = subprocess.Popen(
                chrome_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )

            time.sleep(2)

            if self.chrome_process.poll() is not None:
                stdout, stderr = self.chrome_process.communicate()
                logger.error(f"Chrome failed to start. Error: {stderr.decode()}")

        except Exception as e:
            logger.error(f"Error starting Chrome: {e}")

    def start_chrome_thread(self):
        """Start Chrome in a separate thread."""
        if self.chrome_thread and self.chrome_thread.is_alive():
            return

        self.chrome_thread = threading.Thread(
            target=self._start_chrome_process, daemon=True, name="ChromeDebugProcess"
        )
        self.chrome_thread.start()

        # Wait a bit for Chrome to fully initialize
        time.sleep(3)

    def is_chrome_running(self) -> bool:
        """Check if Chrome process is still running."""
        return self.chrome_process is not None and self.chrome_process.poll() is None

    def cleanup(self):
        """Clean up Chrome process."""
        if self._shutdown:
            return

        self._shutdown = True

        if self.chrome_process and self.chrome_process.poll() is None:
            try:
                os.killpg(os.getpgid(self.chrome_process.pid), signal.SIGTERM)

                try:
                    self.chrome_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.chrome_process.pid), signal.SIGKILL)
                    self.chrome_process.wait()

            except (ProcessLookupError, OSError) as e:
                logger.warning(f"Chrome process cleanup: {e}")

