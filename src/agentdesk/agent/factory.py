"""Builds a ready-to-use `Agent` wired up with this project's tools."""

from __future__ import annotations

from agentdesk.agent.actions import ListFilesTool, ReadEmailsTool
from agentdesk.agent.agent import Agent
from agentdesk.agent.llm import MockLLMProvider
from agentdesk.agent.permissions import PermissionRegistry


def build_default_agent(permissions: PermissionRegistry | None = None) -> Agent:
    """Builds an `Agent` using the mock LLM and this project's default tools.

    Args:
        permissions: The permission registry to use. Defaults to a new
            `PermissionRegistry` with every known permission granted.

    Returns:
        A ready-to-use `Agent`.
    """
    return Agent(
        llm=MockLLMProvider(),
        tools=[ReadEmailsTool(), ListFilesTool()],
        permissions=permissions or PermissionRegistry(),
    )
