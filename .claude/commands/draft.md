---
description: トピックから技術ノートの下書きを作成し、レビュー用の Draft PR を用意する
argument-hint: <トピック（書いてほしい題材）>
---

トピック「$ARGUMENTS」について、技術ノートの**下書き**を作成し、**Draft PR** を出すところまで行う。
これは下書きフェーズなので、トップページ（index.html）にはリンクしない＝まだ公開しない。

この PR は公開まで**同じ1本**を使い回す:
下書きレビュー（Draft PR のまま）→ `/publish <slug>` で公開コミットを同じブランチに追加
→ PR を Ready for review に切り替え → マージ＝公開、という流れになる。
**この段階では PR をマージしない**（レビュー・修正はこの PR 上で行う）。

## 手順

1. **slug を決める**
   - トピックを表す短い英小文字＋ハイフンの slug を作る（例: 「Gitの使い方」→ `git-basics`）。
   - 曖昧なら、ユーザーに slug を確認する。

2. **ブランチを作成**
   - `git checkout main && git pull origin main`
   - `git checkout -b claude/note-<slug>`
   - このブランチが公開まで使う唯一のブランチになる。

3. **下書きを執筆**
   - **執筆前に `writing-guide` スキルを読み込む**（`Skill` ツールで `writing-guide` を起動、または `/writing-guide`）。
     AI臭い表現の禁止リスト・人間味の出し方・情報密度のルールを頭に入れてから書き始め、
     執筆中にAI臭い表現が出たら即座に書き直す。
   - `notes/template/index.html` を元に `notes/_drafts/<slug>.html` を作成する。
   - `<html lang="ja">` を維持。CSS は `../../styles/site.css`（ルートから2階層下）。
   - **メタデータを必ず差し替える**:
     - `<meta name="article:category">`: 値はトピックに合わせて
       `web | security | tools | design | infra | ai | misc` から選ぶ（`misc` は最終手段）。
     - `<meta name="article:summary">`: トップカードに出る紹介文。80〜120文字目安。
     - `<meta name="article:tags">`: 任意。カンマ区切り（例: `pre-commit,gitleaks,CI`）。
     - 記事冒頭の `.note-meta` 内の `badge badge--<category>` クラスも `article:category` と揃える。
   - **AGENTS.md の「公開前の必須チェック」を厳守**する:
     - 個人情報・勤務先固有情報・同僚名・未公開の業務情報を書かない。
     - 認証情報・APIキー・秘密鍵・`.env` の実値を書かない。
     - 引用は出典明記の上15語以内。
     - 参考 URL は**実在を確認してから**記載する（到達確認できた URL のみ。`curl -sI` 等で 200 を確認）。
     - コード例は可能な範囲で動作を確認する。
   - 初心者にも分かるよう、必要な周辺知識を補足する文体にする（既存ノートの粒度を踏襲）。
   - **図解**: 仕組み・関係・流れの説明には積極的に図を使う。
     - 第一選択は**インラインSVG**（`.diagram` クラス、`currentColor`・`var(--color-*)` でテーマ追従）。
     - フロー/シーケンス図など量が多いときは Mermaid を使い、`<head>` の Mermaid CDN コメントを外す。
     - シンタックスハイライトが必要なら Prism CDN コメントを外す。不要な記事では読み込まない。
   - **書き上げたら `writing-guide` の禁止リストと照合してセルフレビュー**する。
     太字・ダッシュ区切りの多用、「〜することができます」「〜を活用する」「〜についてご紹介します」、
     体言止めの連続、均等網羅リストなどが残っていないか確認し、見つけたら直す。

4. **表示を検証**
   - Chromium（Playwright）で `notes/_drafts/<slug>.html` をレンダリングし、CSS 適用・カテゴリバッジ・図・リンク・コードブロック表示に崩れが無いか確認する。

5. **push して Draft PR を作成**
   - `git add` → コミット → `git push -u origin claude/note-<slug>`（失敗時は指数バックオフで最大4回）。
   - GitHub MCP で base `main` の PR を **`draft: true`** で作成する。
   - PR 本文には次を明記:
     - これは**下書き**であり index.html には未リンク＝未公開であること。
     - **この PR はマージせず**、内容をレビューして修正依頼はレビューコメントかセッションで指示すること。
     - レビューが済んだら `/publish <slug>` を実行すると、この PR に公開コミット
       （公開位置への移動＋トップページへのカード追加）が追加され、Ready for review に切り替わること。
     - その後のマージ＝公開であること。
     - 設定したカテゴリ（`article:category`）。
     - `PUBLISHING_CHECKLIST.md` の「内容」項目のチェック状況。

6. **CI を確認**
   - `guardrails` チェック（gitleaks + lychee）の結果を確認し、ユーザーに報告する。

## 補足
- 下書き（`notes/_drafts/<slug>.html`）・公開ノート（`notes/<日付-slug>/index.html`）はいずれも2階層下なので、CSS パスは `../../` のままで移動時も変わらない。
- `notes/_drafts/` は `_` 始まりのため、仮にこの段階でマージされても GitHub Pages（Jekyll）では配信されない＝誤マージしても未公開のまま安全。
- レビュー指摘への修正は同じブランチ `claude/note-<slug>` にコミットして push する（PR は自動で更新される）。
