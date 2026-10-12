#!/usr/bin/env python3
"""記事 HTML の <article> 本文を Markdown 風テキストにして標準出力へ書く。

yomiyasu のリンター（yomiyasu_lint.py）は Markdown と平文を対象にするため、
HTML 記事を検査するときの前処理として使う。標準ライブラリのみ。

使い方:
    python -I tools/extract_article_text.py notes/_drafts/<slug>.html > body.md
    python -I .claude/skills/yomiyasu/scripts/yomiyasu_lint.py body.md

出力は検査用であり、HTML への書き戻しには使わない。図解（svg）は除く。
"""

import re
import sys
from html.parser import HTMLParser

SKIP_TAGS = {"svg", "script", "style", "figcaption"}
HEADINGS = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### "}
BLOCKS = {"p", "ul", "ol", "li", "table", "tr", "blockquote", "div", "section"}

# ソース上の改行を表す目印。text() で日本語同士の間だけ詰める
NEWLINE_MARK = "\x00"


class ArticleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_article = False
        self.skip_depth = 0
        self.in_pre = False
        self.parts = []

    def _break(self):
        if self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self.in_article = True
            return
        if not self.in_article:
            return
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        elif self.skip_depth:
            return
        elif tag in HEADINGS:
            self._break()
            self.parts.append("\n" + HEADINGS[tag])
        elif tag == "pre":
            self._break()
            self.in_pre = True
            self.parts.append("```\n")
        elif tag == "li":
            self._break()
            self.parts.append("- ")
        elif tag == "code" and not self.in_pre:
            self.parts.append("`")
        elif tag == "br":
            self.parts.append("\n")
        elif tag in BLOCKS:
            self._break()

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False
            return
        if not self.in_article:
            return
        if tag in SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
        elif self.skip_depth:
            return
        elif tag in HEADINGS or tag in BLOCKS:
            self._break()
        elif tag == "pre":
            self.in_pre = False
            self._break()
            self.parts.append("```\n")
        elif tag == "code" and not self.in_pre:
            self.parts.append("`")

    def handle_data(self, data):
        if not self.in_article or self.skip_depth:
            return
        if self.in_pre:
            self.parts.append(data)
            return
        data = re.sub(r"\s*\n\s*", NEWLINE_MARK, data)
        self.parts.append(re.sub(r"[ \t]+", " ", data))

    def text(self):
        text = "".join(self.parts)
        text = re.sub(r"(?<=[^\x00-\x7f])\x00(?=[^\x00-\x7f])", "", text)
        text = text.replace(NEWLINE_MARK, " ")
        lines = [line.strip() for line in text.split("\n")]
        return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as handle:
            source = handle.read()
    except OSError as error:
        print(f"読み込めません: {error}", file=sys.stderr)
        return 1
    parser = ArticleText()
    parser.feed(source)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(parser.text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
