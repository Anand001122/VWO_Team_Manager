import os
import json
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

class JiraScout:
    def __init__(self, mode='mock', mock_file='mock_data.json'):
        self.mode = mode
        self.mock_file = mock_file
        if self.mode == 'live':
            self.jira_server = os.getenv('JIRA_SERVER')
            self.jira_email = os.getenv('JIRA_EMAIL')
            self.jira_token = os.getenv('JIRA_TOKEN')
            if not self.jira_server or not self.jira_email or not self.jira_token:
                raise ValueError("Jira credentials not found in environment variables.")
            self.jira = JIRA(server=self.jira_server, basic_auth=(self.jira_email, self.jira_token))

    def get_issues_for_user(self, user_email):
        if self.mode == 'mock':
            return self._get_mock_issues(user_email)
        elif self.mode == 'live':
            return self._get_live_issues(user_email)
        else:
            raise ValueError(f"Invalid mode: {self.mode}")

    def _get_mock_issues(self, user_email):
        try:
            with open(self.mock_file, 'r') as f:
                data = json.load(f)
                users = data.get('users', [])
                for user in users:
                    if user['email'] == user_email:
                        return user.get('jira_issues', [])
                return []
        except FileNotFoundError:
            print(f"Error: {self.mock_file} not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Failed to decode {self.mock_file}.")
            return []

    def _get_live_issues(self, user_email):
        jql_query = f'assignee = "{user_email}" AND status != Done'
        issues = self.jira.search_issues(jql_query, maxResults=5)
        result = []
        for issue in issues:
            result.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name
            })
        return result

if __name__ == "__main__":
    # Test with mock data
    scout = JiraScout(mode='mock')
    email = "alice@example.com"
    print(f"Fetching issues for {email} (Mock Mode):")
    issues = scout.get_issues_for_user(email)
    for issue in issues:
        print(f"- [{issue['key']}] {issue['summary']} ({issue['status']})")
