# Slack Summarizer

A Python application that downloads Slack channel history and uses OpenAI to generate summaries of conversations, including thread replies.

## Features

- Download message history from specified Slack channels
- Include thread replies in message history
- Generate structured summaries using OpenAI's o1-mini model
- Configurable time range for message history
- Support for multiple channels
- Markdown-formatted summaries with sections for:
  - Archived Tasks
  - Conversations & Resolutions
  - Open Issues/Items to Address

## Prerequisites

- Python 3.8 or higher
- Slack App with Bot Token (see [Slack App Setup](#slack-app-setup))
- OpenAI API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/slack-summarizer.git
   cd slack-summarizer
   ```

2. Initialize the project:
   ```bash
   make init
   ```

3. Configure your environment:
   - Copy `.env.example` to `.env` and update with your API keys
   - Copy `config/config.yaml.example` to `config/config.yaml` and modify settings as needed

4. Install dependencies:
   ```bash
   make install
   ```

   Note: If you're already in a virtual environment, the installation will use that environment.
   Otherwise, it will create a new one in `.venv/`.

## Slack App Setup

This application requires a Slack User Token (not a Bot Token) to access message history and private channels. Here's how to set it up:

1. Create a new Slack App at https://api.slack.com/apps

2. Configure the app:
   - Name: "Summarizer" (or your preferred name)
   - Add User Token Scopes (not Bot Token Scopes):
     - `channels:history`, `channels:read` - For public channels
     - `groups:history`, `groups:read` - For private channels
     - `im:history`, `im:read` - For direct messages
     - `mpim:history`, `mpim:read` - For group messages
     - `users:read` - For user information

3. Install the app:
   - Go to "Install App" in the sidebar
   - Install to your workspace
   - Copy the "User OAuth Token" (starts with `xoxp-`)
   - Add the token to your `.env` file

Note: The app needs User Token permissions to access private channels and complete message history. Bot tokens have more limited access.

## OpenAI Setup

1. Create an account at https://platform.openai.com/
2. Generate an API key at https://platform.openai.com/api-keys
3. Copy the API key (starts with `sk-`) to your `.env` file

## Usage

1. Configure channels in `config/config.yaml`:
   ```yaml
   slack:
     channels:
       - "C0123456789"  # Channel ID for #general
       - "C9876543210"  # Channel ID for #random
   ```

2. Run the application:
   ```bash
   make run
   ```

3. The application will:
   - Fetch messages and thread replies from configured channels
   - Generate structured summaries using o1-mini
   - Save summaries as Markdown files in the `summaries/` directory

## Configuration

### Environment Variables

- `SLACK_TOKEN`: Your Slack User OAuth Token (starts with `xoxp-`)
- `OPENAI_API_KEY`: Your OpenAI API key (starts with `sk-`)

### Config File (config/config.yaml)

```yaml
slack:
  token: "${SLACK_TOKEN}"
  channels:
    - "C0123456789"  # Channel IDs
openai:
  api_key: "${OPENAI_API_KEY}"
summary:
  duration_days: 14  # How many days of history to summarize
```

### Customizing the Summary Format

The summary format can be customized by modifying the prompt in `summarizer.py`. The current format includes:

1. **Archived Tasks:** Completed and archived tasks
2. **Conversations & Resolutions:** Important discussions and decisions
3. **Open Issues:** Pending items that need attention

Each section includes:
- Timestamps for important events
- Names of involved users
- Context and outcomes where applicable

## Development

1. Install development dependencies:
   ```bash
   make install-dev
   ```

2. Run tests:
   ```bash
   make test
   ```

3. Format code:
   ```bash
   make format
   ```

4. Run linting:
   ```bash
   make lint
   ```

### Available Make Commands

- `make install`: Install production dependencies
- `make install-dev`: Install development dependencies
- `make test`: Run tests with coverage
- `make lint`: Check code style
- `make format`: Format code using black and isort
- `make clean`: Clean up generated files
- `make run`: Run the application
- `make init`: Initialize configuration files

Note: All commands will detect if you're already in a virtual environment and behave accordingly.

## Project Structure

```
slack-summarizer/
├── config/               # Configuration files
├── logs/                # Application logs
├── summaries/           # Generated summary files
├── cache/               # User and channel mapping cache
├── tests/               # Test files
└── slack_summarizer/    # Main package
    ├── config.py        # Configuration handling
    ├── logger.py        # Logging setup
    ├── main.py          # Application entry point
    ├── slack_client.py  # Slack API integration
    ├── summarizer.py    # OpenAI integration
    └── oauth.py         # Slack OAuth handling
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Slack API Documentation](https://api.slack.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)