---
description: 下書きを公開位置へ移動しトップにリンクする公開コミットを、下書きと同じPRに追加して Ready for review にする
argument-hint: <slug>（notes/_drafts/<slug>.html の slug）
---

下書き `notes/_drafts/$ARGUMENTS.html` を**公開**する。slug は `$ARGUMENTS`。
新しい PR は作らず、`/draft` が作った **同じブランチ・同じ PR**（`claude/note-<slug>`）に
公開コミットを追加し、PR を Draft から **Ready for review** に切り替える。
ユーザーがその PR をマージした時点で公開となる。

## 手順

1. **対象ブランチと PR を特定**
   - `git fetch origin claude/note-<slug>` でブランチの存在を確認し、
     GitHub MCP（`list_pull_requests`、head=`claude/note-<slug>`、state=open）で対応する open PR を探す。
   - **両方見つかった場合（通常フロー）**:
     - `git checkout claude/note-<slug>` → `git pull origin claude/note-<slug>`
     - `git fetch origin main && git merge origin/main` で main の変更を取り込む（コンフリクトは解消する）。
   - **見つからない場合（フォールバック）**: 下書きがすでに main にマージ済みの旧フロー等では、
     `git checkout main && git pull origin main` → `git checkout -b claude/note-<slug>` で新規ブランチを作り、
     手順6で新規 PR を作成する。
   - ブランチ上に `notes/_drafts/<slug>.html` が存在しない場合は中止し、`notes/_drafts/` の一覧を見せて確認する。

2. **公開前チェック**
   - `notes/_drafts/<slug>.html` を読み、`PUBLISHING_CHECKLIST.md` の全項目を確認する。
   - 個人情報・社内情報・鍵・未確認URL が無いか最終確認する。問題があれば公開せず指摘する。
   - メタデータが揃っているか確認する: `article:category`（必須）, `article:summary`（必須）, `article:tags`（任意）。

3. **公開位置へ移動**
   - 公開日は実行時の日付（`date +%F`）を使う。
   - `git mv notes/_drafts/<slug>.html notes/<YYYY-MM-DD>-<slug>/index.html`
   - 記事内の `<time datetime="...">` と表示日付を公開日に更新する。タイトル等の TODO 残りが無いか確認する。
   - CSS パス（`../../styles/site.css`）は2階層下のままで変更不要。

4. **トップページにカードを追加**
   - `index.html` の `.note-list` に新しい `<li class="note-card">` を追加する。
   - カードの内容は記事の `<head>` のメタタグから複製する:
     - `data-category="..."` ← `<meta name="article:category">`
     - `<span class="badge badge--...">カテゴリ表示名</span>` ← 同 category
       （表示名: web=Web開発, security=セキュリティ, tools=ツール, design=設計, infra=インフラ, ai=AI, misc=その他）
     - `<time datetime="...">YYYY-MM-DD</time>` ← 公開日
     - `<h2 class="note-card__title"><a href="...">タイトル</a></h2>`
     - `<p class="note-card__summary">...</p>` ← `<meta name="article:summary">`
     - `<ul class="note-card__tags"><li>#tag</li>...</ul>` ← `<meta name="article:tags">`（カンマ区切りを `#tag` で展開、空なら省略）
   - 一覧は新しい日付が上に来るよう並べる。

5. **表示を検証**
   - Chromium でトップ→記事→戻りの導線、カードのカテゴリ色、ライト/ダーク両モードでの表示崩れを確認する。
   - カテゴリフィルタチップで対象カードのみ表示されるか確認する。

6. **push して PR を公開用に更新**
   - コミット → `git push -u origin claude/note-<slug>`（失敗時は指数バックオフ最大4回）。
   - **通常フロー（既存 PR あり）**: GitHub MCP の `update_pull_request` で
     - タイトルを公開用（例: `publish: <記事タイトル>`）に更新する。
     - 本文を更新し、`PUBLISHING_CHECKLIST.md` のチェック状況と「マージ＝公開」である旨を記載する。
     - **`draft: false`** を指定して Ready for review に切り替える。
   - **フォールバック（PR なし）**: base `main` で新規 PR を作成し、同じ内容を本文に記載する。

7. **CI を確認**
   - `guardrails` チェックの結果を確認して報告する。**この PR をマージすると公開になる**旨を伝える。

## 補足
- 下書きレビューで付いたレビューコメントのスレッドは、公開コミット後も同じ PR に残るため、指摘と対応の履歴が1本で追える。
- 公開後にブランチ `claude/note-<slug>` は削除してよい（GitHub の自動ブランチ削除設定があればそれに任せる）。
