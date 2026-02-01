---
name: git
description: "Run git commands to check repository status, history, and changes"
argument-hint: "<git subcommand and options>"
examples:
  - "/git status"
  - "/git log --oneline -10"
  - "/git diff HEAD~1"
  - "/git branch -a"
---

# Git Repository Operations

Interact with git repositories using read-only git commands.

## Workflow

1. **Verify** we're in a git repository
2. **Parse** the git subcommand from user input
3. **Execute** the git command via `~~terminal`
4. **Format** and present the results

## Allowed Git Commands

The following git operations are pre-approved by default:

| Command | Description |
|---------|-------------|
| `git status` | Working tree status |
| `git log` | Commit history |
| `git diff` | Show changes |
| `git show` | Show commit details |
| `git branch` | List branches |
| `git remote` | List remotes |
| `git tag` | List tags |
| `git stash list` | List stashes |
| `git blame` | Line-by-line authorship |
| `git shortlog` | Summarize commits |
| `git describe` | Describe commit |
| `git config --get` | Read config values |
| `git config --list` | List all config |
| `git rev-parse` | Parse revisions |

## Usage Examples

### Check status
```
/git status
```

### View recent commits
```
/git log --oneline -10
```

### See what changed
```
/git diff
/git diff HEAD~1
/git diff --staged
```

### List branches
```
/git branch -a
```

### Show commit details
```
/git show HEAD
/git show abc1234
```

### Find who changed a line
```
/git blame src/main.py
```

## Write Operations

Git write operations (`commit`, `push`, `pull`, `merge`, `rebase`, etc.) are **not** in the default allowlist. To enable them:

1. Switch to `ask` mode and approve individually
2. Or add them to your `config.yaml` allowlist

## Tips

- Use `--oneline` with `git log` for concise output
- Use `-n <number>` to limit results
- Combine with grep: `/shell git log --oneline | grep "fix"`
