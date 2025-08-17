# sync_user.py Manual

## Overview

[`sync_user.py`](../sync_user.py) is an advanced script for synchronizing user information between CSV files and LiteLLM Proxy servers. It automatically determines and executes user additions, deletions, and updates in bulk. It provides the most comprehensive user management functionality.

## Key Features

- **Complete synchronization between CSV and LiteLLM**
- **Difference detection and automatic decision making**
- **User addition, deletion, and updates**
- **Safe team assignment updates**
- **Role change processing**
- **Fallback functionality (user recreation)**
- **Detailed synchronization reports**
- **Selective synchronization options**

## Usage

### Basic Usage Examples

```bash
# Dry run (no actual changes)
python sync_user.py --csv-file user_list.csv --dry-run

# Execute complete synchronization
python sync_user.py --csv-file user_list.csv

# Synchronize with deletion disabled
python sync_user.py --csv-file user_list.csv --no-delete

# Synchronize with updates disabled
python sync_user.py --csv-file user_list.csv --no-update

# Execute with debug information
python sync_user.py --csv-file user_list.csv --debug
```

### Command Line Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `--base-url` | LiteLLM Proxy server base URL | `http://localhost:4000` |
| `--master-key` | Master key | Retrieved from environment variable `LITELLM_MASTER_KEY` |
| `--csv-file` | Input CSV file path | `user_list.csv` |
| `--user-role` | Default user role | `proxy_admin` |
| `--dry-run` | Display execution content without actual changes | - |
| `--no-delete` | Disable user deletion | - |
| `--no-update` | Disable user updates | - |
| `--debug` | Display debug information | - |

## CSV File Format

### Input File (user_list.csv)

```csv
email,role,team_name
user@example.com,internal_user,development
admin@company.com,proxy_admin,admin
viewer@company.com,internal_user_viewer,support
api_user@example.com,internal_user,api_team
```

### Field Details

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `email` | ✅ | User's email address | `user@example.com` |
| `role` | ❌ | User role | `internal_user` |
| `team_name` | ❌ | Team name | `development` |

## Synchronization Process

### 1. Difference Detection

The script automatically detects the following differences:

- **Addition targets**: Users in CSV but not in LiteLLM
- **Deletion targets**: Users in LiteLLM but not in CSV
- **Update targets**: Users in both but with different roles or teams
- **No changes**: Users in both with matching information

### 2. Execution Order

1. **User Addition** - Create new users
2. **User Deletion** - Delete unnecessary users (can be disabled with `--no-delete`)
3. **User Updates** - Update existing user information (can be disabled with `--no-update`)

### 3. Safe Update Features

When updating teams, the following safety features are provided:

- **Gradual updates**: Add to new team before removing from old team
- **Update verification**: Verify actual state after updates
- **Fallback**: Recreate user if update fails

## Output Files

### Synchronization Report (user_sync_result.csv)

```csv
action,email,user_id,role,team_name,api_keys,status,error_reason
ADDED,new_user@example.com,user_123,internal_user,development,sk-abc123...,SUCCESS,
DELETED,old_user@example.com,user_456,internal_user,support,,SUCCESS,
UPDATED,existing@example.com,user_789,proxy_admin,admin,,SUCCESS,
UNCHANGED,stable@example.com,user_012,internal_user,development,,SUCCESS,
```

### Report Field Details

| Field | Description |
|-------|-------------|
| `action` | Action performed (ADDED/DELETED/UPDATED/UNCHANGED) |
| `email` | User's email address |
| `user_id` | User ID |
| `role` | User role |
| `team_name` | Team name |
| `api_keys` | API key (only for new creations) |
| `status` | Execution result (SUCCESS/FAILED) |
| `error_reason` | Error details (only on failure) |

## Advanced Features

### Safe Team Update Features

When changing teams, updates are performed safely with the following steps:

1. **Temporarily assign to current team + new team**
2. **Update to new team only**
3. **Verify update results**
4. **Recreate user if failed**

```bash
# Check team update debug information
python sync_user.py --csv-file user_list.csv --debug
```

### Fallback Functionality

If user update fails, automatically execute the following:

1. **Delete existing user**
2. **Create new user with correct information**
3. **Verify results**

### API Key Management

- **New users**: API keys are automatically generated during creation and recorded in the report
- **Existing users**: API keys cannot be retrieved for security reasons
- **Updated users**: API keys are not changed

## Usage Examples

### Example 1: Basic Synchronization

```bash
# Create user_list.csv
cat > user_list.csv << EOF
email,role,team_name
user1@example.com,internal_user,development
user2@example.com,proxy_admin,admin
EOF

# Check with dry run
python sync_user.py --csv-file user_list.csv --dry-run

# Actually synchronize
python sync_user.py --csv-file user_list.csv
```

### Example 2: Synchronization with Deletion Disabled

```bash
# Synchronize without deleting existing users
python sync_user.py --csv-file user_list.csv --no-delete --debug
```

### Example 3: Update-only Synchronization

```bash
# Execute only updates, no additions or deletions
python sync_user.py --csv-file user_list.csv --no-delete --debug
```

### Example 4: Large-scale Synchronization

```bash
# Synchronize with CSV containing many users
python sync_user.py --csv-file large_user_list.csv --debug > sync.log 2>&1
```

## Dry Run Mode

Preview execution content with the `--dry-run` option:

```bash
python sync_user.py --csv-file user_list.csv --dry-run
```

Sample output:
```
Synchronization Plan:
  Users to add: 2
  Users to delete: 1
  Users to update: 3
  Users unchanged: 5

DRY RUN - Changes that would be made:

  Users to ADD:
    + new_user@example.com (Role: internal_user, Team: development)
    + another@example.com (Role: proxy_admin, Team: admin)

  Users to DELETE:
    - old_user@example.com (Role: internal_user, Team: support)

  Users to UPDATE:
    ~ existing@example.com (Role: internal_user → proxy_admin, Teams: old_team → new_team)
```

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Team not found` | Specified team does not exist | Check team name or create team beforehand |
| `User recreation failed` | Fallback process failed | Manually check and fix user |
| `Unauthorized` | Master Key is invalid | Set correct Master Key |
| `Connection timeout` | Network error | Check server status |

### Partial Failure Handling

When processing fails for some users:

1. **Successful users** are processed normally
2. **Failed users** are recorded in the report
3. **Error details** are recorded in the `error_reason` field

## Debug and Troubleshooting

### Debug Mode

```bash
python sync_user.py --csv-file user_list.csv --debug
```

Debug information includes:
- Difference detection process
- API request/response
- Detailed team update steps
- Fallback process details

### Log Saving

```bash
# Save detailed logs to file
python sync_user.py --csv-file user_list.csv --debug > sync.log 2>&1
```

### Checking Synchronization Results

```bash
# Check status after synchronization
python list_user.py --show-all

# Check synchronization report
cat user_sync_result.csv
```

## Performance Considerations

### Large User Processing

- **Batch processing**: Efficient processing even with large numbers of users
- **Error continuation**: Continue processing even if some fail
- **Memory efficiency**: Suppress memory usage even with large data

### Network Optimization

- **Minimize API calls**: Call APIs only when necessary
- **Timeout settings**: Set appropriate timeout values
- **Retry functionality**: Automatic retry for temporary errors

## Usage Examples and Workflows

### Regular Synchronization

```bash
#!/bin/bash
# daily_sync.sh - Daily synchronization script

# 1. Backup current status
python list_user.py > backup_$(date +%Y%m%d).txt

# 2. Check with dry run
python sync_user.py --csv-file user_list.csv --dry-run

# 3. Actually synchronize
python sync_user.py --csv-file user_list.csv --debug

# 4. Check results
echo "Sync completed. Check user_sync_result.csv for details."
```

### Gradual Migration

```bash
# 1. Add only new users with deletion disabled
python sync_user.py --csv-file user_list.csv --no-delete

# 2. Execute only updates
python sync_user.py --csv-file user_list.csv --no-delete --no-add

# 3. Finally perform complete synchronization
python sync_user.py --csv-file user_list.csv
```

## Security Considerations

### Access Control

1. **Master Key management**: Manage safely with environment variables
2. **Execution permissions**: Restrict to trusted administrators only
3. **Audit logs**: Maintain records of synchronization operations

### Data Protection

1. **Backup**: Backup current state before synchronization
2. **Gradual execution**: Preview with dry run
3. **Rollback**: Prepare recovery procedures for when problems occur

## Related Scripts

- [`add_user.py`](add_user_manual.md) - Bulk user registration
- [`del_user.py`](del_user_manual.md) - Bulk user deletion
- [`list_user.py`](list_user_manual.md) - User list display

## Important Notes

1. **Irreversible operations**: User deletion is irreversible. Preview with `--dry-run`
2. **Team pre-creation**: Teams specified in CSV must be created beforehand
3. **API keys**: Existing user API keys are not changed
4. **Permissions**: Appropriate administrator permissions are required
5. **Backup**: Back up important data beforehand

## Best Practices

1. **Regular execution**: Maintain data consistency with regular synchronization
2. **Gradual introduction**: Execute large changes gradually
3. **Monitoring**: Regularly check synchronization results
4. **Documentation**: Document synchronization rules and procedures
5. **Testing**: Verify in test environment before production