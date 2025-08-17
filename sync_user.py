#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import requests
import csv
from typing import List, Dict, Set, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_USER_ROLE = "proxy_admin"
INTERNAL_ROLES = {
    "internal_user",
    "internal_user_viewer",
    "proxy_admin",
    "proxy_admin_viewer",
    "user",
    "default",
    "end_user",
}
SENSITIVE_KEYS = {"password", "hashed_password", "salt", "token"}  # 念のため除外

def fetch_all_users(base_url: str, master_key: str, debug: bool = False) -> List[Dict]:
    """Fetch all users from LiteLLM API"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    users: List[Dict] = []

    url = f"{base_url.rstrip('/')}/user/list"
    params = {}

    if debug:
        print(f"DEBUG: Requesting URL: {url}", file=sys.stderr)

    while True:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        
        if debug:
            print(f"DEBUG: Response status: {r.status_code}", file=sys.stderr)
        
        r.raise_for_status()
        data = r.json()

        # data が { "data": [...], "users": [...], "next": ... } の形式でも、単なる配列でも対応
        chunk = data.get("data") or data.get("users") or (data if isinstance(data, list) else [])
        users.extend(chunk)

        next_token = data.get("next") or data.get("next_page_token")
        if next_token:
            params["page_token"] = next_token
        else:
            break

    return users

def get_team_id_by_name(base_url: str, master_key: str, team_name: str, debug: bool = False) -> str:
    """Get team ID by team name"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/team/list"
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        teams = data if isinstance(data, list) else data.get("teams", []) or data.get("data", [])
        
        for team in teams:
            if team.get("team_name") == team_name or team.get("team_alias") == team_name:
                return team.get("team_id", "")
        
        return ""
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error getting team list: {e}", file=sys.stderr)
        return ""

def get_team_name_by_id(base_url: str, master_key: str, team_id: str, debug: bool = False) -> str:
    """Get team name by team ID"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/team/list"
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        teams = data if isinstance(data, list) else data.get("teams", []) or data.get("data", [])
        
        for team in teams:
            if team.get("team_id") == team_id:
                return team.get("team_alias") or team.get("team_name", "")
        
        return ""
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error getting team name for ID {team_id}: {e}", file=sys.stderr)
        return ""

def create_user(base_url: str, master_key: str, user_email: str, user_role: str = DEFAULT_USER_ROLE, team_name: str = None, debug: bool = False) -> Dict:
    """Create a single user via LiteLLM API"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/user/new"
    payload = {
        "user_email": user_email,
        "user_role": user_role,
    }
    
    if team_name:
        team_id = get_team_id_by_name(base_url, master_key, team_name, debug)
        if team_id:
            payload["team_id"] = team_id
            if debug:
                print(f"DEBUG: Found team ID '{team_id}' for team name '{team_name}'", file=sys.stderr)
    
    if debug:
        print(f"DEBUG: Creating user - URL: {url}", file=sys.stderr)
        print(f"DEBUG: Payload: {payload}", file=sys.stderr)
    
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if debug:
        print(f"DEBUG: Response status: {r.status_code}", file=sys.stderr)
        print(f"DEBUG: Response text: {r.text[:500]}...", file=sys.stderr)
    
    r.raise_for_status()
    return r.json()

def update_api_key_alias(base_url: str, master_key: str, key_id: str, key_alias: str, debug: bool = False) -> Dict:
    """Update an existing API key's alias"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/key/update"
    payload = {
        "key": key_id,
        "key_alias": key_alias,
    }
    
    if debug:
        print(f"DEBUG: Updating API key alias - URL: {url}", file=sys.stderr)
        print(f"DEBUG: Update payload: {payload}", file=sys.stderr)
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if debug:
            print(f"DEBUG: Update response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Update response: {r.text[:500]}...", file=sys.stderr)
        
        r.raise_for_status()
        return r.json()
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error updating API key alias: {e}", file=sys.stderr)
        return {}

def delete_user(base_url: str, master_key: str, user_id: str, debug: bool = False) -> bool:
    """Delete a single user via LiteLLM API"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/user/delete"
    payload = {
        "user_ids": [user_id],
    }
    
    if debug:
        print(f"DEBUG: Deleting user - URL: {url}", file=sys.stderr)
        print(f"DEBUG: Payload: {payload}", file=sys.stderr)
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if debug:
            print(f"DEBUG: Response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Response text: {r.text[:500]}...", file=sys.stderr)
        
        r.raise_for_status()
        return True
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error deleting user: {e}", file=sys.stderr)
        return False

def read_csv_users(csv_file: str, default_role: str) -> List[Dict[str, str]]:
    """Read user data (email, role, team_name, and key_name) from CSV file"""
    users = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email', '').strip()
                role = row.get('role', '').strip() or default_role
                team_name = row.get('team_name', '').strip()
                key_name = row.get('key_name', '').strip()
                if email:
                    user_data = {"email": email, "role": role}
                    if team_name:
                        user_data["team_name"] = team_name
                    if key_name:
                        user_data["key_name"] = key_name
                    users.append(user_data)
    except FileNotFoundError:
        print(f"ERROR: CSV file '{csv_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read CSV file '{csv_file}': {e}", file=sys.stderr)
        sys.exit(1)
    
    return users

def update_user_teams_safely(base_url: str, master_key: str, user_id: str, current_team_ids: List[str], new_team_names: str, debug: bool = False) -> Dict:
    """Safely update user's teams by adding to new teams first, then removing from old teams"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    if not new_team_names:
        if debug:
            print(f"DEBUG: No new team names provided for user {user_id}", file=sys.stderr)
        return {"success": True, "message": "No team changes needed"}
    
    # Parse new team names
    new_team_name_list = [name.strip() for name in new_team_names.split() if name.strip()]
    if not new_team_name_list:
        if debug:
            print(f"DEBUG: Empty team names list for user {user_id}", file=sys.stderr)
        return {"success": True, "message": "No team changes needed"}
    
    # Get new team IDs
    new_team_ids = []
    for team_name in new_team_name_list:
        team_id = get_team_id_by_name(base_url, master_key, team_name, debug)
        if team_id:
            new_team_ids.append(team_id)
            if debug:
                print(f"DEBUG: Found team ID '{team_id}' for team name '{team_name}'", file=sys.stderr)
        else:
            if debug:
                print(f"DEBUG: Team '{team_name}' not found", file=sys.stderr)
            raise ValueError(f"Team '{team_name}' not found")
    
    if not new_team_ids:
        raise ValueError("No valid team IDs found for the specified team names")
    
    # Check if teams are actually different
    current_team_ids_set = set(current_team_ids or [])
    new_team_ids_set = set(new_team_ids)
    
    if current_team_ids_set == new_team_ids_set:
        if debug:
            print(f"DEBUG: Team IDs are the same, no changes needed for user {user_id}", file=sys.stderr)
        return {"success": True, "message": "Teams are already up to date"}
    
    url = f"{base_url.rstrip('/')}/user/update"
    
    # Step 1: Add user to new teams (combine current and new teams)
    combined_team_ids = list(current_team_ids_set | new_team_ids_set)
    
    if debug:
        print(f"DEBUG: Step 1 - Adding user {user_id} to new teams", file=sys.stderr)
        print(f"DEBUG: Current teams: {current_team_ids}", file=sys.stderr)
        print(f"DEBUG: New teams: {new_team_ids}", file=sys.stderr)
        print(f"DEBUG: Combined teams: {combined_team_ids}", file=sys.stderr)
    
    # First update: Add to new teams while keeping old ones
    payload_add = {
        "user_id": user_id,
        "team_id": combined_team_ids[0] if combined_team_ids else new_team_ids[0],
        "teams": combined_team_ids
    }
    
    if debug:
        print(f"DEBUG: Step 1 payload: {payload_add}", file=sys.stderr)
    
    try:
        r = requests.post(url, headers=headers, json=payload_add, timeout=30)
        if debug:
            print(f"DEBUG: Step 1 response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Step 1 response text: {r.text[:500]}...", file=sys.stderr)
        r.raise_for_status()
        
        # Step 2: Remove user from old teams (set to only new teams)
        if debug:
            print(f"DEBUG: Step 2 - Setting user {user_id} to only new teams", file=sys.stderr)
        
        payload_final = {
            "user_id": user_id,
            "team_id": new_team_ids[0],
            "teams": new_team_ids
        }
        
        if debug:
            print(f"DEBUG: Step 2 payload: {payload_final}", file=sys.stderr)
        
        r = requests.post(url, headers=headers, json=payload_final, timeout=30)
        if debug:
            print(f"DEBUG: Step 2 response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Step 2 response text: {r.text[:500]}...", file=sys.stderr)
        r.raise_for_status()
        
        return r.json()
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error during safe team update: {e}", file=sys.stderr)
        raise
def recreate_user_with_teams(base_url: str, master_key: str, user_id: str, user_email: str, user_role: str, team_names: str, debug: bool = False) -> Dict:
    """Recreate user with correct teams as fallback when update fails"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    if debug:
        print(f"DEBUG: Recreating user {user_email} with teams {team_names}", file=sys.stderr)
    
    try:
        # Step 1: Delete the user
        delete_url = f"{base_url.rstrip('/')}/user/delete"
        delete_payload = {"user_ids": [user_id]}
        
        if debug:
            print(f"DEBUG: Deleting user {user_id}", file=sys.stderr)
        
        r = requests.post(delete_url, headers=headers, json=delete_payload, timeout=30)
        if debug:
            print(f"DEBUG: Delete response status: {r.status_code}", file=sys.stderr)
        r.raise_for_status()
        
        # Step 2: Get team ID for the new team
        team_name_list = [name.strip() for name in team_names.split() if name.strip()]
        if not team_name_list:
            raise ValueError("No valid team names provided")
        
        # Use the first team as primary team_id
        primary_team_name = team_name_list[0]
        team_id = get_team_id_by_name(base_url, master_key, primary_team_name, debug)
        if not team_id:
            raise ValueError(f"Team '{primary_team_name}' not found")
        
        # Step 3: Recreate the user
        create_url = f"{base_url.rstrip('/')}/user/new"
        create_payload = {
            "user_email": user_email,
            "user_role": user_role,
            "team_id": team_id
        }
        
        if debug:
            print(f"DEBUG: Creating user with payload: {create_payload}", file=sys.stderr)
        
        r = requests.post(create_url, headers=headers, json=create_payload, timeout=30)
        if debug:
            print(f"DEBUG: Create response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Create response text: {r.text[:500]}...", file=sys.stderr)
        r.raise_for_status()
        
        return r.json()
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error during user recreation: {e}", file=sys.stderr)
        raise

def verify_team_update(base_url: str, master_key: str, user_id: str, expected_team_names: str, debug: bool = False) -> bool:
    """Verify if user's teams match expected teams"""
    try:
        # Get current user info
        headers = {
            "Authorization": f"Bearer {master_key}",
            "Content-Type": "application/json",
        }
        
        url = f"{base_url.rstrip('/')}/user/list"
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        users = data if isinstance(data, list) else data.get("data", []) or data.get("users", [])
        
        for user in users:
            if user.get("user_id") == user_id:
                current_team_ids = user.get("teams", [])
                current_team_names = get_team_names_from_ids(base_url, master_key, current_team_ids, debug)
                current_teams_display = " ".join(current_team_names) if current_team_names else ""
                
                expected_teams_normalized = " ".join(expected_team_names.split()) if expected_team_names else ""
                current_teams_normalized = " ".join(current_teams_display.split()) if current_teams_display else ""
                
                if debug:
                    print(f"DEBUG: Expected teams: '{expected_teams_normalized}'", file=sys.stderr)
                    print(f"DEBUG: Current teams: '{current_teams_normalized}'", file=sys.stderr)
                
                return expected_teams_normalized == current_teams_normalized
        
        return False
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error verifying team update: {e}", file=sys.stderr)
        return False


def update_user(base_url: str, master_key: str, user_id: str, user_role: str = None, team_names: str = None, current_team_ids: List[str] = None, user_email: str = None, debug: bool = False) -> Dict:
    """Update a user's role and/or teams via LiteLLM API with fallback recreation"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/user/update"
    payload = {
        "user_id": user_id,
    }
    
    # Add role if specified
    if user_role:
        payload["user_role"] = user_role
    
    # Handle team updates safely if team_names is specified
    if team_names:
        if debug:
            print(f"DEBUG: Team change detected for user {user_id}, using safe update method", file=sys.stderr)
        
        # Use safe team update method
        team_result = update_user_teams_safely(base_url, master_key, user_id, current_team_ids or [], team_names, debug)
        
        # Verify if team update was successful
        if debug:
            print(f"DEBUG: Verifying team update for user {user_id}", file=sys.stderr)
        
        team_update_successful = verify_team_update(base_url, master_key, user_id, team_names, debug)
        
        if not team_update_successful:
            if debug:
                print(f"DEBUG: Team update verification failed, using fallback recreation method", file=sys.stderr)
            
            if not user_email:
                raise ValueError("user_email is required for fallback recreation")
            
            # Fallback: recreate user with correct teams
            recreation_result = recreate_user_with_teams(base_url, master_key, user_id, user_email, user_role or "internal_user", team_names, debug)
            
            if debug:
                print(f"DEBUG: User recreation completed successfully", file=sys.stderr)
            
            return recreation_result
        
        # If only team update was requested, return the team update result
        if not user_role:
            return team_result
        
        # If both role and team update, continue with role update after team update
        if debug:
            print(f"DEBUG: Team update completed, now updating role for user {user_id}", file=sys.stderr)
    
    # Update role if specified (either standalone or after team update)
    if user_role:
        if debug:
            print(f"DEBUG: Updating role for user {user_id} to {user_role}", file=sys.stderr)
        
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if debug:
            print(f"DEBUG: Role update response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Role update response text: {r.text[:500]}...", file=sys.stderr)
        
        r.raise_for_status()
        return r.json()
    
    # This should not happen, but just in case
    return {"success": True, "message": "No updates performed"}

def get_user_virtual_keys(base_url: str, master_key: str, user_id: str, debug: bool = False) -> str:
    """Get user's virtual keys (actual API keys starting with sk-) from LiteLLM API"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    # Try to get user info which contains the keys
    url = f"{base_url.rstrip('/')}/user/info"
    params = {"user_id": user_id}
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        
        if debug:
            print(f"DEBUG: Getting user info for API keys - URL: {url}", file=sys.stderr)
            print(f"DEBUG: Response status: {r.status_code}", file=sys.stderr)
        
        r.raise_for_status()
        data = r.json()
        
        # Extract API keys from the response
        api_keys = []
        if isinstance(data, dict):
            # Check for keys in user info
            keys = data.get("keys", [])
            if isinstance(keys, list):
                for key_info in keys:
                    if isinstance(key_info, dict):
                        # Look for the actual API key in key_name field (sk-...)
                        key_name = key_info.get("key_name", "")
                        if key_name and key_name.startswith("sk-"):
                            api_keys.append(key_name)
                        # Also check token field as fallback
                        elif not key_name:
                            token = key_info.get("token", "") or key_info.get("key", "")
                            if token and token.startswith("sk-"):
                                api_keys.append(token)
            
            # Check for direct api_key field as fallback
            if not api_keys:
                api_key = data.get("api_key", "")
                if api_key and api_key.startswith("sk-"):
                    api_keys.append(api_key)
        
        # Return the first API key found, or empty string if none
        result = api_keys[0] if api_keys else ""
        
        if debug:
            print(f"DEBUG: Found API key for user {user_id}: {'Yes' if result else 'No'}", file=sys.stderr)
            if result:
                print(f"DEBUG: API key: {result[:10]}...", file=sys.stderr)
        
        return result
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error getting API key for user {user_id}: {e}", file=sys.stderr)
        return ""

def get_user_api_key(base_url: str, master_key: str, user_id: str, debug: bool = False) -> str:
    """Get user's API key - wrapper for get_user_virtual_keys for backward compatibility"""
    return get_user_virtual_keys(base_url, master_key, user_id, debug)

def sanitize_user(u: Dict) -> Dict:
    """Remove sensitive information from user data"""
    return {k: v for k, v in u.items() if k not in SENSITIVE_KEYS}

def write_sync_report(sync_results: Dict, filename: str = "user_sync_result.csv"):
    """Write synchronization results to CSV file"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['action', 'email', 'user_id', 'role', 'team_name', 'api_keys', 'status', 'error_reason'])
            
            # Write added users
            for user in sync_results.get('added', []):
                writer.writerow([
                    'ADDED',
                    user.get('email', ''),
                    user.get('user_id', ''),
                    user.get('role', ''),
                    user.get('team_name', ''),
                    user.get('api_key', ''),
                    'SUCCESS' if user.get('success') else 'FAILED',
                    user.get('error', '')
                ])
            
            # Write deleted users
            for user in sync_results.get('deleted', []):
                writer.writerow([
                    'DELETED',
                    user.get('email', ''),
                    user.get('user_id', ''),
                    user.get('role', ''),
                    user.get('team_name', ''),
                    user.get('api_key', ''),
                    'SUCCESS' if user.get('success') else 'FAILED',
                    user.get('error', '')
                ])
            
            # Write updated users
            for user in sync_results.get('updated', []):
                writer.writerow([
                    'UPDATED',
                    user.get('email', ''),
                    user.get('user_id', ''),
                    user.get('role', ''),
                    user.get('team_name', ''),
                    user.get('api_key', ''),
                    'SUCCESS' if user.get('success') else 'FAILED',
                    user.get('error', '')
                ])
            
            # Write unchanged users
            for user in sync_results.get('unchanged', []):
                writer.writerow([
                    'UNCHANGED',
                    user.get('email', ''),
                    user.get('user_id', ''),
                    user.get('role', ''),
                    user.get('team_name', ''),
                    user.get('api_key', ''),
                    'SUCCESS',
                    ''
                ])
        
        print(f"Synchronization report written to '{filename}'")
    except Exception as e:
        print(f"Failed to write sync report: {e}", file=sys.stderr)

def get_team_names_from_ids(base_url: str, master_key: str, team_ids: List[str], debug: bool = False) -> List[str]:
    """Get team names from team IDs"""
    if not team_ids:
        return []
    
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/team/list"
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        teams = data if isinstance(data, list) else data.get("teams", []) or data.get("data", [])
        
        team_names = []
        for team_id in team_ids:
            for team in teams:
                if team.get("team_id") == team_id:
                    team_name = team.get("team_alias") or team.get("team_name", "")
                    if team_name:
                        team_names.append(team_name)
                    break
        
        return team_names
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error getting team names for IDs {team_ids}: {e}", file=sys.stderr)
        return [f"Team ID: {tid}" for tid in team_ids]

def compare_users(csv_users: List[Dict], api_users: List[Dict], base_url: str, master_key: str, debug: bool = False) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """Compare CSV users with API users and determine what needs to be synced"""
    
    # Filter out users without email (like default_user_id) and non-internal roles
    valid_api_users = []
    for user in api_users:
        user_email = user.get("user_email")
        user_role = user.get("user_role")
        if user_email and user_role in INTERNAL_ROLES:
            valid_api_users.append(user)
    
    if debug:
        print(f"DEBUG: Found {len(valid_api_users)} valid API users (with email and internal roles)", file=sys.stderr)
        print(f"DEBUG: Found {len(csv_users)} CSV users", file=sys.stderr)
    
    # Create lookup dictionaries
    csv_users_dict = {user['email']: user for user in csv_users}
    api_users_dict = {user['user_email']: user for user in valid_api_users}
    
    # Users to add (in CSV but not in API)
    to_add = []
    for email, csv_user in csv_users_dict.items():
        if email not in api_users_dict:
            to_add.append(csv_user)
    
    # Users to delete (in API but not in CSV)
    to_delete = []
    for email, api_user in api_users_dict.items():
        if email not in csv_users_dict:
            # Get team names for display
            team_ids = api_user.get('teams', [])
            team_names = get_team_names_from_ids(base_url, master_key, team_ids, debug)
            team_display = " ".join(team_names) if team_names else ""
            
            to_delete.append({
                'email': email,
                'user_id': api_user.get('user_id'),
                'role': api_user.get('user_role'),
                'team_name': team_display
            })
    
    # Users to update (in both but with different roles/teams)
    to_update = []
    unchanged = []
    for email in set(csv_users_dict.keys()) & set(api_users_dict.keys()):
        csv_user = csv_users_dict[email]
        api_user = api_users_dict[email]
        
        # Check if role needs updating
        role_changed = csv_user['role'] != api_user.get('user_role')
        
        # For team comparison, resolve current team names
        csv_teams = csv_user.get('team_name', '').strip()
        api_team_ids = api_user.get('teams', [])
        api_team_names = get_team_names_from_ids(base_url, master_key, api_team_ids, debug)
        current_teams_display = " ".join(api_team_names) if api_team_names else ""
        
        # Compare teams (normalize spaces)
        csv_teams_normalized = " ".join(csv_teams.split()) if csv_teams else ""
        current_teams_normalized = " ".join(current_teams_display.split()) if current_teams_display else ""
        
        team_changed = csv_teams_normalized != current_teams_normalized and csv_teams_normalized != ""
        
        if role_changed or team_changed:
            update_info = {
                'email': email,
                'user_id': api_user.get('user_id'),
                'current_role': api_user.get('user_role'),
                'new_role': csv_user['role'],
                'current_teams': current_teams_display,
                'new_teams': csv_teams,
                'role_changed': role_changed,
                'team_changed': team_changed
            }
            to_update.append(update_info)
        else:
            # API keys are not available for unchanged users
            unchanged.append({
                'email': email,
                'user_id': api_user.get('user_id'),
                'role': api_user.get('user_role'),
                'team_name': current_teams_display,
                'api_key': ''
            })
    
    if debug:
        print(f"DEBUG: Users to add: {len(to_add)}", file=sys.stderr)
        print(f"DEBUG: Users to delete: {len(to_delete)}", file=sys.stderr)
        print(f"DEBUG: Users to update: {len(to_update)}", file=sys.stderr)
        print(f"DEBUG: Users unchanged: {len(unchanged)}", file=sys.stderr)
    
    return to_add, to_delete, to_update, unchanged

def main():
    parser = argparse.ArgumentParser(
        description="Synchronize LiteLLM users with CSV file (excluding default_user_id)",
        epilog="""
This script synchronizes users between a CSV file and LiteLLM API:
- Adds users that exist in CSV but not in LiteLLM
- Removes users that exist in LiteLLM but not in CSV (excluding default_user_id)
- Updates users that exist in both but have different roles/teams
- Reports unchanged users

Available User Roles:
  internal_user         - Standard internal user with basic permissions
  internal_user_viewer  - Read-only internal user (view permissions only)
  proxy_admin          - Full administrative access to proxy settings
  proxy_admin_viewer   - Read-only administrative access
  default              - Default user role with standard permissions

CSV File Format (user_list.csv):
  email,role,team_name
  user@example.com,internal_user,internal_user
  admin@company.com,proxy_admin,proxy_admin

Example usage:
  python sync_user.py --csv-file user_list.csv --dry-run
  python sync_user.py --debug
  python sync_user.py --no-delete --debug
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        help="LiteLLM Proxy base URL (e.g. http://localhost:4000)",
    )
    parser.add_argument(
        "--master-key",
        default=os.getenv("LITELLM_MASTER_KEY"),
        help="Master key for admin API (env LITELLM_MASTER_KEY also honored)",
    )
    parser.add_argument(
        "--csv-file",
        default="user_list.csv",
        help="CSV file containing user data (default: user_list.csv)",
    )
    parser.add_argument(
        "--user-role",
        default=DEFAULT_USER_ROLE,
        help=f"Default role for users without specified role (default: {DEFAULT_USER_ROLE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synchronized without making actual changes",
    )
    parser.add_argument(
        "--no-delete",
        action="store_true",
        help="Do not delete users that exist in LiteLLM but not in CSV",
    )
    parser.add_argument(
        "--no-update",
        action="store_true",
        help="Do not update existing users (only add/delete)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information including raw API requests/responses",
    )
    args = parser.parse_args()

    if not args.master_key:
        print("ERROR: --master-key or env LITELLM_MASTER_KEY is required.", file=sys.stderr)
        sys.exit(1)

    try:
        # Fetch current users from API
        print("Fetching current users from LiteLLM API...")
        api_users = fetch_all_users(args.base_url, args.master_key, args.debug)
        print(f"Found {len(api_users)} total users in LiteLLM")
        
        # Read users from CSV
        print(f"Reading users from '{args.csv_file}'...")
        csv_users = read_csv_users(args.csv_file, args.user_role)
        print(f"Found {len(csv_users)} users in CSV file")
        
        # Compare and determine sync actions
        to_add, to_delete, to_update, unchanged = compare_users(csv_users, api_users, args.base_url, args.master_key, args.debug)
        
        print(f"\nSynchronization Plan:")
        print(f"  Users to add: {len(to_add)}")
        print(f"  Users to delete: {len(to_delete)}")
        print(f"  Users to update: {len(to_update)}")
        print(f"  Users unchanged: {len(unchanged)}")
        
        if args.dry_run:
            print("\nDRY RUN - Changes that would be made:")
            
            if to_add:
                print("\n  Users to ADD:")
                for user in to_add:
                    team_info = f", Team: {user.get('team_name')}" if user.get('team_name') else ""
                    key_info = f", Key Name: {user.get('key_name')}" if user.get('key_name') else ""
                    print(f"    + {user['email']} (Role: {user['role']}{team_info}{key_info})")
            
            if to_delete and not args.no_delete:
                print("\n  Users to DELETE:")
                for user in to_delete:
                    team_info = f", Team: {user.get('team_name')}" if user.get('team_name') else ""
                    print(f"    - {user['email']} (Role: {user['role']}{team_info})")
            
            if to_update and not args.no_update:
                print("\n  Users to UPDATE:")
                for user in to_update:
                    changes = []
                    if user['role_changed']:
                        changes.append(f"Role: {user['current_role']} → {user['new_role']}")
                    if user['team_changed']:
                        current_display = user['current_teams'] if user['current_teams'] else "(none)"
                        new_display = user['new_teams'] if user['new_teams'] else "(none)"
                        changes.append(f"Teams: {current_display} → {new_display}")
                    print(f"    ~ {user['email']} ({', '.join(changes)})")
            
            if unchanged:
                print(f"\n  Users UNCHANGED: {len(unchanged)} users")
            
            return
        
        # Execute synchronization
        sync_results = {
            'added': [],
            'deleted': [],
            'updated': [],
            'unchanged': unchanged
        }
        
        # Add new users
        if to_add:
            print(f"\nAdding {len(to_add)} new users...")
            for user in to_add:
                try:
                    result = create_user(
                        args.base_url,
                        args.master_key,
                        user['email'],
                        user['role'],
                        user.get('team_name'),
                        args.debug
                    )
                    # Get API key for the newly created user (only available in creation response)
                    api_key = result.get('key', '') or result.get('api_key', '') or result.get('token', '')
                    user_id = result.get('user_id')
                    key_name = user.get('key_name')
                    
                    # Update API key alias if key_name is provided
                    if api_key and key_name:
                        update_result = update_api_key_alias(args.base_url, args.master_key, api_key, key_name, args.debug)
                        if update_result:
                            if args.debug:
                                print(f"DEBUG: Updated API key alias to '{key_name}' for user {user['email']}", file=sys.stderr)
                        else:
                            if args.debug:
                                print(f"DEBUG: Failed to update API key alias for user {user['email']}", file=sys.stderr)
                    
                    if args.debug:
                        print(f"DEBUG: API key for new user {user['email']}: {'Found' if api_key else 'Not found'}", file=sys.stderr)
                        if api_key:
                            print(f"DEBUG: API key value: {api_key[:10]}...", file=sys.stderr)
                    
                    sync_results['added'].append({
                        'email': user['email'],
                        'user_id': user_id,
                        'role': user['role'],
                        'team_name': user.get('team_name', ''),
                        'api_key': api_key,
                        'key_name': key_name,
                        'success': True
                    })
                    print(f"  ✓ Added user: {user['email']}")
                    
                except Exception as e:
                    error_msg = str(e)
                    sync_results['added'].append({
                        'email': user['email'],
                        'user_id': '',
                        'role': user['role'],
                        'team_name': user.get('team_name', ''),
                        'api_key': '',
                        'success': False,
                        'error': error_msg
                    })
                    print(f"  ✗ Failed to add user {user['email']}: {error_msg}")
        
        # Delete users (if not disabled)
        if to_delete and not args.no_delete:
            print(f"\nDeleting {len(to_delete)} users...")
            for user in to_delete:
                try:
                    success = delete_user(args.base_url, args.master_key, user['user_id'], args.debug)
                    if success:
                        sync_results['deleted'].append({
                            'email': user['email'],
                            'user_id': user['user_id'],
                            'role': user['role'],
                            'team_name': user.get('team_name', ''),
                            'success': True
                        })
                        print(f"  ✓ Deleted user: {user['email']}")
                    else:
                        sync_results['deleted'].append({
                            'email': user['email'],
                            'user_id': user['user_id'],
                            'role': user['role'],
                            'team_name': user.get('team_name', ''),
                            'success': False,
                            'error': 'API deletion failed'
                        })
                        print(f"  ✗ Failed to delete user: {user['email']}")
                        
                except Exception as e:
                    error_msg = str(e)
                    sync_results['deleted'].append({
                        'email': user['email'],
                        'user_id': user['user_id'],
                        'role': user['role'],
                        'team_name': user.get('team_name', ''),
                        'success': False,
                        'error': error_msg
                    })
                    print(f"  ✗ Failed to delete user {user['email']}: {error_msg}")
        
        # Update users (if not disabled)
        if to_update and not args.no_update:
            print(f"\nUpdating {len(to_update)} users...")
            for user in to_update:
                try:
                    changes = []
                    if user['role_changed']:
                        changes.append(f"Role: {user['current_role']} → {user['new_role']}")
                    if user['team_changed']:
                        current_display = user['current_teams'] if user['current_teams'] else "(none)"
                        new_display = user['new_teams'] if user['new_teams'] else "(none)"
                        changes.append(f"Teams: {current_display} → {new_display}")
                    
                    if args.debug:
                        print(f"\nDEBUG: Updating user: {user['email']} ({', '.join(changes)})", file=sys.stderr)
                    
                    # Determine what to update
                    new_role = user['new_role'] if user['role_changed'] else None
                    new_teams = user['new_teams'] if user['team_changed'] else None
                    current_team_ids = user.get('current_team_ids', [])
                    
                    result = update_user(
                        args.base_url,
                        args.master_key,
                        user['user_id'],
                        new_role,
                        new_teams,
                        current_team_ids,
                        user['email'],
                        args.debug
                    )
                    
                    # API keys are not available for updated users
                    sync_results['updated'].append({
                        'email': user['email'],
                        'user_id': user['user_id'],
                        'role': user['new_role'],
                        'team_name': user.get('new_teams', ''),
                        'api_key': '',
                        'success': True
                    })
                    print(f"  ✓ Updated user: {user['email']} ({', '.join(changes)})")
                    
                except Exception as e:
                    error_msg = str(e)
                    sync_results['updated'].append({
                        'email': user['email'],
                        'user_id': user['user_id'],
                        'role': user['new_role'],
                        'team_name': user.get('new_teams', ''),
                        'api_key': '',
                        'success': False,
                        'error': error_msg
                    })
                    print(f"  ✗ Failed to update user {user['email']}: {error_msg}")
        
        # Summary
        added_success = len([u for u in sync_results['added'] if u.get('success')])
        added_failed = len([u for u in sync_results['added'] if not u.get('success')])
        deleted_success = len([u for u in sync_results['deleted'] if u.get('success')])
        deleted_failed = len([u for u in sync_results['deleted'] if not u.get('success')])
        updated_success = len([u for u in sync_results['updated'] if u.get('success')])
        updated_failed = len([u for u in sync_results['updated'] if not u.get('success')])
        
        print(f"\nSynchronization Summary:")
        print(f"  Successfully added: {added_success} users")
        print(f"  Failed to add: {added_failed} users")
        print(f"  Successfully deleted: {deleted_success} users")
        print(f"  Failed to delete: {deleted_failed} users")
        print(f"  Successfully updated: {updated_success} users")
        print(f"  Failed to update: {updated_failed} users")
        print(f"  Unchanged: {len(unchanged)} users")
        
        # Write sync report
        write_sync_report(sync_results)
        
    except requests.HTTPError as e:
        print(f"HTTPError: {e} - {getattr(e.response, 'text', '')}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()