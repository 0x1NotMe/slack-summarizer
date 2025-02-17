"""
Main entry point for the Slack Summarizer application.
"""

import logging
from pathlib import Path
from typing import NoReturn
from datetime import datetime

from slack_summarizer.config import load_config
from slack_summarizer.logger import setup_logging
from slack_summarizer.slack_client import SlackClient
from slack_summarizer.summarizer import Summarizer


def main() -> NoReturn:
    """Main function to run the Slack Summarizer."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_config()

        # Initialize clients
        slack_client = SlackClient(config)
        summarizer = Summarizer(config)

        # Log startup
        logger.info("Starting Slack Summarizer")

        # Create summaries directory
        summaries_dir = Path("summaries")
        summaries_dir.mkdir(exist_ok=True)

        # Fetch user and channel mappings
        user_mapping = slack_client.fetch_user_mapping()
        channel_mapping = slack_client.fetch_channel_mapping()

        # Process each channel
        duration_days = config["summary"]["duration_days"]

        for channel in config["slack"]["channels"]:
            logger.info(f"Processing channel: {channel}")

            # Get channel name from mapping or fallback to channel info
            channel_name = channel_mapping.get(channel)
            if not channel_name:
                channel_info = slack_client.get_channel_info(channel)
                channel_name = channel_info.get("name", channel)

            # Get messages
            messages = slack_client.get_channel_messages(channel, days=duration_days)

            if messages:
                # Display messages with user names
                logger.info(f"\n=== Messages from #{channel_name} ===")
                for msg in messages:
                    timestamp = datetime.fromtimestamp(float(msg.get("ts", 0)))
                    user_id = msg.get("user", "Unknown")
                    user_name = user_mapping.get(user_id, user_id)
                    text = msg.get("text", "")
                    logger.info(f"[{timestamp}] <{user_name}>: {text}")

                # Generate summary with user context
                summary = summarizer.summarize_messages(messages, user_mapping)

                # Create summary file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                summary_file = summaries_dir / f"{channel_name}_{timestamp}.md"

                # Save summary with metadata
                with open(summary_file, "w") as f:
                    f.write(f"# Summary for #{channel_name}\n\n")
                    f.write(
                        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    f.write(f"Channel ID: {channel}\n")
                    f.write(f"Time Range: Last {duration_days} days\n")
                    f.write(f"Message Count: {len(messages)}\n")
                    f.write("\n---\n\n")
                    f.write(summary)

                logger.info(f"Generated summary for channel: {channel_name}")
                logger.info(f"Summary saved to: {summary_file}")
            else:
                logger.warning(f"No messages found in channel: {channel_name}")

    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
