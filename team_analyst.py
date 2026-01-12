import json
from datetime import datetime, timedelta, timezone
from jira_scout import JiraScout
from git_scout import GitScout

# Helper to parse ISO timestamps with mixed formats (simple approach)
def parse_date(date_str):
    try:
        # Try truncated ISO first
        return datetime.fromisoformat(date_str)
    except ValueError:
        # If UTC Z is present or other formats, we might need a robust parser.
        # But datetime.fromisoformat handles 'Z' in Python 3.11+.
        # For older python, we might need to replace Z.
        if date_str.endswith('Z'):
             return datetime.fromisoformat(date_str[:-1]).replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(date_str)

def get_team_status():
    # Load users to iterate
    try:
        with open('mock_data.json', 'r') as f:
            data = json.load(f)
            users = data['users']
    except Exception as e:
        print(f"Failed to load user list: {e}")
        return []

    jira_scout = JiraScout(mode='mock')
    git_scout = GitScout(mode='mock')
    
    # Current time reference (Simulation Time)
    now = datetime(2026, 1, 12, 12, 15, 0)
    
    results = []

    for user in users:
        email = user['email']
        name = user['name']
        note = user.get('note', '')
        
        issues = jira_scout.get_issues_for_user(email)
        timestamps = git_scout.get_commit_timestamps(email)
        
        last_commit_time = None
        if timestamps:
            # Sort to find latest just in case
            timestamps.sort(reverse=True)
            last_commit_time = parse_date(timestamps[0])
            
        # Logic Flags
        has_active_tickets = any(i['status'] == 'In Progress' for i in issues)
        is_empty_issues = len(issues) == 0
        all_done = len(issues) > 0 and all(i['status'] == 'Done' for i in issues)
        
        time_since_commit = (now - last_commit_time) if last_commit_time else timedelta(days=999)
        
        status = "Standard"
        
        # STUCK: 'In Progress' BUT last_commit > 3 days
        if has_active_tickets and time_since_commit > timedelta(days=3):
            status = "STUCK"

        # AVAILABLE: 'Done' AND last_commit < 24h.
        elif all_done and time_since_commit < timedelta(hours=24):
             status = "AVAILABLE"

        # GHOST WORKER: Issues empty/stale (no "In Progress") BUT last_commit < 24h
        elif not has_active_tickets and time_since_commit < timedelta(hours=24):
            status = "GHOST WORKER"

        results.append({
            "name": name,
            "status": status,
            "note": note,
            "issues": issues,
            "last_commit": last_commit_time,
            "last_commit_timestamp": str(last_commit_time) if last_commit_time else "N/A"
        })
    
    return results

def analyze_team():
    results = get_team_status()
    print(f"{'Name':<25} | {'Status':<15} | {'Note'}")
    print("-" * 65)
    for user in results:
         print(f"{user['name']:<25} | {user['status']:<15} | {user['note']}")

if __name__ == "__main__":
    analyze_team()
