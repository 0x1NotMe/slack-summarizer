"""
Logging configuration for the Slack Summarizer.
"""

import logging
import sys
from pathlib import Path


def setup_logging(level: int = logging.INFO) -> None:
    """
    Set up logging configuration for the application.

    Args:
        level: The logging level to use. Defaults to INFO.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Set up root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(log_dir / "slack_summarizer.log"),
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("slack_sdk").setLevel(logging.WARNING)
