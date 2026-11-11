"""Tests for the agentdesk.agent.tools base contract."""

import pytest

from agentdesk.agent.tools import Tool, ToolResult


class _EchoTool(Tool):
    name = "echo"
    description = "Echoes back whatever text it is given."
    required_permission = "demo.echo"

    def run(self, **kwargs):
        text = kwargs.get("text", "")
        return ToolResult(success=True, message=f"echo: {text}", data=text)


def test_tool_result_defaults_data_to_none():
    result = ToolResult(success=True, message="done")
    assert result.data is None


def test_concrete_tool_runs_and_returns_a_result():
    tool = _EchoTool()
    result = tool.run(text="hello")
    assert result.success is True
    assert result.message == "echo: hello"
    assert result.data == "hello"


def test_tool_is_abstract_and_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        Tool()
