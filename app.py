from datetime import datetime
import pandas as pd
import psycopg2
import streamlit as st

# 1. Page Configuration & Styling
st.set_page_config(
    page_title="SolarDome Project Tracker", page_icon="☀️", layout="wide"
)

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


# Database Connection Function
def get_connection():
    return psycopg2.connect(st.secrets["postgres"]["url"])


# Load Data from Cloud Database
def load_data():
    try:
        conn = get_connection()
        query = "SELECT * FROM projects"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        # Fallback empty dataframe if table is empty or connection fails
        return pd.DataFrame(
            columns=[
                "project_id",
                "customer_name",
                "phone",
                "location",
                "capacity_kw",
                "pan_number",
                "id_details",
                "current_stage",
                "last_updated",
            ]
        )


# Save New Project to Cloud Database
def insert_project(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO projects (project_id, customer_name, phone, location, capacity_kw, pan_number, id_details, current_stage, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            data["project_id"],
            data["customer_name"],
            data["phone"],
            data["location"],
            data["capacity_kw"],
            data["pan_number"],
            data["id_details"],
            data["current_stage"],
            data["last_updated"],
        ),
    )
    conn.commit()
    cur.close()
    conn.close()


# Update Stage in Cloud Database
def update_project_stage(project_id, new_stage, timestamp):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE projects SET current_stage = %s, last_updated = %s WHERE project_id = %s
    """,
        (new_stage, timestamp, project_id),
    )
    conn.commit()
    cur.close()
    conn.close()


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
    "<p style='color: gray; font-size: 0.9rem;'>Private Limited — Live Shared Database</p>",
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
        "<p class='sub-header'>Live Multi-User Project Pipeline</p>",
        unsafe_allow_html=True,
    )

    df = load_data()

    if df.empty:
        st.info(
            "No projects registered yet. Use the sidebar to add your first client lead."
        )
    else:
        total_projects = len(df)
        total_capacity = (
            df["capacity_kw"].sum() if not df.empty else 0.0
        )
        completed_projects = len(
            df[df["current_stage"].isin(["Work Completed", "Handover"])]
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
            filtered_df = df[df["current_stage"] == selected_stage_filter]
        else:
            filtered_df = df

        for idx, row in filtered_df.iterrows():
            with st.expander(
                f"📌 {row['customer_name']} | 📍 {row['location']} | ⚡ {row['capacity_kw']} kW — Stage: **{row['current_stage']}**"
            ):
                col_info, col_update = st.columns([2, 1])

                with col_info:
                    st.write(f"**Project ID:** `{row['project_id']}`")
                    st.write(f"**Phone Number:** {row['phone']}")
                    st.write(f"**PAN Number:** {row['pan_number']}")
                    st.write(f"**ID Details:** {row['id_details']}")
                    st.write(f"**Last Status Update:** {row['last_updated']}")

                with col_update:
                    new_stage = st.selectbox(
                        "Update Project Stage",
                        SOLAR_STAGES,
                        index=SOLAR_STAGES.index(row["current_stage"]),
                        key=f"stage_{row['project_id']}",
                    )

                    if st.button(
                        "Save Status Update", key=f"btn_{row['project_id']}"
                    ):
                        timestamp = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        update_project_stage(
                            row["project_id"], new_stage, timestamp
                        )
                        st.success(
                            f"Successfully updated status for {row['customer_name']}!"
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
        "<p class='sub-header'>Syncs instantly across all staff devices</p>",
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
        st.markdown("### 📌 Document Collection Reminder")
        st.info(
            "Ensure all required documents are collected and shared in the WhatsApp group."
        )

        submitted = st.form_submit_button(
            "🚀 Save & Register Project to Cloud Database"
        )

        if submitted:
            if customer_name and phone:
                new_id = f"SD-{int(datetime.now().timestamp())}"
                new_row = {
                    "project_id": new_id,
                    "customer_name": customer_name,
                    "phone": phone,
                    "location": location,
                    "capacity_kw": capacity_kw,
                    "pan_number": pan_number,
                    "id_details": id_details,
                    "current_stage": initial_stage,
                    "last_updated": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }

                insert_project(new_row)
                st.success(
                    f"Project successfully saved to Solardome cloud database! (ID: {new_id})"
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
        "<p class='sub-header'>Share with team members and clients</p>",
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
