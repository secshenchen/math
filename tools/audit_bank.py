"""Report observed coverage and layout checks for the built geometry bank."""
import json
import re
from collections import Counter
from pathlib import Path


def audit():
    html = Path("candidate/index.html").read_text(encoding="utf-8")
    bank = json.loads(html.split('id="bank">', 1)[1].split("</script>", 1)[0])
    groups = Counter((q["category"], re.sub(r"\d+(?:[./]\d+)?", "N", q["question"])) for q in bank)
    diagram_counts = Counter(re.sub(r"<title>[^<]*</title>", "", q[key])
                             for q in bank for key in ("questionSvg", "answerSvg"))
    return {
        "questions": len(bank),
        "svg_documents": 2*len(bank),
        "distinct_svg_bodies": len(diagram_counts),
        "reused_svg_bodies": sum(count > 1 for count in diagram_counts.values()),
        "topics": dict(Counter(q["category"] for q in bank)),
        "difficulty": dict(Counter(q["difficulty"] for q in bank)),
        "geometry_status": dict(Counter(q["geometryStatus"] for q in bank)),
        "normalized_prompts": len(groups),
        "largest_prompt_group": max(groups.values()),
        "new_model_coverage": dict(Counter(
            f"{q['category']} · {q['subcategory']}" for q in bank if q.get("modelMode",0) >= 27
        )),
        "most_frequent_forms": [
            {"topic": topic, "form": prompt, "count": count}
            for (topic, prompt), count in groups.most_common(15)
        ],
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
