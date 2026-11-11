"""The permissions screen: see and revoke what the agent is allowed to do."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QCheckBox, QLabel, QVBoxLayout, QWidget

from agentdesk.agent.permissions import KNOWN_PERMISSIONS, PermissionRegistry
from agentdesk.gui.widgets import heading_label


class PermissionsScreen(QWidget):
    """Lets the user see and toggle each tool's required permission."""

    def __init__(self, permissions: PermissionRegistry) -> None:
        """Initializes the screen with one checkbox per known permission.

        Args:
            permissions: The shared permission registry to read from and
                write to.
        """
        super().__init__()
        self._permissions = permissions
        self.checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(heading_label("Permissions"))

        subtitle = QLabel(
            "Every tool the agent can use is gated by one of these. Turn one off "
            "to see the agent refuse the matching request."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        for info in KNOWN_PERMISSIONS:
            checkbox = QCheckBox(f"{info.label} -- {info.description}")
            checkbox.setChecked(permissions.is_granted(info.name))
            checkbox.toggled.connect(self._make_toggle_handler(info.name))
            self.checkboxes[info.name] = checkbox
            layout.addWidget(checkbox)

        layout.addStretch(1)

    def _make_toggle_handler(self, permission_name: str) -> Callable[[bool], None]:
        """Builds a closure that writes one permission's toggled state.

        Args:
            permission_name: The permission this checkbox controls.

        Returns:
            A callable suitable for connecting to `QCheckBox.toggled`.
        """

        def handler(checked: bool) -> None:
            self._permissions.set_granted(permission_name, checked)

        return handler
