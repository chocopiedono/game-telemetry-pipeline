.PHONY: setup install test coverage lint format clean package deploy

# Python settings
PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
BLACK := $(VENV)/bin/black
MYPY := $(VENV)/bin/mypy

# AWS settings
FUNCTION_NAME := game-telemetry-dedup
REGION := $(shell aws configure get region)
PACKAGE_FILE := function.zip

# Setup virtual environment
setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

# Install dependencies
install: setup
	$(PIP) install -r requirements.txt
	$(PIP) install black mypy

# Run tests
test:
	$(PYTEST) tests/ -v

# Run tests with coverage
coverage:
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Format code with black
format:
	$(BLACK) src/ tests/

# Type checking with mypy
lint:
	$(MYPY) src/ --ignore-missing-imports

# Clean up generated files
clean:
	rm -rf $(PACKAGE_FILE) htmlcov/ .coverage .pytest_cache/ .mypy_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Package the Lambda function
package: clean
	zip -r $(PACKAGE_FILE) src/ requirements.txt

# Deploy to AWS Lambda
deploy: package
	aws lambda update-function-code \
		--function-name $(FUNCTION_NAME) \
		--zip-file fileb://$(PACKAGE_FILE) \
		--region $(REGION)

# Run all checks (format, lint, test)
check: format lint test

# Development setup (install, format, lint)
dev-setup: install format lint

# Help target
help:
	@echo "Available targets:"
	@echo "  setup      - Create virtual environment"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  coverage   - Run tests with coverage report"
	@echo "  format     - Format code with black"
	@echo "  lint       - Run type checking with mypy"
	@echo "  clean      - Clean up generated files"
	@echo "  package    - Create Lambda deployment package"
	@echo "  deploy     - Deploy to AWS Lambda"
	@echo "  check      - Run all checks (format, lint, test)"
	@echo "  dev-setup  - Setup for development"
