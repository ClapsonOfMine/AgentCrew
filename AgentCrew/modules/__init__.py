import logging
import sys
import tempfile
from datetime import datetime
import os

from typing import TextIO, AnyStr

LOG_LEVEL = logging.ERROR
# Create a logger
logger = logging.getLogger("AgentCrew")
logger.setLevel(LOG_LEVEL)  # Set default level to DEBUG

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(LOG_LEVEL)

# Create a console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(LOG_LEVEL)  # Set handler level

# Create a formatter and set it for the handler
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s"
)
ch.setFormatter(formatter)

# Add the handler to the logger
if not logger.handlers:
    logger.addHandler(ch)

# Optional: Prevent duplicate logging if this module is imported multiple times
logger.propagate = False


class FileLogIO(TextIO):
    """File-like object compatible with sys.stderr for MCP logging."""

    def __init__(self, file_format: str = "agentcrew"):
        log_dir_path = os.getenv("AGENTCREW_LOG_PATH", tempfile.gettempdir())
        os.makedirs(log_dir_path, exist_ok=True)
        self.log_path = (
            log_dir_path + f"/{file_format}_{datetime.now().timestamp()}.log"
        )
        self.file = open(self.log_path, "w+")

    def write(self, data: AnyStr) -> int:
        """Write data to the log file."""
        if isinstance(data, bytes):
            # Convert bytes to string for writing
            str_data = data.decode("utf-8", errors="replace")
        else:
            str_data = str(data)
        self.file.write(str_data)
        self.file.flush()  # Ensure data is written immediately
        return 0

    def flush(self):
        """Flush the file buffer."""
        self.file.flush()

    def close(self):
        """Close the file."""
        self.file.close()

    def fileno(self):
        """Return the file descriptor."""
        return self.file.fileno()
