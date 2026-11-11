"""Tests for agentdesk.agent.agent.Agent."""

from agentdesk.agent.factory import build_default_agent
from agentdesk.agent.permissions import PermissionRegistry


def test_greeting_produces_a_direct_response_with_no_tool_call():
    bundle = build_default_agent()
    response = bundle.agent.handle_message("hello")
    assert response.reply
    kinds = [entry.kind for entry in response.trace]
    assert kinds == ["decision", "response"]


def test_reading_emails_produces_a_full_trace():
    bundle = build_default_agent()
    response = bundle.agent.handle_message("read my emails")

    kinds = [entry.kind for entry in response.trace]
    assert kinds == ["decision", "tool_call", "tool_result", "response"]
    assert "email" in response.reply.lower() or "found" in response.reply.lower()


def test_denied_permission_blocks_the_tool_and_explains_why():
    permissions = PermissionRegistry()
    permissions.set_granted("email.read", False)
    bundle = build_default_agent(permissions=permissions)

    response = bundle.agent.handle_message("read my emails")
    kinds = [entry.kind for entry in response.trace]
    assert kinds == ["decision", "permission_denied", "response"]
    assert "email.read" in response.reply


def test_running_a_nonexistent_workflow_is_reported_gracefully():
    bundle = build_default_agent()
    response = bundle.agent.handle_message("run workflow Nonexistent")
    assert "No workflow named" in response.reply


def test_listing_files_succeeds_end_to_end():
    bundle = build_default_agent()
    response = bundle.agent.handle_message("list my files")
    assert "Documents" in response.reply


def test_creating_and_running_a_workflow_through_chat():
    bundle = build_default_agent()

    create_response = bundle.agent.handle_message(
        "create workflow Morning Briefing: read_emails, list_files"
    )
    assert "Saved workflow" in create_response.reply
    assert bundle.workflow_store.get("Morning Briefing") is not None

    run_response = bundle.agent.handle_message("run workflow Morning Briefing")
    assert "read_emails: OK" in run_response.reply
    assert "list_files: OK" in run_response.reply


def test_workflow_tools_are_also_permission_gated():
    permissions = PermissionRegistry()
    permissions.set_granted("workflows.write", False)
    bundle = build_default_agent(permissions=permissions)

    response = bundle.agent.handle_message("create workflow Test: read_emails")
    assert "workflows.write" in response.reply
    assert bundle.workflow_store.get("Test") is None
