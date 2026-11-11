"""The `Tool` contract that every sandboxed agent action implements.

A tool is a single, named, permission-gated capability the agent can
invoke -- e.g. "read the mock inbox" or "list mock files". Concrete
tools are added in `agentdesk.agent.actions`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    """The outcome of running one tool.

    Attributes:
        success: Whether the tool completed without error.
        message: A short, human-readable summary suitable for showing
            directly in the chat transcript.
        data: Optional structured data the caller can use for its own
            purposes (e.g. rendering a list in a GUI screen), separate
            from the human-readable `message`.
    """

    success: bool
    message: str
    data: Any = field(default=None)


class Tool(ABC):
    """Base class for a single sandboxed, permission-gated agent action."""

    name: str
    description: str
    required_permission: str

    @abstractmethod
    def run(self, **kwargs: Any) -> ToolResult:
        """Executes the tool.

        Args:
            **kwargs: Tool-specific arguments, as decided by the LLM
                layer (see `agentdesk.agent.llm`).

        Returns:
            A `ToolResult` describing what happened.
        """
        raise NotImplementedError
