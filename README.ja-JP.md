# LiteLLM ユーザー登録管理ツール

LiteLLM Proxyサーバーのユーザー管理を効率化するPythonスクリプト集です。CSVファイルを使用してユーザーの一括登録、削除、一覧表示、同期を行うことができます。

## 📋 目次

- [機能概要](#機能概要)
- [必要な環境](#必要な環境)
- [インストール](#インストール)
- [環境設定](#環境設定)
- [スクリプト一覧](#スクリプト一覧)
- [使用方法](#使用方法)
- [CSVファイル形式](#csvファイル形式)
- [ユーザーロール](#ユーザーロール)
- [トラブルシューティング](#トラブルシューティング)
- [詳細ドキュメント](#詳細ドキュメント)

## 🚀 機能概要

このツールセットは以下の機能を提供します：

- **ユーザー一括登録** ([`add_user.py`](add_user.py)) - CSVファイルからユーザーを一括作成
- **ユーザー一括削除** ([`del_user.py`](del_user.py)) - CSVファイルに基づいてユーザーを一括削除
- **ユーザー一覧表示** ([`list_user.py`](list_user.py)) - 登録済みユーザーの一覧表示とフィルタリング
- **ユーザー同期** ([`sync_user.py`](sync_user.py)) - CSVファイルとLiteLLMの状態を同期

## 💻 必要な環境

- Python 3.7以上
- LiteLLM Proxy サーバー
- 管理者権限（Master Key）

## 📦 インストール

1. リポジトリをクローンまたはダウンロード：
```bash
git clone <repository-url>
cd litellm-user-registration
```

2. 必要なパッケージをインストール：
```bash
pip install -r requirements.txt
```

## ⚙️ 環境設定

### 環境変数の設定

`.env`ファイルを作成して以下の環境変数を設定してください：

```bash
# LiteLLM Proxy サーバーのベースURL
LITELLM_BASE_URL=http://localhost:4000

# LiteLLM の管理者キー（Master Key）
LITELLM_MASTER_KEY=your_master_key_here
```

### .envファイルの例

`.env.example`ファイルを参考にして設定してください：

```bash
cp .env.example .env
# .envファイルを編集して実際の値を設定
```

## 📁 スクリプト一覧

| スクリプト | 機能 | 主な用途 | 詳細マニュアル |
|-----------|------|----------|---------------|
| [`add_user.py`](add_user.py) | ユーザー一括登録 | 新規ユーザーの大量登録 | [📖 詳細マニュアル](docs/add_user_manual.md) |
| [`del_user.py`](del_user.py) | ユーザー一括削除 | 不要ユーザーの一括削除 | [📖 詳細マニュアル](docs/del_user_manual.md) |
| [`list_user.py`](list_user.py) | ユーザー一覧表示 | 現在のユーザー状況確認 | [📖 詳細マニュアル](docs/list_user_manual.md) |
| [`sync_user.py`](sync_user.py) | ユーザー同期 | CSVとの差分同期 | [📖 詳細マニュアル](docs/sync_user_manual.md) |

## 🔧 使用方法

### 基本的な使用例

```bash
# ユーザー一括登録（ドライラン）
python add_user.py --csv-file user_addlist.csv --dry-run

# ユーザー一括登録（実行）
python add_user.py --csv-file user_addlist.csv --debug

# ユーザー一覧表示
python list_user.py --role internal_user

# ユーザー同期（ドライラン）
python sync_user.py --csv-file user_list.csv --dry-run

# ユーザー一括削除
python del_user.py --csv-file user_dellist.csv --debug
```

### 共通オプション

すべてのスクリプトで使用可能な共通オプション：

- `--base-url`: LiteLLM ProxyサーバーのURL（デフォルト: http://localhost:4000）
- `--master-key`: 管理者キー（環境変数LITELLM_MASTER_KEYでも設定可能）
- `--debug`: デバッグ情報の表示
- `--dry-run`: 実際の変更を行わずに実行内容を確認

## 📄 CSVファイル形式

### ユーザー登録用（user_addlist.csv）

```csv
email,role,team_name,key_name
user@example.com,internal_user,development,00000001_chatbot
admin@company.com,proxy_admin,admin,00000002_admin
viewer@company.com,internal_user_viewer,support,00000003_support
```

### ユーザー同期用（user_list.csv）

```csv
email,role,team_name
user@example.com,internal_user,development
admin@company.com,proxy_admin,admin
```

### ユーザー削除用（user_dellist.csv）

```csv
email
old_user@example.com
inactive@company.com
```

### フィールド説明

- **email** (必須): ユーザーのメールアドレス
- **role** (オプション): ユーザーロール（未指定時はproxy_admin）
- **team_name** (オプション): 所属チーム名
- **key_name** (オプション): APIキーの名前（add_user.pyのみ）

## 👥 ユーザーロール

LiteLLMで利用可能なユーザーロール：

| ロール | 説明 | 権限レベル |
|--------|------|------------|
| `proxy_admin` | プロキシ管理者 | 全権限 |
| `proxy_admin_viewer` | プロキシ管理者（読み取り専用） | 読み取りのみ |
| `internal_user` | 内部ユーザー | 基本権限 |
| `internal_user_viewer` | 内部ユーザー（読み取り専用） | 読み取りのみ |
| `default` | デフォルトユーザー | 標準権限 |

## 📊 出力ファイル

各スクリプトは実行結果をCSVファイルに出力します：

### 成功時の出力

- `user_reg_result.csv` - 登録成功ユーザー一覧（add_user.py）
- `user_del_result.csv` - 削除成功ユーザー一覧（del_user.py）
- `user_sync_result.csv` - 同期結果一覧（sync_user.py）

### エラー時の出力

- `user_reg_error.csv` - 登録失敗ユーザー一覧（add_user.py）
- `user_del_error.csv` - 削除失敗ユーザー一覧（del_user.py）

## 🔍 トラブルシューティング

### よくある問題と解決方法

#### 1. 認証エラー
```
ERROR: --master-key or env LITELLM_MASTER_KEY is required.
```
**解決方法**: `.env`ファイルでLITELLM_MASTER_KEYを正しく設定してください。

#### 2. 接続エラー
```
HTTPError: 404 - Not Found
```
**解決方法**: `--base-url`またはLITELLM_BASE_URLが正しく設定されているか確認してください。

#### 3. CSVファイルエラー
```
ERROR: CSV file 'user_addlist.csv' not found.
```
**解決方法**: CSVファイルが存在し、正しいパスが指定されているか確認してください。

#### 4. ユーザー重複エラー
```
User already exists in the system
```
**解決方法**: 既存ユーザーの場合は`sync_user.py`を使用して更新してください。

### デバッグモードの活用

問題が発生した場合は`--debug`オプションを使用して詳細な情報を確認してください：

```bash
python add_user.py --csv-file user_addlist.csv --debug
```

### ドライランモードの活用

実際の変更を行う前に`--dry-run`オプションで実行内容を確認してください：

```bash
python sync_user.py --csv-file user_list.csv --dry-run
```

## 📚 詳細ドキュメント

各スクリプトの詳細な使用方法については、以下のマニュアルをご参照ください：

- [📖 add_user.py 詳細マニュアル](docs/add_user_manual.ja-JP.md) - ユーザー一括登録の詳細ガイド
- [📖 del_user.py 詳細マニュアル](docs/del_user_manual.ja-JP.md) - ユーザー一括削除の詳細ガイド
- [📖 list_user.py 詳細マニュアル](docs/list_user_manual.ja-JP.md) - ユーザー一覧表示の詳細ガイド
- [📖 sync_user.py 詳細マニュアル](docs/sync_user_manual.ja-JP.md) - ユーザー同期の詳細ガイド

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 コントリビューション

バグ報告や機能要求は、GitHubのIssueでお知らせください。プルリクエストも歓迎します。

## 📞 サポート

技術的な質問やサポートが必要な場合は、プロジェクトのIssueページをご利用ください。