"""Generates the README screenshots for each GUI screen.

Deliberately does NOT call `window.show()` -- it renders each screen via
Qt's own `QWidget.grab()`, so this never opens a visible window on
screen. Run with the platform's normal (non-offscreen) Qt plugin so
fonts render correctly; see the README for why `offscreen` alone isn't
enough for that on some platforms.

Usage:
    python scripts/capture_screenshots.py [output_dir]
"""

from __future__ import annotations

import sys
from importlib import resources
from pathlib import Path

from PySide6.QtWidgets import QApplication

from agentdesk.agent.factory import build_default_agent
from agentdesk.gui.main_window import MainWindow

SCREEN_NAMES = ("chat", "inbox", "workflows", "permissions")


def _populate_demo_state(app: QApplication, window: MainWindow) -> None:
    """Fills the app with realistic sample interactions for the screenshots.

    Keeps the Chat transcript to two short exchanges deliberately: an
    unshown `QTextBrowser` (this script never calls `window.show()`)
    never computes a real scrollable range, so it always renders from
    the top of its content -- a short transcript that fits within the
    viewport sidesteps that rather than fighting it.

    The workflow is created and run through the Workflows screen's own
    input fields and buttons (as a real user would), not via chat, so
    the Chat screenshot's transcript/trace stay focused on email/file
    lookups and the Workflows screenshot shows its own output panel.

    Args:
        app: The running `QApplication`, used to pump its event loop.
        window: The window to populate.
    """
    for message in ("check my inbox about budget", "list my files"):
        window.chat_screen.send_message(message)
        app.processEvents()

    workflows = window.workflows_screen
    workflows.name_input.setText("Morning Briefing")
    workflows.steps_input.setText("read_emails, list_files")
    workflows._on_create_clicked()
    workflows.workflow_list.setCurrentRow(0)
    workflows._on_run_clicked()
    app.processEvents()


def main() -> int:
    """Captures one screenshot per screen.

    Returns:
        The process exit code (0 on success).
    """
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    output_dir.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv[:1])
    stylesheet = resources.files("agentdesk.gui").joinpath("styles.qss").read_text(encoding="utf-8")
    app.setStyleSheet(stylesheet)

    bundle = build_default_agent()
    window = MainWindow(bundle)
    window.resize(960, 640)
    app.processEvents()
    _populate_demo_state(app, window)

    for index, name in enumerate(SCREEN_NAMES):
        window.sidebar.setCurrentRow(index)
        app.processEvents()
        pixmap = window.grab()
        destination = output_dir / f"screenshot-{name}.jpg"
        pixmap.save(str(destination), "JPG", quality=90)
        print(f"Saved {destination} ({pixmap.width()}x{pixmap.height()})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
