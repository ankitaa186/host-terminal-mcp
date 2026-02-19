# Host Terminal MCP

[![PyPI](https://img.shields.io/pypi/v/host-terminal-mcp)](https://pypi.org/project/host-terminal-mcp/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

An [MCP](https://modelcontextprotocol.io) server that lets AI assistants run terminal commands on your machine with permission controls. Built for **Claude Desktop / Co-work** and any MCP-compatible client.

## How It Works

```
You (in Co-work)                      Your Mac
─────────────────                     ─────────
"run git status"
      │
      ▼
Claude (cloud)
      │  MCP tool call:
      │  execute_command("git status")
      ▼
Claude Desktop (local)
      │  forwards via stdio pipe
      ▼
host-terminal-mcp                     ◄── this project
      │  1. permission check ✅
      │  2. /bin/bash -c "git status"
      ▼
Terminal output flows back up the chain
```

Claude Desktop spawns `host-terminal-mcp` as a child process and communicates over stdin/stdout using the MCP protocol. There is no network server involved — it's a local pipe.

## Setup for Co-work

### 1. Install

```bash
uv tool install host-terminal-mcp
```

Or with pip:

```bash
pip install host-terminal-mcp
```

### 2. Configure Claude Desktop

Add the MCP server to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

> **Important:** Claude Desktop runs with a minimal PATH (`/usr/local/bin`, `/usr/bin`, `/bin`, `/usr/sbin`, `/sbin`, `/opt/homebrew/bin`). If you installed with `uv tool install` or `pip install --user`, the binary is likely in `~/.local/bin/` which is **not** in Claude Desktop's PATH. Use the **full absolute path** to the binary to avoid "No such file or directory" errors.

Find your binary path:

```bash
which host-terminal-mcp
# Example output: /Users/you/.local/bin/host-terminal-mcp
```

Then use that path in the config:

```json
{
  "mcpServers": {
    "host-terminal": {
      "command": "/Users/you/.local/bin/host-terminal-mcp"
    }
  }
}
```

To start in `ask` mode (recommended — prompts you before running unlisted commands):

```json
{
  "mcpServers": {
    "host-terminal": {
      "command": "/Users/you/.local/bin/host-terminal-mcp",
      "args": ["--mode", "ask"]
    }
  }
}
```

> **Tip:** If you installed globally to a system path (e.g. `/usr/local/bin/host-terminal-mcp`), you can use just `"command": "host-terminal-mcp"` without the full path.

### 3. Restart Claude Desktop

Quit and reopen Claude Desktop. It will automatically spawn the `host-terminal-mcp` process. You can verify it's running:

```bash
ps aux | grep host-terminal-mcp
```

### 4. Use it

Open a Co-work session in Claude.ai (or use Claude Desktop directly) and ask:

- "List files in my home directory"
- "Show git status in ~/projects/myapp"
- "What's running on port 3000?"
- "Run the tests for this project"

## Permission Modes

| Mode | Behavior | Safety |
|------|----------|--------|
| `allowlist` (default) | Only pre-approved read-only commands run | Safest |
| `ask` | Prompts **you** for approval on unlisted commands | Recommended for power users |
| `allow_all` | Everything runs except blocked commands | Dangerous |

### How `ask` Mode Works

When Claude tries to run a command not in the allow list, the server uses [MCP elicitation](https://modelcontextprotocol.io/specification/draft/client/elicitation) to prompt **you** (the human) directly in the Claude Desktop UI:

```
┌─────────────────────────────────────────────┐
│ The AI wants to run a command that is not   │
│ in the allow list:                          │
│                                             │
│   npm install                               │
│                                             │
│ Do you approve?                             │
│                                             │
│ [✓] Approve this command?                   │
│ [✓] Add to allowed list permanently?        │
│                                             │
│         [ Cancel ]  [ Submit ]              │
└─────────────────────────────────────────────┘
```

- **Approve** — runs the command for this session
- **Add to allowed list permanently** — saves the command to your config file so you're never asked again
- **Cancel/Decline** — command is blocked

This is a real human-in-the-loop: Claude cannot approve commands on its own.

> **Note:** Elicitation requires MCP client support. If your client doesn't support it, unlisted commands are rejected with a message telling you to add them to the config file.

Permission check order: **blocked** (always wins) > **allowed** > **session-approved** > **mode decision**

## Default Allowed Commands

These commands (and their arguments) are allowed out of the box:

**File listing & navigation:**
`ls`, `ll`, `la`, `pwd`, `tree`, `find`, `locate`, `which`, `whereis`, `file`

**File viewing:**
`cat`, `head`, `tail`, `less`, `more`, `bat`, `wc`

**Search:**
`grep`, `rg`, `ag`, `ack`, `fzf`

**Git (read-only):**
`git status`, `git log`, `git diff`, `git show`, `git branch`, `git remote`, `git tag`, `git stash list`, `git rev-parse`, `git config --get`, `git config --list`, `git blame`, `git shortlog`, `git describe`

**System info:**
`uname`, `hostname`, `whoami`, `id`, `date`, `uptime`, `df`, `du`, `free`, `top -l 1`, `ps`

**Network (read-only):**
`ping -c`, `curl -I`, `curl --head`, `dig`, `nslookup`, `host`, `ifconfig`, `ip addr`, `netstat`, `ss`

**Package managers (info only):**
`npm list`, `npm ls`, `npm view`, `npm show`, `npm outdated`, `pip list`, `pip show`, `pip freeze`, `brew list`, `brew info`, `apt list`, `dpkg -l`

**Dev tool versions:**
`python --version`, `python3 --version`, `node --version`, `npm --version`, `cargo --version`, `rustc --version`, `go version`, `java --version`, `javac --version`, `ruby --version`, `docker --version`

**Docker (read-only):**
`docker ps`, `docker images`, `docker logs`

**Data processing:**
`jq`, `yq`

**Misc:**
`man`, `help`, `type`, `stat`, `md5sum`, `sha256sum`, `shasum`

## Always Blocked Commands

These are blocked regardless of permission mode:

| Pattern | Reason |
|---------|--------|
| `rm -rf /`, `rm -rf ~`, `rm -rf *` | Recursive delete |
| `mkfs`, `dd` | Format/overwrite disk |
| `find ... -exec` | Arbitrary command execution |
| `:(){` | Fork bomb |
| `> /dev/sd*` | Overwrite disk device |
| `chmod -R 777 /`, `chown -R` | Dangerous permission changes |
| `sudo`, `su`, `doas` | Privilege escalation |
| `reboot`, `shutdown`, `halt`, `poweroff` | System control |
| `kill`, `killall`, `pkill` | Process control |
| `nc -l`, `nmap` | Network attacks |
| `*/.ssh/`, `*/.aws/`, `*/.gnupg/` | Sensitive credential access |
| `/etc/shadow`, `/etc/passwd` | System file access |
| `history -c`, `shred` | History/credential wiping |

## Configuration

Config file: `~/.config/host-terminal-mcp/config.yaml`

```bash
# Generate a default config file
host-terminal-mcp --init-config
```

### Add custom allowed commands

```yaml
allowed_commands:
  - pattern: "docker compose logs"
    description: "Docker Compose service logs"
  - pattern: "docker compose ps"
    description: "Docker Compose service status"
  - pattern: "npm install"
    description: "Install npm packages"

  # Use regex for flexible matching
  - pattern: "^kubectl get "
    description: "Kubernetes get resources"
    is_regex: true
```

### Other options

```yaml
permission_mode: allowlist          # allowlist | ask | allow_all
timeout_seconds: 300                # Max command execution time
max_output_size: 100000             # Max output chars (truncated beyond this)
shell: /bin/bash                    # Shell to use
allowed_directories:                # Commands restricted to these dirs
  - /Users/me
environment_passthrough:            # Env vars passed to commands
  - PATH
  - HOME
  - USER
  - LANG
  - LC_ALL
```

## HTTP Transport

For external services (e.g. a chatbot in Docker) that need to call your machine over the network:

```bash
# Install with HTTP extras
uv tool install 'host-terminal-mcp[http]'

# Start
host-terminal-mcp --http --port 8099

# Or in background
nohup host-terminal-mcp --http --port 8099 --mode ask > /tmp/host-terminal-mcp.log 2>&1 &
```

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/execute` | POST | Run a command |
| `/cd` | POST | Change working directory |
| `/cwd` | GET | Get current directory |
| `/permissions` | GET | Get permission config |

### Example

```bash
curl -X POST http://localhost:8099/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "docker compose ps", "working_directory": "/path/to/project"}'
```

## Architecture

```
src/host_terminal_mcp/
├── server.py        ← MCP stdio server, tool handlers, elicitation
├── http_server.py   ← Alternative HTTP/REST transport (FastAPI)
├── config.py        ← Permission rules, allowlist/blocklist, YAML config
└── executor.py      ← Runs commands via asyncio subprocess
```

**Tools exposed to the AI:**

| Tool | Description |
|------|-------------|
| `execute_command` | Run a shell command (main tool) |
| `change_directory` | Change working directory |
| `get_current_directory` | Get current working directory |
| `get_permission_status` | Inspect current permissions |
| `set_permission_mode` | Change permission mode |

## Development

```bash
git clone https://github.com/ankitag-in/host-terminal-mcp.git
cd host-terminal-mcp
make install        # Install all deps (venv auto-created)
make test           # Run tests
make lint           # Run linters
make format         # Format code
make run            # Run stdio server (foreground)
make run MODE=ask   # Run in ask mode
make inspect        # Test with MCP Inspector
make help           # Show all targets
```

### From source with Claude Desktop

```json
{
  "mcpServers": {
    "host-terminal": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/host-terminal-mcp", "host-terminal-mcp"]
    }
  }
}
```

## License

Apache-2.0
