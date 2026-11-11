"""Small, shared widget-construction helpers used by more than one screen."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel


def heading_label(text: str) -> QLabel:
    """Builds a `QLabel` styled as a screen heading.

    Args:
        text: The heading text.

    Returns:
        A `QLabel` with its `heading` dynamic property set to `True`, so
        `styles.qss`'s `QLabel[heading="true"]` rule applies to it.
    """
    label = QLabel(text)
    label.setProperty("heading", True)
    return label
