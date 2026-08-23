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

記事本文の文体は `writing-guide` スキル（[.claude/skills/writing-guide/SKILL.md](./.claude/skills/writing-guide/SKILL.md)）に
まとめています。`/draft`・`/publish` で執筆・レビューする際の品質チェックリストとして使います。

## ガードレール構成

- ローカル: pre-commit + gitleaks（このリポジトリ）
- GitHub: Secret scanning / Push protection（Settings で有効化）
- CI: PR時の `guardrails` ジョブ（[.github/workflows/pre-publish-check.yml](./.github/workflows/pre-publish-check.yml)）で
  gitleaks とリンク切れ検査（lychee）を実行
