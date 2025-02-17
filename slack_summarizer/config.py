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

    # Load environment variables
    load_dotenv()

    # Log environment variable for debugging
    slack_token = os.getenv("SLACK_TOKEN")
    logger.info(f"SLACK_TOKEN from env: {slack_token}")

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
    config["slack"]["token"] = slack_token
    logger.info(f"Token in config after merge: {config['slack']['token']}")

    # Get and log OpenAI API key (first 10 chars)
    openai_key = os.getenv("OPENAI_API_KEY", "")
    logger.info(f"OpenAI API key from env (first 10 chars): {openai_key[:10]}...")
    config["openai"]["api_key"] = openai_key

    return config
