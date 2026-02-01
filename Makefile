.PHONY: all install test test-verbose test-cov lint format build package \
       publish publish-pypi publish-github marketplace \
       clean clean-all run start stop status restart \
       init-config inspect help

UV   := uv
VENV := .venv

# HTTP daemon settings
HTTP_PORT ?= 8099
STATE_DIR := $(HOME)/.local/state/host-terminal-mcp
LOG_FILE  := $(STATE_DIR)/http-server.log
PID_FILE  := $(STATE_DIR)/http-server.pid

# stdio server settings
MODE ?= allowlist

# ---------- Setup ----------

all: install test

$(VENV):
	@$(UV) venv $(VENV)

install: $(VENV)
	@$(UV) pip install -e ".[http,dev]" --quiet
	@echo "Installed host-terminal-mcp with all extras"

# ---------- Quality ----------

test: $(VENV)
	$(UV) run pytest

test-verbose: $(VENV)
	$(UV) run pytest -v --tb=short

test-cov: $(VENV)
	$(UV) run pytest --cov=src/host_terminal_mcp --cov-report=term-missing

lint: $(VENV)
	$(UV) run ruff check src/ tests/ || true
	$(UV) run mypy src/ || true

format: $(VENV)
	$(UV) run ruff format src/ tests/ || true

# ---------- Build & Publish ----------

build: $(VENV)
	$(UV) build

package: build
	$(UV) run python scripts/package_plugin.py

publish-pypi: build
	$(UV) publish

publish-github: package
	@VERSION=$$(python -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])"); \
	gh release create "v$$VERSION" dist/*.plugin dist/*.whl dist/*.tar.gz \
		--title "v$$VERSION" --notes "Release v$$VERSION" --draft

publish: publish-pypi publish-github

marketplace: $(VENV)
	$(UV) run python scripts/setup_marketplace.py

# ---------- Run (stdio, foreground) ----------

run: install
	$(UV) run host-terminal-mcp --mode $(MODE)

# ---------- HTTP daemon (start/stop/status) ----------

start: install
	@mkdir -p $(STATE_DIR)
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "Already running (PID $$(cat $(PID_FILE)), port $(HTTP_PORT))"; \
		exit 1; \
	fi
	@nohup $(UV) run host-terminal-mcp --http --port $(HTTP_PORT) --mode $(MODE) > $(LOG_FILE) 2>&1 & \
		echo $$! > $(PID_FILE); \
		echo "Started on port $(HTTP_PORT) (PID $$!)"; \
		echo "Logs: $(LOG_FILE)"

stop:
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		kill $$(cat $(PID_FILE)); \
		rm -f $(PID_FILE); \
		echo "Stopped"; \
	else \
		echo "Not running"; \
		rm -f $(PID_FILE); \
	fi

status:
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "Running (PID $$(cat $(PID_FILE)), port $(HTTP_PORT))"; \
	else \
		echo "Not running"; \
	fi
	@if [ -f $(LOG_FILE) ]; then echo ""; tail -10 $(LOG_FILE); fi

restart: stop start

# ---------- Utilities ----------

init-config: install
	$(UV) run host-terminal-mcp --init-config

inspect: install
	npx @modelcontextprotocol/inspector $(UV) run host-terminal-mcp

clean:
	rm -rf dist/ build/ *.egg-info/ src/*.egg-info/ \
		.pytest_cache/ .ruff_cache/ .mypy_cache/ htmlcov/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean
	rm -rf $(VENV)

# ---------- Help ----------

help:
	@echo "Host Terminal MCP"
	@echo ""
	@echo "  make install                  Install all dependencies (venv auto-created)"
	@echo ""
	@echo "Stdio server (foreground, for Claude Desktop / MCP Inspector):"
	@echo "  make run                      Run in allowlist mode (default)"
	@echo "  make run MODE=ask             Run in ask mode"
	@echo "  make run MODE=allow_all       Run in allow-all mode"
	@echo ""
	@echo "HTTP server (background daemon, for Annie / external services):"
	@echo "  make start                    Start on port 8099"
	@echo "  make start HTTP_PORT=9000     Start on custom port"
	@echo "  make start MODE=ask           Start with ask permission mode"
	@echo "  make stop                     Stop"
	@echo "  make status                   Show status and recent logs"
	@echo "  make restart                  Stop + start"
	@echo ""
	@echo "MODE controls the permission mode for both run and start:"
	@echo "  allowlist (default)  Only pre-approved commands"
	@echo "  ask                  Prompt for unknown commands"
	@echo "  allow_all            Allow everything (dangerous)"
	@echo ""
	@echo "Testing:"
	@echo "  make test                     Run tests"
	@echo "  make test-verbose             Verbose output"
	@echo "  make test-cov                 With coverage"
	@echo "  make lint                     Run linters"
	@echo "  make format                   Format code"
	@echo ""
	@echo "Build:"
	@echo "  make build                    Build wheel and sdist"
	@echo "  make package                  Package as .plugin"
	@echo "  make publish                  Publish to PyPI + GitHub"
	@echo ""
	@echo "Utilities:"
	@echo "  make init-config              Create default config file"
	@echo "  make inspect                  Test with MCP Inspector"
	@echo "  make clean                    Clean build artifacts"
	@echo "  make clean-all                Clean everything including venv"
