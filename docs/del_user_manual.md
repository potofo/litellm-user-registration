# del_user.py Manual

## Overview

[`del_user.py`](../del_user.py) is a script for bulk user deletion from LiteLLM Proxy servers based on email addresses listed in CSV files. It provides a safe deletion process and detailed error reporting.

## Key Features

- **Bulk user deletion from CSV files**
- **User search by email address**
- **Safe deletion process**
- **Detailed error reporting**
- **Dry run mode**
- **Deletion result recording**

## Usage

### Basic Usage Examples

```bash
# Dry run (no actual deletion)
python del_user.py --csv-file user_dellist.csv --dry-run

# Actually delete users
python del_user.py --csv-file user_dellist.csv

# Execute with debug information
python del_user.py --csv-file user_dellist.csv --debug
```

### Command Line Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `--base-url` | LiteLLM Proxy server base URL | `http://localhost:4000` |
| `--master-key` | Master key | Retrieved from environment variable `LITELLM_MASTER_KEY` |
| `--csv-file` | Input CSV file path | `user_dellist.csv` |
| `--dry-run` | Display execution content without actual deletion | - |
| `--debug` | Display debug information | - |

## CSV File Format

### Input File (user_dellist.csv)

```csv
email
old_user@example.com
inactive@company.com
test_user@example.com
```

### Field Details

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `email` | ✅ | Email address of user to delete | `user@example.com` |

## Output Files

### Success Output (user_del_result.csv)

```csv
email,user_id,status
user@example.com,user_123,Deleted
admin@company.com,user_456,Deleted
```

### Error Output (user_del_error.csv)

```csv
email,user_id,error_reason
notfound@example.com,,User not found in the system
invalid@,user_789,Failed to delete user (API error)
```

## Execution Flow

1. **Environment variables and parameter validation**
2. **CSV file reading**
3. **For each user, execute the following**:
   - Search for user ID from email address
   - If user exists, call deletion API
   - Record deletion result
4. **Result output**
   - Output successful users to `user_del_result.csv`
   - Output failed users to `user_del_error.csv`

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `User not found in the system` | User with specified email address does not exist | Check email address |
| `Unauthorized` | Master Key is invalid | Set correct Master Key |
| `Forbidden` | No deletion permission | Use Master Key with appropriate permissions |
| `Bad request` | Invalid user ID format | Check user ID format |
| `Connection refused` | Cannot connect to LiteLLM server | Check server URL and operational status |

### HTTP Status Code Errors

| Status Code | Description | Solution |
|-------------|-------------|----------|
| 400 | Bad Request - Invalid request | Check user ID format |
| 401 | Unauthorized - Authentication failed | Check Master Key |
| 403 | Forbidden - Insufficient permissions | Use key with deletion permissions |
| 404 | Not Found - User not found | Check user existence |

## Safety Features

### Pre-deletion Confirmation

This script implements the following safety measures:

1. **Dry run mode**: Preview deletion targets with `--dry-run` option
2. **User existence check**: Verify user existence before deletion
3. **Detailed logging**: Comprehensive recording of deletion process
4. **Error handling**: Proper handling of various errors

### Recommended Procedure

```bash
# 1. First check deletion targets with dry run
python del_user.py --csv-file user_dellist.csv --dry-run

# 2. After confirming targets are correct, actually delete
python del_user.py --csv-file user_dellist.csv --debug

# 3. Check deletion status in result files
cat user_del_result.csv
cat user_del_error.csv
```

## Debug Mode

Use the `--debug` option to display detailed execution information:

```bash
python del_user.py --csv-file user_dellist.csv --debug
```

Debug information includes:
- User search process
- API request/response details
- Deletion process details
- Detailed error information

## Usage Examples

### Example 1: Basic User Deletion

```bash
# Create user_dellist.csv
echo "email" > user_dellist.csv
echo "old_user@example.com" >> user_dellist.csv
echo "inactive@company.com" >> user_dellist.csv

# Check with dry run
python del_user.py --csv-file user_dellist.csv --dry-run

# Actually delete
python del_user.py --csv-file user_dellist.csv
```

### Example 2: Bulk User Deletion

```bash
# Create large user list
cat > user_dellist.csv << EOF
email
test1@example.com
test2@example.com
test3@example.com
old_admin@company.com
EOF

# Execute deletion in debug mode
python del_user.py --csv-file user_dellist.csv --debug
```

### Example 3: Checking Deletion Results

```bash
# Execute deletion
python del_user.py --csv-file user_dellist.csv

# Check successful deletions
echo "=== Successful Deletions ==="
cat user_del_result.csv

# Check failed deletions
echo "=== Failed Deletions ==="
cat user_del_error.csv
```

## Output File Details

### user_del_result.csv

Record of successful deletions:

| Field | Description |
|-------|-------------|
| `email` | Email address of deleted user |
| `user_id` | ID of deleted user |
| `status` | Deletion status (always "Deleted") |

### user_del_error.csv

Record of failed deletions:

| Field | Description |
|-------|-------------|
| `email` | Email address of user that failed to delete |
| `user_id` | User ID (empty if not found) |
| `error_reason` | Reason for failure |

## Important Notes

1. **Irreversible Operation**: User deletion is an irreversible operation. Always confirm with dry run before deletion.

2. **Master Key Management**: Master Key is confidential information. Manage it with environment variables and do not write it directly in code.

3. **Backup**: If there is important user data, take a backup before deletion.

4. **Permission Check**: Ensure you are using a Master Key with deletion permissions.

5. **Related Data**: User deletion may also delete related API keys and team assignments.

## Troubleshooting

### Common Issues

**Q: "User not found" errors occur frequently**
A: Check if email addresses in the CSV file are accurate. Users may have already been deleted.

**Q: Deletion permission errors occur**
A: Verify that the Master Key being used has deletion permissions.

**Q: Only some users fail to delete**
A: Check `user_del_error.csv` for error details and handle individually.

### Log Checking

Execution logs are output to standard error output:

```bash
python del_user.py --csv-file user_dellist.csv --debug 2> del_user.log
```

### Checking Deletion Status

After deletion, you can verify if users were actually deleted:

```bash
# Check with user list
python list_user.py --email-like "@example.com"
```

## Related Scripts

- [`add_user.py`](add_user_manual.md) - Bulk user registration
- [`sync_user.py`](sync_user_manual.md) - User information synchronization
- [`list_user.py`](list_user_manual.md) - User list display

## Security Considerations

1. **Access Control**: Restrict execution of deletion scripts to trusted administrators only.
2. **Audit Logs**: Maintain records of deletion operations for auditability.
3. **Approval Process**: Recommend implementing approval processes for deletion of important users.
4. **Regular Review**: Regularly review deletion target lists to prevent accidental deletions.