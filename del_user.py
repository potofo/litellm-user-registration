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

SENSITIVE_KEYS = {"password", "hashed_password", "salt", "token"}  # 念のため除外

def get_user_id_by_email(base_url: str, master_key: str, user_email: str, debug: bool = False) -> str:
    """Get user ID by email address"""
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    
    url = f"{base_url.rstrip('/')}/user/list"
    
    if debug:
        print(f"DEBUG: Getting user list to find user ID for {user_email}", file=sys.stderr)
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        
        if debug:
            print(f"DEBUG: User list response status: {r.status_code}", file=sys.stderr)
        
        r.raise_for_status()
        data = r.json()
        
        # Get users from response
        users = data.get("users") or data.get("data") or (data if isinstance(data, list) else [])
        
        # Find user by email
        for user in users:
            if user.get("user_email") == user_email:
                user_id = user.get("user_id", "")
                if debug:
                    print(f"DEBUG: Found user ID '{user_id}' for email '{user_email}'", file=sys.stderr)
                return user_id
        
        if debug:
            print(f"DEBUG: User '{user_email}' not found in user list", file=sys.stderr)
        return ""
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error getting user list: {e}", file=sys.stderr)
        return ""

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
        print(f"DEBUG: Headers: {headers}", file=sys.stderr)
        print(f"DEBUG: Payload: {payload}", file=sys.stderr)
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if debug:
            print(f"DEBUG: Response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Response headers: {dict(r.headers)}", file=sys.stderr)
            print(f"DEBUG: Response text: {r.text[:500]}...", file=sys.stderr)
        
        r.raise_for_status()
        return True
        
    except Exception as e:
        if debug:
            print(f"DEBUG: Error deleting user: {e}", file=sys.stderr)
        return False

def read_csv_emails(csv_file: str) -> List[str]:
    """Read email addresses from CSV file"""
    emails = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email', '').strip()
                if email:
                    emails.append(email)
    except FileNotFoundError:
        print(f"ERROR: CSV file '{csv_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read CSV file '{csv_file}': {e}", file=sys.stderr)
        sys.exit(1)
    
    return emails

def write_error_csv(failed_deletions: List[Dict], filename: str = "user_del_error.csv"):
    """Write failed user deletions to CSV file"""
    if not failed_deletions:
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'user_id', 'error_reason'])
            for failed in failed_deletions:
                writer.writerow([failed['email'], failed.get('user_id', ''), failed['error']])
        print(f"Error list written to '{filename}'")
    except Exception as e:
        print(f"Failed to write error CSV: {e}", file=sys.stderr)

def write_success_csv(deleted_users: List[Dict], filename: str = "user_del_result.csv"):
    """Write successful user deletions to CSV file"""
    if not deleted_users:
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'user_id', 'status'])
            for user in deleted_users:
                writer.writerow([user['email'], user['user_id'], 'Deleted'])
        print(f"Success list written to '{filename}'")
    except Exception as e:
        print(f"Failed to write success CSV: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="Delete LiteLLM users from CSV file",
        epilog="""
CSV File Format (user_dellist.csv):
  email
  user@example.com
  admin@company.com
  viewer@company.com

Example usage:
  python del_user.py --csv-file user_dellist.csv --dry-run
  python del_user.py --debug
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
        default="user_dellist.csv",
        help="CSV file containing email addresses to delete (default: user_dellist.csv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting users",
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

    # Read emails from CSV
    emails = read_csv_emails(args.csv_file)
    if not emails:
        print(f"ERROR: No emails found in '{args.csv_file}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(emails)} emails in '{args.csv_file}'")
    
    if args.dry_run:
        print("\nDRY RUN - Users that would be deleted:")
        for email in emails:
            print(f"  Email: {email}")
        return

    # Delete users
    deleted_users = []
    failed_deletions = []
    
    for email in emails:
        # Get user ID by email
        user_id = get_user_id_by_email(args.base_url, args.master_key, email, args.debug)
        
        if not user_id:
            error_reason = "User not found in the system"
            print(f"✗ Skipped user {email}: {error_reason}", file=sys.stderr)
            failed_deletions.append({"email": email, "error": error_reason})
            continue
        
        try:
            if args.debug:
                print(f"\nDEBUG: Deleting user: {email} (ID: {user_id})", file=sys.stderr)
            
            success = delete_user(args.base_url, args.master_key, user_id, args.debug)
            
            if success:
                deleted_users.append({"email": email, "user_id": user_id})
                print(f"✓ Deleted user: {email} (ID: {user_id})")
            else:
                error_reason = "Failed to delete user (API error)"
                print(f"✗ Failed to delete user {email}: {error_reason}", file=sys.stderr)
                failed_deletions.append({"email": email, "user_id": user_id, "error": error_reason})
            
        except requests.HTTPError as e:
            error_msg = f"HTTPError: {e}"
            if hasattr(e, 'response') and e.response:
                response_text = e.response.text
                error_msg += f" - {response_text}"
                # Detailed error classification
                if "not found" in response_text.lower():
                    error_reason = "User not found (API response)"
                elif e.response.status_code == 400:
                    error_reason = f"Bad request - invalid user ID format"
                elif e.response.status_code == 401:
                    error_reason = "Unauthorized - invalid master key"
                elif e.response.status_code == 403:
                    error_reason = "Forbidden - insufficient permissions"
                elif e.response.status_code == 404:
                    error_reason = "User not found"
                else:
                    error_reason = f"HTTP {e.response.status_code} error: {response_text[:100]}"
            else:
                error_reason = f"HTTP {e.response.status_code if hasattr(e, 'response') else 'unknown'} error without response details"
            
            print(f"✗ Failed to delete user {email}: {error_msg}", file=sys.stderr)
            failed_deletions.append({"email": email, "user_id": user_id, "error": error_reason})
            
        except Exception as e:
            error_reason = f"Unexpected error: {str(e)}"
            print(f"✗ Failed to delete user {email}: {error_reason}", file=sys.stderr)
            failed_deletions.append({"email": email, "user_id": user_id, "error": error_reason})

    # Summary
    print(f"\nSummary:")
    print(f"  Successfully deleted: {len(deleted_users)} users")
    print(f"  Failed: {len(failed_deletions)} users")
    
    if deleted_users:
        write_success_csv(deleted_users)
    
    if failed_deletions:
        write_error_csv(failed_deletions)
        print(f"\nFailed deletions:")
        for failed in failed_deletions:
            print(f"  {failed['email']}: {failed['error']}")

if __name__ == "__main__":
    main()