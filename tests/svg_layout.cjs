const assert = require("node:assert/strict");
const {readFileSync, writeFileSync} = require("node:fs");
const {gunzipSync} = require("node:zlib");
const {chromium} = require("playwright");

(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH
    ? {executablePath:process.env.CHROMIUM_PATH} : {});
  try {
    const page = await browser.newPage();
    const packed = readFileSync("index.html","utf8").match(/atob\('([A-Za-z0-9+/=]+)'\)/)[1];
    const html = gunzipSync(Buffer.from(packed,"base64")).toString("utf8");
    const data = html.split('id="bank">')[1].split("</script>")[0];
    const bank = JSON.parse(data);
    const lessons = Object.entries(JSON.parse(html.split('id="lessons">')[1].split("</script>")[0]))
      .map(([id,lesson]) => ({id,svg:lesson.svg,fields:["svg"]}));
    const subjects = [...bank,...lessons];
    const issues = [];
    const records = [];
    let covered = 0;
    for (let i=0;i<subjects.length;i+=100) {
      const result = await page.evaluate(batch => {
        const issues = [];
        const records = [];
        function cutsBox(line, box) {
          const [x1,y1,x2,y2] = line;
          let lo = 0, hi = 1;
          for (const [start,delta,min,max] of [[x1,x2-x1,box.x,box.x+box.width],
                                               [y1,y2-y1,box.y,box.y+box.height]]) {
            if (!delta) {
              if (start < min || start > max) return false;
              continue;
            }
            const ends = [(min-start)/delta,(max-start)/delta].sort((a,b) => a-b);
            lo = Math.max(lo,ends[0]);
            hi = Math.min(hi,ends[1]);
            if (lo > hi) return false;
          }
          return true;
        }
        const holder = document.createElement("div");
        document.body.append(holder);
        for (const question of batch) for (const field of question.fields ?? ["questionSvg","answerSvg"]) {
          const record = {id:question.id, field, labels:0, auxiliaryLines:0, haloCrossings:0};
          records.push(record);
          holder.innerHTML = question[field];
          const svg = holder.firstElementChild;
          const {width,height} = svg.viewBox.baseVal;
          const lines = [...svg.querySelectorAll("line")].map(line =>
            ["x1","y1","x2","y2"].map(key => line[key].baseVal.value));
          record.auxiliaryLines = lines.length;
          const shape = [...svg.querySelectorAll("polygon")].at(-1);
          const points = Array.from(shape.points);
          for (const [i,p] of points.entries()) {
            const next = points[(i+1)%points.length];
            lines.push([p.x,p.y,next.x,next.y]);
          }
          const boxes = [];
          for (const label of svg.querySelectorAll("text")) {
            const b = label.getBBox();
            record.labels++;
            for (const [text, a] of boxes) {
              if (Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>1
                  && Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>2) {
                issues.push({id:question.id,field,text:label.textContent,kind:"overlapping labels",with:text});
              }
            }
            boxes.push([label.textContent,b]);
            if (label.getAttribute("text-anchor") === "middle" && lines.some(line => cutsBox(line,b))) {
              if (label.getAttribute("paint-order") === "stroke" && label.getAttribute("stroke") === "white") {
                record.haloCrossings++;
              } else {
                issues.push({id:question.id,field,text:label.textContent,kind:"unprotected line overlap"});
              }
            }
            if (b.x < -.5 || b.y < -.5 || b.x+b.width > width+.5 || b.y+b.height > height+.5) {
              issues.push({id:question.id,field,text:label.textContent, bounds:[b.x,b.y,b.width,b.height]});
            }
          }
        }
        holder.remove();
        return {issues,records};
      },subjects.slice(i,i+100));
      issues.push(...result.issues);
      records.push(...result.records);
      covered += result.records.reduce((sum, row) => sum+row.haloCrossings,0);
    }
    console.log(JSON.stringify({checked:2*bank.length,teachingSVGs:lessons.length, issues:issues.length, labelsWithHaloAtCrossings:covered, examples:issues.slice(0,12)}));
    if (process.env.GEOMETRY_LAYOUT_REPORT) writeFileSync(process.env.GEOMETRY_LAYOUT_REPORT, JSON.stringify({records:records.filter(r => typeof r.id === "number"),lessonRecords:records.filter(r => typeof r.id === "string"),issues}));
    assert.equal(issues.length,0,"SVG text must fit and remain legible at line crossings");
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
