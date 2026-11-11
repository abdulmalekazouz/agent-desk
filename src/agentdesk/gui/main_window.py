"""The main application window: a sidebar nav plus a stacked content area."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from agentdesk.agent.factory import AgentBundle
from agentdesk.gui.screens.chat_screen import ChatScreen
from agentdesk.gui.screens.inbox_screen import InboxScreen
from agentdesk.gui.screens.permissions_screen import PermissionsScreen
from agentdesk.gui.screens.workflows_screen import WorkflowsScreen

NAV_ITEMS = ("Chat", "Inbox", "Workflows", "Permissions")


class MainWindow(QMainWindow):
    """The application's top-level window: sidebar nav + stacked screens."""

    def __init__(self, bundle: AgentBundle) -> None:
        """Builds the window and every screen.

        Args:
            bundle: The agent, permission registry, and workflow store
                to wire into the relevant screens.
        """
        super().__init__()
        self.setWindowTitle("Agent Desk")
        self.resize(960, 640)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        for name in NAV_ITEMS:
            QListWidgetItem(name, self.sidebar)
        self.sidebar.setFixedWidth(180)
        self.sidebar.currentRowChanged.connect(self._on_nav_changed)

        self.chat_screen = ChatScreen(bundle.agent)
        self.inbox_screen = InboxScreen()
        self.workflows_screen = WorkflowsScreen(bundle.workflow_store, bundle.agent)
        self.permissions_screen = PermissionsScreen(bundle.permissions)

        self.stack = QStackedWidget()
        for screen in (
            self.chat_screen,
            self.inbox_screen,
            self.workflows_screen,
            self.permissions_screen,
        ):
            self.stack.addWidget(screen)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, stretch=1)
        self.setCentralWidget(central)

        self.sidebar.setCurrentRow(0)

    def _on_nav_changed(self, index: int) -> None:
        """Switches the visible screen and refreshes it if it supports that.

        Args:
            index: The newly selected sidebar row.
        """
        self.stack.setCurrentIndex(index)
        widget = self.stack.widget(index)
        refresh = getattr(widget, "refresh", None)
        if callable(refresh):
            refresh()
