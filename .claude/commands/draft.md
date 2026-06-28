---
description: トピックから技術ノートの下書きを作成し、PRまで用意する
argument-hint: <トピック（書いてほしい題材）>
---

トピック「$ARGUMENTS」について、技術ノートの**下書き**を作成し、PR を出すところまで行う。
これは下書きフェーズなので、トップページ（index.html）にはリンクしない＝まだ公開しない。

## 手順

1. **slug を決める**
   - トピックを表す短い英小文字＋ハイフンの slug を作る（例: 「Gitの使い方」→ `git-basics`）。
   - 曖昧なら、ユーザーに slug を確認する。

2. **ブランチを作成**
   - `git checkout main && git pull origin main`
   - `git checkout -b claude/draft-<slug>`

3. **下書きを執筆**
   - `notes/template/index.html` を元に `notes/_drafts/<slug>.html` を作成する。
   - `<html lang="ja">` を維持。CSS は `../../styles/site.css`（ルートから2階層下）。
   - **AGENTS.md の「公開前の必須チェック」を厳守**する:
     - 個人情報・勤務先固有情報・同僚名・未公開の業務情報を書かない。
     - 認証情報・APIキー・秘密鍵・`.env` の実値を書かない。
     - 引用は出典明記の上15語以内。
     - 参考 URL は**実在を確認してから**記載する（到達確認できた URL のみ。`curl -sI` 等で 200 を確認）。
     - コード例は可能な範囲で動作を確認する。
   - 初心者にも分かるよう、必要な周辺知識を補足する文体にする（既存ノートの粒度を踏襲）。

4. **表示を検証**
   - Chromium（Playwright）で `notes/_drafts/<slug>.html` をレンダリングし、CSS 適用・リンク・コードブロック表示に崩れが無いか確認する。

5. **push して PR を作成**
   - `git add` → コミット → `git push -u origin claude/draft-<slug>`（失敗時は指数バックオフで最大4回）。
   - GitHub MCP で base `main` の PR を作成する。
   - PR 本文には次を明記:
     - これは**下書き**であり index.html には未リンク＝未公開であること。
     - `PUBLISHING_CHECKLIST.md` の「内容」項目のチェック状況。
     - 公開する際は `/publish <slug>` を使うこと。

6. **CI を確認**
   - `guardrails` チェック（gitleaks + lychee）の結果を確認し、ユーザーに報告する。

## 補足
- 下書き（`notes/_drafts/<slug>.html`）・公開ノート（`notes/<日付-slug>/index.html`）はいずれも2階層下なので、CSS パスは `../../` のままで移動時も変わらない。
- `notes/_drafts/` は `_` 始まりのため、main にマージされても GitHub Pages（Jekyll）では配信されない＝マージしても未公開のまま安全。
