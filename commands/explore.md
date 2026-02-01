---
name: explore
description: "Explore a codebase or directory structure"
argument-hint: "<path or search query>"
examples:
  - "/explore ~/projects/myapp"
  - "/explore find all Python files"
  - "/explore what's the structure of this project"
---

# Codebase Exploration

Explore and understand codebases, directory structures, and file contents.

## Workflow

1. **Identify target** - directory path or search criteria
2. **Gather structure** - list files, directories, key patterns
3. **Analyze contents** - read important files (README, configs, entry points)
4. **Summarize findings** - present organized overview

## Usage

```
/explore <path>
/explore <natural language query>
```

## Exploration Commands Used

This command orchestrates multiple `~~terminal` operations:

| Operation | Command |
|-----------|---------|
| Directory listing | `ls -la <path>` |
| Tree structure | `tree -L 3 <path>` |
| Find files | `find <path> -name "<pattern>"` |
| File contents | `cat <file>` |
| Search content | `grep -r "<pattern>" <path>` |
| File info | `file <path>`, `wc -l <file>` |

## Examples

### Explore a project
```
/explore ~/projects/myapp
```
Returns: directory structure, key files, project type detection

### Find specific files
```
/explore find all test files
```
Executes: `find . -name "*test*.py" -o -name "*_test.go" -o -name "*.test.js"`

### Understand project structure
```
/explore what's the architecture of this codebase
```
Analyzes: README, package.json/pyproject.toml, src/ structure, entry points

### Search for patterns
```
/explore where is authentication handled
```
Searches: `grep -r "auth\|login\|session" --include="*.py"`

## Auto-Detection

The explore command automatically detects:

- **Project type**: Node.js, Python, Go, Rust, Java, etc.
- **Build system**: npm, pip, cargo, maven, gradle
- **Framework**: React, Django, FastAPI, Express, etc.
- **Key files**: Entry points, configs, tests, docs

## Output Format

```
📁 Project: myapp
📋 Type: Python (FastAPI)
📦 Dependencies: requirements.txt (23 packages)

Structure:
├── src/
│   ├── main.py (entry point)
│   ├── api/
│   ├── models/
│   └── utils/
├── tests/
├── docs/
└── config/

Key Files:
- README.md: Project documentation
- pyproject.toml: Build configuration
- src/main.py: FastAPI application entry
```
