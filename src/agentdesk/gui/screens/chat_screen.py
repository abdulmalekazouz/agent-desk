"""The chat screen: talk to the agent and inspect its reasoning trace."""

from __future__ import annotations

import html
from collections.abc import Sequence

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from agentdesk.agent.agent import Agent, TraceEntry
from agentdesk.gui.widgets import heading_label

WELCOME_MESSAGE = (
    "Hi! Ask me to read your (mock) emails, list files, or build a workflow -- "
    'or say "help" for examples.'
)


class ChatScreen(QWidget):
    """Lets the user chat with the agent and see its per-message trace."""

    def __init__(self, agent: Agent) -> None:
        """Initializes the screen.

        Args:
            agent: The agent to send messages to.
        """
        super().__init__()
        self._agent = agent

        self.transcript = QTextBrowser()
        self.transcript.setObjectName("transcript")

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Try "read my emails" or "help"...')
        self.input_field.returnPressed.connect(self._on_send_clicked)

        send_button = QPushButton("Send")
        send_button.setObjectName("primaryButton")
        send_button.clicked.connect(self._on_send_clicked)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_field, stretch=1)
        input_row.addWidget(send_button)

        self.trace_label = QLabel("Trace for the last message will appear here.")
        self.trace_label.setObjectName("traceLabel")
        self.trace_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(heading_label("Chat"))
        layout.addWidget(self.transcript, stretch=1)
        layout.addLayout(input_row)
        layout.addWidget(self.trace_label)

        self._append_assistant_message(WELCOME_MESSAGE)

    def send_message(self, text: str) -> None:
        """Sends a message as if the user had typed and submitted it.

        Args:
            text: The message text.
        """
        self.input_field.setText(text)
        self._on_send_clicked()

    def transcript_text(self) -> str:
        """Returns the chat transcript's current plain text.

        Returns:
            The transcript content, with HTML markup stripped.
        """
        return self.transcript.toPlainText()

    def _on_send_clicked(self) -> None:
        """Handles the Send button / Enter key: sends the input field's text."""
        text = self.input_field.text().strip()
        if not text:
            return

        self.input_field.clear()
        self._append_user_message(text)

        response = self._agent.handle_message(text)
        self._append_assistant_message(response.reply)
        self._update_trace(response.trace)

    def _append_user_message(self, text: str) -> None:
        self._append_html(f"<p><b>You:</b> {html.escape(text)}</p>")

    def _append_assistant_message(self, text: str) -> None:
        escaped = html.escape(text).replace("\n", "<br>")
        self._append_html(f"<p><b>Agent:</b> {escaped}</p>")

    def _append_html(self, snippet: str) -> None:
        """Appends an HTML snippet to the transcript and scrolls to it.

        `QTextBrowser.append` only auto-scrolls when the view was already
        exactly at the bottom; explicitly moving the cursor and calling
        `ensureCursorVisible` keeps the latest message in view
        regardless (e.g. before the widget has ever been shown/laid out,
        such as when building screenshots programmatically).

        Args:
            snippet: The HTML to append as a new paragraph.
        """
        self.transcript.append(snippet)
        self.transcript.moveCursor(QTextCursor.MoveOperation.End)
        self.transcript.ensureCursorVisible()

    def _update_trace(self, trace: Sequence[TraceEntry]) -> None:
        lines = [f"[{entry.kind}] {entry.detail}" for entry in trace]
        self.trace_label.setText("Trace:\n" + "\n".join(lines))
