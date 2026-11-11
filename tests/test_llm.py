"""Tests for agentdesk.agent.llm.MockLLMProvider."""

from agentdesk.agent.llm import MockLLMProvider, TextReply, ToolCallDecision

llm = MockLLMProvider()


def test_greeting_gets_a_text_reply():
    decision = llm.decide("hello")
    assert isinstance(decision, TextReply)


def test_help_gets_a_text_reply_mentioning_every_capability():
    decision = llm.decide("help")
    assert isinstance(decision, TextReply)
    assert "emails" in decision.text
    assert "files" in decision.text
    assert "workflow" in decision.text


def test_read_emails_intent():
    decision = llm.decide("read my emails")
    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "read_emails"
    assert decision.arguments["query"] is None


def test_read_emails_intent_with_a_query():
    decision = llm.decide("check my inbox about budget")
    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "read_emails"
    assert decision.arguments["query"] == "budget"


def test_list_files_intent():
    decision = llm.decide("list my files")
    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "list_files"
    assert decision.arguments["path"] == ""


def test_list_files_intent_with_a_path():
    decision = llm.decide("what's in Documents")
    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "list_files"
    assert decision.arguments["path"] == "Documents"


def test_create_workflow_intent():
    decision = llm.decide("create workflow Morning Briefing: read_emails, list_files")
    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "create_workflow"
    assert decision.arguments["name"] == "Morning Briefing"
    assert decision.arguments["steps"] == ["read_emails", "list_files"]


def test_run_workflow_intent():
    decision = llm.decide("run workflow Morning Briefing")
    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "run_workflow"
    assert decision.arguments["name"] == "Morning Briefing"


def test_unrecognized_message_falls_back_to_help():
    decision = llm.decide("what's the meaning of life?")
    assert isinstance(decision, TextReply)
    assert "not sure" in decision.text.lower()


def test_summarize_tool_result_passes_message_through():
    assert llm.summarize_tool_result("read_emails", "Found 2 emails.") == "Found 2 emails."
