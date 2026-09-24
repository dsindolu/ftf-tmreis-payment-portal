import re
import streamlit as st
from pathlib import Path

from services.cache import get_google_sheets

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="TMREIS Institution Visit Payment Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# GOOGLE SHEETS
# ======================================================

gs = get_google_sheets()

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>

/* Hide Streamlit */

#MainMenu,
header,
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

.stSelectbox,
.stDateInput{
    margin-bottom:12px;
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

</style>
""", unsafe_allow_html=True)

# ======================================================
# SESSION STATE
# ======================================================

if "page" not in st.session_state:
    st.session_state.page = 1

if "volunteer" not in st.session_state:
    st.session_state.volunteer = {
        "name": "",
        "mobile": "",
        "email": "",
        "institution_count": 1
    }

if "institutions" not in st.session_state:
    st.session_state.institutions = []

if "current_institution" not in st.session_state:
    st.session_state.current_institution = 0

if "payment" not in st.session_state:
    st.session_state.payment = {}

# ======================================================
# VALIDATIONS
# ======================================================

def valid_mobile(number):
    return bool(
        re.fullmatch(r"[6-9]\d{9}", number)
    )


def valid_email(email):
    return bool(
        re.fullmatch(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email
        )
    )


# ======================================================
# HEADER
# ======================================================

def page_header(title):

    col1, col2 = st.columns([4, 2])

    with col1:

        st.markdown(
            """
            <div style="
                padding-top: 10px;
                padding-bottom: 5px;
            ">
                <h1 style="
                    font-size: 42px;
                    line-height: 1.15;
                    margin: 0;
                    color: #12345B;
                    font-weight: 700;
                ">
                    TMREIS Institution Visit<br>
                    Payment Portal
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        logo_path = Path("assets/FTF_Logo.png")

        if logo_path.exists():

            st.image(
                str(logo_path),
                width=250
            )

    st.subheader(title)

    st.divider()

    
# ======================================================
# VOLUNTEER DETAILS
# ======================================================

def volunteer_page():

    page_header("Volunteer Details")

    volunteer = st.session_state.volunteer

    # Volunteer Name
    volunteer_name = st.selectbox(
        "Volunteer Name *",
        options=gs.get_names(),
        index=None if volunteer["name"] == "" else gs.get_names().index(volunteer["name"]),
        placeholder=""
    )

    # Mobile Number
    mobile = st.text_input(
        "Mobile Number *",
        value=volunteer["mobile"],
        max_chars=10
    )

    # Email Address
    email = st.text_input(
        "Email Address *",
        value=volunteer["email"]
    )

    # Institution Count
    institution_count = st.selectbox(
        "Total Institutions Visited *",
        options=list(range(1, 21)),
        index=volunteer["institution_count"] - 1
    )

    st.divider()

    if st.button("Save & Continue", use_container_width=True):

        errors = []

        if volunteer_name is None:
            errors.append("Please select Volunteer Name.")

        if not valid_mobile(mobile):
            errors.append("Please enter a valid 10-digit Mobile Number.")

        if not valid_email(email):
            errors.append("Please enter a valid Email Address.")

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

        st.session_state.institutions = []

        for _ in range(institution_count):

            st.session_state.institutions.append({

                "district": "",
                "institution": "",
                "address": "",
                "visit_date": None,
                "visit_mode": ""

            })

        st.session_state.current_institution = 0
        st.session_state.page = 2

        st.rerun()

# ======================================================
# INSTITUTION VISIT DETAILS
# ======================================================

def institution_page():

    page_header("Institution Visit Details")

    index = st.session_state.current_institution
    total = st.session_state.volunteer["institution_count"]
    current = st.session_state.institutions[index]

    st.progress((index + 1) / total)

    st.markdown(
        f"### Institution {index + 1} of {total}"
    )

    st.divider()

    # ------------------------------------------
    # District
    # ------------------------------------------

    districts = gs.get_districts()

    district = st.selectbox(
        "District *",
        options=districts,
        index=(
            districts.index(current["district"])
            if current["district"] in districts
            else None
        ),
        placeholder="",
        key=f"district_{index}"
    )

    # ------------------------------------------
    # Institution
    # ------------------------------------------

    institutions = []

    if district:

        institutions = gs.get_institutions_by_district(
            district
        )

    institution = st.selectbox(
        "Institution Name *",
        options=institutions,
        index=(
            institutions.index(current["institution"])
            if current["institution"] in institutions
            else None
        ),
        placeholder="",
        key=f"institution_{index}"
    )

    # ------------------------------------------
    # Address
    # ------------------------------------------

    address = ""

    if district and institution:

        address = gs.get_address(
            district,
            institution
        )

    address_key = (
        f"address_{index}_{district}_{institution}"
    )

    st.text_area(
        "Address",
        value=address,
        disabled=True,
        height=90,
        key=address_key
    )

    # ------------------------------------------
    # Visit Date
    # ------------------------------------------

    visit_date = st.date_input(
        "Visit Date *",
        value=current["visit_date"],
        key=f"visit_date_{index}"
    )

    # ------------------------------------------
    # Visit Mode
    # ------------------------------------------

    visit_modes = ["Online", "Offline"]

    visit_mode = st.selectbox(
        "Visit Mode *",
        options=visit_modes,
        index=(
            visit_modes.index(current["visit_mode"])
            if current["visit_mode"] in visit_modes
            else None
        ),
        placeholder="",
        key=f"visit_mode_{index}"
    )

    st.divider()

    # ------------------------------------------
    # Navigation
    # ------------------------------------------

    col1, col2 = st.columns(2)

    # ------------------------------------------
    # Previous
    # ------------------------------------------

    with col1:

        if st.button(
            "Previous",
            disabled=index == 0,
            use_container_width=True,
            key=f"institution_previous_{index}"
        ):

            st.session_state.current_institution -= 1

            st.rerun()

    # ------------------------------------------
    # Next / Continue to Payment
    # ------------------------------------------

    button_text = (
        "Continue to Payment"
        if index == total - 1
        else "Next"
    )

    with col2:

        if st.button(
            button_text,
            use_container_width=True,
            key=f"institution_next_{index}"
        ):

            errors = []

            # ----------------------------------
            # Validation
            # ----------------------------------

            if not district:

                errors.append(
                    "Please select District."
                )

            if not institution:

                errors.append(
                    "Please select Institution."
                )

            if not visit_date:

                errors.append(
                    "Please select Visit Date."
                )

            if not visit_mode:

                errors.append(
                    "Please select Visit Mode."
                )

            # ----------------------------------
            # Duplicate Institution Check
            # ----------------------------------

            for i, item in enumerate(
                st.session_state.institutions
            ):

                if i == index:
                    continue

                if (
                    item["district"] == district
                    and item["institution"] == institution
                    and institution != ""
                ):

                    errors.append(
                        "This institution has already been selected."
                    )

                    break

            # ----------------------------------
            # Show Errors
            # ----------------------------------

            if errors:

                for error in errors:

                    st.error(error)

                st.stop()

            # ----------------------------------
            # Save Current Institution
            # ----------------------------------

            st.session_state.institutions[index] = {

                "district": district,

                "institution": institution,

                "address": address,

                "visit_date": visit_date,

                "visit_mode": visit_mode

            }

            # ----------------------------------
            # Move Forward
            # ----------------------------------

            if index < total - 1:

                st.session_state.current_institution += 1

            else:

                st.session_state.page = 3

            st.rerun()

# ======================================================
# PAYMENT VALIDATIONS
# ======================================================

def valid_upi(upi):

    return bool(
        re.fullmatch(
            r"^[A-Za-z0-9._-]+@[A-Za-z0-9._-]+$",
            upi
        )
    )


def valid_ifsc(ifsc):

    return bool(
        re.fullmatch(
            r"^[A-Z]{4}0[A-Z0-9]{6}$",
            ifsc.upper()
        )
    )


# ======================================================
# PAYMENT VALIDATIONS
# ======================================================

def valid_upi(upi):

    return bool(
        re.fullmatch(
            r"^[A-Za-z0-9._-]+@[A-Za-z0-9._-]+$",
            upi.strip()
        )
    )


def valid_ifsc(ifsc):

    return bool(
        re.fullmatch(
            r"^[A-Z]{4}0[A-Z0-9]{6}$",
            ifsc.strip().upper()
        )
    )


# ======================================================
# PAYMENT DETAILS
# ======================================================

def payment_page():

    page_header("Payment Details")

    payment = st.session_state.payment

    # ------------------------------------------
    # Payment Method
    # ------------------------------------------

    payment_method = st.radio(
        "Preferred Payment Method *",
        options=[
            "UPI",
            "Bank Transfer"
        ],
        horizontal=True,
        index=(
            0
            if payment.get("method", "UPI") == "UPI"
            else 1
        ),
        key="payment_method"
    )

    st.divider()

    # ------------------------------------------
    # UPI
    # ------------------------------------------

    if payment_method == "UPI":

        upi_id = st.text_input(
            "UPI ID *",
            value=payment.get("upi_id", ""),
            placeholder="example@bank",
            key="upi_id"
        )

        account_holder = ""
        bank_name = ""
        account_number = ""
        confirm_account = ""
        ifsc = ""

    # ------------------------------------------
    # BANK TRANSFER
    # ------------------------------------------

    else:

        upi_id = ""

        account_holder = st.text_input(
            "Account Holder Name *",
            value=payment.get(
                "account_holder",
                ""
            ),
            key="account_holder"
        )

        bank_name = st.text_input(
            "Bank Name *",
            value=payment.get(
                "bank_name",
                ""
            ),
            key="bank_name"
        )

        account_number = st.text_input(
            "Account Number *",
            value=payment.get(
                "account_number",
                ""
            ),
            key="account_number"
        )

        confirm_account = st.text_input(
            "Confirm Account Number *",
            value=payment.get(
                "confirm_account",
                ""
            ),
            key="confirm_account"
        )

        ifsc = st.text_input(
            "IFSC Code *",
            value=payment.get(
                "ifsc",
                ""
            ),
            key="ifsc"
        ).upper()

    st.divider()

    # ------------------------------------------
    # NAVIGATION
    # ------------------------------------------

    col1, col2 = st.columns(2)

    # ------------------------------------------
    # PREVIOUS
    # ------------------------------------------

    with col1:

        if st.button(
            "Previous",
            use_container_width=True,
            key="payment_previous"
        ):

            st.session_state.page = 2

            st.rerun()

    # ------------------------------------------
    # REVIEW & SUBMIT
    # ------------------------------------------

    with col2:

        if st.button(
            "Review & Submit",
            use_container_width=True,
            key="payment_review"
        ):

            errors = []

            # ======================================
            # UPI VALIDATION
            # ======================================

            if payment_method == "UPI":

                if not upi_id.strip():

                    errors.append(
                        "Please enter UPI ID."
                    )

                elif not valid_upi(upi_id):

                    errors.append(
                        "Please enter a valid UPI ID."
                    )

            # ======================================
            # BANK VALIDATION
            # ======================================

            else:

                if not account_holder.strip():

                    errors.append(
                        "Please enter Account Holder Name."
                    )

                if not bank_name.strip():

                    errors.append(
                        "Please enter Bank Name."
                    )

                if not account_number.strip():

                    errors.append(
                        "Please enter Account Number."
                    )

                if not confirm_account.strip():

                    errors.append(
                        "Please confirm Account Number."
                    )

                if (
                    account_number.strip()
                    != confirm_account.strip()
                ):

                    errors.append(
                        "Account Numbers do not match."
                    )

                if not ifsc.strip():

                    errors.append(
                        "Please enter IFSC Code."
                    )

                elif not valid_ifsc(ifsc):

                    errors.append(
                        "Please enter a valid IFSC Code."
                    )

            # ======================================
            # SHOW ERRORS
            # ======================================

            if errors:

                for error in errors:

                    st.error(error)

                st.stop()

            # ======================================
            # SAVE PAYMENT DETAILS
            # ======================================

            st.session_state.payment = {

                "method": payment_method,

                "upi_id": upi_id.strip(),

                "account_holder": account_holder.strip(),

                "bank_name": bank_name.strip(),

                "account_number": account_number.strip(),

                "confirm_account": confirm_account.strip(),

                "ifsc": ifsc.strip().upper()

            }

            # ======================================
            # GO TO REVIEW PAGE
            # ======================================

            st.session_state.page = 4

            st.rerun()


# ======================================================
# REVIEW & SUBMIT
# ======================================================

def review_page():

    page_header("Review & Submit")

    volunteer = st.session_state.volunteer

    institutions = st.session_state.institutions

    payment = st.session_state.payment

    # ------------------------------------------
    # Already Submitted
    # ------------------------------------------

    if st.session_state.get(
        "submitted",
        False
    ):

        st.success(
            "Your details saved successfully!"
        )

        st.markdown(
            "Our team will verify and process your "
            "payment. Thanks for your support!"
        )

        return

    # ------------------------------------------
    # VOLUNTEER DETAILS
    # ------------------------------------------

    st.markdown(
        "### Volunteer Details"
    )

    st.write(
        f"**Volunteer Name:** "
        f"{volunteer['name']}"
    )

    st.write(
        f"**Mobile Number:** "
        f"{volunteer['mobile']}"
    )

    st.write(
        f"**Email Address:** "
        f"{volunteer['email']}"
    )

    st.write(
        f"**Institutions Visited:** "
        f"{volunteer['institution_count']}"
    )

    st.divider()

    # ------------------------------------------
    # INSTITUTION DETAILS
    # ------------------------------------------

    st.markdown(
        "### Institution Details"
    )

    for i, institution in enumerate(
        institutions
    ):

        st.markdown(
            f"#### Institution {i + 1}"
        )

        st.write(
            f"**District:** "
            f"{institution['district']}"
        )

        st.write(
            f"**Institution:** "
            f"{institution['institution']}"
        )

        st.write(
            f"**Address:** "
            f"{institution['address']}"
        )

        st.write(
            f"**Visit Date:** "
            f"{institution['visit_date']}"
        )

        st.write(
            f"**Visit Mode:** "
            f"{institution['visit_mode']}"
        )

        if i < len(institutions) - 1:

            st.divider()

    st.divider()

    # ------------------------------------------
    # PAYMENT DETAILS
    # ------------------------------------------

    st.markdown(
        "### Payment Details"
    )

    st.write(
        f"**Payment Method:** "
        f"{payment.get('method', '')}"
    )

    if payment.get("method") == "UPI":

        st.write(
            f"**UPI ID:** "
            f"{payment.get('upi_id', '')}"
        )

    else:

        st.write(
            f"**Account Holder Name:** "
            f"{payment.get('account_holder', '')}"
        )

        st.write(
            f"**Bank Name:** "
            f"{payment.get('bank_name', '')}"
        )

        st.write(
            f"**Account Number:** "
            f"{payment.get('account_number', '')}"
        )

        st.write(
            f"**IFSC Code:** "
            f"{payment.get('ifsc', '')}"
        )

    st.divider()

    # ------------------------------------------
    # NAVIGATION
    # ------------------------------------------

    col1, col2 = st.columns(2)

    # ------------------------------------------
    # PREVIOUS
    # ------------------------------------------

    with col1:

        if st.button(
            "Previous",
            use_container_width=True,
            key="review_previous"
        ):

            st.session_state.page = 3

            st.rerun()

    # ------------------------------------------
    # SUBMIT
    # ------------------------------------------

    with col2:

        if st.button(
            "Submit",
            use_container_width=True,
            key="final_submit"
        ):

            st.info(
                "Submitting your details..."
            )

            try:

                # ==================================
                # PREPARE ALL RESPONSE ROWS
                # ==================================

                response_rows = []

                for institution in institutions:

                    response_rows.append([

                        volunteer["name"],

                        volunteer["mobile"],

                        volunteer["email"],

                        volunteer["institution_count"],

                        institution["district"],

                        institution["institution"],

                        institution["address"],

                        str(
                            institution["visit_date"]
                        ),

                        # Visited Alone / Partner Name columns kept
                        # blank to preserve position; Visit Mode is
                        # the new column after Partner Name in the sheet
                        "",

                        "",

                        institution["visit_mode"]

                    ])

                # ==================================
                # SAVE ALL RESPONSES IN ONE CALL
                # ==================================

                if response_rows:

                    gs.save_responses(
                        response_rows
                    )

                # ==================================
                # PAYMENT
                # ==================================

                payment_row = [

                    volunteer["name"],

                    volunteer["mobile"],

                    volunteer["email"],

                    payment.get(
                        "method",
                        ""
                    ),

                    payment.get(
                        "upi_id",
                        ""
                    ),

                    payment.get(
                        "account_holder",
                        ""
                    ),

                    payment.get(
                        "bank_name",
                        ""
                    ),

                    payment.get(
                        "account_number",
                        ""
                    ),

                    payment.get(
                        "ifsc",
                        ""
                    )

                ]

                gs.save_payment(
                    payment_row
                )

                # ==================================
                # SUCCESS
                # ==================================

                st.session_state.submitted = True

                st.rerun()

            except Exception as e:

                st.error(
                    "Unable to submit the details."
                )

                st.error(
                    f"Error: {str(e)}"
                )   

# ======================================================
# MAIN
# ======================================================

if st.session_state.page == 1:

    volunteer_page()

elif st.session_state.page == 2:

    institution_page()

elif st.session_state.page == 3:

    payment_page()

elif st.session_state.page == 4:

    review_page()