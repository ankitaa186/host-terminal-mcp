---
name: codebase-explorer
description: "Expertise in exploring, understanding, and navigating codebases. Use when asked to explore a project, understand architecture, find files, or analyze code structure."
---

# Codebase Explorer

Expert guidance for exploring and understanding codebases.

## Exploration Strategy

### Phase 1: High-Level Structure
```bash
# Get directory tree (limit depth)
tree -L 2 -d

# List top-level contents
ls -la

# Check for documentation
ls README* CONTRIBUTING* docs/ doc/
```

### Phase 2: Project Detection
```bash
# Identify project type by manifest files
ls package.json pyproject.toml Cargo.toml go.mod pom.xml build.gradle Gemfile
```

### Phase 3: Deep Dive
```bash
# Entry points
cat main.py src/index.js cmd/main.go

# Configuration
cat config/*.yaml .env.example

# Dependencies
cat package.json requirements.txt Cargo.toml
```

## Project Type Detection

| File | Project Type | Next Steps |
|------|-------------|------------|
| `package.json` | Node.js | Check `scripts`, `dependencies` |
| `pyproject.toml` | Python (modern) | Check `[project]`, `[tool.*]` |
| `requirements.txt` | Python (legacy) | Check dependencies |
| `Cargo.toml` | Rust | Check `[package]`, `[dependencies]` |
| `go.mod` | Go | Check module path, dependencies |
| `pom.xml` | Java (Maven) | Check `<dependencies>` |
| `build.gradle` | Java (Gradle) | Check `dependencies` block |
| `Gemfile` | Ruby | Check gems |
| `composer.json` | PHP | Check `require` |
| `Makefile` | C/C++/Generic | Check targets |

## Finding Key Components

### Entry Points
```bash
# Common entry point names
find . -name "main.*" -o -name "index.*" -o -name "app.*" | head -20

# Scripts directory
ls bin/ scripts/ cmd/
```

### Configuration
```bash
# Config files
find . -name "*.config.*" -o -name "*.yaml" -o -name "*.toml" | grep -v node_modules
```

### Tests
```bash
# Test directories and files
find . -type d -name "test*" -o -type d -name "__tests__"
find . -name "*test*.py" -o -name "*.test.js" -o -name "*_test.go"
```

### API/Routes
```bash
# Common API patterns
grep -r "app\.\(get\|post\|put\|delete\)" --include="*.js" --include="*.ts"
grep -r "@app\.route\|@router" --include="*.py"
grep -r "func.*Handler\|http\.Handle" --include="*.go"
```

## Code Search Patterns

### Find Function Definitions
```bash
# Python
grep -rn "^def \|^async def \|^class " --include="*.py"

# JavaScript/TypeScript
grep -rn "function \|const .* = \|class " --include="*.js" --include="*.ts"

# Go
grep -rn "^func " --include="*.go"
```

### Find Imports/Dependencies
```bash
# Python
grep -rn "^import \|^from .* import" --include="*.py"

# JavaScript
grep -rn "^import \|require(" --include="*.js" --include="*.ts"

# Go
grep -rn "^import" --include="*.go"
```

### Find TODO/FIXME
```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.py" --include="*.js" --include="*.go"
```

## Architecture Analysis

### Dependency Graph
```bash
# NPM
npm ls --depth=0

# Python
pip list

# Cargo
cargo tree --depth=1
```

### Code Statistics
```bash
# Lines of code by type
find . -name "*.py" | xargs wc -l | tail -1
find . -name "*.js" -not -path "*/node_modules/*" | xargs wc -l | tail -1

# File counts
find . -name "*.py" | wc -l
```

## Output Template

When exploring a codebase, structure findings as:

```
📁 Project: {name}
📋 Type: {language} ({framework})
📦 Package Manager: {manager}

## Structure
{tree output, annotated}

## Key Files
- {file}: {purpose}
- {file}: {purpose}

## Dependencies
{key dependencies with versions}

## Entry Points
- {main entry point}
- {API entry if applicable}

## Architecture Notes
{observations about patterns, structure}
```

## Tips

1. **Start broad, go deep** - Tree first, then specific files
2. **Follow imports** - Trace from entry point
3. **Read tests** - They document expected behavior
4. **Check CI/CD** - `.github/workflows/`, `.gitlab-ci.yml` reveal build process
5. **Look for docs** - `docs/`, `doc/`, wiki, README sections
