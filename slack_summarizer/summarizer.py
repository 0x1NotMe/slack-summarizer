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
        Initialize the summarizer with OpenAI configuration.

        Args:
            config: Application configuration dictionary containing OpenAI API key.
        """
        self.logger = logging.getLogger(__name__)
        api_key = config["openai"]["api_key"].strip()

        if not api_key:
            raise ValueError("OpenAI API key is empty")
        if not api_key.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")

        self.client = OpenAI(api_key=api_key)
        self._test_api_connection()

    def _test_api_connection(self) -> None:
        """Test the OpenAI API connection."""
        try:
            self.client.models.list()
            self.logger.debug("OpenAI API connection successful")
        except Exception as e:
            self.logger.error("OpenAI API connection failed: %s", str(e))
            raise

    def summarize_messages(
        self, messages: List[Dict[str, Any]], user_mapping: Dict[str, str] = None
    ) -> str:
        """
        Generate a summary of Slack messages using OpenAI's chat completion API.

        The summary is structured in Markdown format with sections for:
        - Archived Tasks
        - Conversations & Resolutions
        - Open Issues/Items to Address

        Args:
            messages: List of Slack message dictionaries.
            user_mapping: Optional dictionary mapping user IDs to user names.

        Returns:
            A formatted Markdown string containing the channel summary.
        """
        if not messages:
            return "No messages to summarize."

        try:
            formatted_messages = self._format_messages(messages, user_mapping)
            self.logger.info("Summarizing %d messages", len(messages))

            response = self.client.chat.completions.create(
                model="gpt-4-0125-preview",  # Using the latest GPT-4 Turbo model
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
                max_tokens=4000,
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error("Error generating summary: %s", str(e))
            raise

    def _format_messages(
        self, messages: List[Dict[str, Any]], user_mapping: Dict[str, str] = None
    ) -> str:
        """
        Format Slack messages into a readable conversation format.

        Args:
            messages: List of Slack message dictionaries.
            user_mapping: Optional dictionary mapping user IDs to user names.

        Returns:
            A string containing the formatted conversation.
        """
        formatted = []
        user_mapping = user_mapping or {}

        for msg in messages:
            ts = float(msg.get("ts", 0))
            dt = datetime.fromtimestamp(ts)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            user_id = msg.get("user", "Unknown")
            user_name = user_mapping.get(user_id, user_id)
            text = msg.get("text", "")
            formatted.append(f"[{time_str}] <{user_name}>: {text}")

        return "\n".join(formatted)
