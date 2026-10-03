from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# 1. Mobile-First Page Config
st.set_page_config(
    page_title="Solardome Operations",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Touch-Friendly CSS
st.markdown(
    """
<style>
    /* Generous touch padding and clean margins */
    .block-container {
        padding-top: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        padding-bottom: 3rem;
    }
    
    /* Mobile App Banner */
    .mobile-banner {
        background: #0f172a;
        color: #f8fafc;
        padding: 0.9rem 1.1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .mobile-banner h3 {
        color: #f59e0b !important;
        margin: 0;
        font-size: 1.25rem;
        font-weight: 700;
    }
    .mobile-banner p {
        color: #94a3b8;
        margin: 0;
        font-size: 0.78rem;
    }

    /* Large touch-friendly buttons */
    div.stButton > button {
        min-height: 48px;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 10px;
    }
    
    /* Touch-friendly inputs */
    input {
        min-height: 44px;
        font-size: 1rem !important;
    }

    /* Expanders styling */
    .streamlit-expanderHeader {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding-top: 0.75rem !important;
        padding-bottom: 0.75rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# 3. Database Engine
def get_engine():
  db_url = st.secrets["postgres"]["url"]
  if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
  if db_url.startswith("postgresql://") and not db_url.startswith(
      "postgresql+psycopg2://"
  ):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
  return create_engine(db_url)


def init_db():
  engine = get_engine()
  with engine.begin() as conn:
    conn.execute(
        text("""
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
        """)
    )


init_db()

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

# 4. App Top Header
st.markdown(
    """
<div class="mobile-banner">
    <div>
        <h3>☀️ SOLARDOME</h3>
        <p>Operations & Project Tracker</p>
    </div>
    <div style="text-align: right;">
        <span style="font-size: 0.75rem; background: #1e293b; padding: 4px 8px; border-radius: 6px; color: #38bdf8;">📍 Wayanad Hub</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# 5. Mobile Navigation Bar
menu_options = [
    "📊 Projects",
    "➕ New Lead",
    "📋 Checklist",
    "📞 Support",
]
selected_tab = st.pills(
    "Navigation",
    menu_options,
    default="📊 Projects",
    label_visibility="collapsed",
)

st.markdown("---")

# ---------------------------------------------------------
# TAB 1: MOBILE PROJECTS PIPELINE
# ---------------------------------------------------------
if selected_tab == "📊 Projects":
  engine = get_engine()
  try:
    df = pd.read_sql(
        "SELECT * FROM projects ORDER BY last_updated DESC", engine
    )
  except Exception:
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
    st.info("💡 No entries found. Tap **➕ New Lead** above to add a client.")
  else:
    # KPI Metric Cards including Completed and Load
    total_installs = len(df)
    total_load = df["capacity_kw"].sum()
    completed_count = len(df[df["current_stage"] == "Handover"])
    in_progress_count = total_installs - completed_count

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Installations", total_installs)
    c2.metric("Total Load", f"{total_load:.1f} kW")
    c3.metric(
        "Total Completed",
        completed_count,
        delta=f"{in_progress_count} in progress",
    )

    # Search & Filter
    search_query = st.text_input(
        "🔍 Find Customer", placeholder="Search name, phone, or town..."
    )
    stage_filter = st.selectbox(
        "Filter by Status", ["All Stages"] + SOLAR_STAGES
    )

    filtered = df.copy()
    if search_query:
      q = search_query.lower()
      filtered = filtered[
          filtered["customer_name"].str.lower().str.contains(q)
          | filtered["phone"].str.contains(q)
          | filtered["location"].str.lower().str.contains(q)
          | filtered["project_id"].str.lower().str.contains(q)
      ]
    if stage_filter != "All Stages":
      filtered = filtered[filtered["current_stage"] == stage_filter]

    st.caption(f"Showing **{len(filtered)}** solar projects")

    # Mobile Cards
    for _, row in filtered.iterrows():
      cur_stage = (
          row["current_stage"]
          if row["current_stage"] in SOLAR_STAGES
          else SOLAR_STAGES[0]
      )
      stage_idx = SOLAR_STAGES.index(cur_stage)
      progress_pct = int(((stage_idx + 1) / len(SOLAR_STAGES)) * 100)

      card_label = (
          f"⚡ {row['customer_name']} — {row['capacity_kw']} kW ({row['location']})"
      )

      with st.expander(card_label):
        st.write(
            f"**Status:** `{cur_stage}` (Step {stage_idx + 1} of 10 •"
            f" {progress_pct}%)"
        )
        st.progress(progress_pct / 100.0)

        st.markdown(f"**ID:** `{row['project_id']}`")
        st.markdown(f"**Location:** {row['location']}")
        st.markdown(f"**KYC / PAN:** `{row['pan_number'] or 'Pending'}`")

        # One-Tap Mobile Actions
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
          st.link_button(
              "📞 Call Client",
              f"tel:{row['phone']}",
              use_container_width=True,
          )
        with btn_col2:
          clean_num = "".join(filter(str.isdigit, str(row["phone"])))
          st.link_button(
              "💬 WhatsApp",
              f"https://wa.me/91{clean_num}",
              use_container_width=True,
          )

        st.caption(f"Last updated: {row['last_updated']}")

        st.markdown("---")
        # Update Stage
        new_stage = st.selectbox(
            "Update Milestone:",
            SOLAR_STAGES,
            index=stage_idx,
            key=f"m_stage_{row['project_id']}",
        )

        if st.button(
            "💾 Save Milestone",
            key=f"m_btn_{row['project_id']}",
            use_container_width=True,
        ):
          with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE projects SET current_stage = :stage, last_updated ="
                    " :updated WHERE project_id = :pid"
                ),
                {
                    "stage": new_stage,
                    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pid": row["project_id"],
                },
            )
          st.success("Updated successfully!")
          st.rerun()

# ---------------------------------------------------------
# TAB 2: MOBILE NEW LEAD REGISTRATION
# ---------------------------------------------------------
elif selected_tab == "➕ New Lead":
  st.subheader("➕ New Solar Lead")
  st.caption("Fill customer information for site survey & processing.")

  with st.form("mobile_lead_form", clear_on_submit=True):
    name = st.text_input("Customer Name *", placeholder="Enter full name")
    phone = st.text_input(
        "Phone Number *", placeholder="10-digit mobile number"
    )
    loc = st.text_input(
        "Site Location / Town *", placeholder="e.g., Pulpally, Wayanad"
    )
    cap = st.number_input(
        "Proposed Plant Capacity (kW) *",
        min_value=0.5,
        max_value=100.0,
        value=5.0,
        step=0.5,
    )

    pan = st.text_input("PAN Card Number", placeholder="Optional")
    id_ref = st.text_input(
        "Aadhaar / Voter ID Number", placeholder="KYC Reference"
    )
    stage = st.selectbox("Starting Status", SOLAR_STAGES, index=0)

    st.markdown("##### 📸 Field Uploads (Optional)")
    st.file_uploader(
        "KSEB Bill / Rooftop Image", type=["pdf", "png", "jpg", "jpeg"]
    )

    submitted = st.form_submit_button(
        "✅ Save & Register Client", use_container_width=True
    )

    if submitted:
      if name and phone and loc:
        pid = f"SD-{int(datetime.now().timestamp())}"
        engine = get_engine()
        with engine.begin() as conn:
          conn.execute(
              text("""
                    INSERT INTO projects (project_id, customer_name, phone, location, capacity_kw, pan_number, id_details, current_stage, last_updated)
                    VALUES (:pid, :name, :phone, :loc, :cap, :pan, :id_det, :stage, :updated)
                """),
              {
                  "pid": pid,
                  "name": name,
                  "phone": phone,
                  "loc": loc,
                  "cap": cap,
                  "pan": pan,
                  "id_det": id_ref,
                  "stage": stage,
                  "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              },
          )
        st.success(f"Registered! Reference ID: {pid}")
      else:
        st.error("Please fill Name, Phone, and Location.")

# ---------------------------------------------------------
# TAB 3: CHECKLIST
# ---------------------------------------------------------
elif selected_tab == "📋 Checklist":
  st.subheader("📋 Document Checklist")
  st.caption("Verify required paperwork for KSEB net-metering & bank subsidy.")

  st.markdown("""
    * **1. ID Proof:** Aadhaar Card / Voter ID
    * **2. PAN Card:** Mandatory for subsidy credit & loan
    * **3. KSEB Electricity Bill:** Latest copy with consumer number
    * **4. Land Tax Receipt:** Current year ownership proof
    * **5. Bank Passbook / Cheque:** For MNRE DBT subsidy
    * **6. Site Rooftop Photos:** South-facing unobstructed survey
    """)

# ---------------------------------------------------------
# TAB 4: SUPPORT & QUICK CONTACTS
# ---------------------------------------------------------
elif selected_tab == "📞 Support":
  st.subheader("📞 Direct Support Desk")
  st.caption("Solardome Operations Hub • Pulpally, Wayanad")

  st.link_button(
      "💬 Join WhatsApp Team Group",
      "https://chat.whatsapp.com/gQQxFKC6MP33SAAA99hahN",
      use_container_width=True,
  )
  st.link_button(
      "📞 Call Helpdesk (+91 9961331176)",
      "tel:9961331176",
      use_container_width=True,
  )
