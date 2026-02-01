#!/usr/bin/env python3
"""
Setup script for creating a GitHub-based plugin marketplace.

This creates the necessary structure for hosting your own Cowork plugin marketplace
that users can add via the Claude Desktop UI.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_plugin_info(project_root: Path) -> dict:
    """Read plugin metadata."""
    plugin_json = project_root / ".claude-plugin" / "plugin.json"
    with open(plugin_json) as f:
        return json.load(f)


def create_marketplace_repo(project_root: Path, output_dir: Path, repo_name: str = None):
    """Create a marketplace repository structure."""

    info = get_plugin_info(project_root)
    plugin_name = info["name"]

    if repo_name is None:
        repo_name = f"{plugin_name}-marketplace"

    marketplace_dir = output_dir / repo_name
    plugin_dir = marketplace_dir / plugin_name

    print(f"📦 Creating marketplace: {repo_name}")
    print(f"   Location: {marketplace_dir}")

    # Create directories
    marketplace_dir.mkdir(parents=True, exist_ok=True)
    (marketplace_dir / ".claude-plugin").mkdir(exist_ok=True)

    # Create marketplace manifest
    marketplace_manifest = {
        "name": repo_name,
        "owner": info.get("author", {"name": "Unknown"}),
        "description": f"Marketplace for {plugin_name} and related plugins",
        "plugins": [
            {
                "name": plugin_name,
                "source": f"./{plugin_name}",
                "description": info["description"]
            }
        ]
    }

    with open(marketplace_dir / ".claude-plugin" / "marketplace.json", "w") as f:
        json.dump(marketplace_manifest, f, indent=2)

    # Copy plugin to marketplace
    print(f"   Copying plugin: {plugin_name}")

    # Items to copy
    items_to_copy = [
        ".claude-plugin/plugin.json",
        ".mcp.json",
        "commands",
        "skills",
        "CONNECTORS.md",
        "README.md",
        "LICENSE",
    ]

    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / ".claude-plugin").mkdir(exist_ok=True)

    for item in items_to_copy:
        src = project_root / item
        dst = plugin_dir / item

        if src.exists():
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            print(f"   ✅ {item}")
        else:
            print(f"   ⚠️  {item} (not found)")

    # Create marketplace README
    readme_content = f"""# {repo_name}

A Claude Cowork plugin marketplace.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [{plugin_name}](./{plugin_name}) | {info['description'][:80]}... |

## Installation

### Via Claude Desktop UI

1. Open Claude Desktop
2. Go to Settings → Plugins → Add Marketplace
3. Enter: `github:{info.get('author', {}).get('name', 'username')}/{repo_name}`
4. Browse and install plugins

### Via CLI

```bash
claude plugins add {info.get('author', {}).get('name', 'username')}/{repo_name}/{plugin_name}
```

## Requirements

- Python 3.10+
- The `host-terminal-mcp` package must be installed:

```bash
pip install host-terminal-mcp
# or
uv tool install host-terminal-mcp
```

## License

Apache-2.0
"""

    with open(marketplace_dir / "README.md", "w") as f:
        f.write(readme_content)

    # Create .gitignore
    gitignore_content = """# OS
.DS_Store
Thumbs.db

# IDE
.idea/
.vscode/
*.swp

# Python
__pycache__/
*.pyc
.venv/
"""

    with open(marketplace_dir / ".gitignore", "w") as f:
        f.write(gitignore_content)

    print(f"\n✅ Marketplace created: {marketplace_dir}")

    return marketplace_dir


def init_git_repo(marketplace_dir: Path):
    """Initialize git repository."""
    print("\n📂 Initializing git repository...")

    subprocess.run(["git", "init"], cwd=marketplace_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=marketplace_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial marketplace setup"],
        cwd=marketplace_dir,
        check=True
    )

    print("   ✅ Git repository initialized")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup a GitHub marketplace for your Cowork plugin"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path.home() / "cowork-marketplaces",
        help="Output directory for marketplace (default: ~/cowork-marketplaces)"
    )
    parser.add_argument(
        "--name", "-n",
        type=str,
        default=None,
        help="Marketplace repository name (default: <plugin>-marketplace)"
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Don't initialize git repository"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    print("=" * 50)
    print("Cowork Plugin Marketplace Setup")
    print("=" * 50)

    # Create marketplace structure
    marketplace_dir = create_marketplace_repo(
        project_root,
        args.output,
        args.name
    )

    # Initialize git
    if not args.no_git:
        init_git_repo(marketplace_dir)

    # Print next steps
    info = get_plugin_info(project_root)

    print("\n" + "=" * 50)
    print("📋 Next Steps")
    print("=" * 50)
    print(f"""
1. Create a GitHub repository:
   gh repo create {args.name or info['name'] + '-marketplace'} --public --source={marketplace_dir} --push

2. Users can then add your marketplace:
   - Claude Desktop → Settings → Plugins → Add Marketplace
   - Enter: github:<your-username>/{args.name or info['name'] + '-marketplace'}

3. Or install directly via CLI:
   claude plugins add <your-username>/{args.name or info['name'] + '-marketplace'}/{info['name']}

⚠️  IMPORTANT: Users must also install the MCP server:
   pip install host-terminal-mcp
   # or: uv tool install host-terminal-mcp
""")


if __name__ == "__main__":
    main()
