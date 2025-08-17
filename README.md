# LiteLLM User Registration Management Tools

A collection of Python scripts to streamline user management for LiteLLM Proxy servers. Perform bulk user registration, deletion, listing, and synchronization using CSV files.

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Scripts Overview](#scripts-overview)
- [Usage](#usage)
- [CSV File Formats](#csv-file-formats)
- [User Roles](#user-roles)
- [Troubleshooting](#troubleshooting)
- [Detailed Documentation](#detailed-documentation)

## 🚀 Features

This toolset provides the following functionality:

- **Bulk User Registration** ([`add_user.py`](add_user.py)) - Create users in bulk from CSV files
- **Bulk User Deletion** ([`del_user.py`](del_user.py)) - Delete users in bulk based on CSV files
- **User Listing** ([`list_user.py`](list_user.py)) - Display and filter registered users
- **User Synchronization** ([`sync_user.py`](sync_user.py)) - Synchronize CSV files with LiteLLM state

## 💻 Requirements

- Python 3.7 or higher
- LiteLLM Proxy Server
- Administrator privileges (Master Key)

## 📦 Installation

1. Clone or download the repository:
```bash
git clone <repository-url>
cd litellm-user-registration
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Environment Variables Setup

Create a `.env` file and configure the following environment variables:

```bash
# LiteLLM Proxy Server base URL
LITELLM_BASE_URL=http://localhost:4000

# LiteLLM Master Key
LITELLM_MASTER_KEY=your_master_key_here
```

### .env File Example

Use the `.env.example` file as a reference for configuration:

```bash
cp .env.example .env
# Edit the .env file to set actual values
```

## 📁 Scripts Overview

| Script | Function | Primary Use | Detailed Manual |
|--------|----------|-------------|-----------------|
| [`add_user.py`](add_user.py) | Bulk User Registration | Mass registration of new users | [📖 Detailed Manual](docs/add_user_manual.md) |
| [`del_user.py`](del_user.py) | Bulk User Deletion | Mass deletion of unwanted users | [📖 Detailed Manual](docs/del_user_manual.md) |
| [`list_user.py`](list_user.py) | User Listing | Check current user status | [📖 Detailed Manual](docs/list_user_manual.md) |
| [`sync_user.py`](sync_user.py) | User Synchronization | Sync differences with CSV | [📖 Detailed Manual](docs/sync_user_manual.md) |

## 🔧 Usage

### Basic Usage Examples

```bash
# Bulk user registration (dry run)
python add_user.py --csv-file user_addlist.csv --dry-run

# Bulk user registration (execute)
python add_user.py --csv-file user_addlist.csv --debug

# User listing
python list_user.py --role internal_user

# User synchronization (dry run)
python sync_user.py --csv-file user_list.csv --dry-run

# Bulk user deletion
python del_user.py --csv-file user_dellist.csv --debug
```

### Common Options

Common options available for all scripts:

- `--base-url`: LiteLLM Proxy server URL (default: http://localhost:4000)
- `--master-key`: Master key (can also be set via LITELLM_MASTER_KEY environment variable)
- `--debug`: Display debug information
- `--dry-run`: Preview execution without making actual changes

## 📄 CSV File Formats

### User Registration (user_addlist.csv)

```csv
email,role,team_name,key_name
user@example.com,internal_user,development,00000001_chatbot
admin@company.com,proxy_admin,admin,00000002_admin
viewer@company.com,internal_user_viewer,support,00000003_support
```

### User Synchronization (user_list.csv)

```csv
email,role,team_name
user@example.com,internal_user,development
admin@company.com,proxy_admin,admin
```

### User Deletion (user_dellist.csv)

```csv
email
old_user@example.com
inactive@company.com
```

### Field Descriptions

- **email** (required): User's email address
- **role** (optional): User role (defaults to proxy_admin if not specified)
- **team_name** (optional): Team name
- **key_name** (optional): API key name (add_user.py only)

## 👥 User Roles

Available user roles in LiteLLM:

| Role | Description | Permission Level |
|------|-------------|------------------|
| `proxy_admin` | Proxy Administrator | Full permissions |
| `proxy_admin_viewer` | Proxy Administrator (Read-only) | Read-only |
| `internal_user` | Internal User | Basic permissions |
| `internal_user_viewer` | Internal User (Read-only) | Read-only |
| `default` | Default User | Standard permissions |

## 📊 Output Files

Each script outputs execution results to CSV files:

### Success Output

- `user_reg_result.csv` - Successfully registered users (add_user.py)
- `user_del_result.csv` - Successfully deleted users (del_user.py)
- `user_sync_result.csv` - Synchronization results (sync_user.py)

### Error Output

- `user_reg_error.csv` - Failed user registrations (add_user.py)
- `user_del_error.csv` - Failed user deletions (del_user.py)

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Error
```
ERROR: --master-key or env LITELLM_MASTER_KEY is required.
```
**Solution**: Set LITELLM_MASTER_KEY correctly in the `.env` file.

#### 2. Connection Error
```
HTTPError: 404 - Not Found
```
**Solution**: Verify that `--base-url` or LITELLM_BASE_URL is correctly configured.

#### 3. CSV File Error
```
ERROR: CSV file 'user_addlist.csv' not found.
```
**Solution**: Ensure the CSV file exists and the correct path is specified.

#### 4. User Duplicate Error
```
User already exists in the system
```
**Solution**: For existing users, use `sync_user.py` to update them.

### Using Debug Mode

When issues occur, use the `--debug` option to view detailed information:

```bash
python add_user.py --csv-file user_addlist.csv --debug
```

### Using Dry Run Mode

Before making actual changes, use the `--dry-run` option to preview execution:

```bash
python sync_user.py --csv-file user_list.csv --dry-run
```

## 📚 Detailed Documentation

For detailed usage instructions for each script, please refer to the following manuals:

- [📖 add_user.py Detailed Manual](docs/add_user_manual.md) - Comprehensive guide for bulk user registration
- [📖 del_user.py Detailed Manual](docs/del_user_manual.md) - Comprehensive guide for bulk user deletion
- [📖 list_user.py Detailed Manual](docs/list_user_manual.md) - Comprehensive guide for user listing
- [📖 sync_user.py Detailed Manual](docs/sync_user_manual.md) - Comprehensive guide for user synchronization

## 📝 License

This project is released under the MIT License.

## 🤝 Contributing

Bug reports and feature requests are welcome via GitHub Issues. Pull requests are also welcome.

## 📞 Support

For technical questions or support, please use the project's Issue page.