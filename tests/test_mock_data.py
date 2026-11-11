"""Tests for agentdesk.agent.mock_data."""

from agentdesk.agent.mock_data import MOCK_INBOX, list_directory


def test_mock_inbox_is_non_empty():
    assert len(MOCK_INBOX) > 0


def test_list_directory_root():
    entries = list_directory("")
    assert entries is not None
    assert "Documents" in entries
    assert "budget_report.xlsx" in entries


def test_list_directory_nested_path():
    entries = list_directory("Photos/vacation_2025")
    assert entries == ["beach.jpg", "sunset.jpg"]


def test_list_directory_unknown_path_returns_none():
    assert list_directory("NoSuchFolder") is None


def test_list_directory_on_a_file_returns_none():
    assert list_directory("budget_report.xlsx") is None


def test_list_directory_handles_leading_and_trailing_slashes():
    assert list_directory("/Documents/") == sorted(
        ["resume.pdf", "cover_letter.docx", "notes.txt"]
    )
