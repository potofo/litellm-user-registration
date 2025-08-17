#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import requests
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    headers = {
        "Authorization": f"Bearer {master_key}",
        "Content-Type": "application/json",
    }
    users: List[Dict] = []

    # 典型的にはシンプルなGETで全件返りますが、
    # 将来のページング拡張を考慮し next / page_token があれば辿る実装にしています。
    url = f"{base_url.rstrip('/')}/user/list"
    params = {}

    if debug:
        print(f"DEBUG: Requesting URL: {url}", file=sys.stderr)
        print(f"DEBUG: Headers: {headers}", file=sys.stderr)

    while True:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        
        if debug:
            print(f"DEBUG: Response status: {r.status_code}", file=sys.stderr)
            print(f"DEBUG: Response headers: {dict(r.headers)}", file=sys.stderr)
            print(f"DEBUG: Response text: {r.text[:500]}...", file=sys.stderr)
        
        r.raise_for_status()
        data = r.json()

        if debug:
            print(f"DEBUG: Parsed JSON data: {data}", file=sys.stderr)

        # data が { "data": [...], "users": [...], "next": ... } の形式でも、単なる配列でも対応
        chunk = data.get("data") or data.get("users") or (data if isinstance(data, list) else [])
        users.extend(chunk)

        next_token = data.get("next") or data.get("next_page_token")
        if next_token:
            params["page_token"] = next_token
        else:
            break

    return users

def sanitize_user(u: Dict) -> Dict:
    return {k: v for k, v in u.items() if k not in SENSITIVE_KEYS}

def main():
    parser = argparse.ArgumentParser(
        description="List LiteLLM Internal Users via /user/list",
        epilog="""
Available User Roles:
  internal_user         - Standard internal user with basic permissions
  internal_user_viewer  - Read-only internal user (view permissions only)
  proxy_admin          - Full administrative access to proxy settings
  proxy_admin_viewer   - Read-only administrative access
  default              - Default user role with standard permissions

Example usage:
  python list_user.py --role internal_user
  python list_user.py --show-all --email-like "@company.com"
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
        "--role",
        choices=sorted(INTERNAL_ROLES),
        help="Filter by a specific internal role",
    )
    parser.add_argument(
        "--email-like",
        help="Substring filter for user_email (case-insensitive)",
    )
    parser.add_argument(
        "--columns",
        default="user_id,user_email,user_role,teams,created_at,updated_at",
        help="Comma-separated fields to print (best-effort)",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show all users regardless of role (not just internal roles)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information including raw API response",
    )
    args = parser.parse_args()

    if not args.master_key:
        print("ERROR: --master-key or env LITELLM_MASTER_KEY is required.", file=sys.stderr)
        sys.exit(1)

    try:
        all_users = fetch_all_users(args.base_url, args.master_key, args.debug)
        if args.debug:
            print(f"DEBUG: Fetched {len(all_users)} users from API", file=sys.stderr)
            for i, user in enumerate(all_users[:3]):  # Show first 3 users for debugging
                print(f"DEBUG: User {i+1}: {user}", file=sys.stderr)
    except requests.HTTPError as e:
        print(f"HTTPError: {e} - {getattr(e.response, 'text', '')}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # internal roles に限定（--show-allが指定されていない場合のみ）
    if args.show_all:
        filtered_users = all_users
    else:
        filtered_users = [u for u in all_users if str(u.get("user_role")) in INTERNAL_ROLES]

    # 任意フィルタ
    if args.role:
        filtered_users = [u for u in filtered_users if str(u.get("user_role")) == args.role]
    if args.email_like:
        q = args.email_like.lower()
        filtered_users = [u for u in filtered_users if q in str(u.get("user_email", "")).lower()]

    # センシティブ項目を除去
    filtered_users = [sanitize_user(u) for u in filtered_users]

    # 出力
    cols = [c.strip() for c in args.columns.split(",") if c.strip()]
    # 見出し
    print("\t".join(cols))
    for u in filtered_users:
        row = []
        for c in cols:
            val = u.get(c, "")
            # ネスト対策（軽くJSON化）
            if isinstance(val, (dict, list)):
                import json
                val = json.dumps(val, ensure_ascii=False)
            row.append(str(val))
        print("\t".join(row))

if __name__ == "__main__":
    main()
