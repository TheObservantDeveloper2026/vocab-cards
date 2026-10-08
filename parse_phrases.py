# -*- coding: utf-8 -*-
"""Parse the extracted phrase-list txt into structured JSON (dedup by phrase)."""
import json
import re
import sys
from pathlib import Path

SRC = Path(r"c:\Users\ZhuanZ1\AppData\Roaming\Trae CN\User\workspaceStorage\f13789bbb849b35bd51f2ae62b75249a\long-text\6ac62613b2f5a4a418b5581b\muy251xo-4qre\以下是根据您提供的8....txt")
OUT = Path(__file__).parent / "phrases_data.json"

numbered_re = re.compile(r"^(\d+)[.、]\s*(.+?)\s+-\s+(.+)$")
section_re = re.compile(r"^###\s*第(.)张图")
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8}

def norm_key(phrase: str) -> str:
    return re.sub(r"\s+", " ", phrase.strip().lower())

def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    entries = []
    seen = set()
    part = ""
    skipped = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        sm = section_re.match(line)
        if sm:
            part = f"Part {CN_NUM[sm.group(1)]:02d}"
            continue
        nm = numbered_re.match(line)
        if nm:
            entries.append({"en": nm.group(2).strip(), "zh": nm.group(3).strip(), "group": part})
        else:
            skipped.append(line[:60])

    final = []
    for e in entries:
        key = norm_key(e["en"])
        if key in seen:
            continue
        seen.add(key)
        final.append(e)

    OUT.write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")

    parts = sorted({e["group"] for e in final})
    print(f"raw entries : {len(entries)}")
    print(f"unique      : {len(final)}")
    print(f"parts       : {parts}")
    print(f"skipped     : {len(skipped)}")
    for s in skipped[:10]:
        print(f"  [skip] {s}")

if __name__ == "__main__":
    sys.exit(main())
