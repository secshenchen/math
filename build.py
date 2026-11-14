"""Build the standalone candidate without replacing the published entry."""
import json
from pathlib import Path
from geometry.bank import build_bank

ROOT = Path(__file__).resolve().parent


def build():
    bank = json.dumps(build_bank(), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    template = (ROOT / "web/app.html").read_text(encoding="utf-8")
    app = (ROOT / "web/app.js").read_text(encoding="utf-8")
    output = ROOT / "candidate" / "index.html"
    output.parent.mkdir(exist_ok=True)
    output.write_text(template.replace("__APP__", app).replace("__BANK__", bank), encoding="utf-8")
    print(f"{output.relative_to(ROOT)}: {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()
