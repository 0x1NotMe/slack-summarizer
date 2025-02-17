"""
OpenAI-powered text summarization for Slack messages.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from openai import OpenAI


class Summarizer:
    """Handles text summarization using OpenAI."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the summarizer.

        Args:
            config: Application configuration dictionary.
        """
        self.logger = logging.getLogger(__name__)

        # Validate OpenAI API key
        api_key = config["openai"]["api_key"].strip()  # Remove any whitespace
        self.logger.info(
            f"Validating OpenAI API key (first 10 chars): {api_key[:10]}..."
        )

        if not api_key:
            raise ValueError("OpenAI API key is empty")

        if not api_key.startswith("sk-"):
            raise ValueError(
                f"Invalid OpenAI API key format. Key should start with 'sk-'. Got: {api_key[:10]}... "
                "Get your API key from: https://platform.openai.com/api-keys"
            )

        self.client = OpenAI(api_key=api_key)

        # Test API connection
        try:
            # Make a minimal API call to test the key
            self.client.models.list()
            self.logger.info("✓ OpenAI API connection successful")
        except Exception as e:
            self.logger.error("✗ OpenAI API connection failed")
            self.logger.error(str(e))
            raise

    def summarize_messages(
        self, messages: List[Dict[str, Any]], user_mapping: Dict[str, str] = None
    ) -> str:
        """
        Generate a summary of Slack messages.

        Args:
            messages: List of Slack message dictionaries.
            user_mapping: Optional dictionary mapping user IDs to user names.

        Returns:
            A string containing the summary.
        """
        if not messages:
            return "No messages to summarize."

        try:
            # Format messages for summarization
            formatted_messages = self._format_messages(messages, user_mapping)

            self.logger.info(f"Summarizing {len(messages)} messages")

            response = self.client.chat.completions.create(
                model="o1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "You are a Slack channel summarizer. Your task is to analyze the following Slack channel logs "
                            "and generate a Markdown summary covering three main aspects:\n\n"
                            "1. **Archived Tasks:** Identify and list all tasks that have been completed and archived.\n"
                            "2. **Conversations & Resolutions:** Summarize important conversations, noting any resolutions or decisions that were made.\n"
                            "3. **Open Issues/Items to Address:** Highlight any issues, questions, or topics that were raised and still need further attention.\n\n"
                            "**Additional Instructions:**\n"
                            "- For every task, conversation, or issue mentioned, include the names of the users involved.\n"
                            "- Use clear headings and bullet points.\n"
                            "- Focus on one channel at a time and include relevant context.\n"
                            "- If a section would be empty (no tasks/conversations/issues), omit that section entirely.\n"
                            "- Include timestamps for important events.\n"
                            "- When mentioning users, use their display names for better readability.\n\n"
                            "The output should follow this structure:\n\n"
                            "# Slack Channel Summary\n\n"
                            "## Archived Tasks (if any)\n"
                            "- **Task:** Brief description or outcome.\n"
                            "  - **Involved Users:** User Name 1, User Name 2\n\n"
                            "## Conversations & Resolutions\n"
                            "- **Topic:** Summary of the conversation and the resolution reached.\n"
                            "  - **Participants:** User Name 1, User Name 4\n\n"
                            "## Open Issues/Items to Address\n"
                            "- **Issue:** Description of the issue and any pending actions.\n"
                            "  - **Reported/Discussed By:** User Name 1, User Name 5\n\n"
                            "Here are the messages to summarize:\n\n"
                            f"{formatted_messages}"
                        ),
                    }
                ],
                max_completion_tokens=30000,
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            raise

    def _format_messages(
        self, messages: List[Dict[str, Any]], user_mapping: Dict[str, str] = None
    ) -> str:
        """Format Slack messages into a readable conversation."""
        formatted = []
        user_mapping = user_mapping or {}

        for msg in messages:
            # Convert timestamp to datetime
            ts = float(msg.get("ts", 0))
            dt = datetime.fromtimestamp(ts)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

            # Get user and text
            user_id = msg.get("user", "Unknown")
            user_name = user_mapping.get(user_id, user_id)
            text = msg.get("text", "")

            # Format message
            formatted.append(f"[{time_str}] <{user_name}>: {text}")

        return "\n".join(formatted)
