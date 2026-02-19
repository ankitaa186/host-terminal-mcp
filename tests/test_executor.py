"""Tests for command executor module."""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest

from host_terminal_mcp.config import Config
from host_terminal_mcp.executor import CommandExecutor


class TestCommandExecutor:
    """Tests for CommandExecutor class."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Config(
            allowed_directories=[str(Path.home()), "/tmp"],
            timeout_seconds=10,
            max_output_size=1000,
        )

    @pytest.fixture
    def executor(self, config):
        """Create a test executor."""
        return CommandExecutor(config)

    def test_initial_directory(self, executor):
        """Test initial working directory is home."""
        assert executor.current_directory == str(Path.home())

    def test_change_directory_success(self, executor):
        """Test changing to valid directory."""
        success, message = executor.change_directory("/tmp")
        assert success
        assert executor.current_directory == os.path.realpath("/tmp")

    def test_change_directory_nonexistent(self, executor):
        """Test changing to non-existent directory fails."""
        success, message = executor.change_directory("/nonexistent/path")
        assert not success
        assert "does not exist" in message

    def test_change_directory_not_allowed(self, executor):
        """Test changing to non-allowed directory fails."""
        success, message = executor.change_directory("/etc")
        assert not success
        assert "not in allowed" in message

    def test_change_directory_relative(self, executor):
        """Test changing with relative path."""
        # First change to /tmp
        executor.change_directory("/tmp")

        # Create a temp subdir
        with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
            dirname = os.path.basename(tmpdir)
            success, message = executor.change_directory(dirname)
            assert success
            assert executor.current_directory == os.path.realpath(tmpdir)

    @pytest.mark.asyncio
    async def test_execute_simple_command(self, executor):
        """Test executing a simple command."""
        result = await executor.execute("echo hello")
        assert result.stdout.strip() == "hello"
        assert result.return_code == 0

    @pytest.mark.asyncio
    async def test_execute_command_with_stderr(self, executor):
        """Test executing a command that produces stderr."""
        result = await executor.execute("ls /nonexistent 2>&1 || true")
        assert result.return_code == 0  # Because of || true

    @pytest.mark.asyncio
    async def test_execute_in_specific_directory(self, executor):
        """Test executing command in specific directory."""
        result = await executor.execute("pwd", working_directory="/tmp")
        assert "/tmp" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_in_disallowed_directory(self, executor):
        """Test executing in disallowed directory fails."""
        result = await executor.execute("pwd", working_directory="/etc")
        assert result.return_code == 1
        assert "not allowed" in result.stderr

    @pytest.mark.asyncio
    async def test_output_truncation(self, executor):
        """Test output is truncated when too large."""
        # Generate output larger than max_output_size (1000 chars)
        # yes | head -1000 produces 2000 chars (1000 lines of "y\n")
        result = await executor.execute("yes | head -1000")
        assert result.truncated
        assert "truncated" in result.stdout.lower()

    @pytest.mark.asyncio
    async def test_timeout(self):
        """Test command timeout."""
        config = Config(
            allowed_directories=[str(Path.home())],
            timeout_seconds=1,
        )
        executor = CommandExecutor(config)

        result = await executor.execute("sleep 10")
        assert result.timed_out
        assert result.return_code == -1
