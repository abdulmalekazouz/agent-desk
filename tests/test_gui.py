"""Smoke tests for the PySide6 GUI.

Run with the Qt "offscreen" platform plugin (no real display needed),
set via the QT_QPA_PLATFORM environment variable in CI and in local dev
(see the README). pytest-qt's `qtbot` fixture manages widget lifetime.
"""

from __future__ import annotations

from agentdesk.agent.factory import build_default_agent
from agentdesk.gui.main_window import MainWindow


def _build_window(qtbot):
    bundle = build_default_agent()
    window = MainWindow(bundle)
    qtbot.addWidget(window)
    return window, bundle


def test_main_window_starts_on_the_chat_screen(qtbot):
    window, _ = _build_window(qtbot)
    assert window.stack.currentWidget() is window.chat_screen


def test_sending_a_chat_message_updates_the_transcript_and_trace(qtbot):
    window, _ = _build_window(qtbot)

    window.chat_screen.send_message("list my files")

    assert "Documents" in window.chat_screen.transcript_text()
    assert "list_files" in window.chat_screen.trace_label.text()


def test_navigating_to_inbox_shows_mock_emails(qtbot):
    window, _ = _build_window(qtbot)

    window.sidebar.setCurrentRow(1)

    assert window.stack.currentWidget() is window.inbox_screen
    assert window.inbox_screen.email_list.count() > 0


def test_creating_a_workflow_through_the_gui_lists_it(qtbot):
    window, _ = _build_window(qtbot)
    window.sidebar.setCurrentRow(2)

    screen = window.workflows_screen
    screen.name_input.setText("Morning Briefing")
    screen.steps_input.setText("read_emails, list_files")
    screen._on_create_clicked()

    assert screen.workflow_list.count() == 1
    assert "Morning Briefing" in screen.workflow_list.item(0).text()


def test_running_the_selected_workflow_shows_output(qtbot):
    window, _ = _build_window(qtbot)
    screen = window.workflows_screen
    screen.name_input.setText("Morning Briefing")
    screen.steps_input.setText("read_emails")
    screen._on_create_clicked()

    screen.workflow_list.setCurrentRow(0)
    screen._on_run_clicked()

    assert "read_emails" in screen.output_view.toPlainText()


def test_toggling_a_permission_updates_the_shared_registry(qtbot):
    window, bundle = _build_window(qtbot)
    window.sidebar.setCurrentRow(3)

    checkbox = window.permissions_screen.checkboxes["email.read"]
    checkbox.setChecked(False)

    assert bundle.permissions.is_granted("email.read") is False


def test_revoked_permission_is_reflected_in_a_chat_response(qtbot):
    window, bundle = _build_window(qtbot)
    bundle.permissions.set_granted("files.read", False)

    window.chat_screen.send_message("list my files")

    assert "permission" in window.chat_screen.transcript_text().lower()


def test_workflows_screen_refreshes_workflows_created_via_chat(qtbot):
    window, _ = _build_window(qtbot)

    window.chat_screen.send_message("create workflow From Chat: read_emails")
    window.sidebar.setCurrentRow(2)  # Triggers WorkflowsScreen.refresh().

    items = [
        window.workflows_screen.workflow_list.item(i).text()
        for i in range(window.workflows_screen.workflow_list.count())
    ]
    assert any("From Chat" in item for item in items)
