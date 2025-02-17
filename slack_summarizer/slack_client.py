"""
Slack API client for the Slack Summarizer.
"""

import logging
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackClient:
    """Client for interacting with the Slack API."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Slack client.

        Args:
            config: Application configuration dictionary.
        """
        self.logger = logging.getLogger(__name__)
        self.channels = config["slack"]["channels"]

        # Create cache directory
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.user_cache_file = self.cache_dir / "user_cache.json"
        self.user_cache_ttl = timedelta(hours=24)  # Cache TTL of 24 hours

        # Log token from config for debugging
        config_token = config["slack"]["token"]
        env_token = os.getenv("SLACK_TOKEN")
        self.logger.info("=== Token Debug Information ===")
        self.logger.info(f"Full config token: {config_token}")
        self.logger.info(f"Full env token: {env_token}")

        # Use the token from environment variable directly
        self.token = os.getenv("SLACK_TOKEN", "").strip()

        # Add xoxp- prefix if missing
        if not self.token.startswith("xoxp-") and not self.token.startswith("xoxe."):
            self.token = f"xoxp-{self.token}"
            self.logger.info(f"Added xoxp- prefix to token: {self.token}")

        # Remove any enterprise prefix if present
        if self.token.startswith("xoxe."):
            self.token = self.token[5:]  # Remove "xoxe." prefix
            self.logger.info(f"Token after prefix removal: {self.token}")

        if not self.token:
            raise ValueError("SLACK_TOKEN environment variable is not set")
        if not self.token.startswith("xoxp-"):
            raise ValueError(
                f"Invalid token type. Expected user token (xoxp-), got: {self.token[:10]}..."
            )

        # Initialize WebClient with explicit Authorization header
        self.client = WebClient(
            token=None,  # Don't set token here since we're using headers
            headers={"Authorization": f"Bearer {self.token}"},
        )

        # Required scopes for user token
        self.required_scopes = [
            "channels:read",  # For reading public channel info
            "channels:history",  # For reading public channel messages
            "groups:read",  # For reading private channel info
            "groups:history",  # For reading private channel messages
            "mpim:read",  # For reading group DM info
            "mpim:history",  # For reading group DM messages
            "im:read",  # For reading DM info
            "im:history",  # For reading DM messages
        ]

        # Test auth token on initialization
        self._test_auth()

    def _test_auth(self) -> None:
        """Test authentication and log token information."""
        try:
            # Test auth
            auth_response = self.client.auth_test()

            # Store auth info
            self.user_id = auth_response.get("user_id")
            self.team_id = auth_response.get("team_id")
            self.enterprise_id = auth_response.get("enterprise_id")

            # Log connection info
            self.logger.info("=== Connection Information ===")
            self.logger.info(f"Connected as user: {auth_response['user']}")
            self.logger.info(f"In workspace: {auth_response['team']}")
            self.logger.info(f"User ID: {self.user_id}")
            self.logger.info(f"Team ID: {self.team_id}")
            if self.enterprise_id:
                self.logger.info(f"Enterprise ID: {self.enterprise_id}")

            # Test API endpoints and log results
            self.logger.info("\n=== API Endpoint Tests ===")

            # Log token info (first few chars)
            token_preview = self.token[:10] + "..." if self.token else "None"
            self.logger.info(f"Using token starting with: {token_preview}")

            # Test conversations.list
            try:
                self.logger.info("Testing conversations.list...")
                list_response = self.client.conversations_list(limit=1)
                self.logger.info(f"Raw response: {list_response}")
                self.logger.info("✓ conversations.list works")
                self.logger.info(
                    f"First channel: {list_response['channels'][0]['name'] if list_response.get('channels') else 'No channels found'}"
                )
            except SlackApiError as e:
                self.logger.error(f"✗ conversations.list failed: {str(e)}")
                self.logger.error(f"Error details: {e.response}")

            # Test conversations.info with first channel
            try:
                self.logger.info(
                    f"Testing conversations.info for channel {self.channels[0]}..."
                )
                channel_info = self.client.conversations_info(channel=self.channels[0])
                self.logger.info(f"Raw response: {channel_info}")
                self.logger.info(
                    f"✓ conversations.info works for channel {self.channels[0]}"
                )
                channel_name = channel_info["channel"]["name"]
                is_private = channel_info["channel"].get("is_private", False)
                self.logger.info(
                    f"Channel info: #{channel_name} (private: {is_private})"
                )
            except SlackApiError as e:
                self.logger.error(f"✗ conversations.info failed: {str(e)}")
                self.logger.error(f"Error details: {e.response}")

            # Test conversations.history
            try:
                self.logger.info(
                    f"Testing conversations.history for channel {self.channels[0]}..."
                )
                history = self.client.conversations_history(
                    channel=self.channels[0], limit=1
                )
                self.logger.info(f"Raw response: {history}")
                self.logger.info(
                    f"✓ conversations.history works for channel {self.channels[0]}"
                )
            except SlackApiError as e:
                self.logger.error(f"✗ conversations.history failed: {str(e)}")
                self.logger.error(f"Error details: {e.response}")

            # Test channel membership
            try:
                self.logger.info(
                    f"Testing conversations.members for channel {self.channels[0]}..."
                )
                members = self.client.conversations_members(channel=self.channels[0])
                self.logger.info(f"Raw response: {members}")
                if self.user_id in members.get("members", []):
                    self.logger.info("✓ User is a member of the channel")
                else:
                    self.logger.warning(
                        f"✗ User is not a member of the channel. Please join the channel first."
                    )
            except SlackApiError as e:
                self.logger.error(f"✗ conversations.members failed: {str(e)}")
                self.logger.error(f"Error details: {e.response}")

            # Test usergroups.list since it's known to work
            try:
                self.logger.info("Testing usergroups.list...")
                usergroups = self.client.usergroups_list()
                self.logger.info("✓ usergroups.list works")
                self.logger.info(
                    f"Number of usergroups: {len(usergroups.get('usergroups', []))}"
                )
            except SlackApiError as e:
                self.logger.error(f"✗ usergroups.list failed: {str(e)}")
                self.logger.error(f"Error details: {e.response}")

        except SlackApiError as e:
            self.logger.error("=== Authentication Error ===")
            self.logger.error(str(e))
            if "invalid_auth" in str(e):
                self.logger.error("User token appears to be invalid or expired")
            elif "missing_scope" in str(e):
                self.logger.error(
                    "User token is missing required scopes. Please add these scopes to your Slack App:\n"
                    "- channels:read\n"
                    "- channels:history\n"
                    "- groups:read\n"
                    "- groups:history\n"
                    "- mpim:read\n"
                    "- mpim:history\n"
                    "- im:read\n"
                    "- im:history"
                )
            raise

    def get_channel_messages(
        self, channel: str, days: int = 14
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a Slack channel using conversations.history.
        Includes thread replies.

        Args:
            channel: Channel ID to fetch messages from.
            days: Number of days of history to fetch.

        Returns:
            List of message dictionaries.
        """
        try:
            # Calculate the oldest timestamp to fetch from
            oldest_time = datetime.now() - timedelta(days=days)
            oldest_ts = oldest_time.timestamp()

            messages = []
            cursor = None

            while True:
                try:
                    response = self.client.conversations_history(
                        channel=channel,
                        limit=100,  # Max messages per request
                        oldest=oldest_ts,
                        cursor=cursor,
                    )

                    # Process messages and get thread replies
                    channel_messages = response.get("messages", [])
                    for msg in channel_messages:
                        if msg.get("type") == "message" and not msg.get("subtype"):
                            messages.append(msg)

                            # If message has replies, fetch them
                            if msg.get("thread_ts"):
                                try:
                                    thread_response = self.client.conversations_replies(
                                        channel=channel,
                                        ts=msg["thread_ts"],
                                        oldest=oldest_ts,
                                    )
                                    # Add all replies except the parent message (which we already have)
                                    thread_messages = thread_response.get(
                                        "messages", []
                                    )
                                    messages.extend(
                                        [
                                            reply
                                            for reply in thread_messages[
                                                1:
                                            ]  # Skip parent message
                                            if reply.get("type") == "message"
                                            and not reply.get("subtype")
                                        ]
                                    )
                                except SlackApiError as e:
                                    self.logger.error(
                                        f"Error fetching thread replies: {str(e)}"
                                    )

                    # Check if there are more messages
                    cursor = response.get("response_metadata", {}).get("next_cursor")
                    if not cursor or not response.get("has_more", False):
                        break

                except SlackApiError as e:
                    if "channel_not_found" in str(e):
                        self.logger.error(f"Channel not found: {channel}")
                        return []
                    raise

            self.logger.info(
                f"Fetched {len(messages)} messages from channel: {channel}"
            )
            return messages

        except SlackApiError as e:
            self.logger.error(f"Error fetching messages from {channel}: {str(e)}")
            raise

    def _get_channel_id(self, channel: str) -> str:
        """Get channel ID from channel name."""
        try:
            response = self.client.conversations_list()
            for ch in response["channels"]:
                if ch["name"] == channel or ch["id"] == channel:
                    return ch["id"]
            return ""
        except SlackApiError as e:
            self.logger.error(f"Error getting channel ID: {str(e)}")
            raise

    def get_channel_info(self, channel: str) -> dict:
        """
        Get information about a Slack channel.

        Args:
            channel: Channel ID to get information for.

        Returns:
            Dictionary containing channel information.
        """
        try:
            response = self.client.conversations_info(channel=channel)
            return response["channel"]
        except Exception as e:
            self.logger.error(f"Error getting channel info for {channel}: {str(e)}")
            return {"name": channel}  # Fallback to using channel ID as name

    def fetch_user_mapping(self) -> Dict[str, str]:
        """
        Fetch mapping of user IDs to user names.
        Uses a local cache with 24-hour TTL to minimize API calls.

        Returns:
            Dictionary mapping user IDs to user names.
        """
        try:
            # Check if we have a valid cache
            if self._is_cache_valid():
                self.logger.info("Using cached user mapping")
                return self._load_user_cache()

            # Cache is invalid or doesn't exist, fetch from API
            self.logger.info("Fetching user list from Slack API")
            response = self.client.users_list(pretty=1)

            # Create user mapping
            user_mapping = {}
            for user in response["members"]:
                user_id = user["id"]
                # Use display name if set, otherwise real name, fallback to username
                display_name = user.get("profile", {}).get("display_name")
                real_name = user.get("profile", {}).get("real_name")
                username = user.get("name")
                user_mapping[user_id] = display_name or real_name or username or user_id

            # Save to cache with timestamp
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "users": user_mapping,
            }
            self._save_user_cache(cache_data)

            self.logger.info(
                f"Fetched and cached mapping for {len(user_mapping)} users"
            )
            return user_mapping

        except SlackApiError as e:
            self.logger.error(f"Error fetching user mapping: {str(e)}")
            # Try to use cached data even if expired
            if self.user_cache_file.exists():
                self.logger.warning("Using expired cache due to API error")
                return self._load_user_cache()
            return {}

    def _is_cache_valid(self) -> bool:
        """Check if the user cache is valid."""
        if not self.user_cache_file.exists():
            return False

        try:
            with open(self.user_cache_file, "r") as f:
                cache_data = json.load(f)

            cache_time = datetime.fromisoformat(cache_data["timestamp"])
            return datetime.now() - cache_time < self.user_cache_ttl

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.error(f"Error reading cache: {str(e)}")
            return False

    def _load_user_cache(self) -> Dict[str, str]:
        """Load user mapping from cache."""
        try:
            with open(self.user_cache_file, "r") as f:
                cache_data = json.load(f)
            return cache_data["users"]
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Error loading cache: {str(e)}")
            return {}

    def _save_user_cache(self, cache_data: Dict[str, Any]) -> None:
        """Save user mapping to cache."""
        try:
            with open(self.user_cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache: {str(e)}")

    def fetch_channel_mapping(self) -> Dict[str, str]:
        """
        Fetch mapping of channel IDs to channel names.

        Returns:
            Dictionary mapping channel IDs to channel names.
        """
        try:
            response = self.client.conversations_list(
                types="public_channel,private_channel"
            )
            channel_mapping = {}
            for channel in response["channels"]:
                channel_id = channel["id"]
                channel_name = channel["name"]
                channel_mapping[channel_id] = channel_name
            self.logger.info(f"Fetched mapping for {len(channel_mapping)} channels")
            return channel_mapping
        except SlackApiError as e:
            self.logger.error(f"Error fetching channel mapping: {str(e)}")
            return {}
