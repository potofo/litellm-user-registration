# add_user.py Manual

## Overview

[`add_user.py`](../add_user.py) is a script for bulk user registration to LiteLLM Proxy servers from CSV files. It provides advanced features such as team assignment, custom API key name configuration, and automatic invitation URL generation for password setup.

## Key Features

- **Bulk user registration from CSV files**
- **Automatic team assignment**
- **Custom API key name configuration**
- **Automatic invitation URL generation for password setup**
- **Duplicate user detection and skipping**
- **Detailed error reporting**
- **Dry run mode**

## Usage

### Basic Usage Examples

```bash
# Dry run (no actual registration)
python add_user.py --csv-file user_addlist.csv --dry-run

# Actually register users
python add_user.py --csv-file user_addlist.csv

# Execute with debug information
python add_user.py --csv-file user_addlist.csv --debug

# Output existing user information to CSV
python add_user.py --update-existing
```

### Command Line Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `--base-url` | LiteLLM Proxy server base URL | `http://localhost:4000` |
| `--master-key` | Master key | Retrieved from environment variable `LITELLM_MASTER_KEY` |
| `--csv-file` | Input CSV file path | `user_addlist.csv` |
| `--user-role` | Default user role | `proxy_admin` |
| `--dry-run` | Display execution content without actual registration | - |
| `--debug` | Display debug information | - |
| `--update-existing` | Output existing user information to CSV | - |

## CSV File Format

### Input File (user_addlist.csv)

```csv
email,role,team_name,key_name
user@example.com,internal_user,development,00000001_chatbot
admin@company.com,proxy_admin,admin,00000002_admin
viewer@company.com,internal_user_viewer,support,00000003_support
```

### Field Details

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `email` | ✅ | User's email address | `user@example.com` |
| `role` | ❌ | User role | `internal_user` |
| `team_name` | ❌ | Team name | `development` |
| `key_name` | ❌ | API key name | `00000001_chatbot` |

### Available User Roles

| Role | Description |
|------|-------------|
| `internal_user` | Standard internal user |
| `internal_user_viewer` | Read-only internal user |
| `proxy_admin` | Proxy administrator (full permissions) |
| `proxy_admin_viewer` | Read-only proxy administrator |
| `default` | Default user |

## Output Files

### Success Output (user_reg_result.csv)

```csv
email,role,user_id,team_name,models,api_keys,invitation_url
user@example.com,internal_user,user_123,development,All proxy models,sk-abc123...,http://localhost:4000/ui/?invitation_id=inv_456&action=reset_password
```

### Error Output (user_reg_error.csv)

```csv
email,role,error_reason
duplicate@example.com,internal_user,User already exists in the system
invalid@,internal_user,Invalid email format
```

## Execution Flow

1. **Environment variables and parameter validation**
2. **CSV file reading**
3. **Duplicate check with existing users**
4. **User creation**
   - Create user using LiteLLM API
   - Team assignment (if specified)
   - API key name configuration (if specified)
5. **Invitation URL generation**
   - Automatically generate invitation URLs for password setup
   - Try multiple endpoints
6. **Result output**
   - Output successful users to `user_reg_result.csv`
   - Output failed users to `user_reg_error.csv`

## Advanced Features

### Automatic Team Assignment

When `team_name` is specified in the CSV file, users are automatically assigned to the specified team:

```csv
email,role,team_name
user@example.com,internal_user,development
```

### Custom API Key Names

Use the `key_name` field to set custom names for automatically generated API keys:

```csv
email,role,team_name,key_name
user@example.com,internal_user,development,00000001_chatbot
```

### Invitation URL Generation

Invitation URLs for password setup are automatically generated for newly created users. This feature allows users to securely set their passwords.

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `User already exists` | User with the same email address already exists | Use `sync_user.py` for updating existing users |
| `Invalid role` | Specified role is invalid | Check valid role names |
| `Team not found` | Specified team does not exist | Check team name or create team beforehand |
| `Unauthorized` | Master Key is invalid | Set correct Master Key |
| `Connection refused` | Cannot connect to LiteLLM server | Check server URL and operational status |

### Debug Mode

Use the `--debug` option to display detailed execution information:

```bash
python add_user.py --csv-file user_addlist.csv --debug
```

Debug information includes:
- API request/response details
- Team search results
- API key creation process
- Invitation URL generation process

## Usage Examples

### Example 1: Basic User Registration

```bash
# Create user_addlist.csv
echo "email,role" > user_addlist.csv
echo "user1@example.com,internal_user" >> user_addlist.csv
echo "user2@example.com,proxy_admin" >> user_addlist.csv

# Check with dry run
python add_user.py --csv-file user_addlist.csv --dry-run

# Actually register
python add_user.py --csv-file user_addlist.csv
```

### Example 2: User Registration with Teams

```bash
# Create CSV file with teams
cat > user_addlist.csv << EOF
email,role,team_name
dev1@example.com,internal_user,development
dev2@example.com,internal_user,development
admin@example.com,proxy_admin,admin
EOF

# Execute registration
python add_user.py --csv-file user_addlist.csv --debug
```

### Example 3: User Registration with Custom API Key Names

```bash
# Create CSV file with API key names
cat > user_addlist.csv << EOF
email,role,team_name,key_name
chatbot@example.com,internal_user,ai_team,00000001_chatbot
api_user@example.com,internal_user,api_team,00000002_api_access
EOF

# Execute registration
python add_user.py --csv-file user_addlist.csv --debug
```

## Important Notes

1. **Master Key Management**: Master Key is confidential information. Manage it with environment variables and do not write it directly in code.

2. **Duplicate Check**: Registration with the same email address as existing users is automatically skipped.

3. **Team Pre-creation**: Teams specified in CSV must be created beforehand in LiteLLM.

4. **API Key Management**: Generated API keys are recorded in `user_reg_result.csv`, but cannot be retrieved later for security reasons.

5. **Invitation URLs**: Invitation URLs may have expiration dates. Share them with users promptly after generation.

## Troubleshooting

### Common Issues

**Q: "Team not found" error occurs**
A: The specified team name may not exist in LiteLLM. Check the team name or create the team beforehand.

**Q: Invitation URLs are not generated**
A: Depending on the LiteLLM version or configuration, the invitation feature may not be available. Set passwords manually.

**Q: API key names are not set**
A: API key update may have failed. Check details with the `--debug` option.

### Log Checking

Execution logs are output to standard error output. You can redirect and save them:

```bash
python add_user.py --csv-file user_addlist.csv --debug 2> add_user.log
```

## Related Scripts

- [`sync_user.py`](sync_user_manual.md) - User information synchronization
- [`del_user.py`](del_user_manual.md) - Bulk user deletion
- [`list_user.py`](list_user_manual.md) - User list display