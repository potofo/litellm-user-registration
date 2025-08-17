# list_user.py Manual

## Overview

[`list_user.py`](../list_user.py) is a script that displays a list of users registered on LiteLLM Proxy servers and provides filtering functionality. It is used for understanding the current state of user management and searching for users under specific conditions.

## Key Features

- **Display list of all users**
- **Role-based filtering**
- **Email address partial match search**
- **Custom column display**
- **Automatic internal user filtering**
- **Pagination support**
- **Tab-separated output format**

## Usage

### Basic Usage Examples

```bash
# Display all internal users
python list_user.py

# Display users with specific role
python list_user.py --role internal_user

# Search by email address
python list_user.py --email-like "@company.com"

# Display all users (internal and external)
python list_user.py --show-all

# Execute with debug information
python list_user.py --debug
```

### Command Line Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `--base-url` | LiteLLM Proxy server base URL | `http://localhost:4000` |
| `--master-key` | Master key | Retrieved from environment variable `LITELLM_MASTER_KEY` |
| `--role` | Filter by specific role | None |
| `--email-like` | Partial match search for email addresses | None |
| `--columns` | Specify columns to display (comma-separated) | `user_id,user_email,user_role,teams,created_at,updated_at` |
| `--show-all` | Display all users including non-internal users | None |
| `--debug` | Display debug information | None |

## Filtering Features

### Role-based Filtering

Available roles:

| Role | Description |
|------|-------------|
| `internal_user` | Standard internal user |
| `internal_user_viewer` | Read-only internal user |
| `proxy_admin` | Proxy administrator |
| `proxy_admin_viewer` | Read-only proxy administrator |
| `default` | Default user |
| `user` | General user |
| `end_user` | End user |

```bash
# Display only proxy_admin role users
python list_user.py --role proxy_admin

# Display only internal_user role users
python list_user.py --role internal_user
```

### Email Address Search

Partial match search for email addresses (case-insensitive):

```bash
# Search for users with @company.com domain
python list_user.py --email-like "@company.com"

# Search for users containing specific name
python list_user.py --email-like "admin"

# Combine multiple conditions
python list_user.py --role proxy_admin --email-like "@company.com"
```

## Output Format

### Default Output

```
user_id	user_email	user_role	teams	created_at	updated_at
user_123	user@example.com	internal_user	["team_456"]	2024-01-01T00:00:00Z	2024-01-01T00:00:00Z
user_789	admin@company.com	proxy_admin	["team_123","team_456"]	2024-01-01T00:00:00Z	2024-01-01T00:00:00Z
```

### Custom Column Display

Customize displayed columns with the `--columns` option:

```bash
# Display basic information only
python list_user.py --columns "user_email,user_role"

# Display detailed information
python list_user.py --columns "user_id,user_email,user_role,teams,models,created_at"
```

### Available Columns

| Column Name | Description |
|-------------|-------------|
| `user_id` | User ID |
| `user_email` | Email address |
| `user_role` | User role |
| `teams` | Team memberships (JSON array) |
| `models` | Available models (JSON array) |
| `created_at` | Creation date/time |
| `updated_at` | Update date/time |
| `max_budget` | Maximum budget |
| `spend` | Usage amount |
| `user_alias` | User alias |

## Usage Examples

### Example 1: Basic User List Display

```bash
# Display all internal users
python list_user.py
```

Sample output:
```
user_id	user_email	user_role	teams	created_at	updated_at
user_123	user@example.com	internal_user	[]	2024-01-01T00:00:00Z	2024-01-01T00:00:00Z
user_456	admin@company.com	proxy_admin	["team_123"]	2024-01-01T00:00:00Z	2024-01-01T00:00:00Z
```

### Example 2: Specific Role User Search

```bash
# Display only proxy_admin role users
python list_user.py --role proxy_admin
```

### Example 3: Domain-based User Search

```bash
# Search for users from specific domain
python list_user.py --email-like "@company.com"
```

### Example 4: Custom Column Display

```bash
# Display only email address and role
python list_user.py --columns "user_email,user_role"
```

Sample output:
```
user_email	user_role
user@example.com	internal_user
admin@company.com	proxy_admin
```

### Example 5: Display All Users

```bash
# Display all users including internal and external
python list_user.py --show-all
```

## Data Processing and Filtering

### Automatic Internal User Filtering

By default, only users meeting the following conditions are displayed:

1. **Email address exists** (excludes `default_user_id` etc.)
2. **Has internal role** (roles defined in `INTERNAL_ROLES`)

### Sensitive Information Exclusion

The following information is automatically excluded from output:

- `password`
- `hashed_password`
- `salt`
- `token`

### JSON Format Data Processing

JSON arrays such as teams and models are displayed as strings:

```
teams: ["team_123", "team_456"]
models: ["gpt-4", "gpt-3.5-turbo"]
```

## Debug Mode

Use the `--debug` option to display detailed execution information:

```bash
python list_user.py --debug
```

Debug information includes:
- API request URL
- Response status
- Response headers
- Number of users retrieved
- Filtering results

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Unauthorized` | Master Key is invalid | Set correct Master Key |
| `Connection refused` | Cannot connect to LiteLLM server | Check server URL and operational status |
| `No users found` | No users match the conditions | Check filter conditions |

### HTTP Error Handling

```bash
# Check error details
python list_user.py --debug
```

## Output Utilization

### Save to CSV File

```bash
# Convert tab-separated to CSV format and save
python list_user.py --columns "user_email,user_role" | tr '\t' ',' > users.csv
```

### Integration with Other Scripts

```bash
# Get user list and sync with sync_user.py
python list_user.py --columns "user_email,user_role" > current_users.txt
```

### Filtering and Pipeline

```bash
# Extract users meeting specific conditions
python list_user.py --role internal_user | grep "@company.com"

# Count users
python list_user.py --role proxy_admin | wc -l
```

## Performance Considerations

### Large User Processing

- The script supports pagination functionality and can efficiently process large numbers of users
- The `--debug` option outputs large amounts of logs, so use carefully in production environments

### Network Optimization

- Specifying only necessary columns can reduce network transfer volume
- Filtering is performed client-side, so caution is needed when there are large numbers of users

## Usage Examples and Workflows

### Daily Management Tasks

```bash
# 1. Check overview of all users
python list_user.py --columns "user_email,user_role,teams"

# 2. Check administrator users
python list_user.py --role proxy_admin

# 3. Check users from specific domain
python list_user.py --email-like "@company.com"

# 4. When detailed information is needed
python list_user.py --show-all --debug
```

### Troubleshooting

```bash
# Identify problematic users
python list_user.py --email-like "problem_user@"

# Get detailed information for all users
python list_user.py --show-all --columns "user_id,user_email,user_role,teams,created_at,updated_at"
```

## Related Scripts

- [`add_user.py`](add_user_manual.md) - Bulk user registration
- [`del_user.py`](del_user_manual.md) - Bulk user deletion
- [`sync_user.py`](sync_user_manual.md) - User information synchronization

## Important Notes

1. **Permissions**: Appropriate permissions are required to retrieve user lists
2. **Privacy**: Handle user information with care
3. **Performance**: Execution time may be long in environments with large numbers of users
4. **Filtering**: Client-side filtering may be inefficient with large amounts of data