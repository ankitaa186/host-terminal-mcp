.PHONY: all venv install install-dev test test-verbose lint format build clean run run-ask run-allow-all init-config inspect package publish publish-pypi publish-github marketplace help

# Default Python version
PYTHON ?= python3.10

# Virtual environment directory
VENV := .venv
UV := uv

# Default target
all: install-dev test

# Create virtual environment if it doesn't exist
venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "📦 Creating virtual environment..."; \
		$(UV) venv $(VENV); \
		echo "✅ Virtual environment created at $(VENV)"; \
	else \
		echo "✅ Virtual environment already exists at $(VENV)"; \
	fi

# Install production dependencies (creates venv if needed)
install: venv
	$(UV) pip install -e .
	@echo "✅ Installed in production mode"

# Install with dev dependencies (creates venv if needed)
install-dev: venv
	$(UV) pip install -e ".[dev]"
	@echo "✅ Installed in development mode"

# Run tests
test: venv
	$(UV) run pytest

# Run tests with verbose output
test-verbose: venv
	$(UV) run pytest -v --tb=short

# Run tests with coverage
test-cov: venv
	$(UV) run pytest --cov=src/host_terminal_mcp --cov-report=term-missing

# Lint code
lint: venv
	$(UV) run ruff check src/ tests/ || true
	$(UV) run mypy src/ || true

# Format code
format: venv
	$(UV) run ruff format src/ tests/ || true

# Build Python wheel/sdist
build: venv
	$(UV) build
	@echo "✅ Built Python package in dist/"

# Package as Cowork plugin (.plugin file)
package: build
	$(UV) run python scripts/package_plugin.py
	@echo "✅ Plugin packaged in dist/"

# Publish to PyPI (MCP server only)
publish-pypi: build
	@echo "📤 Publishing to PyPI..."
	$(UV) publish
	@echo "✅ Published to PyPI"

# Create GitHub release (requires gh CLI)
publish-github: package
	@VERSION=$$(python -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])"); \
	echo "📤 Creating GitHub release v$$VERSION..."; \
	gh release create "v$$VERSION" dist/*.plugin dist/*.whl dist/*.tar.gz \
		--title "v$$VERSION" \
		--notes "Release v$$VERSION" \
		--draft; \
	echo "✅ Draft release created - review and publish at GitHub"

# Full publish (PyPI + GitHub)
publish: publish-pypi publish-github
	@echo "✅ Published to PyPI and GitHub"

# Create marketplace repository structure for UI installation
marketplace: venv
	$(UV) run python scripts/setup_marketplace.py
	@echo "✅ Marketplace created - see output for next steps"

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned build artifacts"

# Clean everything including venv
clean-all: clean
	rm -rf $(VENV)
	@echo "✅ Cleaned everything including virtual environment"

# Run the MCP server (default: allowlist mode)
run: install
	$(UV) run host-terminal-mcp

# Run in ask mode
run-ask: install
	$(UV) run host-terminal-mcp --mode ask

# Run in allow-all mode (DANGEROUS)
run-allow-all: install
	@echo "⚠️  WARNING: Running in allow-all mode - all commands will be executed!"
	$(UV) run host-terminal-mcp --mode allow_all

# Initialize default config
init-config: install
	$(UV) run host-terminal-mcp --init-config
	@echo "✅ Config created at ~/.config/host-terminal-mcp/config.yaml"

# Test with MCP Inspector
inspect: install
	npx @modelcontextprotocol/inspector $(UV) run host-terminal-mcp

# Show help
help:
	@echo "Host Terminal MCP - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make venv          Create virtual environment"
	@echo "  make install       Install production dependencies"
	@echo "  make install-dev   Install with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run tests"
	@echo "  make test-verbose  Run tests with verbose output"
	@echo "  make test-cov      Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run linters"
	@echo "  make format        Format code"
	@echo ""
	@echo "Building & Publishing:"
	@echo "  make build         Build Python wheel and sdist"
	@echo "  make package       Package as Cowork plugin (.plugin)"
	@echo "  make marketplace   Create GitHub marketplace for UI install"
	@echo "  make publish-pypi  Publish MCP server to PyPI"
	@echo "  make publish-github Create GitHub release with plugin"
	@echo "  make publish       Publish to both PyPI and GitHub"
	@echo "  make clean         Clean build artifacts"
	@echo "  make clean-all     Clean everything including venv"
	@echo ""
	@echo "Running:"
	@echo "  make run           Run MCP server (allowlist mode)"
	@echo "  make run-ask       Run MCP server (ask mode)"
	@echo "  make run-allow-all Run MCP server (allow-all mode) ⚠️"
	@echo "  make init-config   Create default config file"
	@echo "  make inspect       Test with MCP Inspector"
	@echo ""
	@echo "Environment:"
	@echo "  PYTHON=python3.11 make venv   Use specific Python version"
