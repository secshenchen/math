"""Report observed coverage and layout checks for the built geometry bank."""
import json
import re
import base64
import gzip
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def audit():
    packed = Path("index.html").read_text(encoding="utf-8")
    payload = re.search(r"atob\('([A-Za-z0-9+/=]+)'\)",packed)[1]
    html = gzip.decompress(base64.b64decode(payload)).decode("utf-8")
    bank = json.loads(html.split('id="bank">', 1)[1].split("</script>", 1)[0])
    groups = Counter((q["category"], re.sub(r"\d+(?:[./]\d+)?", "N", q["question"])) for q in bank)
    diagram_counts = Counter(re.sub(r"<title>[^<]*</title>", "", q[key])
                             for q in bank for key in ("questionSvg", "answerSvg"))
    def marks(svg):
        root = ET.fromstring(svg)
        return "".join(ET.tostring(e,encoding="unicode") for e in root if e.tag.rsplit("}",1)[-1] not in ("title","desc","text"))
    from geometry.reasoning import reviewed_multistep
    challenge = [q for q in bank if q["difficulty"] == "挑战"]
    return {
        "questions": len(bank),
        "svg_documents": 2*len(bank),
        "distinct_svg_bodies": len(diagram_counts),
        "reused_svg_bodies": sum(count > 1 for count in diagram_counts.values()),
        "unique_geometry_ignoring_text": len({marks(q[key]) for q in bank for key in ("questionSvg","answerSvg")}),
        "same_geometry_question_answer_pairs": sum(marks(q["questionSvg"]) == marks(q["answerSvg"]) for q in bank),
        "svg_uniqueness_note": "完整独立文档不等于不同几何结构；重复构图可由条件文字区分，答案图包含本题解法。",
        "topics": dict(Counter(q["category"] for q in bank)),
        "difficulty": dict(Counter(q["difficulty"] for q in bank)),
        "geometry_status": dict(Counter(q["geometryStatus"] for q in bank)),
        "normalized_prompts": len(groups),
        "largest_prompt_group": max(groups.values()),
        "reviewed_multistep_challenges": sum(reviewed_multistep(q) for q in challenge),
        "challenge_reasoning_families": dict(Counter(f"{q['category']} / {q['modelMode']}" for q in challenge)),
        "new_model_coverage": dict(Counter(
            f"{q['category']} · {q['subcategory']}" for q in bank if 27 <= q.get("modelMode",0) < 32
        )),
        "diversified_models": dict(Counter(
            f"{q['category']} · {q['subcategory']}" for q in bank if 32 <= q.get("modelMode",0) < 40
        )),
        "curriculum_models": dict(Counter(f"{q['category']} · {q['subcategory']}" for q in bank if q.get("modelMode",0) >= 40)),
        "most_frequent_forms": [
            {"topic": topic, "form": prompt, "count": count}
            for (topic, prompt), count in groups.most_common(15)
        ],
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
