"""Tests for agentdesk.agent.actions."""

from agentdesk.agent.actions import ListFilesTool, ReadEmailsTool


def test_read_emails_with_no_query_returns_everything():
    result = ReadEmailsTool().run(query=None)
    assert result.success is True
    assert len(result.data) == 4


def test_read_emails_filters_by_query():
    result = ReadEmailsTool().run(query="budget")
    assert result.success is True
    assert len(result.data) == 1
    assert "budget" in result.data[0]["subject"].lower()


def test_read_emails_query_is_case_insensitive():
    result = ReadEmailsTool().run(query="BUDGET")
    assert len(result.data) == 1


def test_read_emails_no_matches_still_succeeds_with_empty_data():
    result = ReadEmailsTool().run(query="no such thing in any email")
    assert result.success is True
    assert result.data == []


def test_list_files_root():
    result = ListFilesTool().run(path="")
    assert result.success is True
    assert "Documents" in result.data


def test_list_files_nested_path():
    result = ListFilesTool().run(path="Documents")
    assert result.success is True
    assert "resume.pdf" in result.data


def test_list_files_unknown_path_fails_gracefully():
    result = ListFilesTool().run(path="NoSuchFolder")
    assert result.success is False
    assert "NoSuchFolder" in result.message
