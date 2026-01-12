import streamlit as st
import pandas as pd
import random
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="VWO Team Manager", page_icon="🚀", layout="wide")

# --- 1. MOCK DATA GENERATOR ---
def generate_mock_data():
    names = [
        "Anand Hiremath", "Sarah Jenkings", "Rajesh Kumar", "Emily Chen", 
        "David Ross", "Priya Patel", "Michael Scott", "Dwight Schrute", 
        "Jim Halpert", "Pam Beesly", "Ryan Howard", "Angela Martin", 
        "Kevin Malone", "Oscar Martinez", "Kelly Kapoor"
    ]
    roles = ["Frontend Dev", "Backend Dev", "QA Engineer", "DevOps", "Product Manager"]
    # "Active" means Free/Available
    statuses = ["Active", "Active", "Active", "On Leave", "Remote", "Busy"]
    
    data = []
    
    for name in names:
        jira_closed = random.randint(5, 50)
        git_commits = random.randint(10, 150)
        efficiency = round(random.uniform(70.0, 99.9), 1)
        
        data.append({
            "ID": random.randint(1000, 9999),
            "Name": name,
            "Role": random.choice(roles),
            "Status": random.choice(statuses),
            "Jira Closed": jira_closed,
            "Git Commits": git_commits,
            "Efficiency (%)": efficiency,
            "Email": f"{name.lower().replace(' ', '.')}@vwo.com"
        })
    
    return pd.DataFrame(data)

# --- SESSION STATE ---
if 'team_data' not in st.session_state:
    st.session_state.team_data = generate_mock_data()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filter Team")

# 1. Availability Filter (Answers "Who is free?")
show_only_active = st.sidebar.checkbox("Show Available Only (Active)", value=False)

# 2. Role Filter
selected_roles = st.sidebar.multiselect(
    "Filter by Role", 
    options=st.session_state.team_data["Role"].unique(),
    default=st.session_state.team_data["Role"].unique()
)

# Apply Filters
df_filtered = st.session_state.team_data.copy()
if show_only_active:
    df_filtered = df_filtered[df_filtered["Status"] == "Active"]
df_filtered = df_filtered[df_filtered["Role"].isin(selected_roles)]


# --- MAIN DASHBOARD ---
st.title("🚀 VWO Team Command Center")

# Top Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Team Members", len(st.session_state.team_data))
col2.metric("Active Now", len(st.session_state.team_data[st.session_state.team_data["Status"] == "Active"]))
col3.metric("Total Commits", df_filtered['Git Commits'].sum())
col4.metric("Avg Efficiency", f"{df_filtered['Efficiency (%)'].mean():.1f}%")

st.divider()

# Layout: Table on Left, Actions on Right
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("👥 Team Overview")
    st.markdown("Select a team member to view details or send a message.")
    
    # Interactive Table
    event = st.dataframe(
        df_filtered,
        on_select="rerun",
        selection_mode="single-row",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Active", "Busy", "On Leave", "Remote"],
                width="small"
            ),
            "Efficiency (%)": st.column_config.ProgressColumn(
                "Efficiency", format="%f%%", min_value=0, max_value=100
            ),
             "Email": st.column_config.LinkColumn("Email Link")
        }
    )

with c2:
    st.subheader("⚡ Quick Actions")
    
    # Check if a row is selected
    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        selected_person = df_filtered.iloc[selected_index]
        
        # Profile Card
        with st.container(border=True):
            st.markdown(f"### 👤 {selected_person['Name']}")
            st.markdown(f"**Role:** {selected_person['Role']}")
            
            # Status Badge
            if selected_person['Status'] == "Active":
                st.success(f"🟢 Status: {selected_person['Status']}")
            elif selected_person['Status'] == "On Leave":
                st.error(f"🔴 Status: {selected_person['Status']}")
            else:
                st.warning(f"🟡 Status: {selected_person['Status']}")
            
            st.info(f"📧 {selected_person['Email']}")
            
            st.divider()
            
            # MOCK MESSAGING FEATURE
            st.markdown("#### 💬 Send Message")
            msg_text = st.text_area("Type your message here...", placeholder="Hey, are you free for a quick sync?")
            
            if st.button(f"Send to {selected_person['Name'].split()[0]}", type="primary"):
                if msg_text:
                    with st.spinner("Sending..."):
                        time.sleep(1) # Fake delay
                    st.toast(f"✅ Message sent to {selected_person['Name']}!", icon="🚀")
                    st.balloons()
                else:
                    st.warning("Please type a message first.")
                    
    else:
        st.info("👈 Select a team member from the table to see details and send messages.")
        
        # Fallback: Show a chart if no one is selected
        st.markdown("### 📊 Team Efficiency Comparison")
        st.bar_chart(df_filtered, x="Name", y="Efficiency (%)", color="#ff4b4b")
