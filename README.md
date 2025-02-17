# Slack Summarizer

A Python application that downloads Slack channel history and uses OpenAI to generate summaries of conversations.

## Features

- Download message history from specified Slack channels
- Generate summaries using OpenAI's GPT models
- Configurable time range for message history
- Support for multiple channels
- Customizable output formats

## Prerequisites

- Python 3.8 or higher
- Slack Bot Token with necessary permissions
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

## Usage

1. Run the application:
   ```bash
   make run
   ```

2. The application will:
   - Fetch messages from configured Slack channels
   - Generate summaries using OpenAI
   - Output results to the specified destination

## Configuration

### Environment Variables

- `SLACK_TOKEN`: Your Slack Bot User OAuth Token
- `OPENAI_API_KEY`: Your OpenAI API key

### Config File (config/config.yaml)

```yaml
slack:
  token: "${SLACK_TOKEN}"
  channels:
    - "general"
    - "random"
openai:
  api_key: "${OPENAI_API_KEY}"
summary:
  duration_days: 14
  output_file: "channel_summaries.txt"
```

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

## Project Structure

```
slack-summarizer/
├── config/               # Configuration files
├── logs/                # Application logs
├── tests/               # Test files
└── slack_summarizer/    # Main package
    ├── config.py        # Configuration handling
    ├── exceptions.py    # Custom exceptions
    ├── logger.py        # Logging setup
    ├── main.py          # Application entry point
    ├── slack_client.py  # Slack API integration
    ├── summarizer.py    # OpenAI integration
    └── utils.py         # Utility functions
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

- Slack API Documentation
- OpenAI API Documentation