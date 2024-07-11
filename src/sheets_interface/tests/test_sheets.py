"""Tests for scan_processing.track.sheets.py."""

import pytest
from google.auth.exceptions import DefaultCredentialsError

from src.sheets_interface.sheets import TrackingSheet
from src.sheets_interface.sheets import TRACKING_PATH

SPREADSHEET_ID = ""
TEST_TAB = "unit-testing"
TEST_RANGE = "A1:C"


@pytest.mark.skip_on_github_actions()
def test_credentials_file() -> None:
    """Test get_tracking_data."""
    credentials_path = TRACKING_PATH / "sheet_credentials.json"
    assert credentials_path.exists()


@pytest.mark.skip_on_github_actions()
def test_token_file() -> None:
    """Test token data."""
    sheet = TrackingSheet(SPREADSHEET_ID, TEST_TAB, TEST_RANGE)
    sheet.login()
    token_path = TRACKING_PATH / "sheet_token.json"
    assert token_path.exists()


@pytest.mark.skip_on_github_actions()
def test_get_tracking_data() -> None:
    """Test get_tracking_data."""
    sheet = TrackingSheet(SPREADSHEET_ID, TEST_TAB, TEST_RANGE)
    sheet.login()
    columns, data = sheet.get_tracking_data()
    assert data is not None
    assert isinstance(data, list)
    assert isinstance(data[0], dict)
    assert isinstance(data[0]["Request_UUID"], str)
    assert columns[0] == "Request_UUID"
    assert columns[1] == "Cell_SN"
    assert columns[2] == "Completed"
    assert data[0]["Request_UUID"] == "request1"
    assert data[0]["Cell_SN"] == "some_num"
    assert data[0]["Completed"] == "Done"


@pytest.mark.skip_on_github_actions()
def test_get_tracking_data_no_credentials() -> None:
    """Test get_tracking_data."""
    sheet = TrackingSheet(SPREADSHEET_ID, TEST_TAB, TEST_RANGE)
    with pytest.raises(DefaultCredentialsError):
        columns, data = sheet.get_tracking_data()


@pytest.mark.skip_on_github_actions()
def test_get_tracking_data_no_sheet_id() -> None:
    """Test get_tracking_data."""
    sheet = TrackingSheet("", TEST_TAB, TEST_RANGE)
    sheet.login()
    with pytest.raises(ConnectionError):
        columns, data = sheet.get_tracking_data()


@pytest.mark.skip_on_github_actions()
def test_get_tracking_data_no_range_name() -> None:
    """Test get_tracking_data."""
    sheet = TrackingSheet(SPREADSHEET_ID, TEST_TAB, "")
    sheet.login()
    with pytest.raises(ConnectionError):
        columns, data = sheet.get_tracking_data()


@pytest.mark.skip_on_github_actions()
def test_put_value_by_address() -> None:
    """Test put_value_by_address."""
    sheet = TrackingSheet(SPREADSHEET_ID, TEST_TAB, TEST_RANGE)
    sheet.login()
    sheet.put_single_value_by_address(row=3, column="C", status="Queued")
    columns, data = sheet.get_tracking_data()
    assert data[1]["Completed"] == "Queued"


@pytest.mark.skip_on_github_actions()
def test_find_row() -> None:
    """Test find_row."""
    sheet = TrackingSheet(SPREADSHEET_ID, TEST_TAB, TEST_RANGE)
    sheet.login()
    row = sheet.find_row("request1", "some_num")
    assert row == 2


@pytest.mark.skip_on_github_actions()
def test_find_next_unused_row() -> None:
    """Test find_next_unused_row."""
    sheet = TrackingSheet(SPREADSHEET_ID, TEST_TAB, TEST_RANGE)
    sheet.login()
    if not sheet.request_complete("request1"):
        row, sn = sheet.next_unused_row_sn("request1")
        assert row == 4
        assert sn == "just_entered"


@pytest.mark.skip_on_github_actions()
def test_completed_request() -> None:
    """Test find_next_unused_row."""
    sheet = TrackingSheet(SPREADSHEET_ID, TEST_TAB, TEST_RANGE)
    sheet.login()
    assert sheet.request_complete("request2")
