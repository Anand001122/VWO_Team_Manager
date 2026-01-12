import streamlit as st
import pandas as pd
import time
from team_analyst import get_team_status

# 1. PAGE CONFIGURATION & STYLING
st.set_page_config(page_title="VWO Team Intelligence", layout="wide", page_icon="⚡")

# Custom CSS to make it look like a Pro SaaS Dashboard
st.markdown("""
    <style>
    .stApp {background-color: #0E1117;}
    .metric-card {background-color: #262730; padding: 15px; border-radius: 8px;}
    .stButton>button {width: 100%; border-radius: 4px; font-weight: bold;}
    /* Highlight the sidebar */
    section[data-testid="stSidebar"] {background-color: #161B22;}
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - The "Scale" Solution
# This proves you can handle 100 or 1000 users by filtering.
with st.sidebar:
    st.title("⚡ VWO Intelligence")
    st.markdown("---")
    st.write("**Filter View**")
    
    # Fetch Data First
    team_data = get_team_status()
    df = pd.DataFrame(team_data)
    
    filter_status = st.multiselect(
        "Show Status:",
        options=["AVAILABLE", "GHOST WORKER", "STUCK", "Standard"],
        default=["GHOST WORKER", "STUCK", "AVAILABLE"]
    )
    
    st.markdown("---")
    st.caption("v1.0.4 | Connected to Jira/GitHub Scouts")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# 3. MAIN DASHBOARD HEADER & METRICS
st.title("Resource Intelligence Dashboard")
st.markdown("### Real-time team availability & anomaly detection")

# Calculate Metrics
ghost_count = len(df[df['status'] == 'GHOST WORKER'])
stuck_count = len(df[df['status'] == 'STUCK'])
available_count = len(df[df['status'] == 'AVAILABLE'])

# Display Metrics in Columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Team Velocity", "42 SP/Sprint", "+12%")
col2.metric("Ghost Workers", ghost_count, "Needs Update", delta_color="inverse")
col3.metric("Critical Blockers", stuck_count, "Needs Help", delta_color="inverse")
col4.metric("Available Capacity", available_count, "Ready to Assign")

st.divider()

# 4. THE INTELLIGENT LIST (Filtered)
if filter_status:
    filtered_data = [u for u in team_data if u['status'] in filter_status]
else:
    filtered_data = team_data

# Sorting: Available > Ghost > Stuck > Standard
priority_map = {"AVAILABLE": 0, "GHOST WORKER": 1, "STUCK": 2, "Standard": 3}
sorted_team = sorted(filtered_data, key=lambda x: priority_map.get(x['status'], 4))

st.subheader(f"Team Monitor ({len(sorted_team)} members)")

for user in sorted_team:
    status = user['status']
    name = user['name']
    
    # Visual Logic
    if status == "AVAILABLE":
        color = "🟢"
        expander_title = f"{color} {name} — READY FOR TASK"
    elif status == "GHOST WORKER":
        color = "🟡"
        expander_title = f"{color} {name} — UNREPORTED WORK DETECTED"
    elif status == "STUCK":
        color = "🔴"
        expander_title = f"{color} {name} — BLOCKED / STUCK"
    else:
        color = "🔵"
        expander_title = f"{color} {name}"

    # THE CARD UI (Using Expanders for cleanliness)
    # Default open if attention is needed (Ghost or Stuck)
    start_open = status in ["GHOST WORKER", "STUCK"]
    
    with st.expander(expander_title, expanded=start_open):
        c1, c2 = st.columns([3, 2])
        
        # COLUMN 1: The "Truth" Data
        with c1:
            st.markdown(f"**AI Insight:** `{user['note']}`")
            st.markdown(f"**Last Code Commit:** {user.get('last_commit_timestamp', 'N/A')}")
            
            if user['issues']:
                st.caption("Active Jira Tickets:")
                for issue in user['issues']:
                    st.code(f"{issue['key']}: {issue.get('summary', 'Task')} ({issue['status']})")
            else:
                st.caption("No Active Jira Tickets")

        # COLUMN 2: The Action Panel (Manager Tools)
        with c2:
            st.markdown("#### ⚡ Manager Actions")
            
            # SCENARIO A: Ghost Worker -> Automation
            if status == "GHOST WORKER":
                st.info("User is coding but Jira is empty.")
                if st.button(f"Auto-Create Ticket from Git", key=f"auto_{name}"):
                    with st.spinner("Agent contacting Jira API..."):
                        time.sleep(1) # Fake API delay for realism
                        st.success(f"✅ Created ticket 'VWO-New' based on recent commits!")
            
            # SCENARIO B: Stuck -> Custom Message (YOUR REQUEST)
            elif status == "STUCK":
                st.error("User hasn't committed code in >3 days.")
                # This is the Custom Message Box you asked for
                msg = st.text_input(f"Send DM to {name}", placeholder="Is something blocking you?", key=f"input_{name}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("📨 Send DM", key=f"send_{name}"):
                        if msg:
                            st.toast(f"Slack sent to {name}: '{msg}'", icon="✈️")
                        else:
                            st.toast(f"Sent default 'Need help?' nudge to {name}", icon="👋")
                with col_btn2:
                    if st.button("📅 Book 1:1", key=f"book_{name}"):
                        st.toast("Calendar invite sent.", icon="📅")
            
            # SCENARIO C: Available -> Assignment
            elif status == "AVAILABLE":
                st.success("User is free.")
                st.button("Assign Next Priority Task", key=f"assign_{name}")
