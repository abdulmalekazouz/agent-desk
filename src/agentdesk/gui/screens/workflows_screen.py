"""The workflows screen: create and run saved workflows.

Goes through the same `Agent.handle_message` chat path the Chat screen
uses (by sending the equivalent "create workflow ..."/"run workflow ..."
text), so the GUI and the chat interface stay in sync and demonstrate
the same underlying behavior.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from agentdesk.agent.agent import Agent
from agentdesk.agent.workflows import WorkflowStore
from agentdesk.gui.widgets import heading_label


class WorkflowsScreen(QWidget):
    """Lets the user create and run workflows, and see saved ones."""

    def __init__(self, workflow_store: WorkflowStore, agent: Agent) -> None:
        """Initializes the screen.

        Args:
            workflow_store: Where saved workflows are read from.
            agent: The agent that actually creates/runs workflows.
        """
        super().__init__()
        self._store = workflow_store
        self._agent = agent

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Workflow name")
        self.steps_input = QLineEdit()
        self.steps_input.setPlaceholderText("Steps, comma-separated (e.g. read_emails, list_files)")

        create_button = QPushButton("Create")
        create_button.clicked.connect(self._on_create_clicked)

        form_row = QHBoxLayout()
        form_row.addWidget(self.name_input)
        form_row.addWidget(self.steps_input, stretch=1)
        form_row.addWidget(create_button)

        self.workflow_list = QListWidget()

        run_button = QPushButton("Run selected")
        run_button.setObjectName("primaryButton")
        run_button.clicked.connect(self._on_run_clicked)

        self.output_view = QTextBrowser()

        layout = QVBoxLayout(self)
        layout.addWidget(heading_label("Workflows"))
        layout.addLayout(form_row)
        layout.addWidget(self.workflow_list)
        layout.addWidget(run_button)
        layout.addWidget(self.output_view)

        self.refresh()

    def refresh(self) -> None:
        """Reloads the workflow list from the shared store.

        Called whenever this screen becomes visible, so workflows
        created from the Chat screen also show up here.
        """
        self.workflow_list.clear()
        for workflow in self._store.all():
            self.workflow_list.addItem(f"{workflow.name} ({len(workflow.steps)} step(s))")

    def _on_create_clicked(self) -> None:
        """Creates a workflow from the name/steps fields via the agent."""
        name = self.name_input.text().strip()
        steps = self.steps_input.text().strip()
        if not name or not steps:
            self.output_view.setPlainText("Enter both a name and at least one step.")
            return

        response = self._agent.handle_message(f"create workflow {name}: {steps}")
        self.output_view.setPlainText(response.reply)
        self.name_input.clear()
        self.steps_input.clear()
        self.refresh()

    def _on_run_clicked(self) -> None:
        """Runs the currently selected workflow via the agent."""
        row = self.workflow_list.currentRow()
        workflows = self._store.all()
        if not (0 <= row < len(workflows)):
            self.output_view.setPlainText("Select a workflow to run first.")
            return

        response = self._agent.handle_message(f"run workflow {workflows[row].name}")
        self.output_view.setPlainText(response.reply)
