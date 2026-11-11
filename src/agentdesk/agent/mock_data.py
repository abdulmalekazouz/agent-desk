"""Built-in sample data standing in for a real inbox/filesystem.

Nothing in this module reads or touches anything on the real computer it
runs on -- see the README "Limitations" section.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MockEmail:
    """One sample email.

    Attributes:
        sender: The sender's display name and address.
        subject: The email subject line.
        body: The email body text.
        date: An ISO-8601 date string.
    """

    sender: str
    subject: str
    body: str
    date: str


MOCK_INBOX: tuple[MockEmail, ...] = (
    MockEmail(
        sender="Priya Natarajan <priya@northwind.example>",
        subject="Q3 budget review -- action needed",
        body=(
            "Hi team, the Q3 budget review is due Friday. Please send me your "
            "department's numbers by Wednesday so I have time to consolidate."
        ),
        date="2026-03-02",
    ),
    MockEmail(
        sender="GitHub <notifications@github.example>",
        subject="[agent-desk] New pull request: Add workflow engine",
        body="A new pull request was opened in abdulmalekazouz/agent-desk.",
        date="2026-03-03",
    ),
    MockEmail(
        sender="Marcus Chen <marcus@northwind.example>",
        subject="Re: Interview availability next week",
        body=(
            "Thanks for the update! Tuesday at 2pm works well for me. I'll send "
            "a calendar invite shortly."
        ),
        date="2026-03-04",
    ),
    MockEmail(
        sender="Billing <billing@cloudhost.example>",
        subject="Your invoice for February is ready",
        body="Your invoice (#88213) for $42.00 is now available in your account.",
        date="2026-03-01",
    ),
)


# A small nested mock filesystem: directories map to dicts, files map to
# `None`.
MockDirectory = dict[str, "MockDirectory | None"]

MOCK_FILESYSTEM: MockDirectory = {
    "Documents": {
        "resume.pdf": None,
        "cover_letter.docx": None,
        "notes.txt": None,
    },
    "Photos": {
        "vacation_2025": {
            "beach.jpg": None,
            "sunset.jpg": None,
        },
    },
    "Projects": {
        "agent-desk": {
            "README.md": None,
            "pyproject.toml": None,
        },
    },
    "budget_report.xlsx": None,
}


def list_directory(path: str) -> list[str] | None:
    """Lists the entries of a mock directory.

    Args:
        path: A `/`-separated path, e.g. `"Documents"` or
            `"Photos/vacation_2025"`. An empty string or `"/"` means the
            root directory.

    Returns:
        A sorted list of entry names (directories and files), or `None`
        if `path` does not refer to a directory in the mock filesystem
        (either it doesn't exist, or it names a file).
    """
    node: MockDirectory | None = MOCK_FILESYSTEM
    segments = [segment for segment in path.strip("/").split("/") if segment]

    for segment in segments:
        if not isinstance(node, dict) or segment not in node:
            return None
        node = node[segment]

    if not isinstance(node, dict):
        return None
    return sorted(node.keys())
