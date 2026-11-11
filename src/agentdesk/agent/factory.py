"""Builds a ready-to-use `Agent` wired up with this project's tools."""

from __future__ import annotations

from dataclasses import dataclass

from agentdesk.agent.actions import ListFilesTool, ReadEmailsTool
from agentdesk.agent.agent import Agent
from agentdesk.agent.llm import MockLLMProvider
from agentdesk.agent.permissions import PermissionRegistry
from agentdesk.agent.tools import Tool
from agentdesk.agent.workflow_tools import CreateWorkflowTool, RunWorkflowTool
from agentdesk.agent.workflows import WorkflowEngine, WorkflowStore


@dataclass(frozen=True)
class AgentBundle:
    """Everything a GUI needs beyond just the `Agent` itself.

    Attributes:
        agent: The agent to send chat messages to.
        permissions: The shared permission registry (for a Permissions
            screen to read/toggle).
        workflow_store: The shared workflow store (for a Workflows
            screen to list saved workflows).
    """

    agent: Agent
    permissions: PermissionRegistry
    workflow_store: WorkflowStore


def build_default_agent(permissions: PermissionRegistry | None = None) -> AgentBundle:
    """Builds an `Agent` using the mock LLM and this project's default tools.

    Args:
        permissions: The permission registry to use. Defaults to a new
            `PermissionRegistry` with every known permission granted.

    Returns:
        An `AgentBundle` with the ready-to-use agent plus the shared
        permission registry and workflow store it was built with.
    """
    permissions = permissions or PermissionRegistry()

    base_tools: list[Tool] = [ReadEmailsTool(), ListFilesTool()]
    store = WorkflowStore()
    # The engine only knows about "actionable" tools, not the workflow
    # tools themselves, so a workflow cannot create or run other
    # workflows.
    engine = WorkflowEngine(
        tools={tool.name: tool for tool in base_tools}, permissions=permissions
    )

    all_tools = [*base_tools, CreateWorkflowTool(store), RunWorkflowTool(store, engine)]
    agent = Agent(llm=MockLLMProvider(), tools=all_tools, permissions=permissions)
    return AgentBundle(agent=agent, permissions=permissions, workflow_store=store)
