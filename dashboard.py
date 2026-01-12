import streamlit as st
import pandas as pd
import random

# --- 1. THE MOCK DATA GENERATOR ---
# This function acts like your "fake API"
def generate_mock_data():
    names = [
        "Anand Hiremath", "Sarah Jenkings", "Rajesh Kumar", "Emily Chen", 
        "David Ross", "Priya Patel", "Michael Scott", "Dwight Schrute", 
        "Jim Halpert", "Pam Beesly", "Ryan Howard", "Angela Martin", 
        "Kevin Malone", "Oscar Martinez", "Kelly Kapoor"
    ]
    roles = ["Frontend Dev", "Backend Dev", "QA Engineer", "DevOps", "Product Manager"]
    statuses = ["Active", "Active", "Active", "On Leave", "Remote", "Active"]
    
    data = []
    
    for name in names:
        # Randomly generate realistic metrics for each person
        jira_closed = random.randint(5, 50)
        jira_open = random.randint(0, 10)
        git_commits = random.randint(10, 150)
        efficiency = round(random.uniform(70.0, 99.9), 1)
        
        data.append({
            "ID": random.randint(1000, 9999),
            "Name": name,
            "Role": random.choice(roles),
            "Status": random.choice(statuses),
            "Jira Tickets (Closed)": jira_closed,
            "Git Commits": git_commits,
            "Efficiency (%)": efficiency
        })
    
    return pd.DataFrame(data)

# --- 2. SESSION STATE MANAGEMENT ---
# This ensures data stays stable until you click "Refresh"
if 'team_data' not in st.session_state:
    st.session_state.team_data = generate_mock_data()

# --- 3. THE SIDEBAR & REFRESH BUTTON ---
st.sidebar.header("Data Control")
if st.sidebar.button("🔄 Refresh / Fetch New Data"):
    st.session_state.team_data = generate_mock_data()
    st.sidebar.success("Data updated from server!")
    st.rerun()

# --- 4. DISPLAY THE DATA ---
st.title("VWO Team Manager Dashboard")
st.markdown("### 📊 Live Team Performance Metrics")

# Display the dataframe with Streamlit's fancy column configuration
st.dataframe(
    st.session_state.team_data,
    use_container_width=True,
    column_config={
        "Efficiency (%)": st.column_config.ProgressColumn(
            "Efficiency",
            format="%f%%",
            min_value=0,
            max_value=100,
        ),
        "Git Commits": st.column_config.NumberColumn(
            "Git Commits",
            format="%d 💻"
        ),
         "Jira Tickets (Closed)": st.column_config.NumberColumn(
            "Jira Closed",
            format="%d 🎫"
        ),
    }
)

# --- 5. METRICS ROW ---
# Calculate totals dynamically based on the current data
df = st.session_state.team_data
col1, col2, col3 = st.columns(3)
col1.metric("Total Team Members", len(df))
col2.metric("Total Commits pushed", df['Git Commits'].sum())
col3.metric("Avg. Efficiency", f"{df['Efficiency (%)'].mean():.1f}%")
