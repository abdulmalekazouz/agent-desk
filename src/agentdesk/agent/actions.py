"""Concrete sandboxed tools: reading the mock inbox and listing mock files.

Workflow-related tools (creating/running a saved workflow) are added in
`agentdesk.agent.workflow_tools`.
"""

from __future__ import annotations

from agentdesk.agent.mock_data import MOCK_INBOX, list_directory
from agentdesk.agent.tools import Tool, ToolResult


class ReadEmailsTool(Tool):
    """Reads (optionally filtering) the sample mock inbox."""

    name = "read_emails"
    description = "Reads the mock inbox, optionally filtered by a search term."
    required_permission = "email.read"

    def run(self, **kwargs) -> ToolResult:
        """Lists mock emails, optionally filtered.

        Args:
            **kwargs: May include `query` (str | None) -- a case-insensitive
                substring matched against the sender, subject, and body.

        Returns:
            A `ToolResult` whose `message` is a readable summary and
            whose `data` is the list of matching emails (as dicts).
        """
        query = (kwargs.get("query") or "").strip().lower()

        matches = [
            email
            for email in MOCK_INBOX
            if not query
            or query in email.subject.lower()
            or query in email.sender.lower()
            or query in email.body.lower()
        ]

        if not matches:
            return ToolResult(success=True, message="No matching emails found.", data=[])

        lines = [f"- From {email.sender}: \"{email.subject}\" ({email.date})" for email in matches]
        summary = f"Found {len(matches)} email(s):\n" + "\n".join(lines)
        return ToolResult(
            success=True,
            message=summary,
            data=[
                {
                    "sender": email.sender,
                    "subject": email.subject,
                    "body": email.body,
                    "date": email.date,
                }
                for email in matches
            ],
        )


class ListFilesTool(Tool):
    """Lists the contents of a mock directory."""

    name = "list_files"
    description = "Lists the entries of a mock directory."
    required_permission = "files.read"

    def run(self, **kwargs) -> ToolResult:
        """Lists a mock directory's contents.

        Args:
            **kwargs: May include `path` (str) -- a `/`-separated mock
                directory path; defaults to the root.

        Returns:
            A `ToolResult` describing the directory's entries, or an
            unsuccessful result if `path` does not exist.
        """
        path = kwargs.get("path") or ""
        entries = list_directory(path)

        if entries is None:
            return ToolResult(
                success=False, message=f"No such mock directory: '{path or '/'}'."
            )
        if not entries:
            return ToolResult(success=True, message=f"'{path or '/'}' is empty.", data=[])

        summary = f"Contents of '{path or '/'}':\n" + "\n".join(f"- {entry}" for entry in entries)
        return ToolResult(success=True, message=summary, data=entries)
