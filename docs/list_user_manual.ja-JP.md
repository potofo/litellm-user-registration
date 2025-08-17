# list_user.py マニュアル

## 概要

[`list_user.py`](../list_user.py)は、LiteLLM Proxyサーバーに登録されているユーザーの一覧を表示し、フィルタリング機能を提供するスクリプトです。ユーザー管理の現状把握や特定条件でのユーザー検索に使用します。

## 主な機能

- **全ユーザーの一覧表示**
- **ロール別フィルタリング**
- **メールアドレス部分一致検索**
- **カスタム列表示**
- **内部ユーザーの自動フィルタリング**
- **ページング対応**
- **タブ区切り形式での出力**

## 使用方法

### 基本的な使用例

```bash
# 全ての内部ユーザーを表示
python list_user.py

# 特定のロールのユーザーを表示
python list_user.py --role internal_user

# メールアドレスで検索
python list_user.py --email-like "@company.com"

# 全ユーザー（内部・外部問わず）を表示
python list_user.py --show-all

# デバッグ情報付きで実行
python list_user.py --debug
```

### コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--base-url` | LiteLLM ProxyサーバーのベースURL | `http://localhost:4000` |
| `--master-key` | 管理者キー | 環境変数`LITELLM_MASTER_KEY`から取得 |
| `--role` | 特定のロールでフィルタリング | なし |
| `--email-like` | メールアドレスの部分一致検索 | なし |
| `--columns` | 表示する列をカンマ区切りで指定 | `user_id,user_email,user_role,teams,created_at,updated_at` |
| `--show-all` | 内部ユーザー以外も含めて全ユーザーを表示 | なし |
| `--debug` | デバッグ情報を表示 | なし |

## フィルタリング機能

### ロール別フィルタリング

利用可能なロール：

| ロール | 説明 |
|--------|------|
| `internal_user` | 標準内部ユーザー |
| `internal_user_viewer` | 読み取り専用内部ユーザー |
| `proxy_admin` | プロキシ管理者 |
| `proxy_admin_viewer` | 読み取り専用プロキシ管理者 |
| `default` | デフォルトユーザー |
| `user` | 一般ユーザー |
| `end_user` | エンドユーザー |

```bash
# proxy_adminロールのユーザーのみ表示
python list_user.py --role proxy_admin

# internal_userロールのユーザーのみ表示
python list_user.py --role internal_user
```

### メールアドレス検索

部分一致でメールアドレスを検索できます（大文字小文字を区別しません）：

```bash
# @company.comドメインのユーザーを検索
python list_user.py --email-like "@company.com"

# 特定の名前を含むユーザーを検索
python list_user.py --email-like "admin"

# 複数条件の組み合わせ
python list_user.py --role proxy_admin --email-like "@company.com"
```

## 出力形式

### デフォルト出力

```
user_id	user_email	user_role	teams	created_at	updated_at
user_123	user@example.com	internal_user	["team_456"]	2024-01-01T00:00:00Z	2024-01-01T00:00:00Z
user_789	admin@company.com	proxy_admin	["team_123","team_456"]	2024-01-01T00:00:00Z	2024-01-01T00:00:00Z
```

### カスタム列表示

`--columns`オプションで表示する列をカスタマイズできます：

```bash
# 基本情報のみ表示
python list_user.py --columns "user_email,user_role"

# 詳細情報を表示
python list_user.py --columns "user_id,user_email,user_role,teams,models,created_at"
```

### 利用可能な列

| 列名 | 説明 |
|------|------|
| `user_id` | ユーザーID |
| `user_email` | メールアドレス |
| `user_role` | ユーザーロール |
| `teams` | 所属チーム（JSON配列） |
| `models` | 利用可能モデル（JSON配列） |
| `created_at` | 作成日時 |
| `updated_at` | 更新日時 |
| `max_budget` | 最大予算 |
| `spend` | 使用量 |
| `user_alias` | ユーザーエイリアス |

## 実行例

### 例1: 基本的なユーザー一覧表示

```bash
# 全ての内部ユーザーを表示
python list_user.py
```

出力例：
```
user_id	user_email	user_role	teams	created_at	updated_at
user_123	user@example.com	internal_user	[]	2024-01-01T00:00:00Z	2024-01-01T00:00:00Z
user_456	admin@company.com	proxy_admin	["team_123"]	2024-01-01T00:00:00Z	2024-01-01T00:00:00Z
```

### 例2: 特定ロールのユーザー検索

```bash
# proxy_adminロールのユーザーのみ表示
python list_user.py --role proxy_admin
```

### 例3: ドメイン別ユーザー検索

```bash
# 特定ドメインのユーザーを検索
python list_user.py --email-like "@company.com"
```

### 例4: カスタム列での表示

```bash
# メールアドレスとロールのみ表示
python list_user.py --columns "user_email,user_role"
```

出力例：
```
user_email	user_role
user@example.com	internal_user
admin@company.com	proxy_admin
```

### 例5: 全ユーザーの表示

```bash
# 内部・外部ユーザーを含む全ユーザーを表示
python list_user.py --show-all
```

## データ処理とフィルタリング

### 内部ユーザーの自動フィルタリング

デフォルトでは、以下の条件を満たすユーザーのみが表示されます：

1. **メールアドレスが存在する**（`default_user_id`などを除外）
2. **内部ロールを持つ**（`INTERNAL_ROLES`に定義されたロール）

### センシティブ情報の除外

以下の情報は自動的に出力から除外されます：

- `password`
- `hashed_password`
- `salt`
- `token`

### JSON形式データの処理

チームやモデルなどのJSON配列は、そのまま文字列として表示されます：

```
teams: ["team_123", "team_456"]
models: ["gpt-4", "gpt-3.5-turbo"]
```

## デバッグモード

`--debug`オプションを使用すると、詳細な実行情報が表示されます：

```bash
python list_user.py --debug
```

デバッグ情報には以下が含まれます：
- APIリクエストURL
- レスポンスステータス
- レスポンスヘッダー
- 取得したユーザー数
- フィルタリング結果

## エラーハンドリング

### 一般的なエラーと対処法

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `Unauthorized` | Master Keyが無効 | 正しいMaster Keyを設定 |
| `Connection refused` | LiteLLMサーバーに接続できない | サーバーのURLと稼働状況を確認 |
| `No users found` | 条件に一致するユーザーがいない | フィルタ条件を確認 |

### HTTPエラーの処理

```bash
# エラーの詳細を確認
python list_user.py --debug
```

## 出力の活用

### CSVファイルへの保存

```bash
# タブ区切りをCSV形式に変換して保存
python list_user.py --columns "user_email,user_role" | tr '\t' ',' > users.csv
```

### 他のスクリプトとの連携

```bash
# ユーザー一覧を取得してsync_user.pyで同期
python list_user.py --columns "user_email,user_role" > current_users.txt
```

### フィルタリングとパイプライン

```bash
# 特定条件のユーザーを抽出
python list_user.py --role internal_user | grep "@company.com"

# ユーザー数をカウント
python list_user.py --role proxy_admin | wc -l
```

## パフォーマンス考慮事項

### 大量ユーザーの処理

- スクリプトはページング機能に対応しており、大量のユーザーでも効率的に処理できます
- `--debug`オプションは大量のログを出力するため、本番環境では注意して使用してください

### ネットワーク最適化

- 必要な列のみを指定することで、ネットワーク転送量を削減できます
- フィルタリングはクライアント側で行われるため、大量ユーザーがいる場合は注意が必要です

## 使用例とワークフロー

### 日常的な管理タスク

```bash
# 1. 全ユーザーの概要を確認
python list_user.py --columns "user_email,user_role,teams"

# 2. 管理者ユーザーを確認
python list_user.py --role proxy_admin

# 3. 特定ドメインのユーザーを確認
python list_user.py --email-like "@company.com"

# 4. 詳細情報が必要な場合
python list_user.py --show-all --debug
```

### トラブルシューティング

```bash
# 問題のあるユーザーを特定
python list_user.py --email-like "problem_user@"

# 全ユーザーの詳細情報を取得
python list_user.py --show-all --columns "user_id,user_email,user_role,teams,created_at,updated_at"
```

## 関連スクリプト

- [`add_user.py`](add_user_manual.md) - ユーザーの一括登録
- [`del_user.py`](del_user_manual.md) - ユーザーの一括削除
- [`sync_user.py`](sync_user_manual.md) - ユーザー情報の同期

## 注意事項

1. **権限**: ユーザー一覧の取得には適切な権限が必要です
2. **プライバシー**: ユーザー情報の取り扱いには注意してください
3. **パフォーマンス**: 大量ユーザーがいる環境では実行時間が長くなる場合があります
4. **フィルタリング**: クライアント側フィルタリングのため、大量データでは効率が悪い場合があります