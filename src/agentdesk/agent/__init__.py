"""The agent core: tools, the (mock) LLM decision layer, permissions, and
the orchestrator that ties them into a single request/response loop.

Nothing in this package depends on the GUI -- it is plain, independently
testable Python, with PySide6 only used by `agentdesk.gui` to present it.
"""
