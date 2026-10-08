# -*- coding: utf-8 -*-
"""Parse the extracted vocab txt into structured JSON (dedup by word)."""
import json
import re
import sys
from pathlib import Path

SRC = Path(r"c:\Users\ZhuanZ1\AppData\Roaming\Trae CN\User\workspaceStorage\f13789bbb849b35bd51f2ae62b75249a\long-text\home\muxztat3-b8t7\以下是图片中提取的所....txt")
OUT = Path(__file__).parent / "data.json"

numbered_re = re.compile(r"^(\d+)[.、]\s*(.+?)\s+-\s+(.+)$")
group_re = re.compile(r"^\*\*Group\s*(\d+)")
compact_pair_re = re.compile(r"^(.+?)\(([^()]+)\)\s*$")

def norm_key(word: str) -> str:
    return re.sub(r"\s+", " ", word.strip().lower())

def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    entries = []
    seen = set()
    group = ""
    dropped = []

    for raw in lines:
        line = raw.strip()
        if not line or line in {"---", "..."} or line.startswith("*（注") or line.startswith("#"):
            continue

        m = group_re.match(line)
        if m:
            group = f"Group {int(m.group(1)):02d}"
            continue

        # compact phrase lines: "*   左栏：come about(发生), come off(成功/脱落), ..."
        if line.startswith("*") and "：" in line:
            body = line.split("：", 1)[1]
            for part in body.split(","):
                part = part.strip()
                if not part:
                    continue
                pm = compact_pair_re.match(part)
                if not pm:
                    dropped.append((group, part, "compact-no-match"))
                    continue
                word, zh = pm.group(1).strip(), pm.group(2).strip()
                entries.append((word, zh, group))
            continue

        # numbered entries: "1. consider - 考虑"
        nm = numbered_re.match(line)
        if nm:
            word = nm.group(2).strip()
            zh = nm.group(3).strip()
            # strip trailing duplicate-note like （注：原书重复）
            zh = re.sub(r"（注：.*?）$", "", zh).strip()
            entries.append((word, zh, group))
            continue

        # any other non-empty line is unexpected
        dropped.append((group, line, "unmatched"))

    # dedup, keep first occurrence; drop OCR fragment "of sth."
    final = []
    for word, zh, grp in entries:
        if norm_key(word) == "of sth.":
            dropped.append((grp, f"{word} - {zh}", "fragment"))
            continue
        key = norm_key(word)
        if key in seen:
            continue
        seen.add(key)
        final.append({"en": word, "zh": zh, "group": grp})

    OUT.write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")

    groups = sorted({e["group"] for e in final})
    print(f"total raw entries : {len(entries)}")
    print(f"unique cards      : {len(final)}")
    print(f"groups            : {len(groups)} -> {groups[0]}..{groups[-1]}")
    print(f"dropped/unmatched : {len(dropped)}")
    for g, txt, why in dropped[:20]:
        print(f"  [{why}] {g}: {txt[:80]}")

if __name__ == "__main__":
    sys.exit(main())
