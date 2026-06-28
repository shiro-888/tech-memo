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

## ガードレール構成

- ローカル: pre-commit + gitleaks（このリポジトリ）
- GitHub: Secret scanning / Push protection（Settings で有効化）
- CI: PR時の pre-publish-check（フェーズ3で追加予定）
