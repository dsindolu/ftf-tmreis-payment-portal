import streamlit as st

from services.google_sheets import GoogleSheets


@st.cache_resource(show_spinner=False, ttl=300)
def get_google_sheets():

    return GoogleSheets()