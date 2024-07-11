"""Create a Google Sheets API service object and output data from a spreadsheet."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TRACKING_PATH = Path(__file__).resolve().parents[1]

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# https://docs.google.com/spreadsheets/d/1aTY9W65EznsZmflq3DdjuvoKCbgTLrPAoApdOgyPORo/edit?usp=sharing
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = ""
REQUEST_AND_SN_COLUMNS = 2
TEST_TAB = "unit-testing"
TEST_RANGE = "A1:C"


class TrackingSheet:
    """Class for tracking the scan."""

    def __init__(self, sheet_id: str, tab_name: str, cell_range: str = "A1:C") -> None:
        self.sheet_id = sheet_id
        self.tab_name = tab_name
        self.cell_range = cell_range
        self.creds: None | Credentials = None
        self.num_columns = REQUEST_AND_SN_COLUMNS

    def login(self) -> None:
        """Login to Google Sheets."""
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_path = TRACKING_PATH / "sheet_token.json"
        if token_path.exists():
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            if not self.creds.valid:
                self.creds = None
            elif self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                return

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds:
            credentials_path = TRACKING_PATH / "sheet_credentials.json"
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with Path(token_path).open("w") as token:
                token.write(self.creds.to_json())

    def get_tracking_data(self) -> tuple[list[str], list[dict[str, str]]]:
        """Get values from tracking sheet.

        Prints values from a sample spreadsheet.

        Raises
        ------
        ConnectionError
            If the connection to the Google Sheet fails.

        Returns
        -------
        list[str]
            column_names
                The column names of the cells. First row of the sheet.
        list[dict[str, str]]
            column_data
                The values of the cells. Remaining rows of the sheet.
        """
        sheet_range = f"{self.tab_name}!{self.cell_range}"
        try:
            service = build("sheets", "v4", credentials=self.creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.sheet_id, range=sheet_range).execute()
            values = result.get("values", [])

            if not values:
                msg = "No data found."
                raise ValueError(msg)

        except HttpError as err:
            raise ConnectionError from err

        column_names = values[0]

        data = []
        for row in values[1:]:
            row_dict = {}
            for column_indx, column_value in enumerate(row):
                row_dict[column_names[column_indx]] = column_value
            data.append(row_dict)

        return column_names, data

    def put_single_value_by_address(self, row: int, column: str, status: str) -> None:
        """Put the tracking status to the tracking sheet.

        Parameters
        ----------
        row
            The row number.
        column
            Column letter.
        status
            The tracking status.

        Raises
        ------
        ConnectionError
            If the connection to the Google Sheet fails.
        """
        try:
            service = build("sheets", "v4", credentials=self.creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            body = {"values": [[status]], "majorDimension": "COLUMNS"}

            cell_address = f"{self.tab_name}!{column}{row!s}"
            result = (
                sheet.values()
                .update(
                    spreadsheetId=self.sheet_id,
                    range=cell_address,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )

        except HttpError as err:
            raise ConnectionError from err

        return result

    def find_row(self, request_uuid: str, cell_sn: str) -> int:
        """Find the row number by the request UUID.

        Parameters
        ----------
        request_uuid
            The request UUID.
        cell_sn
            The cell SN.

        Raises
        ------
        ValueError
            If the request UUID and cell SN are not found or found multiple times.

        Returns
        -------
        int
            The row number.
        """
        column_names, data = self.get_tracking_data()
        row_ids = []
        for row, row_data in enumerate(data):
            if (
                len(row_data) > 0
                and row_data["Request_UUID"] == request_uuid
                and len(row_data) > 1
                and row_data["Cell_SN"] == cell_sn
            ):
                row_ids.append(row + 2)
        if len(row_ids) == 0:
            msg = f"Request UUID {request_uuid} and Cell SN {cell_sn} not found."
            raise ValueError(msg)

        if len(row_ids) > 1:
            msg = f"Request UUID {request_uuid} and Cell SN {cell_sn} found multiple times."
            raise ValueError(msg)

        return row_ids[0]

    def request_complete(self, request_uuid: str) -> bool:
        """Determine if the request is done.

        If there are any rows with the request UUID and a cell SN but no status, then the request is not done.
        If there are rows with the request UUID and no cell SN, then the request is done.

        Parameters
        ----------
        request_uuid
            The request UUID.

        Returns
        -------
        bool
            True if the request is done.
        """
        column_names, data = self.get_tracking_data()
        for row_data in data:
            if len(row_data) > 1 and row_data["Request_UUID"] == request_uuid and len(row_data) == self.num_columns:
                return False
            if (
                len(row_data) > self.num_columns
                and row_data["Request_UUID"] == request_uuid
                and row_data["Completed"].isspace()
            ):
                return False
        return True

    def next_unused_row_sn(self, request_uuid: str) -> tuple[int, str]:
        """Find the next row number.

        Parameters
        ----------
        request_uuid
            The request UUID.

        Raises
        ------
        ValueError
            If the request UUID is not found.

        Returns
        -------
        tuple[int, str]
            row, sn
                The row number and the cell SN of the first row without a status.
        """
        column_names, data = self.get_tracking_data()
        for row, row_data in enumerate(data):
            if len(row_data) > 1 and row_data["Request_UUID"] == request_uuid and len(row_data) == self.num_columns:
                return row + 2, row_data["Cell_SN"]
            if (
                len(row_data) > self.num_columns
                and row_data["Request_UUID"] == request_uuid
                and row_data["Completed"].isspace()
            ):
                return row + 2, row_data["Cell_SN"]
        msg = f"Request UUID {request_uuid} not found."
        raise ValueError(msg)


if __name__ == "__main__":
    sheet = TrackingSheet(SAMPLE_SPREADSHEET_ID, "v1", "A1:C")
    sheet.login()
    sheet.get_tracking_data()
