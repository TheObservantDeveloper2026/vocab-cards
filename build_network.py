# -*- coding: utf-8 -*-
"""Parse network-engineer vocab table txt -> JSON -> web page (network/index.html) + Anki .apkg."""
import json
import random
import re
from pathlib import Path

import genanki

BASE = Path(__file__).parent
SRC = Path(r"c:\Users\ZhuanZ1\AppData\Roaming\Trae CN\User\workspaceStorage\f13789bbb849b35bd51f2ae62b75249a\long-text\6ac62613b2f5a4a418b5581b\muy2lqbz-c896\以下是根据您提供的1....txt")
DATA_OUT = BASE / "network_data.json"
WEB_OUT = BASE / "network" / "index.html"
APKG_OUT = BASE / "网络工程师英语词汇_英译中.apkg"

TITLE = "网络工程师英语词汇卡"
HINT = "看术语想中文"
STORE_KEY = "vn_known"
DECK_ID = 2059400112  # vocab 2059400110 / phrases 2059400111
GUID_PREFIX = "net::"

MODEL_ID = 1846213051
model = genanki.Model(
    MODEL_ID,
    "EN->ZH Vocabulary (simple)",
    fields=[{"name": "English"}, {"name": "Chinese"}, {"name": "Group"}],
    templates=[
        {
            "name": "EN -> ZH",
            "qfmt": '<div class="tag">{{Group}}</div><div class="word">{{English}}</div>'
                    '<div class="hint">想好中文意思，再显示答案</div>',
            "afmt": "{{FrontSide}}<hr id=answer><div class=\"word zh\">{{Chinese}}</div>",
        }
    ],
    css="""
.card { font-family: -apple-system, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        font-size: 22px; text-align: center; color: #1c2333;
        background: #f4f6fb; padding: 24px 16px; }
.tag { font-size: 12px; color: #6b7280; margin-bottom: 18px; }
.word { font-size: 32px; font-weight: 700; word-break: break-word; line-height: 1.3; }
.word.zh { font-size: 26px; color: #3b55d9; font-weight: 600; }
.hint { margin-top: 24px; font-size: 14px; color: #9aa1b2; }
hr#answer { border: none; border-top: 1px solid #dfe3ee; margin: 22px 0; }
""",
)


def parse() -> list:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    entries = []
    group = ""
    for raw in lines:
        line = raw.strip()
        if line.startswith("###"):
            group = line.lstrip("#").strip()
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or all(c.startswith(":") for c in cells):
            continue
        if cells[0] in {"英文术语", "英文表达", "缩写"}:  # table header rows
            continue
        en = cells[0]
        zh = f"{cells[1]} · {cells[2]}" if len(cells) >= 3 else cells[1]
        entries.append({"en": en, "zh": zh, "group": group})

    # dedupe keep-first, but prefer richer translation (full name included)
    by_key, order = {}, []
    for e in entries:
        k = re.sub(r"\s+", " ", e["en"].strip().lower())
        if k not in by_key:
            by_key[k] = dict(e)
            order.append(k)
        elif len(e["zh"]) > len(by_key[k]["zh"]):
            by_key[k]["zh"] = e["zh"]
    final = [by_key[k] for k in order]

    DATA_OUT.write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    groups = sorted({e["group"] for e in final})
    print(f"raw {len(entries)} -> unique {len(final)}, {len(groups)} sections: {groups}")
    return final


def build_web(data: list) -> None:
    tpl = (BASE / "template.html").read_text(encoding="utf-8")
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = (tpl.replace("__DATA__", compact)
               .replace("英语词汇卡", TITLE)
               .replace("看英文想中文", HINT)
               .replace("vc_known", STORE_KEY)
               .replace("vc_wrong", "vn_wrong"))
    assert "__DATA__" not in html
    WEB_OUT.parent.mkdir(exist_ok=True)
    WEB_OUT.write_text(html, encoding="utf-8")
    print(f"network/index.html written: {len(html) / 1024:.1f} KB")


def build_apkg(data: list) -> None:
    random.seed(44)
    deck = genanki.Deck(DECK_ID, "网络工程师英语词汇（英文→中文）")
    for e in data:
        deck.add_note(genanki.Note(
            model=model,
            fields=[e["en"], e["zh"], e["group"]],
            tags=[e["group"].split("、")[0]],
            guid=genanki.guid_for(GUID_PREFIX + e["en"]),
        ))
    genanki.Package(deck).write_to_file(APKG_OUT)
    print(f"{APKG_OUT.name} written: {len(data)} notes, {APKG_OUT.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    data = parse()
    build_web(data)
    build_apkg(data)
