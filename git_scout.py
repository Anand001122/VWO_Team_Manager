import os
import json
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitScout:
    def __init__(self, mode='mock', mock_file='mock_data.json'):
        self.mode = mode
        self.mock_file = mock_file
        if self.mode == 'live':
            self.github_token = os.getenv('GITHUB_TOKEN')
            if not self.github_token:
                raise ValueError("GitHub token not found in environment variables.")
            self.g = Github(self.github_token)

    def get_commit_timestamps(self, username):
        if self.mode == 'mock':
            return self._get_mock_timestamps(username)
        elif self.mode == 'live':
            return self._get_live_timestamps(username)
        else:
            raise ValueError(f"Invalid mode: {self.mode}")

    def _get_mock_timestamps(self, username):
        try:
            with open(self.mock_file, 'r') as f:
                data = json.load(f)
                users = data.get('users', [])
                for user in users:
                    # In new mock data, using email or id as identifier might be safer, 
                    # but logic keeps 'username' arg. We check if username matches email or id or name or implied username.
                    # As 'username' passed might be email, we strictly check email or id now.
                    if user.get('username') == username or user.get('email') == username:
                        ts = user.get('last_commit_timestamp')
                        if ts:
                            return [ts]
                        return user.get('commit_timestamps', [])
                return []
        except FileNotFoundError:
            print(f"Error: {self.mock_file} not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Failed to decode {self.mock_file}.")
            return []

    def _get_live_timestamps(self, username):
        try:
            user = self.g.get_user(username)
            # Fetching public events for the user to find PushEvents
            events = user.get_public_events()
            timestamps = []
            count = 0
            for event in events:
                if event.type == 'PushEvent':
                    timestamps.append(event.created_at.isoformat())
                    count += 1
                    if count >= 5:
                        break
            return timestamps
        except Exception as e:
            print(f"Error fetching data from GitHub: {e}")
            return []

if __name__ == "__main__":
    # Test with mock data
    scout = GitScout(mode='mock')
    user = "alice_dev"
    print(f"Fetching commit timestamps for {user} (Mock Mode):")
    timestamps = scout.get_commit_timestamps(user)
    for ts in timestamps:
        print(f"- {ts}")
