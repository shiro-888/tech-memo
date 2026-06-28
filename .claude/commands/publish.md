---
description: 下書きを公開位置へ移動し、トップにリンクして公開PRを作る
argument-hint: <slug>（notes/_drafts/<slug>.html の slug）
---

下書き `notes/_drafts/$ARGUMENTS.html` を**公開**する。slug は `$ARGUMENTS`。
下書きが存在しない場合は中止し、`notes/_drafts/` の一覧を見せて確認する。

## 手順

1. **公開前チェック**
   - `notes/_drafts/<slug>.html` を読み、`PUBLISHING_CHECKLIST.md` の全項目を確認する。
   - 個人情報・社内情報・鍵・未確認URL が無いか最終確認する。問題があれば公開せず指摘する。

2. **ブランチを作成**
   - `git checkout main && git pull origin main`
   - `git checkout -b claude/publish-<slug>`

3. **公開位置へ移動**
   - 公開日は実行時の日付（`date +%F`）を使う。
   - `git mv notes/_drafts/<slug>.html notes/<YYYY-MM-DD>-<slug>/index.html`
   - 記事内の `<time datetime="...">` と表示日付を公開日に更新する。タイトル等の TODO 残りが無いか確認する。
   - CSS パス（`../../styles/site.css`）は2階層下のままで変更不要。

4. **トップページにリンク追加**
   - `index.html` の `.note-list` に新しい `<li>` を追加する（記事へのリンク＋`<time>`）。
   - 一覧は新しい日付が上に来るよう並べる。

5. **表示を検証**
   - Chromium でトップ→記事→戻りの導線と表示を確認する。

6. **push して PR を作成**
   - コミット → `git push -u origin claude/publish-<slug>`（失敗時は指数バックオフ最大4回）。
   - GitHub MCP で base `main` の PR を作成。本文に `PUBLISHING_CHECKLIST.md` のチェック状況を記載する。

7. **CI を確認**
   - `guardrails` チェックの結果を確認して報告する。マージ＝公開になる旨を伝える。
