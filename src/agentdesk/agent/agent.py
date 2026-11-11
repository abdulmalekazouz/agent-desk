"""The agent orchestrator.

Ties the LLM decision layer, the permission registry, and the tool
registry into a single request/response loop, producing a full,
inspectable trace of every step for each message handled.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from agentdesk.agent.llm import LLMProvider, TextReply, ToolCallDecision
from agentdesk.agent.permissions import PermissionRegistry
from agentdesk.agent.tools import Tool


@dataclass(frozen=True)
class TraceEntry:
    """One step of the agent's reasoning, for display/debugging.

    Attributes:
        kind: One of "decision", "tool_call", "permission_denied",
            "tool_result", or "response".
        detail: A short human-readable description of this step.
        timestamp: When the step occurred, in UTC.
    """

    kind: str
    detail: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AgentResponse:
    """What the agent produced for one user message.

    Attributes:
        reply: The text to show in the chat transcript.
        trace: Every step the agent took to produce `reply`, in order.
    """

    reply: str
    trace: list[TraceEntry]


class Agent:
    """Ties together the LLM decision layer, permissions, and tools."""

    def __init__(
        self, llm: LLMProvider, tools: list[Tool], permissions: PermissionRegistry
    ) -> None:
        """Initializes the agent.

        Args:
            llm: The decision layer (see `agentdesk.agent.llm`).
            tools: Every tool the agent may invoke.
            permissions: The permission registry gating tool use.
        """
        self._llm = llm
        self._tools: dict[str, Tool] = {tool.name: tool for tool in tools}
        self._permissions = permissions

    def handle_message(self, message: str) -> AgentResponse:
        """Processes one user chat message end to end.

        Args:
            message: The user's raw chat message.

        Returns:
            An `AgentResponse` with the final reply and a full trace of
            how the agent arrived at it.
        """
        trace: list[TraceEntry] = []
        decision = self._llm.decide(message)

        if isinstance(decision, TextReply):
            trace.append(TraceEntry("decision", "Decided to reply directly (no tool needed)."))
            trace.append(TraceEntry("response", decision.text))
            return AgentResponse(reply=decision.text, trace=trace)

        return self._handle_tool_call(decision, trace)

    def _handle_tool_call(
        self, decision: ToolCallDecision, trace: list[TraceEntry]
    ) -> AgentResponse:
        """Resolves and executes a `ToolCallDecision`, building the trace.

        Args:
            decision: The tool call the LLM layer decided on.
            trace: The trace so far; more entries are appended to it.

        Returns:
            The resulting `AgentResponse`.
        """
        trace.append(
            TraceEntry(
                "decision",
                f"Decided to call tool '{decision.tool_name}' with {decision.arguments!r}.",
            )
        )

        tool = self._tools.get(decision.tool_name)
        if tool is None:
            reply = (
                f"I tried to use a tool called '{decision.tool_name}', but it isn't "
                "available."
            )
            trace.append(TraceEntry("tool_call", reply))
            trace.append(TraceEntry("response", reply))
            return AgentResponse(reply=reply, trace=trace)

        if not self._permissions.is_granted(tool.required_permission):
            reply = (
                f"I can't do that -- the '{tool.required_permission}' permission is "
                "turned off. Enable it on the Permissions screen to use this feature."
            )
            trace.append(TraceEntry("permission_denied", reply))
            trace.append(TraceEntry("response", reply))
            return AgentResponse(reply=reply, trace=trace)

        trace.append(TraceEntry("tool_call", f"Calling '{tool.name}'..."))
        result = tool.run(**decision.arguments)
        outcome = "succeeded" if result.success else "failed"
        trace.append(TraceEntry("tool_result", f"'{tool.name}' {outcome}: {result.message}"))

        reply = self._llm.summarize_tool_result(tool.name, result.message)
        trace.append(TraceEntry("response", reply))
        return AgentResponse(reply=reply, trace=trace)
