#!/usr/bin/env python3
"""Package the host-terminal plugin for distribution."""

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Files/directories to include in the plugin
INCLUDE = [
    ".claude-plugin/",
    ".mcp.json",
    "commands/",
    "skills/",
    "config/",
    "src/",
    "tests/",
    "CONNECTORS.md",
    "LICENSE",
    "Makefile",
    "pyproject.toml",
    "README.md",
    ".gitignore",
]

# Files/directories to exclude
EXCLUDE = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".git",
    ".venv",
    "venv",
    "dist",
    "build",
    "*.egg-info",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".coverage",
    "htmlcov",
    "*.plugin",
]


def get_plugin_info(project_root: Path) -> dict:
    """Read plugin metadata."""
    plugin_json = project_root / ".claude-plugin" / "plugin.json"
    with open(plugin_json) as f:
        return json.load(f)


def should_exclude(path: Path, exclude_patterns: list[str]) -> bool:
    """Check if path matches any exclude pattern."""
    name = path.name
    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def package_plugin(project_root: Path, output_dir: Path) -> Path:
    """Create a .plugin package."""
    info = get_plugin_info(project_root)
    plugin_name = info["name"]
    version = info["version"]

    # Output filename
    output_file = output_dir / f"{plugin_name}-{version}.plugin"

    print(f"📦 Packaging {plugin_name} v{version}...")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create zip file
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in INCLUDE:
            item_path = project_root / item

            if not item_path.exists():
                print(f"  ⚠️  Skipping (not found): {item}")
                continue

            if item_path.is_file():
                if not should_exclude(item_path, EXCLUDE):
                    arcname = item
                    zf.write(item_path, arcname)
                    print(f"  ✅ Added: {item}")
            elif item_path.is_dir():
                for root, dirs, files in os.walk(item_path):
                    # Filter out excluded directories
                    dirs[:] = [d for d in dirs if not should_exclude(Path(d), EXCLUDE)]

                    for file in files:
                        file_path = Path(root) / file
                        if not should_exclude(file_path, EXCLUDE):
                            arcname = str(file_path.relative_to(project_root))
                            zf.write(file_path, arcname)

                file_count = sum(1 for _ in item_path.rglob("*") if _.is_file())
                print(f"  ✅ Added: {item} ({file_count} files)")

    print(f"\n✅ Created: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")

    return output_file


def build_wheel(project_root: Path) -> Path | None:
    """Build the Python wheel."""
    print("\n🔨 Building Python wheel...")

    try:
        result = subprocess.run(
            ["uv", "build"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"  ❌ Build failed: {result.stderr}")
            return None

        # Find the wheel file
        dist_dir = project_root / "dist"
        wheels = list(dist_dir.glob("*.whl"))

        if wheels:
            wheel = wheels[0]
            print(f"  ✅ Built: {wheel.name}")
            return wheel

    except FileNotFoundError:
        print("  ⚠️  uv not found, trying pip...")

        try:
            subprocess.run(
                [sys.executable, "-m", "build"],
                cwd=project_root,
                check=True,
            )
            dist_dir = project_root / "dist"
            wheels = list(dist_dir.glob("*.whl"))
            if wheels:
                return wheels[0]
        except Exception as e:
            print(f"  ❌ Build failed: {e}")

    return None


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Package host-terminal plugin")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("dist"),
        help="Output directory (default: dist/)",
    )
    parser.add_argument(
        "--no-wheel",
        action="store_true",
        help="Skip building Python wheel",
    )

    args = parser.parse_args()

    # Find project root
    project_root = Path(__file__).parent.parent

    print("=" * 50)
    print("Host Terminal Plugin Packager")
    print("=" * 50)

    # Build wheel first (needed for installation)
    if not args.no_wheel:
        wheel = build_wheel(project_root)
        if wheel:
            # Copy wheel into plugin package location
            pass  # Wheel stays in dist/

    # Package the plugin
    plugin_file = package_plugin(project_root, args.output)

    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("=" * 50)
    print(f"""
1. Install locally:
   unzip {plugin_file} -d ~/.claude/cowork_plugins/host-terminal
   cd ~/.claude/cowork_plugins/host-terminal
   make install

2. Publish to GitHub:
   git tag v{get_plugin_info(project_root)['version']}
   git push origin --tags
   # Create a GitHub Release and attach {plugin_file.name}

3. Publish to PyPI (MCP server only):
   uv publish
   # or: twine upload dist/*
""")


if __name__ == "__main__":
    main()
