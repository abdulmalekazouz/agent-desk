"""Tests for agentdesk.agent.workflows."""

from agentdesk.agent.actions import ListFilesTool, ReadEmailsTool
from agentdesk.agent.permissions import PermissionRegistry
from agentdesk.agent.workflows import Workflow, WorkflowEngine, WorkflowStore


def _build_engine(permissions=None):
    tools = {tool.name: tool for tool in (ReadEmailsTool(), ListFilesTool())}
    return WorkflowEngine(tools=tools, permissions=permissions or PermissionRegistry())


def test_store_save_and_get():
    store = WorkflowStore()
    workflow = Workflow(name="Daily", steps=["read_emails"])
    store.save(workflow)

    assert store.get("Daily") == workflow
    assert store.get("Nonexistent") is None


def test_store_all_lists_every_saved_workflow():
    store = WorkflowStore()
    store.save(Workflow(name="A", steps=["read_emails"]))
    store.save(Workflow(name="B", steps=["list_files"]))

    assert {w.name for w in store.all()} == {"A", "B"}


def test_store_save_overwrites_same_name():
    store = WorkflowStore()
    store.save(Workflow(name="Daily", steps=["read_emails"]))
    store.save(Workflow(name="Daily", steps=["list_files"]))

    assert store.get("Daily").steps == ["list_files"]
    assert len(store.all()) == 1


def test_engine_runs_every_step_in_order():
    engine = _build_engine()
    run = engine.run(Workflow(name="Daily", steps=["read_emails", "list_files"]))

    assert run.workflow_name == "Daily"
    assert [step.tool_name for step in run.steps] == ["read_emails", "list_files"]
    assert run.all_succeeded is True


def test_engine_reports_unknown_tool_without_raising():
    engine = _build_engine()
    run = engine.run(Workflow(name="Bad", steps=["no_such_tool"]))

    assert run.all_succeeded is False
    assert "Unknown tool" in run.steps[0].result.message


def test_engine_respects_denied_permissions():
    permissions = PermissionRegistry()
    permissions.set_granted("files.read", False)
    engine = _build_engine(permissions)

    run = engine.run(Workflow(name="Daily", steps=["read_emails", "list_files"]))

    assert run.steps[0].result.success is True
    assert run.steps[1].result.success is False
    assert "permission is turned off" in run.steps[1].result.message
    assert run.all_succeeded is False
