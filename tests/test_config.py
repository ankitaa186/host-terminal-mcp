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
        assert not pattern.matches("lsof")  # Different command, not just ls with args
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

        # Secret-leaking commands should NOT be in the allowlist
        assert "env" not in patterns
        assert "printenv" not in patterns
        assert "echo $" not in patterns

        # No duplicate entries for df/ps
        assert patterns.count("df") == 1
        assert patterns.count("ps") == 1

    def test_default_blocked_commands(self):
        """Test default blocked commands include dangerous operations."""
        commands = get_default_blocked_commands()
        patterns = [c.pattern for c in commands]

        # Dangerous patterns should be blocked
        assert "sudo " in patterns
        assert "mkfs" in patterns
        assert "dd" in patterns
        assert "reboot" in patterns
        assert "shutdown" in patterns
        assert "kill" in patterns
        assert "killall" in patterns
        assert "pkill" in patterns


class TestFindExecBlocking:
    """Tests for find -exec blocking with detailed error messages."""

    @pytest.fixture
    def config(self):
        return Config(
            allowed_commands=[
                CommandPattern(pattern="find ", description="Find files"),
            ],
            blocked_commands=get_default_blocked_commands(),
        )

    def test_find_without_exec_allowed(self, config):
        """find without -exec should be allowed."""
        allowed, reason = config.is_command_allowed("find /tmp -name '*.py'")
        assert allowed

    def test_find_with_type_allowed(self, config):
        """find with -type filter should be allowed."""
        allowed, reason = config.is_command_allowed("find . -type f -name '*.log'")
        assert allowed

    def test_find_exec_blocked(self, config):
        """find with -exec should be blocked."""
        allowed, reason = config.is_command_allowed("find / -exec rm -rf {} \\;")
        assert not allowed
        assert "blocked" in reason.lower()

    def test_find_exec_error_includes_regex(self, config):
        """Blocked find -exec error message should include the regex pattern."""
        allowed, reason = config.is_command_allowed("find / -exec rm {} \\;")
        assert not allowed
        assert "Blocked regex:" in reason
        assert "^find\\s+.*-exec" in reason

    def test_find_exec_error_includes_guidance(self, config):
        """Blocked find -exec error message should include usage guidance."""
        allowed, reason = config.is_command_allowed("find . -name '*.tmp' -exec rm {} +")
        assert not allowed
        assert "xargs" in reason

    def test_find_execdir_blocked(self, config):
        """find with -execdir should also be blocked (matched by -exec prefix)."""
        allowed, reason = config.is_command_allowed("find . -execdir mv {} /tmp \\;")
        assert not allowed


class TestRmVariants:
    """Tests for rm command variant blocking."""

    @pytest.fixture
    def config(self):
        return Config(
            allowed_commands=[
                CommandPattern(pattern="rm", description="Remove files"),
            ],
            blocked_commands=get_default_blocked_commands(),
        )

    def test_rm_single_file_allowed(self, config):
        """rm on a single file should be allowed."""
        allowed, _ = config.is_command_allowed("rm file.txt")
        assert allowed

    def test_rm_rf_root_blocked(self, config):
        allowed, _ = config.is_command_allowed("rm -rf /")
        assert not allowed

    def test_rm_rf_dot_blocked(self, config):
        """rm -rf . (current dir) should be blocked."""
        allowed, _ = config.is_command_allowed("rm -rf .")
        assert not allowed

    def test_rm_rf_dotdot_blocked(self, config):
        """rm -rf .. (parent dir) should be blocked."""
        allowed, _ = config.is_command_allowed("rm -rf ..")
        assert not allowed

    def test_rm_fr_root_blocked(self, config):
        """rm -fr / (reversed flags) should be blocked."""
        allowed, _ = config.is_command_allowed("rm -fr /")
        assert not allowed

    def test_rm_recursive_long_flag_blocked(self, config):
        """rm --recursive should be blocked."""
        allowed, _ = config.is_command_allowed("rm --recursive --force /")
        assert not allowed


class TestSensitiveFileBlocking:
    """Tests for sensitive file access blocking regardless of reader command."""

    @pytest.fixture
    def config(self):
        return Config(
            allowed_commands=[
                CommandPattern(pattern="cat ", description="Cat files"),
                CommandPattern(pattern="head ", description="Head files"),
                CommandPattern(pattern="tail ", description="Tail files"),
                CommandPattern(pattern="less ", description="Less files"),
                CommandPattern(pattern="grep ", description="Grep files"),
            ],
            blocked_commands=get_default_blocked_commands(),
        )

    def test_cat_etc_shadow_blocked(self, config):
        allowed, _ = config.is_command_allowed("cat /etc/shadow")
        assert not allowed

    def test_head_etc_shadow_blocked(self, config):
        allowed, _ = config.is_command_allowed("head -1 /etc/shadow")
        assert not allowed

    def test_tail_etc_passwd_blocked(self, config):
        allowed, _ = config.is_command_allowed("tail /etc/passwd")
        assert not allowed

    def test_grep_etc_passwd_blocked(self, config):
        allowed, _ = config.is_command_allowed("grep root /etc/passwd")
        assert not allowed

    def test_cat_ssh_key_blocked(self, config):
        allowed, _ = config.is_command_allowed("cat ~/.ssh/id_rsa")
        assert not allowed

    def test_less_ssh_config_blocked(self, config):
        allowed, _ = config.is_command_allowed("less ~/.ssh/config")
        assert not allowed

    def test_cat_aws_credentials_blocked(self, config):
        allowed, _ = config.is_command_allowed("cat ~/.aws/credentials")
        assert not allowed

    def test_grep_gnupg_blocked(self, config):
        allowed, _ = config.is_command_allowed("grep key ~/.gnupg/pubring.kbx")
        assert not allowed

    def test_cat_normal_file_allowed(self, config):
        """Normal file access should still work."""
        allowed, _ = config.is_command_allowed("cat /etc/hosts")
        assert allowed

    def test_sensitive_file_error_includes_regex(self, config):
        """Error for sensitive file access should include the regex."""
        allowed, reason = config.is_command_allowed("cat /etc/shadow")
        assert "Blocked regex:" in reason


class TestDdBlocking:
    """Tests for dd command blocking."""

    @pytest.fixture
    def config(self):
        return Config(
            permission_mode=PermissionMode.ALLOW_ALL,
            blocked_commands=get_default_blocked_commands(),
        )

    def test_dd_if_blocked(self, config):
        allowed, _ = config.is_command_allowed("dd if=/dev/zero of=/dev/sda")
        assert not allowed

    def test_dd_of_blocked(self, config):
        allowed, _ = config.is_command_allowed("dd of=/dev/sda")
        assert not allowed

    def test_dd_standalone_blocked(self, config):
        allowed, _ = config.is_command_allowed("dd")
        assert not allowed


class TestDeviceOverwrite:
    """Tests for device overwrite blocking across device types."""

    @pytest.fixture
    def config(self):
        return Config(
            permission_mode=PermissionMode.ALLOW_ALL,
            blocked_commands=get_default_blocked_commands(),
        )

    def test_redirect_to_sda(self, config):
        allowed, _ = config.is_command_allowed("echo x > /dev/sda")
        assert not allowed

    def test_redirect_to_nvme(self, config):
        allowed, _ = config.is_command_allowed("echo x > /dev/nvme0n1")
        assert not allowed

    def test_redirect_to_disk_macos(self, config):
        allowed, _ = config.is_command_allowed("echo x > /dev/disk0")
        assert not allowed

    def test_redirect_to_vd(self, config):
        allowed, _ = config.is_command_allowed("echo x > /dev/vda")
        assert not allowed


class TestSystemShutdownBlocking:
    """Tests for system shutdown and process kill blocking."""

    @pytest.fixture
    def config(self):
        return Config(
            permission_mode=PermissionMode.ALLOW_ALL,
            blocked_commands=get_default_blocked_commands(),
        )

    def test_reboot_blocked(self, config):
        allowed, _ = config.is_command_allowed("reboot")
        assert not allowed

    def test_shutdown_blocked(self, config):
        allowed, _ = config.is_command_allowed("shutdown -h now")
        assert not allowed

    def test_halt_blocked(self, config):
        allowed, _ = config.is_command_allowed("halt")
        assert not allowed

    def test_poweroff_blocked(self, config):
        allowed, _ = config.is_command_allowed("poweroff")
        assert not allowed

    def test_kill_blocked(self, config):
        allowed, _ = config.is_command_allowed("kill -9 1234")
        assert not allowed

    def test_killall_blocked(self, config):
        allowed, _ = config.is_command_allowed("killall firefox")
        assert not allowed

    def test_pkill_blocked(self, config):
        allowed, _ = config.is_command_allowed("pkill -f node")
        assert not allowed

    def test_kill_does_not_match_killall(self, config):
        """kill pattern should not accidentally match killall (word boundary)."""
        # Both are blocked by separate patterns, but verify the kill pattern
        # itself respects word boundaries
        pattern = CommandPattern(pattern="kill", description="Kill")
        assert pattern.matches("kill -9 1234")
        assert not pattern.matches("killall firefox")
