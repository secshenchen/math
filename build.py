"""Build the standalone candidate without replacing the published entry."""
import json
from collections import Counter
import re
from html import escape
from hashlib import sha256
from pathlib import Path
from geometry.bank import build_bank
from geometry.lessons import build_lessons

ROOT = Path(__file__).resolve().parent


def add_question_caption(svg, question):
    """Keep the shared construction and show the actual prompt beneath it."""
    y = int(re.search(r'viewBox="0 0 420 (\d+)"',svg)[1])
    chunks = [question[i:i+22] for i in range(0,len(question),22)]
    caption = "".join(
        f'<text x="18" y="{y+23*i}" text-anchor="start">{escape(text)}</text>'
        for i,text in enumerate(chunks)
    )
    svg = svg.replace(f'viewBox="0 0 420 {y}"',f'viewBox="0 0 420 {y+23*len(chunks)}"',1)
    return svg.replace("</svg>",caption+"</svg>",1)


def build():
    questions = build_bank()
    previous = json.loads((ROOT / "geometry/previous_bank.json").read_text())
    current = {sha256(q["question"].encode()).hexdigest()[:20]:q["id"] for q in questions}
    migration = [current.get(key,0) for key in previous]
    retired = [q["id"] for q in questions if q.get("modelMode",0) >= 18]
    retired3 = [q["id"] for q in questions if q.get("modelMode",0) >= 20]
    retired4 = [q["id"] for q in questions if q.get("modelMode",0) >= 22]
    retired5 = [q["id"] for q in questions if q.get("modelMode",0) >= 24]
    retired6 = [q["id"] for q in questions if q.get("modelMode",0) >= 27]
    retired7 = [q["id"] for q in questions if q.get("modelMode",0) >= 32]
    retired8 = json.loads((ROOT / "geometry/retired_v8.json").read_text())
    retired,retired3,retired4,retired5,retired6,retired7 = [sorted(set(ids)|set(retired8)) for ids in (retired,retired3,retired4,retired5,retired6,retired7)]
    occurrences = Counter(q[key] for q in questions for key in ("questionSvg","answerSvg"))
    for q in questions:
        for key,label in (("questionSvg","题图"),("answerSvg","解析图")):
            svg = q[key]
            if occurrences[svg] > 1:
                svg = add_question_caption(svg,q["question"])
            name = escape(f"第{q['id']}题 · {q['category']} · {label}")
            q[key] = svg.replace("<title>几何关系图</title>",f"<title>{name}</title>",1)
    bank = json.dumps(questions, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    template = (ROOT / "web/app.html").read_text(encoding="utf-8")
    lessons = json.dumps(build_lessons(),ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    template = template.replace("__LESSONS__",lessons)
    template = template.replace("__RETIRED8__",json.dumps(retired8))
    app = (ROOT / "web/app.js").read_text(encoding="utf-8")
    output = ROOT / "candidate" / "index.html"
    output.parent.mkdir(exist_ok=True)
    output.write_text(template.replace("__APP__", app).replace("__BANK__", bank).replace("__RETIRED7__", json.dumps(retired7)).replace("__RETIRED6__", json.dumps(retired6)).replace("__RETIRED5__", json.dumps(retired5)).replace("__RETIRED4__", json.dumps(retired4)).replace("__RETIRED3__", json.dumps(retired3)).replace("__RETIRED__", json.dumps(retired)).replace("__MIGRATION__", json.dumps(migration,separators=(",",":"))), encoding="utf-8", newline="\n")
    print(f"{output.relative_to(ROOT)}: {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()
