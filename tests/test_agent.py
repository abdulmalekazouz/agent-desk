"""Tests for agentdesk.agent.agent.Agent."""

from agentdesk.agent.factory import build_default_agent
from agentdesk.agent.permissions import PermissionRegistry


def test_greeting_produces_a_direct_response_with_no_tool_call():
    agent = build_default_agent()
    response = agent.handle_message("hello")
    assert response.reply
    kinds = [entry.kind for entry in response.trace]
    assert kinds == ["decision", "response"]


def test_reading_emails_produces_a_full_trace():
    agent = build_default_agent()
    response = agent.handle_message("read my emails")

    kinds = [entry.kind for entry in response.trace]
    assert kinds == ["decision", "tool_call", "tool_result", "response"]
    assert "email" in response.reply.lower() or "found" in response.reply.lower()


def test_denied_permission_blocks_the_tool_and_explains_why():
    permissions = PermissionRegistry()
    permissions.set_granted("email.read", False)
    agent = build_default_agent(permissions=permissions)

    response = agent.handle_message("read my emails")
    kinds = [entry.kind for entry in response.trace]
    assert kinds == ["decision", "permission_denied", "response"]
    assert "email.read" in response.reply


def test_unknown_tool_name_is_reported_gracefully():
    agent = build_default_agent()
    # "run workflow" is recognized by the mock LLM but no workflow tool is
    # registered in this branch yet, so the agent should say so rather
    # than crash.
    response = agent.handle_message("run workflow Nonexistent")
    assert "isn't available" in response.reply


def test_listing_files_succeeds_end_to_end():
    agent = build_default_agent()
    response = agent.handle_message("list my files")
    assert "Documents" in response.reply
