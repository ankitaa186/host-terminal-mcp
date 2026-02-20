"""Tests for HTTP server transport."""

import pytest
from fastapi.testclient import TestClient

from host_terminal_mcp.config import CommandPattern, Config, PermissionMode
from host_terminal_mcp.http_server import create_app


@pytest.fixture
def allowlist_app():
    """App with allowlist mode and a few allowed commands."""
    config = Config(
        permission_mode=PermissionMode.ALLOWLIST,
        allowed_commands=[
            CommandPattern(pattern="ls", description="List files"),
            CommandPattern(pattern="echo ", description="Echo"),
            CommandPattern(pattern="pwd", description="Working dir"),
            CommandPattern(pattern="cat ", description="Cat files"),
        ],
        blocked_commands=[
            CommandPattern(
                pattern=r"^rm\s+-rf\s+/",
                description="Recursive delete root",
                is_regex=True,
            ),
            CommandPattern(pattern="sudo ", description="Superuser"),
        ],
        allowed_directories=["/tmp", "/"],
        timeout_seconds=10,
        max_output_size=1000,
    )
    return create_app(config)


@pytest.fixture
def ask_app():
    """App with ask mode."""
    config = Config(
        permission_mode=PermissionMode.ASK,
        allowed_commands=[
            CommandPattern(pattern="ls", description="List files"),
        ],
        blocked_commands=[
            CommandPattern(pattern="sudo ", description="Superuser"),
        ],
        allowed_directories=["/tmp", "/"],
        timeout_seconds=10,
    )
    return create_app(config)


@pytest.fixture
def client(allowlist_app):
    return TestClient(allowlist_app)


@pytest.fixture
def ask_client(ask_app):
    return TestClient(ask_app)


# ---------- /health ----------


class TestHealth:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "host-terminal-mcp"
        assert data["permission_mode"] == "allowlist"

    def test_health_reflects_mode(self, ask_client):
        resp = ask_client.get("/health")
        assert resp.json()["permission_mode"] == "ask"


# ---------- /execute ----------


class TestExecute:
    def test_allowed_command(self, client):
        resp = client.post("/execute", json={"command": "echo hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "hello" in data["stdout"]
        assert data["exit_code"] == 0
        assert data["timed_out"] is False

    def test_allowed_command_with_working_directory(self, client):
        resp = client.post(
            "/execute", json={"command": "pwd", "working_directory": "/tmp"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        # macOS /tmp -> /private/tmp
        assert "tmp" in data["stdout"]

    def test_blocked_command(self, client):
        resp = client.post("/execute", json={"command": "rm -rf /"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"
        assert "not allowed" in data["error"].lower()

    def test_blocked_sudo(self, client):
        resp = client.post("/execute", json={"command": "sudo ls"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"
        assert "not allowed" in data["error"].lower()

    def test_unlisted_command_rejected_in_allowlist_mode(self, client):
        resp = client.post("/execute", json={"command": "curl example.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"
        assert "not allowed" in data["error"].lower()

    def test_empty_command(self, client):
        resp = client.post("/execute", json={"command": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"
        assert "no command" in data["error"].lower()

    def test_whitespace_command(self, client):
        resp = client.post("/execute", json={"command": "   "})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"

    def test_needs_approval_in_ask_mode(self, ask_client):
        resp = ask_client.post("/execute", json={"command": "curl example.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "needs_approval"
        assert data["command"] == "curl example.com"
        assert "message" in data

    def test_allowed_command_in_ask_mode(self, ask_client):
        resp = ask_client.post("/execute", json={"command": "ls /tmp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_blocked_overrides_ask_mode(self, ask_client):
        resp = ask_client.post("/execute", json={"command": "sudo ls"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"
        assert "not allowed" in data["error"].lower()

    def test_command_failure_returns_nonzero_exit(self, client):
        resp = client.post("/execute", json={"command": "ls /nonexistent_dir_xyz"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"  # execution succeeded, command failed
        assert data["exit_code"] != 0

    def test_output_truncation(self, client):
        # max_output_size is 1000 in the fixture
        resp = client.post("/execute", json={"command": "echo $(yes | head -1000)"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["truncated"] is True


# ---------- /cd ----------


class TestCd:
    def test_change_directory(self, client):
        resp = client.post("/cd", json={"path": "/tmp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        # macOS /tmp -> /private/tmp
        assert "tmp" in data["current_directory"]

    def test_change_to_nonexistent(self, client):
        resp = client.post("/cd", json={"path": "/nonexistent_xyz"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"

    def test_empty_path(self, client):
        resp = client.post("/cd", json={"path": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"


# ---------- /cwd ----------


class TestCwd:
    def test_get_current_directory(self, client):
        resp = client.get("/cwd")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "current_directory" in data
        assert len(data["current_directory"]) > 0


# ---------- /permissions ----------


class TestPermissions:
    def test_permissions_allowlist(self, client):
        resp = client.get("/permissions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["permission_mode"] == "allowlist"
        assert data["num_allowed_patterns"] == 4
        assert data["num_blocked_patterns"] == 2
        assert data["timeout_seconds"] == 10
        assert isinstance(data["allowed_directories"], list)

    def test_permissions_ask_mode(self, ask_client):
        resp = ask_client.get("/permissions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["permission_mode"] == "ask"
