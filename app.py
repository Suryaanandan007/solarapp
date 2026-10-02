from datetime import datetime
import pandas as pd
import streamlit as st

# 1. Page Configuration & Styling
st.set_page_config(
    page_title="SolarDome Project Tracker", page_icon="☀️", layout="wide"
)

# Custom CSS for modern visual UI
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .doc-box {
        background-color: #F8FAFC;
        border-left: 4px solid #2563EB;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State Data
if "projects_df" not in st.session_state:
    st.session_state.projects_df = pd.DataFrame(
        columns=[
            "Project_ID",
            "Customer_Name",
            "Phone",
            "Location",
            "Capacity_kW",
            "PAN_Number",
            "ID_Details",
            "Current_Stage",
            "Last_Updated",
        ]
    )

# Define Solar Stages in Exact Order
SOLAR_STAGES = [
    "Lead Generated",
    "Site Visit Completed",
    "Document Procurement",
    "Applied for Loan",
    "Loan Dispersal",
    "Components Procured",
    "Work Going On",
    "Work Completed",
    "KSEB Approval",
    "Handover",
]

# Sidebar Brand Header & Quick WhatsApp Info
st.sidebar.markdown("## ☀️ SOLARDOME")
st.sidebar.markdown(
    "<p style='color: gray; font-size: 0.9rem;'>Private Limited — Project & Lead Management</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 Quick Support & Share")
st.sidebar.markdown("**WhatsApp No:** `9961331176`")
st.sidebar.markdown(
    "[🔗 Join WhatsApp Group](https://chat.whatsapp.com/LgQQxFKC6Mp33SAA99hahN)"
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Summary Dashboard",
        "📝 Register New Lead/Project",
        "📋 Document Checklist & WhatsApp",
    ],
)

# ---------------------------------------------------------
# TAB 1: SUMMARY DASHBOARD
# ---------------------------------------------------------
if menu == "📊 Summary Dashboard":
    st.markdown(
        "<p class='main-header'>SOLARDOME PRIVATE LIMITED</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Executive Summary & Real-Time Project Pipeline</p>",
        unsafe_allow_html=True,
    )

    df = st.session_state.projects_df

    if df.empty:
        st.info(
            "No projects registered yet. Use the sidebar to add your first client lead."
        )
    else:
        total_projects = len(df)
        total_capacity = df["Capacity_kW"].sum()
        completed_projects = len(
            df[df["Current_Stage"].isin(["Work Completed", "Handover"])]
        )
        in_progress_projects = total_projects - completed_projects

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="Total Projects / Leads", value=f"{total_projects}"
            )
        with col2:
            st.metric(
                label="Total Capacity Pipeline",
                value=f"{total_capacity:.1f} kW",
            )
        with col3:
            st.metric(label="In Progress", value=f"{in_progress_projects}")
        with col4:
            st.metric(label="Completed / Handed Over", value=f"{completed_projects}")

        st.markdown("---")
        st.subheader("📋 Active Project Pipeline Tracker")
        selected_stage_filter = st.selectbox(
            "Filter Pipeline by Stage", ["All Stages"] + SOLAR_STAGES
        )

        if selected_stage_filter != "All Stages":
            filtered_df = df[df["Current_Stage"] == selected_stage_filter]
        else:
            filtered_df = df

        for idx, row in filtered_df.iterrows():
            with st.expander(
                f"📌 {row['Customer_Name']} | 📍 {row['Location']} | ⚡ {row['Capacity_kW']} kW — Stage: **{row['Current_Stage']}**"
            ):
                col_info, col_update = st.columns([2, 1])

                with col_info:
                    st.write(f"**Project ID:** `{row['Project_ID']}`")
                    st.write(f"**Phone Number:** {row['Phone']}")
                    st.write(f"**PAN Number:** {row['PAN_Number']}")
                    st.write(f"**ID Details:** {row['ID_Details']}")
                    st.write(f"**Last Status Update:** {row['Last_Updated']}")

                with col_update:
                    new_stage = st.selectbox(
                        "Update Project Stage",
                        SOLAR_STAGES,
                        index=SOLAR_STAGES.index(row["Current_Stage"]),
                        key=f"stage_{row['Project_ID']}",
                    )

                    if st.button(
                        "Save Status Update", key=f"btn_{row['Project_ID']}"
                    ):
                        st.session_state.projects_df.loc[
                            st.session_state.projects_df["Project_ID"]
                            == row["Project_ID"],
                            "Current_Stage",
                        ] = new_stage
                        st.session_state.projects_df.loc[
                            st.session_state.projects_df["Project_ID"]
                            == row["Project_ID"],
                            "Last_Updated",
                        ] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.success(
                            f"Successfully updated status for {row['Customer_Name']}!"
                        )
                        st.rerun()

# ---------------------------------------------------------
# TAB 2: REGISTER NEW PROJECT
# ---------------------------------------------------------
elif menu == "📝 Register New Lead/Project":
    st.markdown(
        "<p class='main-header'>New Customer & Project Registration</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Capture customer credentials and track profile requirements</p>",
        unsafe_allow_html=True,
    )

    with st.form("project_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👤 Client Details")
            customer_name = st.text_input("Customer Full Name")
            phone = st.text_input("Phone Number")
            location = st.text_input(
                "Site Location / Address (e.g., Pulpally, Wayanad)"
            )
            capacity_kw = st.number_input(
                "Proposed Plant Capacity (kW)", min_value=0.5, value=5.0, step=0.5
            )

        with col2:
            st.markdown("### 📄 Identification & Status")
            pan_number = st.text_input("PAN Card Number")
            id_details = st.text_input(
                "ID Card Reference / Details (Aadhaar / Voter ID)"
            )
            initial_stage = st.selectbox(
                "Initial Pipeline Stage", SOLAR_STAGES, index=0
            )

        st.markdown("---")
        st.markdown(
            "### 📌 Note: Document Collection Reminder for this Project"
        )
        st.info(
            "Make sure to collect all required documents (Aadhaar, PAN, KSEB Bill, Tax Receipts, Passbook, and Geo-tagged photo) and have the customer share them via our WhatsApp group or direct number."
        )

        submitted = st.form_submit_button(
            "🚀 Save & Register Project to Dashboard"
        )

        if submitted:
            if customer_name and phone:
                new_id = f"SD-{int(datetime.now().timestamp())}"
                new_row = {
                    "Project_ID": new_id,
                    "Customer_Name": customer_name,
                    "Phone": phone,
                    "Location": location,
                    "Capacity_kW": capacity_kw,
                    "PAN_Number": pan_number,
                    "ID_Details": id_details,
                    "Current_Stage": initial_stage,
                    "Last_Updated": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }

                st.session_state.projects_df = pd.concat(
                    [
                        st.session_state.projects_df,
                        pd.DataFrame([new_row]),
                    ],
                    ignore_index=True,
                )
                st.success(
                    f"Project successfully registered under Solardome Private Limited! (ID: {new_id})"
                )
            else:
                st.error("Please enter at least the Customer Name and Phone.")

# ---------------------------------------------------------
# TAB 3: DOCUMENT CHECKLIST & WHATSAPP SHARING
# ---------------------------------------------------------
elif menu == "📋 Document Checklist & WhatsApp":
    st.markdown(
        "<p class='main-header'>Required Documents Checklist</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Share this checklist with clients or staff to ensure all paperwork is collected</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class='doc-box'>
    <h3>📲 Quick Document Sharing Hub</h3>
    <p>Staff and clients can submit or forward all required documents directly via WhatsApp:</p>
    <ul>
        <li><b>Solardome WhatsApp Number:</b> <code>9961331176</code></li>
        <li><b>Official WhatsApp Group:</b> <a href="https://chat.whatsapp.com/LgQQxFKC6Mp33SAA99hahN" target="_blank">Click here to join & share documents</a></li>
    </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("📁 Mandatory Documents List")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(
            """
        * **1. Aadhaar Card** (Identity & Address proof)
        * **2. PAN Card** (For tax & financial compliance)
        * **3. KSEB Registered Phone Number** (Linked with consumer portal)
        * **4. KSEB Electricity Bill** (Recent copy showing consumer number & sanctioned load)
        """
        )

    with col_b:
        st.markdown(
            """
        * **5. Bank Passbook Front Page** (For subsidy & loan processing)
        * **6. Land Tax Receipt** (Ownership verification)
        * **7. Building Tax Receipt** (Roof clearance verification)
        * **8. Geo-Tagged Site Photo** (Rooftop layout & coordinates)
        """
        )