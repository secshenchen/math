"""Build the standalone candidate without replacing the published entry."""
import json
from hashlib import sha256
from pathlib import Path
from geometry.bank import build_bank

ROOT = Path(__file__).resolve().parent


def build():
    questions = build_bank()
    previous = json.loads((ROOT / "geometry/previous_bank.json").read_text())
    current = {sha256(q["question"].encode()).hexdigest()[:20]:q["id"] for q in questions}
    migration = [current.get(key,0) for key in previous]
    retired = [q["id"] for q in questions if q.get("modelMode",0) >= 18]
    bank = json.dumps(questions, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    template = (ROOT / "web/app.html").read_text(encoding="utf-8")
    app = (ROOT / "web/app.js").read_text(encoding="utf-8")
    output = ROOT / "candidate" / "index.html"
    output.parent.mkdir(exist_ok=True)
    output.write_text(template.replace("__APP__", app).replace("__BANK__", bank).replace("__RETIRED__", json.dumps(retired)).replace("__MIGRATION__", json.dumps(migration,separators=(",",":"))), encoding="utf-8")
    print(f"{output.relative_to(ROOT)}: {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()
