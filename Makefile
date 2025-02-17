.PHONY: install install-dev test lint format clean run

# Python interpreter to use
PYTHON := python3
VENV := .venv

# Create virtual environment if it doesn't exist
$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/pip install --upgrade pip

# Install production dependencies
install: $(VENV)/bin/activate
	./$(VENV)/bin/pip install -e .

# Install development dependencies
install-dev: $(VENV)/bin/activate
	./$(VENV)/bin/pip install -e ".[dev]"

# Run tests
test: install-dev
	./$(VENV)/bin/pytest tests/ -v --cov=slack_summarizer

# Run linting
lint: install-dev
	./$(VENV)/bin/flake8 slack_summarizer tests
	./$(VENV)/bin/black --check slack_summarizer tests
	./$(VENV)/bin/isort --check-only slack_summarizer tests

# Format code
format: install-dev
	./$(VENV)/bin/black slack_summarizer tests
	./$(VENV)/bin/isort slack_summarizer tests

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
	./$(VENV)/bin/slack-summarizer

# Create config from example if it doesn't exist
config/config.yaml:
	cp config/config.yaml.example config/config.yaml

# Create .env from example if it doesn't exist
.env:
	cp .env.example .env

# Initialize project (create config and .env files)
init: config/config.yaml .env 