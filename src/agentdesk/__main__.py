"""Entry point: `python -m agentdesk`, or the `agentdesk` console script."""

from __future__ import annotations

import sys
from importlib import resources

from PySide6.QtWidgets import QApplication

from agentdesk.agent.factory import build_default_agent
from agentdesk.gui.main_window import MainWindow


def main() -> int:
    """Launches the Agent Desk application.

    Returns:
        The process exit code, from `QApplication.exec()`.
    """
    app = QApplication(sys.argv)

    stylesheet = resources.files("agentdesk.gui").joinpath("styles.qss").read_text(encoding="utf-8")
    app.setStyleSheet(stylesheet)

    bundle = build_default_agent()
    window = MainWindow(bundle)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
