# -*- coding: utf-8 -*-
"""Build phrase web page (phrases/index.html) + Anki .apkg from phrases_data.json."""
import json
import random
from pathlib import Path

import genanki

BASE = Path(__file__).parent
OUT_DIR = BASE / "phrases"
OUT_APKG = BASE / "英语词组卡_英译中_715条.apkg"

random.seed(43)
DECK_ID = 2059400111  # differs from vocab deck 2059400110; model ID is shared on purpose

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
.word { font-size: 34px; font-weight: 700; word-break: break-word; line-height: 1.3; }
.word.zh { font-size: 28px; color: #3b55d9; font-weight: 600; }
.hint { margin-top: 24px; font-size: 14px; color: #9aa1b2; }
hr#answer { border: none; border-top: 1px solid #dfe3ee; margin: 22px 0; }
""",
)


def build_web(data: list) -> None:
    tpl = (BASE / "template.html").read_text(encoding="utf-8")
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = (tpl.replace("__DATA__", compact)
               .replace("英语词汇卡", "英语词组卡")
               .replace("看英文想中文", "看词组想中文")
               .replace("vc_known", "vp_known")
               .replace("vc_wrong", "vp_wrong"))
    assert "__DATA__" not in html
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"phrases/index.html written: {len(html) / 1024:.1f} KB")


def build_apkg(data: list) -> None:
    deck = genanki.Deck(DECK_ID, "英语词组卡（英文→中文）")
    for e in data:
        deck.add_note(genanki.Note(
            model=model,
            fields=[e["en"], e["zh"], e["group"]],
            tags=[e["group"].replace(" ", "")],
            guid=genanki.guid_for("phrase::" + e["en"]),
        ))
    genanki.Package(deck).write_to_file(OUT_APKG)
    print(f"{OUT_APKG.name} written: {len(data)} notes, {OUT_APKG.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    data = json.loads((BASE / "phrases_data.json").read_text(encoding="utf-8"))
    build_web(data)
    build_apkg(data)
