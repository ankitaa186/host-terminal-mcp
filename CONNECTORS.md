# Connector Mapping

This document maps tool-agnostic placeholders to concrete MCP servers.

## Tool Categories

| Category | Placeholder | Included Server | Alternatives |
|----------|-------------|-----------------|--------------|
| Terminal | `~~terminal` | host-terminal | SSH MCP, remote-shell |

## Placeholder Reference

### `~~terminal`

**Purpose**: Execute commands on the host machine's terminal/shell.

**Included MCP**: `host-terminal`

**Tools Provided**:

| Tool | Description |
|------|-------------|
| `execute_command` | Execute a shell command |
| `change_directory` | Change working directory |
| `get_current_directory` | Get current directory |
| `approve_command` | Approve command (in ask mode) |
| `get_permission_status` | View permission settings |
| `set_permission_mode` | Change permission mode |

**Alternative MCPs**:

- **SSH MCP**: For remote server access
- **Container MCP**: For Docker/Kubernetes execution
- **Cloud Shell MCP**: For cloud provider CLIs (AWS, GCP, Azure)

## Customization

To replace the terminal connector with an alternative:

1. Edit `.mcp.json`:
```json
{
  "mcpServers": {
    "host-terminal": {
      "command": "alternative-terminal-mcp",
      "args": ["--config", "/path/to/config"]
    }
  }
}
```

2. Ensure the alternative MCP provides compatible tools.

## Authentication

The `host-terminal` MCP runs locally and doesn't require authentication.

For remote alternatives, configure auth in `.mcp.json`:

```json
{
  "mcpServers": {
    "remote-terminal": {
      "type": "http",
      "url": "https://remote-mcp.example.com",
      "headers": {
        "Authorization": "Bearer ${REMOTE_TERMINAL_TOKEN}"
      }
    }
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST_TERMINAL_CONFIG` | Path to config file | `~/.config/host-terminal-mcp/config.yaml` |

## Integration with Other Plugins

Other plugins can reference `~~terminal` to use this connector:

```markdown
# In another plugin's command or skill:

To check the project status:
1. Use `~~terminal` to run `git status`
2. Use `~~terminal` to run `npm test`
```

This allows plugins to be terminal-agnostic—they work whether using local terminal, SSH, or containers.
