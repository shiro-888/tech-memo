# AGENTS.md

このリポジトリは技術ノートを公開する静的サイトです。Claude Code を含む
すべての作業者（人間・AIエージェント）は、以下のルールを厳守してください。

## 公開前の必須チェック（Claude Code も厳守）

- 個人情報（氏名・勤務先固有情報・家族構成・住所・連絡先等）を記載しない。
- 勤務先の社内システム名・プロジェクト名・同僚名・未公開の業務情報を記載しない。
- 引用は出典を明記したうえで 15 語以内に収める。
- 参考 URL は実在を確認してから記載する（推測で URL を書かない）。
- 未完成の記事は `notes/_drafts/` に置き、`index.html` からリンクしない。
- 認証情報・APIキー・秘密鍵・`.env` の実値を絶対にコミットしない
  （pre-commit + gitleaks が一次防御。詳細は README 参照）。
- コード例は実行・動作を確認してから掲載する。

## ディレクトリ構成

```
.
├── index.html              # トップページ（公開済みノートの一覧）
├── styles/
│   └── site.css            # サイト共通スタイル
├── notes/
│   ├── template/
│   │   └── index.html      # 新規ノートのテンプレート
│   ├── _drafts/            # 未完成の下書き（index.html からリンクしない）
│   │   └── <slug>.html     # 下書きは <slug>.html を直置き（2 階層下）
│   └── <公開日-スラッグ>/    # 公開済みノート（例: 2026-06-28-foo/）
│       └── index.html
├── AGENTS.md               # このファイル
├── README.md
├── .pre-commit-config.yaml # ガードレール（gitleaks 等）
├── .gitleaks.toml
└── .gitignore
```

## 新しいノートを追加する手順

1. `notes/_drafts/<slug>.html` を `notes/template/index.html` を元に作成する。
2. 執筆中はここに置き、`index.html` からはリンクしない。
3. 上記「公開前の必須チェック」をすべて確認する。
4. 完成したら `notes/<公開日-スラッグ>/index.html`（例: `notes/2026-06-28-slug/index.html`）へ移動する。下書き・公開とも 2 階層下なので相対パス（`../../`）の修正は不要。
5. `index.html` の `.note-list` に新しい `<li>`（リンクと `<time>`）を追加する。
6. コミットして PR を作成する（`main` への直接 push は避け、PR 経由で公開する）。

## スタイル / 実装方針

- ビルドツールは使わない素の静的 HTML / CSS。依存を増やさない。
- テンプレート・下書き（`notes/_drafts/<slug>.html`）・公開ノート
  （`notes/<slug>/index.html`）はいずれもルートから 2 階層下にあるため、
  CSS は一貫して `../../styles/site.css` を参照する（移動時のパス修正は不要）。
- 日本語で記述する。`<html lang="ja">` を維持する。
