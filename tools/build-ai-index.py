#!/usr/bin/env python3
"""
build-ai-index.py — index.html의 'AI용 목차 스냅샷'을 manifest.json에서 다시 생성한다.

왜? 홈페이지 하단 <section id="ai-readme">의 전체 작품 목록(스냅샷)은 자바스크립트
없이 fetch만으로 AI가 읽는 정적 목록이라, 만화를 추가/삭제/순서변경하면 낡는다.
(스냅샷이 낡아도 AI는 manifest.json을 '정답'으로 교차확인하므로 치명적이진 않지만,
 맞춰두면 홈 링크 하나로 더 정확히 읽힌다.)

사용법:  python3 tools/build-ai-index.py
  → manifest.json을 읽어 index.html의 <!-- AI-CATALOG:START -->..<!-- AI-CATALOG:END -->
    사이를 raw.githubusercontent.com 링크가 박힌 시리즈별 목록으로 덮어쓴다.
만화를 바꾼 뒤 이 스크립트를 돌리고 git push 하면 배포에 반영된다.
"""
import json
import re
import sys
import urllib.parse
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW  = "https://raw.githubusercontent.com/Greenteavillain/manhwa-viewer/main/"
START = "<!-- AI-CATALOG:START (tools/build-ai-index.py 가 생성 — 직접 수정 금지) -->"
END   = "<!-- AI-CATALOG:END -->"


def esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_snapshot(items) -> str:
    groups = OrderedDict()
    for it in items:
        groups.setdefault(it.get("genre", "기타"), []).append(it)
    lines = []
    for genre, arr in groups.items():
        lines.append(f'      <p class="ai-series"><b>{esc(genre)}</b> ({len(arr)}편)</p>')
        lines.append('      <ol class="ai-eplist">')
        for it in arr:
            href = RAW + urllib.parse.quote(it["file"])
            lines.append(f'        <li><a href="{href}">{esc(it["title"])}</a></li>')
        lines.append("      </ol>")
    return "\n".join(lines)


def main() -> int:
    manifest_path = ROOT / "manifest.json"
    index_path = ROOT / "index.html"
    items = json.loads(manifest_path.read_text(encoding="utf-8"))
    html = index_path.read_text(encoding="utf-8")

    if START not in html or END not in html:
        print("ERROR: index.html에서 AI-CATALOG 마커를 찾지 못했습니다.", file=sys.stderr)
        return 1

    snapshot = build_snapshot(items)
    new_block = f"{START}\n{snapshot}\n      {END}"
    html = re.sub(re.escape(START) + r".*?" + re.escape(END), new_block, html, count=1, flags=re.S)
    index_path.write_text(html, encoding="utf-8")
    print(f"OK: {len(items)}편을 index.html AI 목차에 반영했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
