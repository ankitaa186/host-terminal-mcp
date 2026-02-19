# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.2] - 2026-02-19

### Changed

- README now documents full absolute path requirement for Claude Desktop config (Claude Desktop uses a minimal PATH that excludes `~/.local/bin`).

### Added

- Contributing guide and changelog.
- GitHub Actions CI workflow.

## [0.2.0] - 2026-02-01

### Added

- HTTP transport with FastAPI (`--http` flag) for external service access.
- `Makefile` with `start`/`stop`/`status`/`restart` targets for HTTP daemon management.
- `set_permission_mode` tool to change permission mode at runtime.
- `get_permission_status` tool to inspect current permissions.
- Configurable `allowed_directories` to restrict command execution scope.
- MCP elicitation support for `ask` mode (human-in-the-loop approval).

### Changed

- Improved README with architecture diagram, permission mode docs, and HTTP transport instructions.

## [0.1.0] - 2026-01-31

### Added

- Initial release.
- MCP stdio server for executing terminal commands from Claude Desktop / Co-work.
- Permission system with `allowlist`, `ask`, and `allow_all` modes.
- Default allowed commands for file listing, git (read-only), system info, and more.
- Always-blocked commands for dangerous operations (`rm -rf /`, `sudo`, etc.).
- YAML configuration file support (`~/.config/host-terminal-mcp/config.yaml`).
- `execute_command`, `change_directory`, and `get_current_directory` tools.
