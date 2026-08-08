import time
import pandas as pd
import gspread
import streamlit as st

from google.oauth2.service_account import Credentials


class GoogleSheets:

    def __init__(self):

        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        # ------------------------------------------
        # Google Credentials
        # ------------------------------------------

        try:

            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=SCOPES
            )

        except Exception:

            credentials = Credentials.from_service_account_file(
                "secrets/service_account.json",
                scopes=SCOPES
            )

        self.client = gspread.authorize(
            credentials
        )

        spreadsheet_id = (
            "15lbT4DgpkgRyC17y9mkwMLarafWYlij6NTM5YI0Es8s"
        )

        # ------------------------------------------
        # Open Spreadsheet
        # ------------------------------------------

        self.spreadsheet = None

        for attempt in range(5):

            try:

                self.spreadsheet = self.client.open_by_key(
                    spreadsheet_id
                )

                break

            except Exception:

                if attempt == 4:
                    raise

                time.sleep(2)

        # ------------------------------------------
        # Worksheets
        # ------------------------------------------

        self.names_sheet = self._get_worksheet(
            "Names"
        )

        self.institutions_sheet = self._get_worksheet(
            "Institutions"
        )

        self.responses_sheet = self._get_worksheet(
            "Responses"
        )

        self.payments_sheet = self._get_worksheet(
            "Payments"
        )

        # ------------------------------------------
        # Names
        # ------------------------------------------

        self.names_df = pd.DataFrame(
            self.names_sheet.get_all_records()
        )

        # ------------------------------------------
        # Institutions
        # ------------------------------------------

        self.institutions_df = pd.DataFrame(
            self.institutions_sheet.get_all_records()
        )

        self.institutions_df.columns = (
            self.institutions_df.columns
            .str.strip()
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

    # ==================================================
    # WORKSHEET
    # ==================================================

    def _get_worksheet(
        self,
        worksheet_name
    ):

        for attempt in range(5):

            try:

                return self.spreadsheet.worksheet(
                    worksheet_name
                )

            except Exception:

                if attempt == 4:
                    raise

                time.sleep(2)

    # ==================================================
    # NAMES
    # ==================================================

    def get_names(self):

        return sorted(
            self.names_df["Name"]
            .dropna()
            .unique()
            .tolist()
        )

    # ==================================================
    # DISTRICTS
    # ==================================================

    def get_districts(self):

        return sorted(
            self.institutions_df["District"]
            .dropna()
            .unique()
            .tolist()
        )

    # ==================================================
    # INSTITUTIONS
    # ==================================================

    def get_institutions_by_district(
        self,
        district
    ):

        df = self.institutions_df[
            self.institutions_df["District"] == district
        ]

        return sorted(
            df["Institution Name"]
            .dropna()
            .unique()
            .tolist()
        )

    # ==================================================
    # ADDRESS
    # ==================================================

    def get_address(
        self,
        district,
        institution
    ):

        row = self.institutions_df[
            (
                self.institutions_df["District"]
                == district
            )
            &
            (
                self.institutions_df["Institution Name"]
                == institution
            )
        ]

        if row.empty:

            return ""

        return row.iloc[0]["Address"]

    # ==================================================
    # SAVE MULTIPLE RESPONSES
    # ==================================================

    def save_responses(
        self,
        rows
    ):

        if not rows:
            return

        for attempt in range(3):

            try:

                self.responses_sheet.append_rows(
                    rows,
                    value_input_option="USER_ENTERED"
                )

                return

            except Exception:

                if attempt == 2:
                    raise

                time.sleep(2)

    # ==================================================
    # SAVE PAYMENT
    # ==================================================

    def save_payment(
        self,
        row
    ):

        for attempt in range(3):

            try:

                self.payments_sheet.append_row(
                    row,
                    value_input_option="USER_ENTERED"
                )

                return

            except Exception:

                if attempt == 2:
                    raise

                time.sleep(2)