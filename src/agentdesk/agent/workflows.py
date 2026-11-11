"""In-memory workflow storage and execution.

A workflow is a named, ordered list of tool names. Running it invokes
each named tool in turn (with no per-step arguments -- see the README
"Limitations" section), respecting the same permission checks as a
normal chat-driven tool call, and records every step's outcome.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentdesk.agent.permissions import PermissionRegistry
from agentdesk.agent.tools import Tool, ToolResult


@dataclass(frozen=True)
class Workflow:
    """A named, ordered sequence of tool names.

    Attributes:
        name: The workflow's unique name.
        steps: The tool names to invoke, in order.
    """

    name: str
    steps: list[str]


@dataclass(frozen=True)
class StepOutcome:
    """The outcome of one step of a workflow run.

    Attributes:
        tool_name: The tool that was (attempted to be) invoked.
        result: The step's `ToolResult` -- a synthetic failed result if
            the tool name was unknown or its permission was denied,
            rather than raising.
    """

    tool_name: str
    result: ToolResult


@dataclass(frozen=True)
class WorkflowRun:
    """The outcome of running an entire workflow once.

    Attributes:
        workflow_name: The workflow that was run.
        steps: Each step's outcome, in order.
    """

    workflow_name: str
    steps: list[StepOutcome]

    @property
    def all_succeeded(self) -> bool:
        """Whether every step in this run succeeded."""
        return all(step.result.success for step in self.steps)


class WorkflowStore:
    """An in-memory registry of saved workflows, keyed by name."""

    def __init__(self) -> None:
        """Initializes an empty store."""
        self._workflows: dict[str, Workflow] = {}

    def save(self, workflow: Workflow) -> None:
        """Saves (or overwrites) a workflow.

        Args:
            workflow: The workflow to save.
        """
        self._workflows[workflow.name] = workflow

    def get(self, name: str) -> Workflow | None:
        """Looks up a saved workflow by name.

        Args:
            name: The workflow's name.

        Returns:
            The workflow, or `None` if no workflow has that name.
        """
        return self._workflows.get(name)

    def all(self) -> list[Workflow]:
        """Lists every saved workflow.

        Returns:
            All saved workflows, in insertion order.
        """
        return list(self._workflows.values())


class WorkflowEngine:
    """Executes saved workflows against a tool registry and permissions."""

    def __init__(self, tools: dict[str, Tool], permissions: PermissionRegistry) -> None:
        """Initializes the engine.

        Args:
            tools: Maps tool name to `Tool` instance. Deliberately holds
                only the "actionable" tools (e.g. not `create_workflow`/
                `run_workflow` themselves), so a workflow cannot create
                or trigger other workflows.
            permissions: The permission registry gating each step.
        """
        self._tools = tools
        self._permissions = permissions

    def run(self, workflow: Workflow) -> WorkflowRun:
        """Runs every step of a workflow in order.

        Args:
            workflow: The workflow to run.

        Returns:
            A `WorkflowRun` with each step's outcome. A step whose tool
            is unknown or whose permission is denied is recorded as a
            failed `ToolResult` rather than raising, so the remaining
            steps still run.
        """
        outcomes = [
            StepOutcome(tool_name=tool_name, result=self._run_step(tool_name))
            for tool_name in workflow.steps
        ]
        return WorkflowRun(workflow_name=workflow.name, steps=outcomes)

    def _run_step(self, tool_name: str) -> ToolResult:
        """Runs a single named step, never raising.

        Args:
            tool_name: The tool to invoke.

        Returns:
            The tool's `ToolResult`, or a synthetic failed `ToolResult`
            if the tool is unknown or not permitted.
        """
        tool = self._tools.get(tool_name)
        if tool is None:
            return ToolResult(success=False, message=f"Unknown tool '{tool_name}'.")

        if not self._permissions.is_granted(tool.required_permission):
            return ToolResult(
                success=False,
                message=(
                    f"Skipped '{tool_name}': the '{tool.required_permission}' "
                    "permission is turned off."
                ),
            )

        return tool.run()
