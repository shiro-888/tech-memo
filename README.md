# tech-memo

技術ノート公開サイト。**ガードレール（機密情報の誤公開防止）を土台に**構築しています。

## セットアップ（必須: ローカルのコミット前チェック）

```bash
pip install pre-commit      # または: brew install pre-commit
pre-commit install          # git commit 時に自動でフックが走るようにする
pre-commit run --all-files  # 初回: 全ファイルに対して手動実行
```

これにより、コミット時に gitleaks（シークレット検出）と秘密鍵・大容量ファイルの
混入チェックが自動で実行されます。

## サイト構成 / 執筆ルール

素の静的 HTML / CSS で構成しています。ディレクトリ構成と新しいノートの
追加手順、公開前の必須チェックは [AGENTS.md](./AGENTS.md) を参照してください。
公開前には [PUBLISHING_CHECKLIST.md](./PUBLISHING_CHECKLIST.md) を毎回確認します。

## ガードレール構成

- ローカル: pre-commit + gitleaks（このリポジトリ）
- GitHub: Secret scanning / Push protection（Settings で有効化）
- CI: PR時の pre-publish-check（フェーズ3で追加予定）
