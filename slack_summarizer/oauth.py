"""
OAuth handler for Slack authentication.
"""

import os
from typing import Optional, Dict, Any

from slack_sdk import WebClient
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore


class SlackOAuth:
    """Handles Slack OAuth flow."""

    def __init__(self):
        """Initialize the OAuth handler."""
        self.client_id = os.getenv("SLACK_CLIENT_ID")
        self.client_secret = os.getenv("SLACK_CLIENT_SECRET")
        self.scopes = [
            "channels:read",
            "channels:history",
            "groups:read",
            "groups:history",
        ]

        # Create storage for installations and state
        self.installation_store = FileInstallationStore(base_dir="./data")
        self.state_store = FileOAuthStateStore(
            expiration_seconds=300, base_dir="./data"
        )

    def get_authorization_url(self, team_id: Optional[str] = None) -> str:
        """
        Generate the OAuth authorization URL.

        Args:
            team_id: Optional team ID to pre-select workspace

        Returns:
            The authorization URL
        """
        generator = AuthorizeUrlGenerator(
            client_id=self.client_id,
            scopes=self.scopes,
        )
        state = self.state_store.issue()
        url = generator.generate(state=state)
        if team_id:
            url = f"{url}&team={team_id}"
        return url

    def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """
        Exchange the temporary code for an access token.

        Args:
            code: The temporary authorization code
            state: The state parameter for verification

        Returns:
            The OAuth response containing the access token
        """
        # Verify state
        if not self.state_store.consume(state):
            raise ValueError("Invalid state parameter")

        # Exchange code for token
        client = WebClient()
        response = client.oauth_v2_access(
            client_id=self.client_id, client_secret=self.client_secret, code=code
        )

        # Store the installation
        self.installation_store.save(response)

        return response

    def get_installation(
        self, team_id: str, enterprise_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get stored installation data.

        Args:
            team_id: The team ID
            enterprise_id: Optional enterprise ID

        Returns:
            The installation data including tokens
        """
        installation = self.installation_store.find_installation(
            enterprise_id=enterprise_id,
            team_id=team_id,
        )
        if not installation:
            raise ValueError(f"No installation found for team {team_id}")
        return installation
