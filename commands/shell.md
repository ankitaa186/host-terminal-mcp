---
name: shell
description: "Execute a shell command on the host machine"
argument-hint: "<command to execute>"
examples:
  - "/shell ls -la"
  - "/shell git status"
  - "/shell find . -name '*.py' -type f"
---

# Shell Command Execution

Execute terminal commands on the host machine with permission controls.

## Workflow

1. **Parse the command** from user input
2. **Check permissions** against the configured allowlist
3. **Execute** if allowed, or request approval if in "ask" mode
4. **Return results** with stdout, stderr, and exit code

## Usage

```
/shell <command>
```

## Examples

### List files
```
/shell ls -la ~/projects
```

### Check git status
```
/shell git status
```

### Search for files
```
/shell find . -name "*.js" -type f | head -20
```

### View file contents
```
/shell cat package.json
```

## Permission Handling

Commands are checked against the permission configuration:

- **Allowed commands**: Execute immediately
- **Blocked commands**: Always rejected (e.g., `sudo`, `rm -rf /`)
- **Unknown commands**:
  - In `allowlist` mode: Rejected
  - In `ask` mode: Prompt for approval
  - In `allow_all` mode: Execute (use with caution!)

## Safety Notes

- Commands run in the configured allowed directories only
- Output is truncated if too large
- Commands timeout after the configured limit
- Dangerous commands are always blocked regardless of mode
