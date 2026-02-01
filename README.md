# Host Terminal MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

An MCP (Model Context Protocol) server that enables AI assistants like Claude to execute terminal commands on your host machine with **configurable, granular permission controls**.

> ⚠️ **Security Warning**: This tool executes commands on your actual computer. Please read the [Security Considerations](#security-considerations) and [Disclaimer](#disclaimer) sections carefully before use.

## Features

- 🔒 **Three Permission Modes**:
  - `allowlist` - Only pre-approved commands can run (default, safest)
  - `ask` - Prompt for approval when a command isn't in the allow list
  - `allow_all` - Allow all commands (use with extreme caution!)

- 📋 **Extensive Default Allow List** - Common developer read-only commands pre-configured:
  - File operations: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`
  - Git read operations: `git status`, `git log`, `git diff`, `git branch`
  - System info: `ps`, `df`, `du`, `uname`, `whoami`
  - Package managers (info only): `npm list`, `pip show`, `brew info`
  - And many more...

- 🚫 **Blocked Commands** - Dangerous commands are always blocked:
  - `rm -rf /`, `sudo`, `mkfs`, fork bombs, etc.

- ⚙️ **Highly Configurable**:
  - YAML configuration file
  - Custom command patterns (prefix or regex)
  - Directory restrictions
  - Timeout controls
  - Environment variable passthrough

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or pipx

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/host-terminal-mcp.git
cd host-terminal-mcp

# Install with pip
pip install .

# Or install in development mode
pip install -e .
```

### Install with pipx (recommended for CLI tools)

```bash
pipx install .
```

## Quick Start

### 1. Initialize Configuration

Create a default configuration file:

```bash
host-terminal-mcp --init-config
```

This creates `~/.config/host-terminal-mcp/config.yaml` with sensible defaults.

### 2. Configure Claude Desktop (or other MCP client)

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "host-terminal": {
      "command": "host-terminal-mcp",
      "args": []
    }
  }
}
```

Or with custom options:

```json
{
  "mcpServers": {
    "host-terminal": {
      "command": "host-terminal-mcp",
      "args": [
        "--mode", "ask",
        "--allow-dir", "/path/to/projects"
      ]
    }
  }
}
```

### 3. Restart Claude Desktop

Restart the application to load the new MCP server.

## Configuration

### Configuration File Location

Default: `~/.config/host-terminal-mcp/config.yaml`

You can specify a custom location with the `--config` flag.

### Configuration Options

```yaml
# Permission mode: allowlist | ask | allow_all
permission_mode: allowlist

# Command execution timeout (seconds)
timeout_seconds: 300

# Maximum output size (characters)
max_output_size: 100000

# Shell to use
shell: /bin/bash

# Directories where commands can run
allowed_directories:
  - "~"
  - "/opt/projects"

# Environment variables to pass through
environment_passthrough:
  - PATH
  - HOME
  - USER

# Commands that are always blocked
blocked_commands:
  - pattern: "sudo "
    description: "Superuser commands"
  - pattern: "^rm\\s+-rf\\s+/"
    description: "Recursive delete root"
    is_regex: true

# Commands that are allowed
allowed_commands:
  - pattern: "ls"
    description: "List directory"
  - pattern: "git status"
    description: "Git status"
```

### Adding Custom Commands

To allow additional commands, add them to `allowed_commands`:

```yaml
allowed_commands:
  # Simple prefix match
  - pattern: "kubectl get"
    description: "Kubectl get operations"

  # Regex pattern
  - pattern: "^make\\s+(build|test|clean)$"
    description: "Make targets"
    is_regex: true
```

## Available Tools

The MCP server exposes these tools to Claude:

| Tool | Description |
|------|-------------|
| `execute_command` | Execute a terminal command |
| `change_directory` | Change working directory |
| `get_current_directory` | Get current working directory |
| `approve_command` | Approve a command (in `ask` mode) |
| `get_permission_status` | View current permission settings |
| `set_permission_mode` | Change permission mode |

## Usage Examples

Once configured, you can ask Claude to:

- "Show me the files in my project directory"
- "What's the git status of this repository?"
- "Find all Python files modified in the last week"
- "Show me the disk usage of my home directory"
- "List running Docker containers"

## Command-Line Options

```
usage: host-terminal-mcp [-h] [--config CONFIG] [--init-config]
                         [--mode {allowlist,ask,allow_all}]
                         [--allow-dir ALLOWED_DIRS]

Host Terminal MCP Server

options:
  -h, --help            show this help message and exit
  --config, -c CONFIG   Path to configuration file
  --init-config         Create default configuration file and exit
  --mode {allowlist,ask,allow_all}
                        Override permission mode for this session
  --allow-dir ALLOWED_DIRS
                        Add allowed directory (can be used multiple times)
```

## Security Considerations

### Permission Modes

1. **`allowlist` (Default)**: Safest option. Only commands matching patterns in `allowed_commands` can execute. Recommended for production use.

2. **`ask`**: Commands not in the allow list prompt for approval. Approved commands are remembered for the session only.

3. **`allow_all`**: **DANGEROUS**. All commands execute without restriction. Only use in isolated/sandboxed environments.

### Default Protections

- **Blocked commands**: Dangerous patterns (like `rm -rf /`, `sudo`, `mkfs`) are always blocked regardless of permission mode.
- **Directory restrictions**: Commands only execute within allowed directories.
- **Timeouts**: Commands are killed after the configured timeout.
- **Output limits**: Large outputs are truncated to prevent memory issues.

### Best Practices

1. **Review the config**: Always review `config.yaml` before using.
2. **Start with `allowlist`**: Begin with the default mode and add commands as needed.
3. **Use specific patterns**: Prefer specific command patterns over broad ones.
4. **Restrict directories**: Only allow necessary directories.
5. **Audit regularly**: Periodically review approved commands and configuration.

---

## Disclaimer

**IMPORTANT: PLEASE READ THIS DISCLAIMER CAREFULLY BEFORE USING THIS SOFTWARE.**

### No Warranty

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS, COPYRIGHT HOLDERS, OR CONTRIBUTORS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Use at Your Own Risk

This software executes commands directly on your computer's operating system. By using this software, you acknowledge and agree that:

1. **You are solely responsible** for any commands executed through this tool and their consequences.

2. **The authors and contributors are not liable** for any damage, data loss, security breaches, or other harm that may result from using this software.

3. **AI systems can make mistakes**. Commands suggested or executed by AI assistants may not always be appropriate, safe, or correct for your specific situation.

4. **Security configurations may be insufficient**. While this tool includes permission controls, no security system is perfect. Malicious or malformed inputs could potentially bypass protections.

5. **You should never use this tool** on production systems, systems containing sensitive data, or systems where unauthorized access could cause harm without taking appropriate precautions.

### Not for Production Use Without Review

This software is intended for development and personal use. If you intend to deploy it in a production environment:

- Conduct a thorough security review
- Implement additional access controls
- Consider running in a sandboxed environment
- Maintain audit logs
- Have incident response procedures in place

### No Professional Advice

This software does not constitute professional security, legal, or technical advice. Consult with qualified professionals before using this tool in any context where security or compliance is critical.

### Indemnification

By using this software, you agree to indemnify and hold harmless the authors, contributors, and any affiliated parties from any claims, damages, losses, or expenses arising from your use of the software.

### Jurisdiction

This disclaimer shall be governed by and construed in accordance with applicable laws. If any provision is found to be unenforceable, the remaining provisions shall continue in full force and effect.

---

## License

MIT License

Copyright (c) 2025 Ankit

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Clone and install in dev mode
git clone https://github.com/yourusername/host-terminal-mcp.git
cd host-terminal-mcp
pip install -e ".[dev]"

# Run tests
pytest
```

---

## Acknowledgments

- Built on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Designed for use with [Claude](https://claude.ai) by Anthropic

---

## Support

- **Issues**: Please report bugs and feature requests on GitHub Issues
- **Discussions**: For questions and general discussion, use GitHub Discussions

---

**Remember**: With great power comes great responsibility. Always review commands before execution and maintain appropriate security practices.
