#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()
base_url = os.getenv('LITELLM_BASE_URL', 'http://localhost:4000')
master_key = os.getenv('LITELLM_MASTER_KEY')

headers = {
    'Authorization': f'Bearer {master_key}',
    'Content-Type': 'application/json',
}

url = f'{base_url.rstrip("/")}/team/list'
r = requests.get(url, headers=headers, timeout=30)
r.raise_for_status()
data = r.json()

teams = data if isinstance(data, list) else data.get('teams', []) or data.get('data', [])

print('Team ID\t\t\t\t\tTeam Name')
print('-' * 60)
for team in teams:
    team_id = team.get('team_id', '')
    team_name = team.get('team_alias') or team.get('team_name', '')
    print(f'{team_id}\t{team_name}')