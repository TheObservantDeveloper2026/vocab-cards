# -*- coding: utf-8 -*-
"""Build Anki .apkg deck from data.json: Front=English, Back=Chinese."""
import json
import random
from pathlib import Path

import genanki

BASE = Path(__file__).parent
OUT = BASE / "英语词汇卡_英译中_1409张.apkg"

random.seed(42)
MODEL_ID = 1846213051
DECK_ID = 2059400110

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
.word { font-size: 40px; font-weight: 700; word-break: break-word; line-height: 1.25; }
.word.zh { font-size: 32px; color: #3b55d9; font-weight: 600; }
.hint { margin-top: 24px; font-size: 14px; color: #9aa1b2; }
hr#answer { border: none; border-top: 1px solid #dfe3ee; margin: 22px 0; }
""",
)

deck = genanki.Deck(DECK_ID, "英语词汇卡（英文→中文）")
data = json.loads((BASE / "data.json").read_text(encoding="utf-8"))
for e in data:
    note = genanki.Note(
        model=model,
        fields=[e["en"], e["zh"], e["group"]],
        tags=[e["group"].replace(" ", "")],
        guid=genanki.guid_for(e["en"]),
    )
    deck.add_note(note)

genanki.Package(deck).write_to_file(OUT)
print(f"{OUT.name} written: {len(data)} notes, {OUT.stat().st_size / 1024:.1f} KB")
