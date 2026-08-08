# COMPLETE REPLACEMENT FILE
# services/google_sheets.py

import time
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

        spreadsheet_id = "15lbT4DgpkgRyC17y9mkwMLarafWYlij6NTM5YI0Es8s"

        # Retry 3 times
        for attempt in range(3):

            try:

                self.spreadsheet = client.open_by_key(
                    spreadsheet_id
                )

                break

            except Exception:

                if attempt == 2:
                    raise

                time.sleep(2)

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

        self.institutions_df["District"] = (
            self.institutions_df["District"]
            .astype(str)
            .str.strip()
        )

        self.institutions_df["Institution Name"] = (
            self.institutions_df["Institution Name"]
            .astype(str)
            .str.strip()
        )

        self.institutions_df["Address"] = (
            self.institutions_df["Address"]
            .astype(str)
            .str.strip()
        )

    # ------------------------------------------------

    def get_names(self):

        return sorted(
            self.names_df["Name"]
            .dropna()
            .unique()
            .tolist()
        )

    # ------------------------------------------------

    def get_districts(self):

        return sorted(
            self.institutions_df["District"]
            .dropna()
            .unique()
            .tolist()
        )

    # ------------------------------------------------

    def get_institutions_by_district(self, district):

        df = self.institutions_df[
            self.institutions_df["District"] == district
        ]

        return sorted(
            df["Institution Name"]
            .dropna()
            .unique()
            .tolist()
        )

    # ------------------------------------------------

    def get_address(self, district, institution):

        row = self.institutions_df[
            (self.institutions_df["District"] == district) &
            (self.institutions_df["Institution Name"] == institution)
        ]

        if row.empty:
            return ""

        return row.iloc[0]["Address"]

    # ------------------------------------------------

    def save_response(self, row):

        self.responses_sheet.append_row(row)

    # ------------------------------------------------

    def save_payment(self, row):

        self.payments_sheet.append_row(row)