#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import requests
import csv
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_USER_ROLE = "proxy_admin"
SENSITIVE_KEYS = {"password", "hashed_password", "salt", "token"}  # 念のため除外

def get_user_details(base_url: str, master_key: str, user_id: str, debug: bool = False) -> Dict:
    """Get detailed user information including API keys"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/user/info"
    params = {"user_id": user_id}
    
    if debug:
        print(f"DEBUG: Getting user details - URL: {url}, user_id: {user_id}", file=sys.stderr)
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        
        if debug:
            print(f"DEBUG: User details response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: User details response: {r.text[:500]}...", file=sys.stderr)
        
        r.raise_for_status()
        return r.json()
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error getting user details: {e}", file=sys.stderr)
        return {}

def get_team_id_by_name(base_url: str, master_key: str, team_name: str, debug: bool = False) -> str:
    """Get team ID by team name"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/team/list"
    
    if debug:
        print(f"DEBUG: Getting team list - URL: {url}", file=sys.stderr)
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        
        if debug:
            print(f"DEBUG: Team list response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Team list response: {r.text[:500]}...", file=sys.stderr)
        
        r.raise_for_status()
        data = r.json()
        
        # Get teams from response - API returns list directly
        teams = data if isinstance(data, list) else data.get("teams", []) or data.get("data", [])
        
        # Find team by name (check both team_name and team_alias)
        for team in teams:
            if team.get("team_name") == team_name or team.get("team_alias") == team_name:
                return team.get("team_id", "")
        
        if debug:
            print(f"DEBUG: Team '{team_name}' not found in available teams", file=sys.stderr)
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
        
        # Get teams from response - API returns list directly
        teams = data if isinstance(data, list) else data.get("teams", []) or data.get("data", [])
        
        # Find team by ID
        for team in teams:
            if team.get("team_id") == team_id:
                return team.get("team_alias") or team.get("team_name", "")
        
        return ""
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error getting team name for ID {team_id}: {e}", file=sys.stderr)
        return ""

def check_user_exists(base_url: str, master_key: str, user_email: str, debug: bool = False) -> bool:
    """Check if user already exists"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/user/list"
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # Get users from response
        users = data.get("users") or data.get("data") or (data if isinstance(data, list) else [])
        
        # Check if user email exists
        for user in users:
            if user.get("user_email") == user_email:
                return True
        return False
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error checking user existence: {e}", file=sys.stderr)
        return False  # If we can't check, assume user doesn't exist

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
    
    # Add team_id to payload if team_name is provided
    if team_name:
        team_id = get_team_id_by_name(base_url, master_key, team_name, debug)
        if team_id:
            payload["team_id"] = team_id
            if debug:
                print(f"DEBUG: Found team ID '{team_id}' for team name '{team_name}'", file=sys.stderr)
        else:
            if debug:
                print(f"DEBUG: Team '{team_name}' not found, creating user without team assignment", file=sys.stderr)
    
    if debug:
        print(f"DEBUG: Creating user - URL: {url}", file=sys.stderr)
        print(f"DEBUG: Headers: {headers}", file=sys.stderr)
        print(f"DEBUG: Payload: {payload}", file=sys.stderr)
    
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if debug:
        print(f"DEBUG: Response status: {r.status_code}", file=sys.stderr)
        print(f"DEBUG: Response headers: {dict(r.headers)}", file=sys.stderr)
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

def generate_invitation_id(base_url: str, master_key: str, user_id: str, debug: bool = False) -> str:
    """Generate invitation ID for password setup"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    # Try different possible endpoints for invitation ID generation
    possible_endpoints = [
        f"{base_url.rstrip('/')}/user/invite",
        f"{base_url.rstrip('/')}/invite",
        f"{base_url.rstrip('/')}/user/invitation",
        f"{base_url.rstrip('/')}/user/{user_id}/invite",
        f"{base_url.rstrip('/')}/user/generate_invite",
        f"{base_url.rstrip('/')}/generate_invite"
    ]
    
    payload = {
        "user_id": user_id,
        "action": "reset_password"
    }
    
    for url in possible_endpoints:
        if debug:
            print(f"DEBUG: Trying invitation endpoint - URL: {url}", file=sys.stderr)
            print(f"DEBUG: Invitation payload: {payload}", file=sys.stderr)
        
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if debug:
                print(f"DEBUG: Invitation response status: {r.status_code}", file=sys.stderr)
                print(f"DEBUG: Invitation response: {r.text[:500]}...", file=sys.stderr)
            
            if r.status_code == 200:
                r.raise_for_status()
                response_data = r.json()
                
                # Try to extract invitation ID from different possible response formats
                invitation_id = (
                    response_data.get('invitation_id') or
                    response_data.get('invite_id') or
                    response_data.get('id') or
                    response_data.get('token') or
                    response_data.get('invitation_token')
                )
                
                if invitation_id:
                    if debug:
                        print(f"DEBUG: Successfully generated invitation ID: {invitation_id}", file=sys.stderr)
                    return invitation_id
                
        except requests.HTTPError as e:
            if debug and e.response.status_code != 404:
                print(f"DEBUG: HTTP error for {url}: {e}", file=sys.stderr)
            continue
        except Exception as e:
            if debug:
                print(f"DEBUG: Error trying {url}: {e}", file=sys.stderr)
            continue
    
    if debug:
        print(f"DEBUG: No invitation endpoint found, unable to generate invitation ID", file=sys.stderr)
    
    return ""

def generate_invitation_url(base_url: str, master_key: str, user_id: str, debug: bool = False) -> str:
    """Generate invitation URL for password setup"""
    # First try to generate an invitation ID
    invitation_id = generate_invitation_id(base_url, master_key, user_id, debug)
    
    if invitation_id:
        # Create the proper invitation URL with invitation_id and action
        invitation_url = f"{base_url.rstrip('/')}/ui/?invitation_id={invitation_id}&action=reset_password"
        if debug:
            print(f"DEBUG: Generated invitation URL: {invitation_url}", file=sys.stderr)
        return invitation_url
    
    # Fallback: provide manual setup instructions
    manual_url = f"Manual setup required - User ID: {user_id} (No invitation endpoint available)"
    
    if debug:
        print(f"DEBUG: No invitation ID generated, using manual setup: {manual_url}", file=sys.stderr)
    
    return manual_url

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

def sanitize_user(u: Dict) -> Dict:
    """Remove sensitive information from user data"""
    return {k: v for k, v in u.items() if k not in SENSITIVE_KEYS}

def write_error_csv(failed_users: List[Dict], filename: str = "user_reg_error.csv"):
    """Write failed user registrations to CSV file"""
    if not failed_users:
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'role', 'error_reason'])
            for failed in failed_users:
                writer.writerow([failed['email'], failed['role'], failed['error']])
        print(f"Error list written to '{filename}'")
    except Exception as e:
        print(f"Failed to write error CSV: {e}", file=sys.stderr)

def write_success_csv(created_users: List[Dict], filename: str = "user_reg_result.csv", base_url: str = "", master_key: str = "", debug: bool = False):
    """Write successful user registrations to CSV file"""
    if not created_users:
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'role', 'user_id', 'team_name', 'models', 'api_keys', 'invitation_url'])
            for user in created_users:
                email = user.get('user_email', '')
                role = user.get('user_role', '')
                user_id = user.get('user_id', '')
                models = user.get('models', [])
                
                # Get team information
                team_name = ''
                if user.get('team_id') and base_url and master_key:
                    # Get actual team name from team ID
                    team_name = get_team_name_by_id(base_url, master_key, user.get('team_id'))
                    if not team_name:
                        team_name = f"Team ID: {user.get('team_id')}"
                elif user.get('team_id'):
                    team_name = f"Team ID: {user.get('team_id')}"
                
                # Get API key from different possible fields
                api_key = user.get('key', '') or user.get('api_key', '')
                if not api_key and 'user_info' in user:
                    # Check in user_info if available
                    user_info = user.get('user_info', {})
                    api_key = user_info.get('key', '') or user_info.get('api_key', '')
                
                # Generate invitation URL for password setup
                invitation_url = ''
                if user_id and base_url and master_key:
                    invitation_url = generate_invitation_url(base_url, master_key, user_id, debug)
                elif user_id and base_url:
                    # Fallback: provide manual setup instructions
                    invitation_url = f"Manual setup required - User ID: {user_id} (Access {base_url.rstrip('/')}/ui/ for password setup)"
                elif user_id:
                    # If no base_url, provide user ID for manual setup
                    invitation_url = f"Manual setup required - User ID: {user_id}"
                
                # Convert lists to string representation, handle empty lists properly
                if isinstance(models, list):
                    if models:
                        models_str = ';'.join(models)
                    else:
                        # Empty models list means user has access to all proxy models
                        models_str = 'All proxy models'
                else:
                    models_str = str(models) if models else 'All proxy models'
                
                api_keys_str = api_key if api_key else ''
                
                writer.writerow([email, role, user_id, team_name, models_str, api_keys_str, invitation_url])
        print(f"Success list written to '{filename}'")
    except Exception as e:
        print(f"Failed to write success CSV: {e}", file=sys.stderr)

def update_existing_users_csv(base_url: str, master_key: str, debug: bool = False, filename: str = "user_reg_result.csv"):
    """Update CSV with existing user information"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/user/list"
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # Get users from response
        users = data.get("users") or data.get("data") or (data if isinstance(data, list) else [])
        
        # Filter out users without email (like default_user_id)
        valid_users = [user for user in users if user.get("user_email")]
        
        # For existing users, we can't retrieve the actual API keys (security reasons)
        # So we'll indicate that keys were created during registration
        for user in valid_users:
            if user.get('key_count', 0) > 0:
                user['api_key'] = 'Created during registration (not retrievable)'
            else:
                user['api_key'] = 'No API key found'
        
        if valid_users:
            write_success_csv(valid_users, filename, base_url, master_key)
            print(f"Updated {len(valid_users)} existing users in '{filename}'")
        else:
            print("No valid users found to update")
            
    except Exception as e:
        print(f"Failed to update existing users: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="Create LiteLLM users from CSV file",
        epilog="""
Available User Roles for CSV file:
  internal_user         - Standard internal user with basic permissions
  internal_user_viewer  - Read-only internal user (view permissions only)
  proxy_admin          - Full administrative access to proxy settings
  proxy_admin_viewer   - Read-only administrative access
  default              - Default user role with standard permissions

CSV File Format (user_addlist.csv):
  email,role,team_name,key_name
  user@example.com,internal_user,internal_user,00000001_chatbot
  admin@company.com,proxy_admin,proxy_admin,00000002_chatbot
  viewer@company.com,internal_user_viewer,internal_user_viewer,00000003_chatbot

Example usage:
  python add_user.py --csv-file user_addlist.csv --dry-run
  python add_user.py --user-role proxy_admin --debug
  python add_user.py --update-existing --debug
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
        default="user_addlist.csv",
        help="CSV file containing email addresses (default: user_addlist.csv)",
    )
    parser.add_argument(
        "--user-role",
        default=DEFAULT_USER_ROLE,
        help=f"Default role for created users (default: {DEFAULT_USER_ROLE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating users",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information including raw API requests/responses",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update CSV with existing user information instead of creating new users",
    )
    args = parser.parse_args()

    if not args.master_key:
        print("ERROR: --master-key or env LITELLM_MASTER_KEY is required.", file=sys.stderr)
        sys.exit(1)

    # Handle update existing users mode
    if args.update_existing:
        print("Updating existing users information...")
        update_existing_users_csv(args.base_url, args.master_key, args.debug)
        return

    # Read users from CSV
    users = read_csv_users(args.csv_file, args.user_role)
    if not users:
        print(f"ERROR: No users found in '{args.csv_file}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(users)} users in '{args.csv_file}'")
    
    if args.dry_run:
        print("\nDRY RUN - Users that would be created:")
        for user in users:
            display_msg = f"  Email: {user['email']}, Role: {user['role']}"
            if user.get('team_name'):
                display_msg += f", Team: {user['team_name']}"
            if user.get('key_name'):
                display_msg += f", Key Name: {user['key_name']}"
            print(display_msg)
        return

    # Create users
    created_users = []
    failed_users = []
    
    for user in users:
        email = user['email']
        role = user['role']
        team_name = user.get('team_name')
        key_name = user.get('key_name')
        
        # Check if user already exists
        if check_user_exists(args.base_url, args.master_key, email, args.debug):
            error_reason = "User already exists in the system"
            print(f"✗ Skipped user {email}: {error_reason}", file=sys.stderr)
            failed_users.append({"email": email, "role": role, "error": error_reason})
            continue
        
        try:
            if args.debug:
                debug_msg = f"\nDEBUG: Creating user: {email} with role: {role}"
                if team_name:
                    debug_msg += f" and team: {team_name}"
                if key_name:
                    debug_msg += f" and key name: {key_name}"
                print(debug_msg, file=sys.stderr)
            
            result = create_user(args.base_url, args.master_key, email, role, team_name, args.debug)
            created_user = sanitize_user(result)
            
            # Get user_id and API key from creation result
            user_id = result.get('user_id')
            api_key = result.get('key')
            
            if user_id and api_key and key_name:
                # Update the automatically created API key's alias
                update_result = update_api_key_alias(args.base_url, args.master_key, api_key, key_name, args.debug)
                if update_result:
                    created_user['key_name'] = key_name
                    if args.debug:
                        print(f"DEBUG: Updated API key alias to '{key_name}' for user {email}", file=sys.stderr)
                else:
                    if args.debug:
                        print(f"DEBUG: Failed to update API key alias for user {email}", file=sys.stderr)
            
            if user_id:
                # Get detailed user information including API keys
                user_details = get_user_details(args.base_url, args.master_key, user_id, args.debug)
                if user_details:
                    # Merge creation result with detailed info
                    created_user.update(user_details)
            
            created_users.append(created_user)
            print(f"✓ Created user: {email} (role: {role})")
            
        except requests.HTTPError as e:
            error_msg = f"HTTPError: {e}"
            if hasattr(e, 'response') and e.response:
                response_text = e.response.text
                error_msg += f" - {response_text}"
                # Detailed error classification
                if "already exists" in response_text.lower() or "duplicate" in response_text.lower():
                    error_reason = "User already exists (API response)"
                elif "invalid" in response_text.lower() and "role" in response_text.lower():
                    error_reason = f"Invalid role '{role}' - not supported by LiteLLM"
                elif "invalid" in response_text.lower() and "email" in response_text.lower():
                    error_reason = f"Invalid email format '{email}'"
                elif e.response.status_code == 400:
                    error_reason = f"Bad request - check email format and role validity"
                elif e.response.status_code == 401:
                    error_reason = "Unauthorized - invalid master key"
                elif e.response.status_code == 403:
                    error_reason = "Forbidden - insufficient permissions"
                elif e.response.status_code == 409:
                    error_reason = "Conflict - user already exists"
                else:
                    error_reason = f"HTTP {e.response.status_code} error: {response_text[:100]}"
            else:
                error_reason = f"HTTP {e.response.status_code if hasattr(e, 'response') else 'unknown'} error without response details"
            
            print(f"✗ Failed to create user {email}: {error_msg}", file=sys.stderr)
            failed_users.append({"email": email, "role": role, "error": error_reason})
            
        except Exception as e:
            error_reason = f"Unexpected error: {str(e)}"
            print(f"✗ Failed to create user {email}: {error_reason}", file=sys.stderr)
            failed_users.append({"email": email, "role": role, "error": error_reason})

    # Summary
    print(f"\nSummary:")
    print(f"  Successfully created: {len(created_users)} users")
    print(f"  Failed: {len(failed_users)} users")
    
    if created_users:
        write_success_csv(created_users, "user_reg_result.csv", args.base_url, args.master_key, args.debug)
    
    if failed_users:
        write_error_csv(failed_users)
        print(f"\nFailed users:")
        for failed in failed_users:
            print(f"  {failed['email']} ({failed['role']}): {failed['error']}")

if __name__ == "__main__":
    main()