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
user_email = 'test@domain.org'
user_role = 'internal_user'
proxy_admin_team_id = '4662e501-33cc-42c1-bffa-b2035c0b9cc0'

print("=== Step 1: Delete user ===")
delete_url = f'{base_url.rstrip("/")}/user/delete'
delete_payload = {"user_ids": [user_id]}

try:
    r = requests.post(delete_url, headers=headers, json=delete_payload, timeout=30)
    print(f"Delete Status: {r.status_code}")
    print(f"Delete Response: {r.text[:300]}...")
    
    if r.status_code == 200:
        print("\n=== Step 2: Recreate user with correct team ===")
        create_url = f'{base_url.rstrip("/")}/user/new'
        create_payload = {
            "user_email": user_email,
            "user_role": user_role,
            "team_id": proxy_admin_team_id
        }
        
        r2 = requests.post(create_url, headers=headers, json=create_payload, timeout=30)
        print(f"Create Status: {r2.status_code}")
        print(f"Create Response: {r2.text[:500]}...")
        
        if r2.status_code == 200:
            print("\n=== Step 3: Verify user teams ===")
            list_url = f'{base_url.rstrip("/")}/user/list'
            list_r = requests.get(list_url, headers=headers, timeout=30)
            if list_r.status_code == 200:
                users = list_r.json()
                if isinstance(users, dict):
                    users = users.get('data', []) or users.get('users', [])
                
                for user in users:
                    if user.get('user_email') == user_email:
                        print(f"New User ID: {user.get('user_id')}")
                        print(f"User Role: {user.get('user_role')}")
                        print(f"User Teams: {user.get('teams', [])}")
                        break
    
except Exception as e:
    print(f"Error: {e}")