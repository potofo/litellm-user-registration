# del_user.py マニュアル

## 概要

[`del_user.py`](../del_user.py)は、CSVファイルに記載されたメールアドレスに基づいて、LiteLLM Proxyサーバーからユーザーを一括削除するためのスクリプトです。安全な削除プロセスと詳細なエラーレポートを提供します。

## 主な機能

- **CSVファイルからの一括ユーザー削除**
- **メールアドレスによるユーザー検索**
- **安全な削除プロセス**
- **詳細なエラーレポート**
- **ドライランモード**
- **削除結果の記録**

## 使用方法

### 基本的な使用例

```bash
# ドライラン（実際の削除は行わない）
python del_user.py --csv-file user_dellist.csv --dry-run

# 実際にユーザーを削除
python del_user.py --csv-file user_dellist.csv

# デバッグ情報付きで実行
python del_user.py --csv-file user_dellist.csv --debug
```

### コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--base-url` | LiteLLM ProxyサーバーのベースURL | `http://localhost:4000` |
| `--master-key` | 管理者キー | 環境変数`LITELLM_MASTER_KEY`から取得 |
| `--csv-file` | 入力CSVファイルのパス | `user_dellist.csv` |
| `--dry-run` | 実際の削除を行わずに実行内容を表示 | - |
| `--debug` | デバッグ情報を表示 | - |

## CSVファイル形式

### 入力ファイル（user_dellist.csv）

```csv
email
old_user@example.com
inactive@company.com
test_user@example.com
```

### フィールド詳細

| フィールド | 必須 | 説明 | 例 |
|-----------|------|------|-----|
| `email` | ✅ | 削除対象ユーザーのメールアドレス | `user@example.com` |

## 出力ファイル

### 成功時の出力（user_del_result.csv）

```csv
email,user_id,status
user@example.com,user_123,Deleted
admin@company.com,user_456,Deleted
```

### エラー時の出力（user_del_error.csv）

```csv
email,user_id,error_reason
notfound@example.com,,User not found in the system
invalid@,user_789,Failed to delete user (API error)
```

## 実行フロー

1. **環境変数とパラメータの検証**
2. **CSVファイルの読み込み**
3. **各ユーザーに対して以下を実行**：
   - メールアドレスからユーザーIDを検索
   - ユーザーが存在する場合、削除APIを呼び出し
   - 削除結果を記録
4. **結果の出力**
   - 成功したユーザーを`user_del_result.csv`に出力
   - 失敗したユーザーを`user_del_error.csv`に出力

## エラーハンドリング

### 一般的なエラーと対処法

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `User not found in the system` | 指定されたメールアドレスのユーザーが存在しない | メールアドレスを確認 |
| `Unauthorized` | Master Keyが無効 | 正しいMaster Keyを設定 |
| `Forbidden` | 削除権限がない | 適切な権限を持つMaster Keyを使用 |
| `Bad request` | 無効なユーザーID形式 | ユーザーIDの形式を確認 |
| `Connection refused` | LiteLLMサーバーに接続できない | サーバーのURLと稼働状況を確認 |

### HTTPステータスコード別エラー

| ステータスコード | 説明 | 対処法 |
|-----------------|------|--------|
| 400 | Bad Request - 無効なリクエスト | ユーザーIDの形式を確認 |
| 401 | Unauthorized - 認証失敗 | Master Keyを確認 |
| 403 | Forbidden - 権限不足 | 削除権限のあるキーを使用 |
| 404 | Not Found - ユーザーが見つからない | ユーザーの存在を確認 |

## 安全性について

### 削除前の確認

このスクリプトは以下の安全対策を実装しています：

1. **ドライランモード**: `--dry-run`オプションで削除対象を事前確認
2. **ユーザー存在確認**: 削除前にユーザーの存在を確認
3. **詳細ログ**: 削除プロセスの詳細な記録
4. **エラーハンドリング**: 各種エラーの適切な処理

### 推奨手順

```bash
# 1. まずドライランで削除対象を確認
python del_user.py --csv-file user_dellist.csv --dry-run

# 2. 削除対象が正しいことを確認後、実際に削除
python del_user.py --csv-file user_dellist.csv --debug

# 3. 結果ファイルで削除状況を確認
cat user_del_result.csv
cat user_del_error.csv
```

## デバッグモード

`--debug`オプションを使用すると、詳細な実行情報が表示されます：

```bash
python del_user.py --csv-file user_dellist.csv --debug
```

デバッグ情報には以下が含まれます：
- ユーザー検索プロセス
- APIリクエスト/レスポンスの詳細
- 削除プロセスの詳細
- エラーの詳細情報

## 使用例

### 例1: 基本的なユーザー削除

```bash
# user_dellist.csvを作成
echo "email" > user_dellist.csv
echo "old_user@example.com" >> user_dellist.csv
echo "inactive@company.com" >> user_dellist.csv

# ドライランで確認
python del_user.py --csv-file user_dellist.csv --dry-run

# 実際に削除
python del_user.py --csv-file user_dellist.csv
```

### 例2: 大量ユーザーの削除

```bash
# 大量のユーザーリストを作成
cat > user_dellist.csv << EOF
email
test1@example.com
test2@example.com
test3@example.com
old_admin@company.com
EOF

# デバッグモードで削除実行
python del_user.py --csv-file user_dellist.csv --debug
```

### 例3: 削除結果の確認

```bash
# 削除実行
python del_user.py --csv-file user_dellist.csv

# 成功した削除を確認
echo "=== 削除成功 ==="
cat user_del_result.csv

# 失敗した削除を確認
echo "=== 削除失敗 ==="
cat user_del_error.csv
```

## 出力ファイルの詳細

### user_del_result.csv

成功した削除の記録：

| フィールド | 説明 |
|-----------|------|
| `email` | 削除されたユーザーのメールアドレス |
| `user_id` | 削除されたユーザーのID |
| `status` | 削除ステータス（常に"Deleted"） |

### user_del_error.csv

失敗した削除の記録：

| フィールド | 説明 |
|-----------|------|
| `email` | 削除に失敗したユーザーのメールアドレス |
| `user_id` | ユーザーID（見つからない場合は空） |
| `error_reason` | 失敗の理由 |

## 注意事項

1. **不可逆的操作**: ユーザー削除は不可逆的な操作です。削除前に必ずドライランで確認してください。

2. **Master Keyの管理**: Master Keyは機密情報です。環境変数で管理し、コードに直接記述しないでください。

3. **バックアップ**: 重要なユーザーデータがある場合は、削除前にバックアップを取得してください。

4. **権限確認**: 削除権限のあるMaster Keyを使用していることを確認してください。

5. **関連データ**: ユーザー削除により、関連するAPIキーやチーム割り当ても削除される可能性があります。

## トラブルシューティング

### よくある問題

**Q: "User not found"エラーが多発する**
A: CSVファイルのメールアドレスが正確か確認してください。また、既に削除済みのユーザーが含まれている可能性があります。

**Q: 削除権限エラーが発生する**
A: 使用しているMaster Keyに削除権限があることを確認してください。

**Q: 一部のユーザーだけ削除に失敗する**
A: `user_del_error.csv`でエラーの詳細を確認し、個別に対処してください。

### ログの確認

実行時のログは標準エラー出力に出力されます：

```bash
python del_user.py --csv-file user_dellist.csv --debug 2> del_user.log
```

### 削除状況の確認

削除後、ユーザーが実際に削除されたかを確認できます：

```bash
# ユーザー一覧で確認
python list_user.py --email-like "@example.com"
```

## 関連スクリプト

- [`add_user.py`](add_user_manual.md) - ユーザーの一括登録
- [`sync_user.py`](sync_user_manual.md) - ユーザー情報の同期
- [`list_user.py`](list_user_manual.md) - ユーザー一覧の表示

## セキュリティ考慮事項

1. **アクセス制御**: 削除スクリプトの実行は信頼できる管理者のみに制限してください。
2. **監査ログ**: 削除操作の記録を保持し、監査可能にしてください。
3. **承認プロセス**: 重要なユーザーの削除には承認プロセスを設けることを推奨します。
4. **定期的な確認**: 削除対象リストを定期的に見直し、誤削除を防いでください。