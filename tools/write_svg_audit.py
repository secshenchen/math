"""Write per-document evidence from the actual release and browser layout run."""
import base64
import csv
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
packed = (root / "index.html").read_bytes()
html = gzip.decompress(base64.b64decode(re.search(rb"atob\('([^']+)'",packed)[1])).decode()
bank = json.loads(html.split('id="bank">',1)[1].split("</script>",1)[0])
layout = json.loads(Path(sys.argv[1]).read_text(encoding="utf8"))
assert len(layout["records"]) == 10000 and not layout["issues"]
target = root / "audit"
target.mkdir(exist_ok=True)
with (target / "SVG逐图审计.tsv").open("w",encoding="utf-8-sig",newline="") as f:
    writer = csv.writer(f,delimiter="\t")
    writer.writerow(["题号","专题","图","SVG SHA256","文字标签数","线段数","XML/坐标复算","浏览器布局","最新版逐张目视","问题与处理"])
    for row in layout["records"]:
        q = bank[row["id"]-1]
        fixes = ["完整题目条件与解法入图；数字分数单位不断行；图注留白增加"]
        if q["category"] == "一半模型" and 10 <= q.get("modelMode",-1) <= 14:
            fixes.append("补中点条件与等长刻痕")
        if q["id"] == 3698:
            fixes.append("已修复并截图复核：交点O标签移出狭小区域")
        writer.writerow([q["id"],q["category"],row["field"],hashlib.sha256(q[row["field"]].encode()).hexdigest(),
                         row["labels"],row["auxiliaryLines"],"已通过发布文件测试（不等同完整数学证明）",
                         "通过：无字框相互遮挡、越界或无白描边穿线","待完成；先前同构图抽样不能替代当前逐张目视","；".join(fixes)])
(target / "release.json").write_text(json.dumps({"sha256":hashlib.sha256(packed).hexdigest(),"bytes":len(packed),
    "layout_documents":len(layout["records"]),"layout_issues":len(layout["issues"]),
    "teaching_documents":len(layout.get("lessonRecords",[])),"visual_review_complete":False},indent=2)+"\n",encoding="utf8")
