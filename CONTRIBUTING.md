# Contributing to Host Terminal MCP

Thanks for your interest in contributing! This guide will help you get started.

## Development Setup

```bash
git clone git@github.com:ankitaa186/host-terminal-mcp.git
cd host-terminal-mcp
make install    # creates venv and installs all dependencies
```

This uses [uv](https://docs.astral.sh/uv/) under the hood. The virtual environment is created in `.venv/`.

## Running Tests and Linting

```bash
make test           # run tests
make test-verbose   # verbose output
make test-cov       # with coverage report
make lint           # ruff + mypy
make format         # auto-format with ruff
```

All checks must pass before a PR can be merged.

## Code Style

- Code is formatted and linted with [Ruff](https://docs.astral.sh/ruff/).
- Type hints are checked with [mypy](https://mypy-lang.org/).
- CI enforces both on every pull request.

## Submitting a Pull Request

1. Fork the repository and create a branch from `main`.
2. Make your changes.
3. Add or update tests if applicable.
4. Run `make lint` and `make test` to verify everything passes.
5. Open a pull request against `main`.

Please keep PRs focused on a single change. If you're fixing a bug and adding a feature, open separate PRs.

## Reporting Issues

Open an issue on GitHub with:

- What you expected to happen
- What actually happened
- Steps to reproduce (if applicable)
- Your OS and Python version

## License

By contributing, you agree that your contributions will be licensed under the [Apache 2.0 License](LICENSE).
