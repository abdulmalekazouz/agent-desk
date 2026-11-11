"""Tests for agentdesk.agent.permissions."""

from agentdesk.agent.permissions import KNOWN_PERMISSIONS, PermissionRegistry


def test_all_known_permissions_default_to_granted():
    registry = PermissionRegistry()
    for info in KNOWN_PERMISSIONS:
        assert registry.is_granted(info.name) is True


def test_unknown_permission_defaults_to_not_granted():
    registry = PermissionRegistry()
    assert registry.is_granted("made.up.permission") is False


def test_revoking_a_permission_is_reflected_immediately():
    registry = PermissionRegistry()
    registry.set_granted("email.read", False)
    assert registry.is_granted("email.read") is False

    registry.set_granted("email.read", True)
    assert registry.is_granted("email.read") is True
