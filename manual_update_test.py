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

user_id = 'e55a1885-a5db-489d-9cca-9112d626b3ca'
proxy_admin_team_id = '4662e501-33cc-42c1-bffa-b2035c0b9cc0'

# Try different payload formats
payloads = [
    # Format 1: Only teams
    {
        "user_id": user_id,
        "teams": [proxy_admin_team_id]
    },
    # Format 2: team_id + teams
    {
        "user_id": user_id,
        "team_id": proxy_admin_team_id,
        "teams": [proxy_admin_team_id]
    },
    # Format 3: Only team_id
    {
        "user_id": user_id,
        "team_id": proxy_admin_team_id
    }
]

url = f'{base_url.rstrip("/")}/user/update'

for i, payload in enumerate(payloads, 1):
    print(f"\n=== Test {i}: {payload} ===")
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}...")
        
        if r.status_code == 200:
            # Check current user state
            list_url = f'{base_url.rstrip("/")}/user/list'
            list_r = requests.get(list_url, headers=headers, timeout=30)
            if list_r.status_code == 200:
                users = list_r.json()
                if isinstance(users, dict):
                    users = users.get('data', []) or users.get('users', [])
                
                for user in users:
                    if user.get('user_id') == user_id:
                        print(f"Current teams: {user.get('teams', [])}")
                        break
        
    except Exception as e:
        print(f"Error: {e}")