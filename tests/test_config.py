"""Tests for configuration module."""

import pytest
from host_terminal_mcp.config import (
    CommandPattern,
    Config,
    PermissionMode,
    get_default_allowed_commands,
    get_default_blocked_commands,
)


class TestCommandPattern:
    """Tests for CommandPattern matching."""

    def test_simple_prefix_match(self):
        """Test simple prefix matching."""
        pattern = CommandPattern(pattern="ls", description="List files")
        assert pattern.matches("ls")
        assert pattern.matches("ls -la")
        assert pattern.matches("lsof")  # Also matches since it starts with "ls"
        assert not pattern.matches("echo ls")

    def test_prefix_with_space(self):
        """Test prefix with trailing space."""
        pattern = CommandPattern(pattern="git status", description="Git status")
        assert pattern.matches("git status")
        assert pattern.matches("git status --short")
        assert not pattern.matches("git statusx")

    def test_regex_pattern(self):
        """Test regex pattern matching."""
        pattern = CommandPattern(
            pattern=r"^rm\s+-rf\s+/",
            description="Dangerous rm",
            is_regex=True
        )
        assert pattern.matches("rm -rf /")
        assert pattern.matches("rm -rf /home")
        assert not pattern.matches("rm file.txt")
        assert not pattern.matches("rm -r /")

    def test_invalid_regex(self):
        """Test invalid regex doesn't crash."""
        pattern = CommandPattern(
            pattern=r"[invalid",
            description="Invalid regex",
            is_regex=True
        )
        assert not pattern.matches("anything")


class TestConfig:
    """Tests for Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.permission_mode == PermissionMode.ALLOWLIST
        assert config.timeout_seconds == 300
        assert config.max_output_size == 100000

    def test_allowed_command(self):
        """Test command allow check."""
        config = Config(
            allowed_commands=[
                CommandPattern(pattern="ls", description="List"),
                CommandPattern(pattern="pwd", description="Working dir"),
            ]
        )

        allowed, reason = config.is_command_allowed("ls -la")
        assert allowed
        assert "List" in reason

    def test_blocked_command_takes_precedence(self):
        """Test blocked commands take precedence over allowed."""
        config = Config(
            allowed_commands=[
                CommandPattern(pattern="rm", description="Remove"),
            ],
            blocked_commands=[
                CommandPattern(
                    pattern=r"^rm\s+-rf",
                    description="Dangerous rm",
                    is_regex=True
                ),
            ]
        )

        # Regular rm should be allowed
        allowed, reason = config.is_command_allowed("rm file.txt")
        assert allowed

        # rm -rf should be blocked
        allowed, reason = config.is_command_allowed("rm -rf /")
        assert not allowed
        assert "blocked" in reason.lower()

    def test_ask_mode(self):
        """Test ask permission mode."""
        config = Config(
            permission_mode=PermissionMode.ASK,
            allowed_commands=[
                CommandPattern(pattern="ls", description="List"),
            ]
        )

        # Allowed command works
        allowed, reason = config.is_command_allowed("ls")
        assert allowed

        # Unknown command needs approval
        allowed, reason = config.is_command_allowed("curl example.com")
        assert not allowed
        assert reason == "NEEDS_APPROVAL"

    def test_allow_all_mode(self):
        """Test allow_all permission mode."""
        config = Config(permission_mode=PermissionMode.ALLOW_ALL)

        allowed, reason = config.is_command_allowed("any command")
        assert allowed
        assert "allow_all" in reason.lower()

    def test_session_approval(self):
        """Test session command approval."""
        config = Config(
            permission_mode=PermissionMode.ASK,
            allowed_commands=[]
        )

        # Command initially needs approval
        allowed, reason = config.is_command_allowed("custom-cmd")
        assert not allowed

        # Approve for session
        config.approve_command_for_session("custom-cmd")

        # Now it should be allowed
        allowed, reason = config.is_command_allowed("custom-cmd")
        assert allowed
        assert "session" in reason.lower()


class TestDefaultCommands:
    """Tests for default command lists."""

    def test_default_allowed_commands(self):
        """Test default allowed commands include common dev tools."""
        commands = get_default_allowed_commands()
        patterns = [c.pattern for c in commands]

        # Basic commands should be present
        assert "ls" in patterns
        assert "pwd" in patterns
        assert "cat " in patterns
        assert "git status" in patterns
        assert "grep " in patterns

    def test_default_blocked_commands(self):
        """Test default blocked commands include dangerous operations."""
        commands = get_default_blocked_commands()
        patterns = [c.pattern for c in commands]

        # Dangerous patterns should be blocked
        assert "sudo " in patterns
        assert "mkfs" in patterns
