"""Tests for agentdesk.agent.workflow_tools."""

from agentdesk.agent.actions import ListFilesTool, ReadEmailsTool
from agentdesk.agent.permissions import PermissionRegistry
from agentdesk.agent.workflow_tools import CreateWorkflowTool, RunWorkflowTool
from agentdesk.agent.workflows import WorkflowEngine, WorkflowStore


def _build_tools():
    store = WorkflowStore()
    tools = {tool.name: tool for tool in (ReadEmailsTool(), ListFilesTool())}
    engine = WorkflowEngine(tools=tools, permissions=PermissionRegistry())
    return CreateWorkflowTool(store), RunWorkflowTool(store, engine), store


def test_create_workflow_requires_a_name():
    create_tool, _, _ = _build_tools()
    result = create_tool.run(name="", steps=["read_emails"])
    assert result.success is False


def test_create_workflow_requires_at_least_one_step():
    create_tool, _, _ = _build_tools()
    result = create_tool.run(name="Empty", steps=[])
    assert result.success is False


def test_create_workflow_saves_and_reports_steps():
    create_tool, _, store = _build_tools()
    result = create_tool.run(name="Daily", steps=["read_emails", "list_files"])

    assert result.success is True
    assert "read_emails" in result.message
    assert store.get("Daily").steps == ["read_emails", "list_files"]


def test_run_workflow_reports_unknown_workflow():
    _, run_tool, _ = _build_tools()
    result = run_tool.run(name="Nonexistent")
    assert result.success is False
    assert "No workflow named" in result.message


def test_run_workflow_executes_saved_steps():
    create_tool, run_tool, _ = _build_tools()
    create_tool.run(name="Daily", steps=["read_emails", "list_files"])

    result = run_tool.run(name="Daily")
    assert result.success is True
    assert "read_emails: OK" in result.message
    assert "list_files: OK" in result.message
