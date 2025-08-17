# sync_user.py マニュアル

## 概要

[`sync_user.py`](../sync_user.py)は、CSVファイルとLiteLLM Proxyサーバーのユーザー情報を同期するための高度なスクリプトです。ユーザーの追加、削除、更新を自動的に判断し、一括で実行します。最も包括的なユーザー管理機能を提供します。

## 主な機能

- **CSVとLiteLLMの完全同期**
- **差分検出と自動判断**
- **ユーザーの追加・削除・更新**
- **チーム割り当ての安全な更新**
- **ロール変更の処理**
- **フォールバック機能（ユーザー再作成）**
- **詳細な同期レポート**
- **選択的同期オプション**

## 使用方法

### 基本的な使用例

```bash
# ドライラン（実際の変更は行わない）
python sync_user.py --csv-file user_list.csv --dry-run

# 完全同期を実行
python sync_user.py --csv-file user_list.csv

# 削除を無効にして同期
python sync_user.py --csv-file user_list.csv --no-delete

# 更新を無効にして同期
python sync_user.py --csv-file user_list.csv --no-update

# デバッグ情報付きで実行
python sync_user.py --csv-file user_list.csv --debug
```

### コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--base-url` | LiteLLM ProxyサーバーのベースURL | `http://localhost:4000` |
| `--master-key` | 管理者キー | 環境変数`LITELLM_MASTER_KEY`から取得 |
| `--csv-file` | 入力CSVファイルのパス | `user_list.csv` |
| `--user-role` | デフォルトユーザーロール | `proxy_admin` |
| `--dry-run` | 実際の変更を行わずに実行内容を表示 | - |
| `--no-delete` | ユーザーの削除を無効化 | - |
| `--no-update` | ユーザーの更新を無効化 | - |
| `--debug` | デバッグ情報を表示 | - |

## CSVファイル形式

### 入力ファイル（user_list.csv）

```csv
email,role,team_name
user@example.com,internal_user,development
admin@company.com,proxy_admin,admin
viewer@company.com,internal_user_viewer,support
api_user@example.com,internal_user,api_team
```

### フィールド詳細

| フィールド | 必須 | 説明 | 例 |
|-----------|------|------|-----|
| `email` | ✅ | ユーザーのメールアドレス | `user@example.com` |
| `role` | ❌ | ユーザーロール | `internal_user` |
| `team_name` | ❌ | 所属チーム名 | `development` |

## 同期プロセス

### 1. 差分検出

スクリプトは以下の差分を自動検出します：

- **追加対象**: CSVにあるがLiteLLMにないユーザー
- **削除対象**: LiteLLMにあるがCSVにないユーザー
- **更新対象**: 両方にあるがロールまたはチームが異なるユーザー
- **変更なし**: 両方にあり情報が一致するユーザー

### 2. 実行順序

1. **ユーザー追加** - 新規ユーザーの作成
2. **ユーザー削除** - 不要ユーザーの削除（`--no-delete`で無効化可能）
3. **ユーザー更新** - 既存ユーザーの情報更新（`--no-update`で無効化可能）

### 3. 安全な更新機能

チーム更新時には以下の安全機能を提供：

- **段階的更新**: 新チームに追加してから旧チームを削除
- **更新検証**: 更新後に実際の状態を確認
- **フォールバック**: 更新失敗時にユーザーを再作成

## 出力ファイル

### 同期レポート（user_sync_result.csv）

```csv
action,email,user_id,role,team_name,api_keys,status,error_reason
ADDED,new_user@example.com,user_123,internal_user,development,sk-abc123...,SUCCESS,
DELETED,old_user@example.com,user_456,internal_user,support,,SUCCESS,
UPDATED,existing@example.com,user_789,proxy_admin,admin,,SUCCESS,
UNCHANGED,stable@example.com,user_012,internal_user,development,,SUCCESS,
```

### レポートフィールド詳細

| フィールド | 説明 |
|-----------|------|
| `action` | 実行されたアクション（ADDED/DELETED/UPDATED/UNCHANGED） |
| `email` | ユーザーのメールアドレス |
| `user_id` | ユーザーID |
| `role` | ユーザーロール |
| `team_name` | チーム名 |
| `api_keys` | APIキー（新規作成時のみ） |
| `status` | 実行結果（SUCCESS/FAILED） |
| `error_reason` | エラーの詳細（失敗時のみ） |

## 高度な機能

### チーム更新の安全機能

チーム変更時には以下の手順で安全に更新します：

1. **現在のチーム + 新しいチーム**に一時的に割り当て
2. **新しいチームのみ**に更新
3. **更新結果を検証**
4. **失敗時はユーザーを再作成**

```bash
# チーム更新のデバッグ情報を確認
python sync_user.py --csv-file user_list.csv --debug
```

### フォールバック機能

ユーザー更新に失敗した場合、自動的に以下を実行：

1. **既存ユーザーを削除**
2. **正しい情報で新規作成**
3. **結果を検証**

### APIキー管理

- **新規ユーザー**: 作成時にAPIキーが自動生成され、レポートに記録
- **既存ユーザー**: セキュリティ上の理由でAPIキーは取得不可
- **更新ユーザー**: APIキーは変更されません

## 実行例

### 例1: 基本的な同期

```bash
# user_list.csvを作成
cat > user_list.csv << EOF
email,role,team_name
user1@example.com,internal_user,development
user2@example.com,proxy_admin,admin
EOF

# ドライランで確認
python sync_user.py --csv-file user_list.csv --dry-run

# 実際に同期
python sync_user.py --csv-file user_list.csv
```

### 例2: 削除を無効にした同期

```bash
# 既存ユーザーを削除せずに同期
python sync_user.py --csv-file user_list.csv --no-delete --debug
```

### 例3: 更新のみの同期

```bash
# 追加と削除は行わず、更新のみ実行
python sync_user.py --csv-file user_list.csv --no-delete --debug
```

### 例4: 大規模な同期

```bash
# 大量のユーザーを含むCSVで同期
python sync_user.py --csv-file large_user_list.csv --debug > sync.log 2>&1
```

## ドライランモード

`--dry-run`オプションで実行内容を事前確認：

```bash
python sync_user.py --csv-file user_list.csv --dry-run
```

出力例：
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

## エラーハンドリング

### 一般的なエラーと対処法

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `Team not found` | 指定されたチームが存在しない | チーム名を確認、または事前にチームを作成 |
| `User recreation failed` | フォールバック処理が失敗 | 手動でユーザーを確認・修正 |
| `Unauthorized` | Master Keyが無効 | 正しいMaster Keyを設定 |
| `Connection timeout` | ネットワークエラー | サーバーの状況を確認 |

### 部分的失敗の処理

一部のユーザーで処理が失敗した場合：

1. **成功したユーザー**は正常に処理される
2. **失敗したユーザー**はレポートに記録される
3. **エラーの詳細**が`error_reason`フィールドに記録される

## デバッグとトラブルシューティング

### デバッグモード

```bash
python sync_user.py --csv-file user_list.csv --debug
```

デバッグ情報には以下が含まれます：
- 差分検出プロセス
- APIリクエスト/レスポンス
- チーム更新の詳細手順
- フォールバック処理の詳細

### ログの保存

```bash
# 詳細ログをファイルに保存
python sync_user.py --csv-file user_list.csv --debug > sync.log 2>&1
```

### 同期結果の確認

```bash
# 同期後の状況を確認
python list_user.py --show-all

# 同期レポートを確認
cat user_sync_result.csv
```

## パフォーマンス考慮事項

### 大量ユーザーの処理

- **バッチ処理**: 大量ユーザーでも効率的に処理
- **エラー継続**: 一部失敗しても処理を継続
- **メモリ効率**: 大量データでもメモリ使用量を抑制

### ネットワーク最適化

- **API呼び出し最小化**: 必要な場合のみAPIを呼び出し
- **タイムアウト設定**: 適切なタイムアウト値を設定
- **リトライ機能**: 一時的なエラーに対する自動リトライ

## 使用例とワークフロー

### 定期的な同期

```bash
#!/bin/bash
# daily_sync.sh - 日次同期スクリプト

# 1. 現在の状況をバックアップ
python list_user.py > backup_$(date +%Y%m%d).txt

# 2. ドライランで確認
python sync_user.py --csv-file user_list.csv --dry-run

# 3. 実際に同期
python sync_user.py --csv-file user_list.csv --debug

# 4. 結果を確認
echo "Sync completed. Check user_sync_result.csv for details."
```

### 段階的な移行

```bash
# 1. 削除を無効にして新規ユーザーのみ追加
python sync_user.py --csv-file user_list.csv --no-delete

# 2. 更新のみ実行
python sync_user.py --csv-file user_list.csv --no-delete --no-add

# 3. 最終的に完全同期
python sync_user.py --csv-file user_list.csv
```

## セキュリティ考慮事項

### アクセス制御

1. **Master Key管理**: 環境変数で安全に管理
2. **実行権限**: 信頼できる管理者のみに制限
3. **監査ログ**: 同期操作の記録を保持

### データ保護

1. **バックアップ**: 同期前に現在の状態をバックアップ
2. **段階的実行**: ドライランで事前確認
3. **ロールバック**: 問題発生時の復旧手順を準備

## 関連スクリプト

- [`add_user.py`](add_user_manual.md) - ユーザーの一括登録
- [`del_user.py`](del_user_manual.md) - ユーザーの一括削除
- [`list_user.py`](list_user_manual.md) - ユーザー一覧の表示

## 注意事項

1. **不可逆的操作**: ユーザー削除は不可逆的です。`--dry-run`で事前確認してください
2. **チーム事前作成**: CSVで指定するチームは事前に作成が必要です
3. **APIキー**: 既存ユーザーのAPIキーは変更されません
4. **権限**: 適切な管理者権限が必要です
5. **バックアップ**: 重要なデータは事前にバックアップしてください

## ベストプラクティス

1. **定期実行**: 定期的な同期でデータの整合性を保つ
2. **段階的導入**: 大きな変更は段階的に実行
3. **監視**: 同期結果を定期的に確認
4. **文書化**: 同期ルールと手順を文書化
5. **テスト**: 本番前にテスト環境で検証