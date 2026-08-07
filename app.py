import streamlit as st
import re
from datetime import date
from services.google_sheets import GoogleSheets

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------

st.set_page_config(
    page_title="TMREIS Institution Visit Payment Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>

.stApp{
    background:#FFFFFF;
}

section[data-testid="stSidebar"]{
    display:none;
}

.block-container{
    padding-top:2rem;
    max-width:900px;
}

h1,h2,h3{
    color:#222222;
}

hr{
    margin-top:10px;
    margin-bottom:25px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOAD GOOGLE SHEETS
# -------------------------------------------------------

gs = GoogleSheets()

volunteers = [""] + gs.get_names()

districts = [""] + gs.get_districts()

# -------------------------------------------------------
# HEADER
# -------------------------------------------------------

st.title("TMREIS Institution Visit Payment Portal")
st.caption("Volunteer Payment Information Collection")

st.divider()

# -------------------------------------------------------
# FORM
# -------------------------------------------------------

with st.form("payment_form"):

    st.subheader("Volunteer Details")

    volunteer = st.selectbox(
        "Volunteer Name *",
        volunteers,
        format_func=lambda x: "Choose Volunteer Name" if x == "" else x
    )

    mobile = st.text_input(
        "Mobile Number *",
        max_chars=10,
        placeholder="10-digit Mobile Number"
    )

    email = st.text_input(
        "Email Address *",
        placeholder="example@gmail.com"
    )

    institution_count = st.selectbox(
        "Total Institutions Visited *",
        list(range(1, 21))
    )

    st.divider()

    st.subheader("Institution Details")

    institution_data = []

    for i in range(institution_count):

        st.markdown(f"### Institution {i+1}")

        district = st.selectbox(
            "District *",
            districts,
            key=f"district_{i}",
            format_func=lambda x: "Choose District" if x == "" else x
        )

        institutions = []

        if district != "":
            institutions = [""] + gs.get_institutions(district)

        institution = st.selectbox(
            "Institution *",
            institutions,
            key=f"institution_{i}",
            format_func=lambda x: "Choose Institution" if x == "" else x
        )

        address = ""

        if institution != "":
            address = gs.get_address(institution)

        st.text_area(
            "Address",
            value=address,
            disabled=True,
            height=80,
            key=f"address_{i}"
        )

        visit_date = st.date_input(
            "Visit Date",
            value=date.today(),
            key=f"visit_{i}"
        )

        visited_alone = st.checkbox(
            "I Visited Alone",
            key=f"alone_{i}"
        )

        if visited_alone:

            partner = ""

            st.selectbox(
                "Partner Name",
                [""],
                disabled=True,
                key=f"partner_disabled_{i}"
            )

        else:

            partner = st.selectbox(
                "Partner Name",
                volunteers,
                key=f"partner_{i}",
                format_func=lambda x: "Choose Partner Name" if x == "" else x
            )

        institution_data.append(
            {
                "District": district,
                "Institution": institution,
                "Address": address,
                "Visit Date": visit_date,
                "Visited Alone": visited_alone,
                "Partner": partner
            }
        )

        st.divider()

    # -------------------------------------------------------
    # PAYMENT DETAILS
    # -------------------------------------------------------

    st.subheader("Payment Details")

    payment_method = st.radio(
        "Preferred Payment Method *",
        ["UPI", "Bank Transfer"],
        horizontal=True
    )

    upi_id = ""
    account_holder = ""
    bank_name = ""
    account_number = ""
    confirm_account_number = ""
    ifsc = ""

    if payment_method == "UPI":

        upi_id = st.text_input(
            "UPI ID *",
            placeholder="example@upi"
        )

    else:

        account_holder = st.text_input(
            "Account Holder Name *"
        )

        bank_name = st.text_input(
            "Bank Name *"
        )

        account_number = st.text_input(
            "Account Number *"
        )

        confirm_account_number = st.text_input(
            "Confirm Account Number *"
        )

        ifsc = st.text_input(
            "IFSC Code *"
        )

    st.divider()

    # -------------------------------------------------------
    # DECLARATION
    # -------------------------------------------------------

    declaration = st.checkbox(
        "I confirm that the above information is correct."
    )

    submit = st.form_submit_button(
        "Submit",
        use_container_width=True
    )

# -------------------------------------------------------
# VALIDATION
# -------------------------------------------------------

if submit:

    errors = []

    if volunteer == "":
        errors.append("Please select Volunteer Name.")

    if not mobile.isdigit() or len(mobile) != 10:
        errors.append("Enter a valid 10-digit Mobile Number.")

    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(email_pattern, email):
        errors.append("Enter a valid Email Address.")

    for idx, row in enumerate(institution_data):

        if row["District"] == "":
            errors.append(f"Institution {idx+1}: Select District.")

        if row["Institution"] == "":
            errors.append(f"Institution {idx+1}: Select Institution.")

        if not row["Visited Alone"] and row["Partner"] == "":
            errors.append(f"Institution {idx+1}: Select Partner Name.")

    if payment_method == "UPI":

        if upi_id.strip() == "":
            errors.append("Enter UPI ID.")

    else:

        if account_holder.strip() == "":
            errors.append("Enter Account Holder Name.")

        if bank_name.strip() == "":
            errors.append("Enter Bank Name.")

        if account_number.strip() == "":
            errors.append("Enter Account Number.")

        if confirm_account_number.strip() == "":
            errors.append("Confirm Account Number.")

        if account_number != confirm_account_number:
            errors.append("Account Numbers do not match.")

        if ifsc.strip() == "":
            errors.append("Enter IFSC Code.")

    if not declaration:
        errors.append("Please accept the declaration.")

    if errors:

        st.error("Please correct the following:")

        for error in errors:
            st.write(f"• {error}")

    else:

        st.success("Validation Successful ✅")

        st.write("Ready to save to Google Sheets.")

        # ---------------------------------------------
        # SAVE TO RESPONSES SHEET
        # ---------------------------------------------

        import uuid

        submission_id = str(uuid.uuid4())[:8].upper()

        for row in institution_data:

            gs.save_response([
                submission_id,
                volunteer,
                mobile,
                email,
                institution_count,
                row["District"],
                row["Institution"],
                row["Address"],
                row["Visit Date"].strftime("%d-%m-%Y"),
                "Yes" if row["Visited Alone"] else "No",
                row["Partner"],
                payment_method,
                date.today().strftime("%d-%m-%Y")
            ])

        # ---------------------------------------------
        # SAVE PAYMENT DETAILS
        # ---------------------------------------------

        if payment_method == "UPI":

            gs.save_payment([
                submission_id,
                volunteer,
                mobile,
                payment_method,
                upi_id,
                "",
                "",
                "",
                "",
                "",
                "Pending"
            ])

        else:

            gs.save_payment([
                submission_id,
                volunteer,
                mobile,
                payment_method,
                "",
                account_holder,
                bank_name,
                account_number,
                ifsc,
                "",
                "Pending"
            ])

        st.success("Application Submitted Successfully.")

        st.balloons()