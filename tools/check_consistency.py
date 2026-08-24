#!/usr/bin/env python3
"""index.html のカードと各記事のメタ情報が食い違っていないか検査する。

このサイトはビルドツールを使わないため、記事 <head> の article:* メタと
トップページ `index.html` のカードに同じ内容が二重に存在する。/publish が
手作業でコピーしている以上、公開済み記事を後から直すとカード側が取り残される。
その食い違いを CI で落とすのがこのスクリプトの役目。

使い方:
    python tools/check_consistency.py           # 通常（要約の文字数超過は警告）
    python tools/check_consistency.py --strict   # 警告もエラー扱いにする

標準ライブラリのみで動く。依存を増やさないというリポジトリの方針に従う。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# カテゴリ値 → バッジ表示名。AGENTS.md / styles/site.css の --cat-* と対応する。
CATEGORY_LABELS = {
    "web": "Web開発",
    "security": "セキュリティ",
    "tools": "ツール",
    "design": "設計",
    "infra": "インフラ",
    "ai": "AI",
    "misc": "その他",
}

TITLE_SUFFIX = " — tech-memo"
EXPECTED_CSS_HREF = "../../styles/site.css"
SUMMARY_MIN, SUMMARY_MAX = 80, 120

# 公開記事のディレクトリだけを対象にする。これにより notes/template/ と
# notes/_drafts/ が自動的に外れる。guardrails は下書き PR でも走るので、
# ここを緩めるとカードがまだ無い下書き PR が落ちて /draft が壊れる。
NOTE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def norm(text: str | None) -> str:
    """比較用にテキストを正規化する（空白畳み込み + NFC）。

    HTMLParser は convert_charrefs=True なので文字参照は復元済み。
    日本語は結合文字の有無で見た目が同じでもバイト列が変わるため NFC に寄せる。
    """
    if text is None:
        return ""
    return unicodedata.normalize("NFC", " ".join(text.split()))


class _Base(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._buf: list[str] | None = None

    def _start_capture(self) -> None:
        self._buf = []

    def _end_capture(self) -> str:
        text = "".join(self._buf or [])
        self._buf = None
        return norm(text)

    def handle_data(self, data: str) -> None:
        if self._buf is not None:
            self._buf.append(data)


class IndexParser(_Base):
    """index.html から .note-list 内のカードを取り出す。

    正規表現ではなく HTMLParser を使うのが重要。index.html にはカード記法を
    説明する HTML コメントがあり、素朴な文字列検索だとそれを 1 件多く拾う。
    コメントは handle_comment に流れ handle_starttag には現れないため、
    パーサ方式なら構造的に誤検出しない。
    """

    def __init__(self) -> None:
        super().__init__()
        self.cards: list[dict] = []
        self.draft_links: list[tuple[str, int]] = []
        self._in_list = False
        self._stack: list[str] = []
        self._card: dict | None = None
        self._card_depth = 0
        self._pending: str | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        cls = a.get("class", "") or ""
        self._stack.append(tag)

        if tag == "ul" and "note-list" in cls:
            self._in_list = True
            return

        if a.get("href", "").startswith("notes/_drafts/"):
            self.draft_links.append((a["href"], self.getpos()[0]))

        if not self._in_list:
            return

        if tag == "li" and "note-card" in cls:
            self._card = {
                "line": self.getpos()[0],
                "category": a.get("data-category"),
                "badge_class": None,
                "badge_text": None,
                "datetime": None,
                "date_text": None,
                "href": None,
                "title": None,
                "summary": None,
                "tags": [],
            }
            self._card_depth = len(self._stack)
            return

        if self._card is None:
            return

        if tag == "span" and "badge" in cls:
            m = re.search(r"badge--(\w+)", cls)
            self._card["badge_class"] = m.group(1) if m else None
            self._pending = "badge_text"
            self._start_capture()
        elif tag == "time":
            self._card["datetime"] = a.get("datetime")
            self._pending = "date_text"
            self._start_capture()
        elif tag == "a" and "note-card__title" in " ".join(self._stack[-3:-1]) or (
            tag == "a" and self._card["href"] is None and "note-card__title" in cls
        ):
            pass  # 下の h2 経由で処理する
        elif tag == "p" and "note-card__summary" in cls:
            self._pending = "summary"
            self._start_capture()
        elif tag == "ul" and "note-card__tags" in cls:
            self._pending = "tags"
        elif tag == "li" and self._pending == "tags":
            self._start_capture()
        elif tag == "a" and self._card["href"] is None:
            self._card["href"] = a.get("href")
            self._pending = "title"
            self._start_capture()

    def handle_endtag(self, tag: str) -> None:
        if self._card is not None and self._buf is not None:
            if tag == "span" and self._pending == "badge_text":
                self._card["badge_text"] = self._end_capture()
                self._pending = None
            elif tag == "time" and self._pending == "date_text":
                self._card["date_text"] = self._end_capture()
                self._pending = None
            elif tag == "p" and self._pending == "summary":
                self._card["summary"] = self._end_capture()
                self._pending = None
            elif tag == "a" and self._pending == "title":
                self._card["title"] = self._end_capture()
                self._pending = None
            elif tag == "li" and self._pending == "tags":
                self._card["tags"].append(self._end_capture())

        if tag == "ul" and self._pending == "tags":
            self._pending = None

        if tag == "li" and self._card is not None and len(self._stack) == self._card_depth:
            self.cards.append(self._card)
            self._card = None

        if tag == "ul" and self._in_list and self._card is None and len(self._stack) == 2:
            self._in_list = False

        if self._stack and self._stack[-1] == tag:
            self._stack.pop()


class ArticleParser(_Base):
    """記事 HTML から <head> のメタ情報と本文冒頭の表示要素を取り出す。"""

    def __init__(self) -> None:
        super().__init__()
        self.lang: str | None = None
        self.title: str | None = None
        self.meta: dict[str, str] = {}
        self.css_hrefs: list[str] = []
        self.h1: str | None = None
        self.badge_class: str | None = None
        self.badge_text: str | None = None
        self.badge_href: str | None = None
        self.has_skip_link = False
        self.has_notice = False
        self.datetime: str | None = None
        self.date_text: str | None = None
        self._pending: str | None = None
        self._in_note_meta = False
        # 図解のインライン SVG にもスクリーンリーダ向けの <title> があるため、
        # SVG の中に入っている間は <head> の <title> と取り違えないようにする。
        self._svg_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        cls = a.get("class", "") or ""

        if tag == "svg":
            self._svg_depth += 1
            return

        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title" and self._svg_depth == 0 and self.title is None:
            self._pending = "title"
            self._start_capture()
        elif tag == "meta" and a.get("name") and a.get("content") is not None:
            self.meta[a["name"]] = norm(a["content"])
        elif tag == "link" and a.get("rel") == "stylesheet":
            self.css_hrefs.append(a.get("href", ""))
        elif tag == "h1" and self.h1 is None:
            self._pending = "h1"
            self._start_capture()
        elif tag == "a" and "skip-link" in cls:
            self.has_skip_link = True
        elif tag == "p" and "site-notice--compact" in cls:
            self.has_notice = True
        elif tag == "p" and "note-meta" in cls:
            self._in_note_meta = True
        elif self._in_note_meta and tag == "a" and "badge-link" in cls:
            self.badge_href = a.get("href")
        elif self._in_note_meta and tag == "span" and "badge" in cls:
            m = re.search(r"badge--(\w+)", cls)
            self.badge_class = m.group(1) if m else None
            self._pending = "badge_text"
            self._start_capture()
        elif self._in_note_meta and tag == "time":
            self.datetime = a.get("datetime")
            self._pending = "date_text"
            self._start_capture()

    def handle_endtag(self, tag: str) -> None:
        if tag == "svg":
            self._svg_depth = max(0, self._svg_depth - 1)
            return
        if self._buf is not None:
            if tag == "title" and self._pending == "title":
                self.title = self._end_capture()
            elif tag == "h1" and self._pending == "h1":
                self.h1 = self._end_capture()
            elif tag == "span" and self._pending == "badge_text":
                self.badge_text = self._end_capture()
            elif tag == "time" and self._pending == "date_text":
                self.date_text = self._end_capture()
            else:
                return
            self._pending = None
        if tag == "p":
            self._in_note_meta = False


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, file: str, line: int | None, msg: str) -> None:
        self.errors.append(_annotate("error", file, line, msg))

    def warn(self, file: str, line: int | None, msg: str) -> None:
        self.warnings.append(_annotate("warning", file, line, msg))


def _annotate(level: str, file: str, line: int | None, msg: str) -> str:
    """GitHub Actions 上では PR の差分に注釈として出る形式で返す。"""
    flat = msg.replace("\n", " ")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        loc = f"file={file}" + (f",line={line}" if line else "")
        return f"::{level} {loc}::{flat}"
    where = f"{file}:{line}" if line else file
    return f"[{level}] {where}: {flat}"


def check() -> Report:
    rep = Report()
    index_path = REPO_ROOT / "index.html"

    ip = IndexParser()
    ip.feed(index_path.read_text(encoding="utf-8"))
    cards = ip.cards

    for href, line in ip.draft_links:
        rep.error("index.html", line, f"未公開の下書きへリンクしています: {href}")

    notes_dir = REPO_ROOT / "notes"
    note_dirs = sorted(
        d for d in notes_dir.iterdir() if d.is_dir() and NOTE_DIR_RE.match(d.name)
    )

    if len(cards) != len(note_dirs):
        rep.error(
            "index.html",
            None,
            f"カード数 {len(cards)} と公開記事数 {len(note_dirs)} が一致しません",
        )

    by_href = {c["href"]: c for c in cards}

    for d in note_dirs:
        rel = f"notes/{d.name}/index.html"
        article_file = d / "index.html"
        if not article_file.exists():
            rep.error(rel, None, "index.html がありません")
            continue

        ap = ArticleParser()
        ap.feed(article_file.read_text(encoding="utf-8"))

        date = d.name[:10]
        cat = ap.meta.get("article:category")
        summary = ap.meta.get("article:summary")

        # --- 記事単体の検査 ---
        if ap.lang != "ja":
            rep.error(rel, None, f'<html lang="ja"> が必要です（現在: {ap.lang}）')
        for key in ("description", "article:category", "article:summary"):
            if not ap.meta.get(key):
                rep.error(rel, None, f"必須メタ {key} がありません")
        if cat and cat not in CATEGORY_LABELS:
            rep.error(rel, None, f"未知のカテゴリ: {cat}")
        if EXPECTED_CSS_HREF not in ap.css_hrefs:
            rep.error(rel, None, f"CSS は {EXPECTED_CSS_HREF} を参照してください（現在: {ap.css_hrefs}）")
        if ap.h1 and ap.title and ap.title != ap.h1 + TITLE_SUFFIX:
            rep.error(rel, None, f"<title> は「<h1> + {TITLE_SUFFIX!r}」にしてください（現在: {ap.title!r}）")
        if cat and ap.badge_class and ap.badge_class != cat:
            rep.error(rel, None, f"記事内バッジ badge--{ap.badge_class} がカテゴリ {cat} と不一致")
        # 記事内バッジは同カテゴリの一覧へのリンク。ここも二重管理なので検査する。
        want_href = f"../../index.html?cat={cat}"
        if not ap.badge_href:
            rep.error(rel, None, f"記事内バッジが .badge-link で包まれていません（期待: {want_href}）")
        elif cat and ap.badge_href != want_href:
            rep.error(rel, None, f"バッジのリンク先 {ap.badge_href!r} がカテゴリ {cat} と不一致（期待: {want_href}）")
        if not ap.has_skip_link:
            rep.error(rel, None, "スキップリンク（.skip-link）がありません")
        if not ap.has_notice:
            rep.error(rel, None, "AI生成の注意書き（.site-notice--compact）がありません")
        if ap.datetime != date:
            rep.error(rel, None, f"<time datetime={ap.datetime!r}> がディレクトリ名の日付 {date} と不一致")
        if ap.date_text and ap.datetime and ap.date_text != ap.datetime:
            rep.error(rel, None, f"<time> の表示 {ap.date_text!r} と datetime {ap.datetime!r} が不一致")
        if summary and not (SUMMARY_MIN <= len(summary) <= SUMMARY_MAX):
            rep.warn(rel, None, f"article:summary が {len(summary)} 字（推奨 {SUMMARY_MIN}〜{SUMMARY_MAX} 字）")

        # --- カードとの突き合わせ ---
        card = by_href.get(rel)
        if card is None:
            rep.error("index.html", None, f"{rel} のカードが index.html にありません")
            continue

        line = card["line"]
        expected_label = CATEGORY_LABELS.get(cat or "", "")

        checks = [
            ("data-category", card["category"], cat),
            ("バッジのクラス", card["badge_class"], cat),
            ("バッジの表示名", card["badge_text"], expected_label),
            ("タイトル", card["title"], ap.h1),
            ("要約", card["summary"], summary),
            ("日付(datetime)", card["datetime"], date),
            ("日付(表示)", card["date_text"], date),
        ]
        for label, got, want in checks:
            if norm(got) != norm(want):
                rep.error(
                    "index.html", line,
                    f"{rel} の{label}が記事と不一致 / カード: {got!r} / 記事: {want!r}",
                )

        want_tags = [norm(t) for t in (ap.meta.get("article:tags") or "").split(",") if t.strip()]
        got_tags = [t.lstrip("#") for t in card["tags"]]
        if got_tags != want_tags:
            rep.error(
                "index.html", line,
                f"{rel} のタグが article:tags と不一致 / カード: {got_tags} / 記事: {want_tags}",
            )

    # --- 全体の検査 ---
    for card in cards:
        href = card["href"] or ""
        if href and not (REPO_ROOT / href).exists():
            rep.error("index.html", card["line"], f"リンク先が存在しません: {href}")

    dates = [c["datetime"] for c in cards if c["datetime"]]
    if dates != sorted(dates, reverse=True):
        rep.error("index.html", None, "カードが日付の降順に並んでいません")

    _print_tag_report(note_dirs)
    return rep


def _print_tag_report(note_dirs: list[Path]) -> None:
    """タグ頻度を出力する。タグ別ページを作る価値が出たか判断する材料。"""
    counter: Counter[str] = Counter()
    for d in note_dirs:
        f = d / "index.html"
        if not f.exists():
            continue
        m = re.search(r'<meta name="article:tags" content="([^"]*)"', f.read_text(encoding="utf-8"))
        if m:
            counter.update(norm(t) for t in m.group(1).split(",") if t.strip())
    if not counter:
        return
    repeated = [(t, n) for t, n in counter.most_common() if n > 1]
    singles = len(counter) - len(repeated)
    print(f"\nタグ: {len(counter)} 種 / 1記事のみ {singles} 種")
    if repeated:
        print("  2記事以上: " + ", ".join(f"{t}×{n}" for t, n in repeated))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="警告もエラーとして扱う")
    args = parser.parse_args()

    rep = check()

    for line in rep.warnings:
        print(line)
    for line in rep.errors:
        print(line)

    failed = bool(rep.errors) or (args.strict and rep.warnings)
    print(
        f"\n結果: エラー {len(rep.errors)} 件 / 警告 {len(rep.warnings)} 件"
        + ("" if not args.strict else "（--strict: 警告もエラー扱い）")
    )
    if failed:
        print("index.html のカードと記事のメタ情報が食い違っています。")
        return 1
    print("index.html のカードと記事のメタ情報は一致しています。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
