"""Pytest for login functionality.

This file replaces the old script-style tests with pytest parametrized
cases. It posts to the running server at localhost:5000 which is started by
the test runner when running the full suite.
"""
import json
import socket
import os

import pytest
import requests


# Determine base URL (supports codespaces or local runs)
hostname = socket.gethostname()
if '.codespaces.' in hostname:
    BASE_URL = f"https://{os.environ.get('CODESPACE_NAME')}-5000.{os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN')}"
else:
    BASE_URL = 'http://localhost:5000'


@pytest.mark.parametrize(
    "username,password,should_succeed",
    [
        ("teacher1", "password123", True),
        ("student1", "password123", True),
        ("invalid_user", "password123", False),
        ("teacher1", "wrong_password", False),
    ],
)
def test_login_endpoint(username: str, password: str, should_succeed: bool):
    """POST to /api/security/login and assert success/failure as expected."""
    resp = requests.post(
        f"{BASE_URL}/api/security/login",
        json={"username": username, "password": password},
        headers={"Content-Type": "application/json"},
        timeout=5,
    )

    # For successful logins we expect a 200 and a JSON access_token
    if should_succeed:
        assert resp.status_code == 200, f"Expected 200 OK for valid creds, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert isinstance(data, dict)
        assert "access_token" in data or "token" in data or "role" in data
    else:
        # For invalid credentials we expect a 4xx response
        assert 400 <= resp.status_code < 500, f"Expected client error for invalid creds, got {resp.status_code}: {resp.text}"