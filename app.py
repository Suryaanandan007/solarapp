from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Solardome Project Tracker", page_icon="☀️", layout="wide"
)


# Initialize Database Connection via SQLAlchemy (optimized for Supabase)
def get_engine():
  db_url = st.secrets["postgres"]["url"]
  if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
  return create_engine(db_url)


# Initialize Database Table if it doesn't exist
def init_db():
  engine = get_engine()
  with engine.begin() as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            customer_name TEXT,
            phone TEXT,
            location TEXT,
            capacity_kw REAL,
            pan_number TEXT,
            id_details TEXT,
            current_stage TEXT,
            last_updated TEXT
        )
    """
    )


init_db()

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

# Sidebar Brand & Quick Support
st.sidebar.title("☀️ SOLARDOME")
st.sidebar.markdown("Private Limited — Live Shared Database")
st.sidebar.markdown("---")
st.sidebar.subheader("📞 Quick Support & Share")
st.sidebar.write("WhatsApp No: `9961331176`")
st.sidebar.markdown(
    "[🔗 Join WhatsApp Group](https://chat.whatsapp.com/gQQxFKC6MP33SAAA99hahN)"
)
st.sidebar.markdown("---")

# Navigation Menu
menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Summary Dashboard",
        "📝 Register New Lead/Project",
        "📁 Document Checklist & WhatsApp",
    ],
)

# ---------------------------------------------------------
# TAB 1: SUMMARY DASHBOARD & STAGE UPDATER
# ---------------------------------------------------------
if menu == "📊 Summary Dashboard":
  st.header("📊 Active Projects Pipeline & Status Board")

  engine = get_engine()
  try:
    df = pd.read_sql("SELECT * FROM projects", engine)
  except Exception as e:
    df = pd.DataFrame(
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

  if df.empty:
    st.info(
        "No projects found in the cloud database yet. Go to 'Register New"
        " Lead/Project' in the sidebar to add your first customer."
    )
  else:
    selected_stage_filter = st.selectbox(
        "Filter by Stage", ["All Stages"] + SOLAR_STAGES
    )
    if selected_stage_filter != "All Stages":
      filtered_df = df[df["current_stage"] == selected_stage_filter]
    else:
      filtered_df = df

    st.metric(
        label="Total Filtered Leads/Projects", value=len(filtered_df)
    )

    st.subheader("Update Project Stages & Inspect Details")

    for idx, row in filtered_df.iterrows():
      with st.expander(
          f"📌 {row['customer_name']} — Location: {row['location']} [{row['capacity_kw']} kW] (Stage: **{row['current_stage']}**)"
      ):
        col_info, col_update = st.columns([2, 1])

        with col_info:
          st.write(f"**Project ID:** {row['project_id']}")
          st.write(f"**Phone:** {row['phone']}")
          st.write(f"**PAN Number:** {row['pan_number']}")
          st.write(f"**ID Details:** {row['id_details']}")
          st.write(f"**Last Updated:** {row['last_updated']}")

        with col_update:
          new_stage = st.selectbox(
              "Update Stage",
              SOLAR_STAGES,
              index=SOLAR_STAGES.index(row["current_stage"]),
              key=f"stage_{row['project_id']}",
          )

          if st.button("Save Stage Update", key=f"btn_{row['project_id']}"):
            with engine.begin() as conn:
              conn.execute(
                  f"""
                            UPDATE projects 
                            SET current_stage = '{new_stage}', last_updated = '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' 
                            WHERE project_id = '{row['project_id']}'
                        """
              )
            st.success(
                f"Updated {row['customer_name']} to '{new_stage}' successfully!"
            )
            st.rerun()

# ---------------------------------------------------------
# TAB 2: REGISTER NEW PROJECT / LEAD
# ---------------------------------------------------------
elif menu == "📝 Register New Lead/Project":
  st.header("📝 Register New Solar Lead / Project")

  with st.form("project_form"):
    col1, col2 = st.columns(2)

    with col1:
      customer_name = st.text_input("Customer Full Name")
      phone = st.text_input("Phone Number")
      location = st.text_input(
          "Site Location / Address (e.g., Pulpally, Wayanad)"
      )
      capacity_kw = st.number_input(
          "Proposed Plant Capacity (kW)", min_value=0.5, value=5.0, step=0.5
      )

    with col2:
      pan_number = st.text_input("PAN Card Number")
      id_details = st.text_input(
          "ID Card Reference / Details (Aadhaar / Voter ID)"
      )
      initial_stage = st.selectbox("Initial Pipeline Stage", SOLAR_STAGES, index=0)

    st.subheader("📁 Document & Photo Uploads")
    doc_col1, doc_col2 = st.columns(2)

    with doc_col1:
      elec_bill = st.file_uploader(
          "Upload Electricity Bill (PDF/Image)",
          type=["pdf", "png", "jpg", "jpeg"],
      )
      land_tax = st.file_uploader(
          "Upload Land Tax Receipt (PDF/Image)",
          type=["pdf", "png", "jpg", "jpeg"],
      )

    with doc_col2:
      site_photo = st.file_uploader(
          "Upload Site / Rooftop Photo", type=["png", "jpg", "jpeg"]
      )
      geo_lat_long = st.text_input(
          "Geo-tagged Coordinates (e.g., 11.6854° N, 76.1320° E)"
      )

    submitted = st.form_submit_button("Save & Register Project to Cloud Database")

    if submitted:
      if customer_name and phone:
        new_id = f"SD-{int(datetime.now().timestamp())}"
        engine = get_engine()

        with engine.begin() as conn:
          conn.execute(
              f"""
                    INSERT INTO projects (project_id, customer_name, phone, location, capacity_kw, pan_number, id_details, current_stage, last_updated)
                    VALUES ('{new_id}', '{customer_name}', '{phone}', '{location}', {capacity_kw}, '{pan_number}', '{id_details}', '{initial_stage}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                """
          )
        st.success(
            f"Project successfully saved to Solardome cloud database! (ID:"
            f" {new_id})"
        )
      else:
        st.error("Please fill in at least the Customer Name and Phone.")

# ---------------------------------------------------------
# TAB 3: DOCUMENT CHECKLIST & WHATSAPP
# ---------------------------------------------------------
elif menu == "📁 Document Checklist & WhatsApp":
  st.header("📌 Document Collection Reminder")
  st.info(
      "Ensure all required documents are collected and shared in the WhatsApp"
      " group."
  )

  st.markdown("---")
  st.subheader("📋 Mandatory Documents List")

  col_a, col_b = st.columns(2)

  with col_a:
    st.markdown("""
        * **1. ID Proof** (Identity & Address proof)
        * **2. PAN Card** (For tax & financial compliance)
        * **3. KSEB Registered Phone Number** (Linked with consumer portal)
        * **4. KSEB Electricity Bill** (Recent copy showing consumer number & sanctioned load)
        """)

  with col_b:
    st.markdown("""
        * **5. Land Tax Receipt** (Latest receipt for property verification)
        * **6. Site Photos** (Clear rooftop pictures with geo-tagging)
        * **7. Bank Passbook / Cancelled Cheque** (For subsidy & loan processing)
        """)

  st.markdown("---")
  st.markdown(
      "**Official WhatsApp Group:**"
      " [Join WhatsApp Group](https://chat.whatsapp.com/gQQxFKC6MP33SAAA99hahN)"
  )
