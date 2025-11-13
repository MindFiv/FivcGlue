.PHONY: help install install-min dev lint format test test-cov clean build

# Default target
help:
	@echo "FivcGlue - Available Make Commands"
	@echo "==================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install      - Install with dev dependencies (default)"
	@echo "  install-min  - Install minimal runtime dependencies only"
	@echo "  dev          - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  lint         - Run code linting with ruff"
	@echo "  format       - Format code with ruff"
	@echo "  test         - Run tests with pytest"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  clean        - Clean temporary files and caches"
	@echo "  build        - Build distribution packages"
	@echo ""

# Installation targets
install:
	@echo "Installing FivcGlue with development dependencies..."
	uv sync --extra dev --extra yaml

install-min:
	@echo "Installing FivcGlue with minimal dependencies..."
	uv sync

dev:
	@echo "Installing development dependencies..."
	uv sync --extra dev --extra yaml

# Development targets
lint: dev
	@echo "Running code linting..."
	uv run ruff check src tests

format: dev
	@echo "Formatting code..."
	uv run ruff format src tests

test: dev
	@echo "Running tests..."
	uv run pytest -v

test-cov: dev
	@echo "Running tests with coverage..."
	uv run pytest --cov=fivcglue --cov-report=term-missing --cov-report=html

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true
	@echo "Clean complete!"

build: dev
	@echo "Building distribution packages..."
	uv build
	@echo "Build complete! Check the dist/ directory."

