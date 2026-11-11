"""agentdesk: a desktop AI-agent assistant.

A PySide6 desktop app wrapping a small, transparent agent loop: a mock
LLM decides which "tool" (a sandboxed, simulated action -- reading a
mock inbox, listing mock files, running a workflow) to invoke, a
permission system gates what the agent is allowed to do, and every step
is logged to a visible trace. See the README for why the LLM and the
actions it takes are deliberately mocked/simulated rather than wired up
to a real account or a real model API.
"""

__version__ = "0.1.0"
