# -*- coding: utf-8 -*-
"""Parse CET-4 grammar table -> JSON -> web page (grammar/index.html) + Anki .apkg.

Card logic: front = 考点 (or 句型 name), back = 必背结构 (+例句/提醒) or 示例.
Section 15 (7天背诵计划) is a study plan, not flashcards -> skipped.
"""
import json
import re
from pathlib import Path

import genanki

BASE = Path(__file__).parent
SRC = BASE / "grammar_source.md"
DATA_OUT = BASE / "grammar_data.json"
WEB_OUT = BASE / "grammar" / "index.html"
APKG_OUT = BASE / "英语四级语法卡_考点到结构.apkg"

TITLE = "英语四级语法卡片"
HINT = "看考点想结构"
STORE_KEY = "vg_known"
DECK_ID = 2059400113  # vocab 110 / phrases 111 / network 112
GUID_PREFIX = "gram::"

MODEL_ID = 1846213051
model = genanki.Model(
    MODEL_ID,
    "EN->ZH Vocabulary (simple)",
    fields=[{"name": "English"}, {"name": "Chinese"}, {"name": "Group"}],
    templates=[
        {
            "name": "EN -> ZH",
            "qfmt": '<div class="tag">{{Group}}</div><div class="word">{{English}}</div>'
                    '<div class="hint">想好必背结构，再显示答案</div>',
            "afmt": "{{FrontSide}}<hr id=answer><div class=\"word zh\">{{Chinese}}</div>",
        }
    ],
    css="""
.card { font-family: -apple-system, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        font-size: 22px; text-align: center; color: #1c2333;
        background: #f4f6fb; padding: 24px 16px; }
.tag { font-size: 13px; color: #6b7280; margin-bottom: 18px; }
.word { font-size: 30px; font-weight: 700; word-break: break-word; line-height: 1.35; }
.word.zh { font-size: 22px; color: #3b55d9; font-weight: 600; line-height: 1.5; }
.hint { margin-top: 24px; font-size: 14px; color: #9aa1b2; }
hr#answer { border: none; border-top: 1px solid #dfe3ee; margin: 22px 0; }
""",
)

section_re = re.compile(r"^##\s*\d+[.、]?\s*(.+)$")


def parse() -> list:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    entries = []
    group = ""
    mode = ""  # "point" (考点 3-col) | "pattern" (句型 2-col) | "" skip

    for raw in lines:
        line = raw.strip()
        sm = section_re.match(line)
        if sm:
            group = sm.group(1).strip()
            mode = ""
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(c.startswith(":") for c in cells):
            continue
        if cells[0] == "考点" and len(cells) >= 3:
            mode = "point"
            continue
        if cells[0] == "句型" and len(cells) >= 2:
            mode = "pattern"
            continue
        if cells[0] in {"考点", "句型", "天数", "缩写", "英文术语", "英文表达"}:
            mode = ""  # a new table header (e.g. 天数) ends the current section's table
        if not mode or not cells[0]:
            continue
        if mode == "point":
            en, zh = cells[0], cells[1]
            if len(cells) >= 3 and cells[2]:
                zh += "<br>" + cells[2]
        else:  # pattern
            en, zh = cells[0], cells[1]
        entries.append({"en": en, "zh": zh, "group": group})

    by_key, order = {}, []
    for e in entries:
        k = f'{e["group"]}::{e["en"]}'
        if k not in by_key:
            by_key[k] = e
            order.append(k)
    final = [by_key[k] for k in order]

    DATA_OUT.write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    groups = sorted({e["group"] for e in final})
    print(f"raw {len(entries)} -> unique {len(final)}, sections {len(groups)}: {groups}")
    return final


def build_web(data: list) -> None:
    tpl = (BASE / "template.html").read_text(encoding="utf-8")
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = (tpl.replace("__DATA__", compact)
               .replace("英语词汇卡", TITLE)
               .replace("看英文想中文", HINT)
               .replace("vc_known", STORE_KEY)
               .replace("vc_wrong", "vg_wrong"))
    assert "__DATA__" not in html
    WEB_OUT.parent.mkdir(exist_ok=True)
    WEB_OUT.write_text(html, encoding="utf-8")
    print(f"grammar/index.html written: {len(html) / 1024:.1f} KB")


def build_apkg(data: list) -> None:
    sec_no: dict = {}
    for e in data:  # group name -> 01, 02, ... in order of first appearance
        if e["group"] not in sec_no:
            sec_no[e["group"]] = f"{len(sec_no) + 1:02d}"
    deck = genanki.Deck(DECK_ID, "英语四级语法（考点→结构）")
    for e in data:
        deck.add_note(genanki.Note(
            model=model,
            fields=[e["en"], e["zh"], e["group"]],
            tags=[sec_no[e["group"]]],
            guid=genanki.guid_for(GUID_PREFIX + e["group"] + "::" + e["en"]),
        ))
    genanki.Package(deck).write_to_file(APKG_OUT)
    print(f"{APKG_OUT.name} written: {len(data)} notes, {APKG_OUT.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    data = parse()
    build_web(data)
    build_apkg(data)
