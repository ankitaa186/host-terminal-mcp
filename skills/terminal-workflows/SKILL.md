---
name: terminal-workflows
description: "Expertise in terminal command execution, shell scripting patterns, and command-line workflows. Use when executing commands via ~~terminal, debugging command failures, or building shell pipelines."
---

# Terminal Workflows

Expert guidance for terminal command execution and shell workflows.

## Command Execution Patterns

### Safe Execution

Always prefer:
1. **Read operations first** - Understand before modifying
2. **Dry-run flags** - Use `--dry-run`, `-n` when available
3. **Confirmation prompts** - Add `-i` for interactive confirmation
4. **Limited scope** - Be specific, avoid wildcards when possible

### Command Chaining

```bash
# Sequential (stop on failure)
cmd1 && cmd2 && cmd3

# Sequential (continue on failure)
cmd1; cmd2; cmd3

# Conditional
cmd1 && cmd2 || cmd3  # cmd3 runs if cmd1 or cmd2 fails

# Pipeline
cmd1 | cmd2 | cmd3
```

### Output Handling

```bash
# Capture stdout
result=$(command)

# Redirect stderr to stdout
command 2>&1

# Discard output
command > /dev/null 2>&1

# Tee to file and stdout
command | tee output.log
```

## Common Workflows

### File Discovery
```bash
# Find by name
find . -name "*.py" -type f

# Find by content
grep -r "pattern" --include="*.js"

# Find recent files
find . -mtime -7 -type f

# Find large files
find . -size +100M -type f
```

### Text Processing
```bash
# Extract column
awk '{print $2}' file

# Filter lines
grep "pattern" file

# Replace text
sed 's/old/new/g' file

# Count occurrences
grep -c "pattern" file

# Sort and unique
sort file | uniq -c | sort -rn
```

### Process Management
```bash
# Find process
ps aux | grep "name"

# Kill by name
pkill -f "pattern"

# Background job
command &

# Check port usage
lsof -i :8080
```

## Error Handling

### Check Command Availability
```bash
command -v git > /dev/null || echo "git not installed"
which python3 || which python
```

### Handle Missing Files
```bash
[ -f file.txt ] && cat file.txt || echo "File not found"
```

### Timeout Protection
```bash
timeout 30 long_running_command
```

## Best Practices

1. **Quote variables**: `"$var"` not `$var`
2. **Use absolute paths** when possible
3. **Check exit codes**: `$?` after commands
4. **Limit output**: Use `head`, `tail`, or `| head -n 100`
5. **Avoid destructive commands** without confirmation

## Permission Escalation

If a command fails due to permissions in `allowlist` mode:

1. Check if command should be in allowlist
2. Use `/permissions mode ask` to enable prompting
3. Approve specific command with `/permissions approve <cmd>`
4. Or add to config for permanent access

## Platform Differences

| Operation | macOS | Linux |
|-----------|-------|-------|
| List open files | `lsof` | `lsof` |
| Process tree | `pstree` | `pstree` |
| Memory info | `top -l 1` | `free -h` |
| Disk usage | `df -h` | `df -h` |
| Network config | `ifconfig` | `ip addr` |
| Clipboard | `pbcopy`/`pbpaste` | `xclip` |
