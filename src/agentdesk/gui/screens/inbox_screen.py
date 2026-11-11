"""The inbox screen: browse the sample mock emails.

Reads `agentdesk.agent.mock_data` directly rather than going through the
agent, since simply browsing a list is not itself an agent action.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from agentdesk.agent.mock_data import MOCK_INBOX
from agentdesk.gui.widgets import heading_label


class InboxScreen(QWidget):
    """Displays the sample mock inbox: a list plus a reading pane."""

    def __init__(self) -> None:
        """Initializes the screen and populates it with `MOCK_INBOX`."""
        super().__init__()

        self.email_list = QListWidget()
        for email in MOCK_INBOX:
            QListWidgetItem(f"{email.subject}\n{email.sender}", self.email_list)
        self.email_list.currentRowChanged.connect(self._on_selection_changed)

        self.detail_view = QTextBrowser()

        splitter = QSplitter()
        splitter.addWidget(self.email_list)
        splitter.addWidget(self.detail_view)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(heading_label("Mock Inbox"))
        layout.addWidget(splitter, stretch=1)

        if MOCK_INBOX:
            self.email_list.setCurrentRow(0)

    def _on_selection_changed(self, index: int) -> None:
        """Shows the selected email's full body in the detail pane.

        Args:
            index: The newly selected row in `email_list`, or -1 if
                nothing is selected.
        """
        if not (0 <= index < len(MOCK_INBOX)):
            self.detail_view.clear()
            return

        email = MOCK_INBOX[index]
        self.detail_view.setHtml(
            f"<h3>{email.subject}</h3>"
            f"<p><b>From:</b> {email.sender}<br><b>Date:</b> {email.date}</p>"
            f"<p>{email.body}</p>"
        )
