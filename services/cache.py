import streamlit as st

from services.google_sheets import GoogleSheets


@st.cache_resource(show_spinner=False)
def get_google_sheets():

    return GoogleSheets()