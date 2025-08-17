# add_user.py マニュアル

## 概要

[`add_user.py`](../add_user.py)は、CSVファイルからLiteLLM Proxyサーバーにユーザーを一括登録するためのスクリプトです。チーム割り当て、カスタムAPIキー名の設定、パスワード設定用の招待URLの生成などの高度な機能を提供します。

## 主な機能

- **CSVファイルからの一括ユーザー登録**
- **チーム自動割り当て**
- **カスタムAPIキー名の設定**
- **パスワード設定用招待URLの自動生成**
- **重複ユーザーの検出とスキップ**
- **詳細なエラーレポート**
- **ドライランモード**

## 使用方法

### 基本的な使用例

```bash
# ドライラン（実際の登録は行わない）
python add_user.py --csv-file user_addlist.csv --dry-run

# 実際にユーザーを登録
python add_user.py --csv-file user_addlist.csv

# デバッグ情報付きで実行
python add_user.py --csv-file user_addlist.csv --debug

# 既存ユーザー情報をCSVに出力
python add_user.py --update-existing
```

### コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--base-url` | LiteLLM ProxyサーバーのベースURL | `http://localhost:4000` |
| `--master-key` | 管理者キー | 環境変数`LITELLM_MASTER_KEY`から取得 |
| `--csv-file` | 入力CSVファイルのパス | `user_addlist.csv` |
| `--user-role` | デフォルトユーザーロール | `proxy_admin` |
| `--dry-run` | 実際の登録を行わずに実行内容を表示 | - |
| `--debug` | デバッグ情報を表示 | - |
| `--update-existing` | 既存ユーザー情報をCSVに出力 | - |

## CSVファイル形式

### 入力ファイル（user_addlist.csv）

```csv
email,role,team_name,key_name
user@example.com,internal_user,development,00000001_chatbot
admin@company.com,proxy_admin,admin,00000002_admin
viewer@company.com,internal_user_viewer,support,00000003_support
```

### フィールド詳細

| フィールド | 必須 | 説明 | 例 |
|-----------|------|------|-----|
| `email` | ✅ | ユーザーのメールアドレス | `user@example.com` |
| `role` | ❌ | ユーザーロール | `internal_user` |
| `team_name` | ❌ | 所属チーム名 | `development` |
| `key_name` | ❌ | APIキーの名前 | `00000001_chatbot` |

### 利用可能なユーザーロール

| ロール | 説明 |
|--------|------|
| `internal_user` | 標準内部ユーザー |
| `internal_user_viewer` | 読み取り専用内部ユーザー |
| `proxy_admin` | プロキシ管理者（全権限） |
| `proxy_admin_viewer` | 読み取り専用プロキシ管理者 |
| `default` | デフォルトユーザー |

## 出力ファイル

### 成功時の出力（user_reg_result.csv）

```csv
email,role,user_id,team_name,models,api_keys,invitation_url
user@example.com,internal_user,user_123,development,All proxy models,sk-abc123...,http://localhost:4000/ui/?invitation_id=inv_456&action=reset_password
```

### エラー時の出力（user_reg_error.csv）

```csv
email,role,error_reason
duplicate@example.com,internal_user,User already exists in the system
invalid@,internal_user,Invalid email format
```

## 実行フロー

1. **環境変数とパラメータの検証**
2. **CSVファイルの読み込み**
3. **既存ユーザーの重複チェック**
4. **ユーザー作成**
   - LiteLLM APIを使用してユーザー作成
   - チーム割り当て（指定されている場合）
   - APIキー名の設定（指定されている場合）
5. **招待URL生成**
   - パスワード設定用の招待URLを自動生成
   - 複数のエンドポイントを試行
6. **結果の出力**
   - 成功したユーザーを`user_reg_result.csv`に出力
   - 失敗したユーザーを`user_reg_error.csv`に出力

## 高度な機能

### チーム自動割り当て

CSVファイルで`team_name`を指定すると、ユーザーを自動的に指定されたチームに割り当てます：

```csv
email,role,team_name
user@example.com,internal_user,development
```

### カスタムAPIキー名

`key_name`フィールドを使用して、自動生成されるAPIキーにカスタム名を設定できます：

```csv
email,role,team_name,key_name
user@example.com,internal_user,development,00000001_chatbot
```

### 招待URL生成

新規作成されたユーザーには、パスワード設定用の招待URLが自動生成されます。この機能により、ユーザーは安全にパスワードを設定できます。

## エラーハンドリング

### 一般的なエラーと対処法

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `User already exists` | 同じメールアドレスのユーザーが既に存在 | 既存ユーザーの更新は`sync_user.py`を使用 |
| `Invalid role` | 指定されたロールが無効 | 有効なロール名を確認 |
| `Team not found` | 指定されたチームが存在しない | チーム名を確認、または事前にチームを作成 |
| `Unauthorized` | Master Keyが無効 | 正しいMaster Keyを設定 |
| `Connection refused` | LiteLLMサーバーに接続できない | サーバーのURLと稼働状況を確認 |

### デバッグモード

`--debug`オプションを使用すると、詳細な実行情報が表示されます：

```bash
python add_user.py --csv-file user_addlist.csv --debug
```

デバッグ情報には以下が含まれます：
- APIリクエスト/レスポンスの詳細
- チーム検索結果
- APIキー作成プロセス
- 招待URL生成プロセス

## 使用例

### 例1: 基本的なユーザー登録

```bash
# user_addlist.csvを作成
echo "email,role" > user_addlist.csv
echo "user1@example.com,internal_user" >> user_addlist.csv
echo "user2@example.com,proxy_admin" >> user_addlist.csv

# ドライランで確認
python add_user.py --csv-file user_addlist.csv --dry-run

# 実際に登録
python add_user.py --csv-file user_addlist.csv
```

### 例2: チーム付きユーザー登録

```bash
# チーム付きCSVファイルを作成
cat > user_addlist.csv << EOF
email,role,team_name
dev1@example.com,internal_user,development
dev2@example.com,internal_user,development
admin@example.com,proxy_admin,admin
EOF

# 登録実行
python add_user.py --csv-file user_addlist.csv --debug
```

### 例3: カスタムAPIキー名付きユーザー登録

```bash
# APIキー名付きCSVファイルを作成
cat > user_addlist.csv << EOF
email,role,team_name,key_name
chatbot@example.com,internal_user,ai_team,00000001_chatbot
api_user@example.com,internal_user,api_team,00000002_api_access
EOF

# 登録実行
python add_user.py --csv-file user_addlist.csv --debug
```

## 注意事項

1. **Master Keyの管理**: Master Keyは機密情報です。環境変数で管理し、コードに直接記述しないでください。

2. **重複チェック**: 既存ユーザーと同じメールアドレスでの登録は自動的にスキップされます。

3. **チーム事前作成**: CSVで指定するチームは事前にLiteLLMで作成されている必要があります。

4. **APIキー管理**: 生成されたAPIキーは`user_reg_result.csv`に記録されますが、セキュリティ上の理由で後から取得することはできません。

5. **招待URL**: 招待URLには有効期限がある場合があります。生成後は速やかにユーザーに共有してください。

## トラブルシューティング

### よくある問題

**Q: "Team not found"エラーが発生する**
A: 指定されたチーム名がLiteLLMに存在しない可能性があります。チーム名を確認するか、事前にチームを作成してください。

**Q: 招待URLが生成されない**
A: LiteLLMのバージョンや設定によっては招待機能が利用できない場合があります。手動でパスワード設定を行ってください。

**Q: APIキー名が設定されない**
A: APIキーの更新に失敗している可能性があります。`--debug`オプションで詳細を確認してください。

### ログの確認

実行時のログは標準エラー出力に出力されます。リダイレクトして保存することも可能です：

```bash
python add_user.py --csv-file user_addlist.csv --debug 2> add_user.log
```

## 関連スクリプト

- [`sync_user.py`](sync_user_manual.md) - ユーザー情報の同期
- [`del_user.py`](del_user_manual.md) - ユーザーの一括削除
- [`list_user.py`](list_user_manual.md) - ユーザー一覧の表示