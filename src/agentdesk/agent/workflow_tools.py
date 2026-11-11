"""Tools that let the agent create and run its own workflows.

Separate from `agentdesk.agent.actions` since these two tools need a
reference to the shared `WorkflowStore`/`WorkflowEngine` (via
constructor injection), unlike the stateless tools in that module.
"""

from __future__ import annotations

from agentdesk.agent.tools import Tool, ToolResult
from agentdesk.agent.workflows import Workflow, WorkflowEngine, WorkflowStore


class CreateWorkflowTool(Tool):
    """Saves a new named workflow (an ordered list of tool names)."""

    name = "create_workflow"
    description = "Saves a new workflow: a name plus an ordered list of tool names to run."
    required_permission = "workflows.write"

    def __init__(self, store: WorkflowStore) -> None:
        """Initializes the tool.

        Args:
            store: Where to save the new workflow.
        """
        self._store = store

    def run(self, **kwargs) -> ToolResult:
        """Saves a workflow.

        Args:
            **kwargs: Must include `name` (str) and `steps` (list[str],
                tool names in execution order).

        Returns:
            A `ToolResult` confirming the save, or an unsuccessful result
            if `name` or `steps` is missing/empty.
        """
        name = (kwargs.get("name") or "").strip()
        steps = list(kwargs.get("steps") or [])

        if not name:
            return ToolResult(success=False, message="A workflow needs a name.")
        if not steps:
            return ToolResult(success=False, message="A workflow needs at least one step.")

        self._store.save(Workflow(name=name, steps=steps))
        return ToolResult(
            success=True,
            message=f"Saved workflow '{name}' with {len(steps)} step(s): {', '.join(steps)}.",
            data=Workflow(name=name, steps=steps),
        )


class RunWorkflowTool(Tool):
    """Runs a previously saved workflow."""

    name = "run_workflow"
    description = "Runs a previously saved workflow by name."
    required_permission = "workflows.run"

    def __init__(self, store: WorkflowStore, engine: WorkflowEngine) -> None:
        """Initializes the tool.

        Args:
            store: Where saved workflows are looked up.
            engine: Executes the workflow's steps.
        """
        self._store = store
        self._engine = engine

    def run(self, **kwargs) -> ToolResult:
        """Runs a saved workflow by name.

        Args:
            **kwargs: Must include `name` (str), the workflow to run.

        Returns:
            A `ToolResult` summarizing every step's outcome, or an
            unsuccessful result if no workflow has that name.
        """
        name = (kwargs.get("name") or "").strip()
        workflow = self._store.get(name)
        if workflow is None:
            return ToolResult(success=False, message=f"No workflow named '{name}'.")

        run = self._engine.run(workflow)
        lines = [
            f"- {step.tool_name}: {'OK' if step.result.success else 'FAILED'} -- "
            f"{step.result.message}"
            for step in run.steps
        ]
        summary = f"Ran workflow '{name}' ({len(run.steps)} step(s)):\n" + "\n".join(lines)
        return ToolResult(success=run.all_succeeded, message=summary, data=run)
