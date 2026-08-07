import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


class GoogleSheets:

    def __init__(self):

        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        credentials = Credentials.from_service_account_file(
            "secrets/service_account.json",
            scopes=SCOPES
        )

        client = gspread.authorize(credentials)

        self.spreadsheet = client.open_by_key(
            "15lbT4DgpkgRyC17y9mkwMLarafWYlij6NTM5YI0Es8s"
        )

        self.names_sheet = self.spreadsheet.worksheet("Names")
        self.institutions_sheet = self.spreadsheet.worksheet("Institutions")
        self.responses_sheet = self.spreadsheet.worksheet("Responses")
        self.payments_sheet = self.spreadsheet.worksheet("Payments")

        self.names_df = pd.DataFrame(
            self.names_sheet.get_all_records()
        )

        self.institutions_df = pd.DataFrame(
            self.institutions_sheet.get_all_records()
        )

        self.institutions_df.columns = (
            self.institutions_df.columns.str.strip()
        )

    # ----------------------------
    # Volunteers
    # ----------------------------

    def get_names(self):

        return sorted(
            self.names_df["Name"].dropna().unique().tolist()
        )

    # ----------------------------
    # Districts
    # ----------------------------

    def get_districts(self):

        return sorted(
            self.institutions_df["District"]
            .dropna()
            .unique()
            .tolist()
        )

    # ----------------------------
    # Institutions
    # ----------------------------

    def get_institutions(self, district):

        df = self.institutions_df[
            self.institutions_df["District"] == district
        ]

        return sorted(
            df["Institution Name"].tolist()
        )

    # ----------------------------
    # Address
    # ----------------------------

    def get_address(self, institution):

        row = self.institutions_df[
            self.institutions_df["Institution Name"] == institution
        ]

        if row.empty:
            return ""

        return row.iloc[0]["Address"]

    # ----------------------------
    # Save Response
    # ----------------------------

    def save_response(self, row):

        self.responses_sheet.append_row(row)

    # ----------------------------
    # Save Payment
    # ----------------------------

    def save_payment(self, row):

        self.payments_sheet.append_row(row)