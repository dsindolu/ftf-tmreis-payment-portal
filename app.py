import streamlit as st
import re

from services.cache import get_google_sheets

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="TMREIS Institution Visit Payment Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

/* Hide Streamlit */

#MainMenu{
    visibility:hidden;
}

header{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

[data-testid="stSidebar"]{
    display:none;
}

[data-testid="collapsedControl"]{
    display:none;
}

/* Page */

.block-container{

    max-width:900px;

    padding-top:2rem;

    padding-bottom:2rem;

}

/* Inputs */

.stTextInput input{

    height:46px;

}

.stSelectbox{

    margin-bottom:10px;

}

/* Buttons */

.stButton>button{

    width:100%;

    height:48px;

    background:#0d6efd;

    color:white;

    border:none;

    border-radius:8px;

    font-size:16px;

    font-weight:600;

}

.stButton>button:hover{

    background:#0b5ed7;

    color:white;

}

/* Progress */

.stProgress{

    margin-top:10px;

    margin-bottom:25px;

}

</style>
""", unsafe_allow_html=True)

# =====================================================
# GOOGLE SHEETS
# =====================================================

gs = get_google_sheets()

# =====================================================
# SESSION STATE
# =====================================================

if "page" not in st.session_state:

    st.session_state.page = 1

if "volunteer" not in st.session_state:

    st.session_state.volunteer = {

        "name":"",

        "mobile":"",

        "email":"",

        "institution_count":1

    }

if "institutions" not in st.session_state:

    st.session_state.institutions = []

if "payment" not in st.session_state:

    st.session_state.payment = {}

# =====================================================
# VALIDATIONS
# =====================================================

def valid_mobile(number):

    return bool(
        re.fullmatch(
            r"[6-9]\d{9}",
            number
        )
    )


def valid_email(email):

    return bool(
        re.fullmatch(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email
        )
    )

# =====================================================
# HEADER
# =====================================================

def render_header():

    st.title(
        "TMREIS Institution Visit Payment Portal"
    )

    st.markdown("""
**Volunteer Details** &nbsp;&nbsp;>&nbsp;&nbsp;
Institution Details &nbsp;&nbsp;>&nbsp;&nbsp;
Payment Details &nbsp;&nbsp;>&nbsp;&nbsp;
Review & Submit
""")

    st.divider()

# =====================================================
# VOLUNTEER DETAILS PAGE
# =====================================================

def volunteer_page():

    render_header()

    st.subheader("Volunteer Details")

    st.write("Please enter your details below.")

    st.divider()

    volunteer = st.session_state.volunteer

    names = gs.get_names()

    col1, col2 = st.columns(2)

    with col1:

        volunteer_name = st.selectbox(

            "Volunteer Name *",

            names,

            index=(
                names.index(volunteer["name"])
                if volunteer["name"] in names
                else None
            ),

            placeholder=""

        )

    with col2:

        institution_count = st.selectbox(

            "Total Institutions Visited *",

            list(range(1, 21)),

            index=volunteer["institution_count"] - 1

        )

    col3, col4 = st.columns(2)

    with col3:

        mobile = st.text_input(

            "Mobile Number *",

            value=volunteer["mobile"],

            max_chars=10

        )

    with col4:

        email = st.text_input(

            "Email Address *",

            value=volunteer["email"]

        )

    st.divider()

    errors = []

    if st.button("Save & Continue", use_container_width=True):

        if volunteer_name is None:

            errors.append(
                "Please select Volunteer Name."
            )

        if not valid_mobile(mobile):

            errors.append(
                "Please enter a valid 10-digit Mobile Number."
            )

        if not valid_email(email):

            errors.append(
                "Please enter a valid Email Address."
            )

        if errors:

            for error in errors:

                st.error(error)

            st.stop()

        st.session_state.volunteer = {

            "name": volunteer_name,

            "mobile": mobile,

            "email": email,

            "institution_count": institution_count

        }

        if len(st.session_state.institutions) != institution_count:

            st.session_state.institutions = []

            for _ in range(institution_count):

                st.session_state.institutions.append({

                    "district": "",

                    "institution": "",

                    "address": "",

                    "visit_date": None,

                    "visited_alone": False,

                    "partner": ""

                })

        st.session_state.page = 2

        st.rerun()

# =====================================================
# INSTITUTION DETAILS PLACEHOLDER
# =====================================================

def institution_page():

    render_header()

    st.subheader("Institution Details")

    st.info(
        "Institution Details page will be built in Version 2."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("← Previous", use_container_width=True):

            st.session_state.page = 1

            st.rerun()

    with col2:

        st.button(
            "Next →",
            disabled=True,
            use_container_width=True
        )

# =====================================================
# MAIN APP
# =====================================================

if st.session_state.page == 1:

    volunteer_page()

elif st.session_state.page == 2:

    institution_page()