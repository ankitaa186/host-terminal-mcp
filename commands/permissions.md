---
name: permissions
description: "View or change terminal permission settings"
argument-hint: "[status|mode <allowlist|ask|allow_all>|approve <command>]"
examples:
  - "/permissions status"
  - "/permissions mode ask"
  - "/permissions approve npm install"
---

# Permission Management

View and manage terminal command permissions.

## Workflow

1. **Parse action** from user input
2. **Execute** the appropriate permission tool
3. **Display** current status or confirm changes

## Usage

```
/permissions status              # View current settings
/permissions mode <mode>         # Change permission mode
/permissions approve <command>   # Approve a specific command
```

## Actions

### View Status
```
/permissions status
```

Shows:
- Current permission mode
- Allowed directories
- Number of allowed/blocked patterns
- Session-approved commands

### Change Mode
```
/permissions mode allowlist    # Only pre-approved commands (safest)
/permissions mode ask          # Prompt for unlisted commands
/permissions mode allow_all    # Allow everything (DANGEROUS!)
```

### Approve Command
```
/permissions approve npm install
```

Approves a specific command for the current session (when in `ask` mode).

## Permission Modes Explained

| Mode | Behavior | Risk Level |
|------|----------|------------|
| `allowlist` | Only commands in the allow list can run | 🟢 Safest |
| `ask` | Unknown commands prompt for approval | 🟡 Moderate |
| `allow_all` | All commands execute without checks | 🔴 Dangerous |

## Example Output

```
🔐 Terminal Permissions
━━━━━━━━━━━━━━━━━━━━━━

Mode:              allowlist
Allowed dirs:      ~, /tmp
Timeout:           300s
Max output:        100,000 chars

Patterns:
  ✅ Allowed:      73 patterns
  🚫 Blocked:      15 patterns

Session approved:
  - npm install
  - make build
```

## Security Notes

- **`allowlist`** is the default and recommended for production
- **`ask`** mode approvals are session-only (not persisted)
- **`allow_all`** should only be used in isolated/sandboxed environments
- Blocked commands (like `sudo`, `rm -rf /`) are **always** blocked regardless of mode
- Changes can optionally be persisted to config with `persist: true`

## Configuration File

For permanent changes, edit `~/.config/host-terminal-mcp/config.yaml`:

```yaml
permission_mode: ask

allowed_commands:
  - pattern: "npm install"
    description: "Install npm packages"
  - pattern: "make "
    description: "Run make targets"
```
