"""
Configuration management for the Slack Summarizer.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables and config file."""
    logger = logging.getLogger(__name__)
    load_dotenv()

    # Ensure required environment variables are set
    required_env_vars = ["SLACK_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    # Load config file
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Merge environment variables into config
    config["slack"]["token"] = os.getenv("SLACK_TOKEN")
    config["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")

    logger.debug("Configuration loaded successfully")
    return config
