---
name: system-info
description: "Get information about the host system, environment, and installed tools"
argument-hint: "[category: all|os|tools|env|disk|network]"
examples:
  - "/system-info"
  - "/system-info tools"
  - "/system-info disk"
---

# System Information

Gather information about the host machine, development environment, and installed tools.

## Workflow

1. **Parse category** (or default to summary)
2. **Execute** relevant system commands via `~~terminal`
3. **Format** results in a readable format
4. **Present** organized system overview

## Usage

```
/system-info [category]
```

## Categories

### `all` or no argument - Overview
Quick summary of the system.

### `os` - Operating System
- OS name and version
- Kernel version
- Architecture
- Hostname
- Uptime

### `tools` - Development Tools
- Language versions (Python, Node, Go, Rust, Java, Ruby)
- Package managers (npm, pip, cargo, brew)
- Dev tools (git, docker, kubectl)

### `env` - Environment
- Shell and version
- Key environment variables
- PATH directories

### `disk` - Disk Usage
- Filesystem usage
- Home directory size
- Common directory sizes

### `network` - Network Info
- Network interfaces
- IP addresses
- DNS configuration

## Commands Used

| Category | Commands |
|----------|----------|
| OS | `uname -a`, `hostname`, `uptime` |
| Tools | `python --version`, `node --version`, `git --version`, etc. |
| Env | `echo $SHELL`, `env`, `echo $PATH` |
| Disk | `df -h`, `du -sh ~` |
| Network | `ifconfig`, `ip addr`, `cat /etc/resolv.conf` |

## Example Output

```
🖥️  System Information
━━━━━━━━━━━━━━━━━━━━━

OS:        macOS 14.2 (Darwin 23.2.0)
Arch:      arm64 (Apple Silicon)
Hostname:  MacBook-Pro.local
Uptime:    5 days, 3:42

💻 Development Tools
━━━━━━━━━━━━━━━━━━━━━
Python:    3.11.6
Node.js:   20.10.0
npm:       10.2.3
Git:       2.43.0
Docker:    24.0.7

💾 Disk Usage
━━━━━━━━━━━━━━━━━━━━━
/          456G / 1.0T (45%)
~ (home)   234G
```

## Use Cases

- **Debugging environment issues**: Check tool versions match requirements
- **Onboarding**: Understand what's available on a new machine
- **Troubleshooting**: Verify system resources and configurations
- **Documentation**: Generate environment specs for bug reports
