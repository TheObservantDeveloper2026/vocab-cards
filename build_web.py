# -*- coding: utf-8 -*-
"""Inject data.json into template.html -> index.html"""
import json
from pathlib import Path

base = Path(__file__).parent
data = (base / "data.json").read_text(encoding="utf-8")
# compact JSON to shrink file size
data = json.dumps(json.loads(data), ensure_ascii=False, separators=(",", ":"))
tpl = (base / "template.html").read_text(encoding="utf-8")
assert "__DATA__" in tpl
html = tpl.replace("__DATA__", data)
(base / "index.html").write_text(html, encoding="utf-8")
print(f"index.html written: {len(html) / 1024:.1f} KB, {len(json.loads(data))} cards")
