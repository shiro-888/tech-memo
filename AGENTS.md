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

下書きから公開まで **1本の PR**（ブランチ `claude/note-<slug>`）で行う。
下書き段階は Draft PR としてレビューし、公開コミットを同じ PR に追加してから
Ready for review に切り替え、マージ＝公開とする。

1. ブランチ `claude/note-<slug>` を main から作成する。
2. `notes/_drafts/<slug>.html` を `notes/template/index.html` を元に作成する。
   執筆中はここに置き、`index.html` からはリンクしない。
3. **メタデータを記入する**: `<meta name="article:category">`（`web|security|tools|design|infra|ai|misc` から選択）、`<meta name="article:summary">`（80〜120文字）、`<meta name="article:tags">`（任意、カンマ区切り）。`<article>` 冒頭の `.note-meta` 内 `badge--<category>` クラスも揃える。
4. push して base `main` の **Draft PR** を作成し、この PR 上で内容をレビューする
   （この段階ではマージしない。修正は同じブランチにコミットする）。
5. 上記「公開前の必須チェック」をすべて確認する。
6. レビューが済んだら、同じブランチ上で `notes/<公開日-スラッグ>/index.html`
   （例: `notes/2026-06-28-slug/index.html`）へ移動する。下書き・公開とも 2 階層下なので相対パス（`../../`）の修正は不要。
7. `index.html` の `.note-list` に新しい `<li class="note-card">` カードを追加する（記事メタを複製。詳細は `.claude/commands/publish.md` 参照）。
8. 公開コミットを push し、PR を Draft から Ready for review に切り替える。
   マージ＝公開（`main` への直接 push は避け、PR 経由で公開する）。

## カテゴリ / 図解の方針

- **カテゴリ**: `web`（Web開発）/ `security`（セキュリティ）/ `tools`（ツール・運用）/ `design`（設計・アーキテクチャ）/ `infra`（インフラ・CI/CD）/ `ai`（AI/機械学習）/ `misc`（その他）の7種。これは `styles/site.css` の `--cat-*` トークンと `.badge--*` クラスに一致する。新カテゴリを足す場合は両方を更新する。
- **図解**: 仕組み・関係・流れの説明には**インラインSVG**を第一選択にする（`.diagram` クラス、`currentColor`・`var(--color-*)` でテーマ追従、外部依存ゼロ）。フロー/シーケンス図など量が多い記事のみ Mermaid CDN を `<head>` で読み込む（テンプレのコメント参照）。
- **シンタックスハイライト**: 必要な記事のみ Prism CDN を `<head>` で読み込む。不要な記事では読み込まない（依存ゼロを優先）。

### Claude Code コマンドでの自動化

上記の流れは Claude Code のスラッシュコマンドにまとめてある（`.claude/commands/`）。
下書きと公開で PR は分けず、**同じ PR** を Draft → Ready for review と進める。

- `/draft <トピック>` … トピックから下書き（`notes/_drafts/<slug>.html`）を起こし、レビュー用の **Draft PR** を作る（未公開・マージしない）。
- `/publish <slug>` … 下書きを `notes/<公開日-slug>/index.html` へ移動し、トップにリンクする公開コミットを**同じ PR に追加**して Ready for review に切り替える（マージ＝公開）。

## スタイル / 実装方針

- ビルドツールは使わない素の静的 HTML / CSS。依存を増やさない。
- テンプレート・下書き（`notes/_drafts/<slug>.html`）・公開ノート
  （`notes/<slug>/index.html`）はいずれもルートから 2 階層下にあるため、
  CSS は一貫して `../../styles/site.css` を参照する（移動時のパス修正は不要）。
- 日本語で記述する。`<html lang="ja">` を維持する。
