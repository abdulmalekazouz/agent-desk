"""The decision layer: given a user's chat message, decide what to do.

`LLMProvider` is the seam a real model API would be wired in behind;
`MockLLMProvider` is a small, deterministic, rule-based implementation
(keyword/pattern matching) used instead, so the whole project runs
offline with no API key and fully predictable behavior. See the README
"Limitations" section.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

GREETINGS = frozenset({"hi", "hello", "hey", "hiya", "yo"})

HELP_TEXT = (
    "I'm a demo agent -- I can:\n"
    "- Read the mock inbox: try \"read my emails\" or \"check my inbox about budget\"\n"
    "- List mock files: try \"list my files\" or \"what's in Documents\"\n"
    "- Create a workflow: try \"create workflow Morning Briefing: read_emails, list_files\"\n"
    "- Run a workflow: try \"run workflow Morning Briefing\"\n"
    "Everything above operates on sample data, not your real accounts or files."
)

_ABOUT_QUERY_PATTERN = re.compile(r"\b(?:about|for|regarding)\s+(.+)$", re.IGNORECASE)
_IN_PATH_PATTERN = re.compile(r"\bin\s+([\w/\- ]+)$", re.IGNORECASE)
_WHATS_IN_PATTERN = re.compile(r"what'?s in\s+([\w/\- ]+)$", re.IGNORECASE)
_WORKFLOW_NAME_PATTERN = re.compile(r"workflow\s+([^:]+?)\s*:\s*(.+)$", re.IGNORECASE)
_RUN_WORKFLOW_PATTERN = re.compile(r"run\s+workflow\s+(.+)$", re.IGNORECASE)


@dataclass(frozen=True)
class TextReply:
    """A decision to answer directly, without invoking a tool.

    Attributes:
        text: The reply text to show the user.
    """

    text: str


@dataclass(frozen=True)
class ToolCallDecision:
    """A decision to invoke a specific tool.

    Attributes:
        tool_name: The name of the tool to call (must match a registered
            `Tool.name`).
        arguments: Keyword arguments to pass to the tool's `run`.
    """

    tool_name: str
    arguments: dict[str, Any]


Decision = TextReply | ToolCallDecision


class LLMProvider(ABC):
    """Decides how to respond to a user's chat message.

    A real integration would implement this by calling an actual model
    API; nothing elsewhere in `agentdesk.agent` needs to know which kind
    of provider it's talking to.
    """

    @abstractmethod
    def decide(self, message: str) -> Decision:
        """Decides how to respond to one user message.

        Args:
            message: The user's raw chat message.

        Returns:
            Either a `TextReply` (answer directly) or a `ToolCallDecision`
            (invoke a tool and report its result instead).
        """
        raise NotImplementedError

    @abstractmethod
    def summarize_tool_result(self, tool_name: str, result_message: str) -> str:
        """Turns a raw tool result into a final chat reply.

        Args:
            tool_name: The tool that was called.
            result_message: The tool's own human-readable result message.

        Returns:
            The text to show the user.
        """
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """A deterministic, rule-based stand-in for a real language model."""

    def decide(self, message: str) -> Decision:
        """Matches `message` against a small set of keyword patterns.

        Args:
            message: The user's raw chat message.

        Returns:
            A `ToolCallDecision` for recognized email/file/workflow
            requests, or a `TextReply` (a greeting, help text, or a
            generic "I didn't understand that" fallback) otherwise.
        """
        text = message.strip()
        lower = text.lower()

        if lower in GREETINGS:
            return TextReply(
                "Hi! Ask me to read your (mock) emails, list files, or build a "
                'workflow -- or say "help" for examples.'
            )
        if lower in {"help", "what can you do", "what can you do?"}:
            return TextReply(HELP_TEXT)

        run_match = _RUN_WORKFLOW_PATTERN.search(text)
        if run_match:
            return ToolCallDecision("run_workflow", {"name": run_match.group(1).strip()})

        workflow_match = _WORKFLOW_NAME_PATTERN.search(text)
        if "workflow" in lower and workflow_match:
            name, steps_text = workflow_match.groups()
            steps = [step.strip() for step in steps_text.split(",") if step.strip()]
            return ToolCallDecision("create_workflow", {"name": name.strip(), "steps": steps})

        if "email" in lower or "inbox" in lower:
            query_match = _ABOUT_QUERY_PATTERN.search(text)
            query = query_match.group(1).strip() if query_match else None
            return ToolCallDecision("read_emails", {"query": query})

        whats_in_match = _WHATS_IN_PATTERN.search(text)
        if "file" in lower or "folder" in lower or "directory" in lower or whats_in_match:
            if whats_in_match:
                path = whats_in_match.group(1).strip()
            else:
                path_match = _IN_PATH_PATTERN.search(text)
                path = path_match.group(1).strip() if path_match else ""
            return ToolCallDecision("list_files", {"path": path})

        return TextReply(f"I'm not sure how to help with that yet. {HELP_TEXT}")

    def summarize_tool_result(self, tool_name: str, result_message: str) -> str:
        """Passes the tool's own message straight through.

        A real LLM-backed provider would likely paraphrase or elaborate
        on `result_message` here instead of returning it verbatim.

        Args:
            tool_name: The tool that was called (unused by this simple
                implementation, but part of the interface since a real
                provider would likely want it).
            result_message: The tool's own human-readable result message.

        Returns:
            `result_message`, unchanged.
        """
        del tool_name  # Unused by this simple implementation.
        return result_message
