.PHONY: install install-dev test lint format clean run

# Python interpreter to use
PYTHON := python3
VENV := .venv

# Check if we're already in a virtual environment
INVENV := $(shell echo $$VIRTUAL_ENV)

# Create virtual environment if it doesn't exist and not already in one
$(VENV)/bin/activate:
	@if [ -z "$(INVENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		./$(VENV)/bin/pip install --upgrade pip; \
	fi

# Install production dependencies
install: $(VENV)/bin/activate
	@if [ -z "$(INVENV)" ]; then \
		./$(VENV)/bin/pip install -e .; \
	else \
		pip install -e .; \
	fi

# Install development dependencies
install-dev: $(VENV)/bin/activate
	@if [ -z "$(INVENV)" ]; then \
		./$(VENV)/bin/pip install -e ".[dev]"; \
	else \
		pip install -e ".[dev]"; \
	fi

# Run tests
test: install-dev
	@if [ -z "$(INVENV)" ]; then \
		./$(VENV)/bin/pytest tests/ -v --cov=slack_summarizer; \
	else \
		pytest tests/ -v --cov=slack_summarizer; \
	fi

# Run linting
lint: install-dev
	@if [ -z "$(INVENV)" ]; then \
		./$(VENV)/bin/flake8 slack_summarizer tests; \
		./$(VENV)/bin/black --check slack_summarizer tests; \
		./$(VENV)/bin/isort --check-only slack_summarizer tests; \
	else \
		flake8 slack_summarizer tests; \
		black --check slack_summarizer tests; \
		isort --check-only slack_summarizer tests; \
	fi

# Format code
format: install-dev
	@if [ -z "$(INVENV)" ]; then \
		./$(VENV)/bin/black slack_summarizer tests; \
		./$(VENV)/bin/isort slack_summarizer tests; \
	else \
		black slack_summarizer tests; \
		isort slack_summarizer tests; \
	fi

# Clean up generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf **/__pycache__
	rm -rf $(VENV)

# Run the application
run: install
	@if [ -z "$(INVENV)" ]; then \
		./$(VENV)/bin/slack-summarizer; \
	else \
		slack-summarizer; \
	fi

# Create config from example if it doesn't exist
config/config.yaml:
	cp config/config.yaml.example config/config.yaml

# Create .env from example if it doesn't exist
.env:
	cp .env.example .env

# Initialize project (create config and .env files)
init: config/config.yaml .env 