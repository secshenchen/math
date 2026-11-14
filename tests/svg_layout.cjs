const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {chromium} = require("playwright");

(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const data = readFileSync("candidate/index.html","utf8").split('id="bank">')[1].split("</script>")[0];
    const bank = JSON.parse(data);
    const issues = [];
    let covered = 0;
    for (let i=0;i<bank.length;i+=100) {
      const result = await page.evaluate(batch => {
        const issues = [];
        let covered = 0;
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
        for (const question of batch) for (const field of ["questionSvg","answerSvg"]) {
          holder.innerHTML = question[field];
          const svg = holder.firstElementChild;
          const {width,height} = svg.viewBox.baseVal;
          const lines = [...svg.querySelectorAll("line")].map(line =>
            ["x1","y1","x2","y2"].map(key => line[key].baseVal.value));
          const shape = [...svg.querySelectorAll("polygon")].at(-1);
          const points = Array.from(shape.points);
          for (const [i,p] of points.entries()) {
            const next = points[(i+1)%points.length];
            lines.push([p.x,p.y,next.x,next.y]);
          }
          for (const label of svg.querySelectorAll("text")) {
            const b = label.getBBox();
            if (label.getAttribute("text-anchor") === "middle" && lines.some(line => cutsBox(line,b))) {
              if (label.getAttribute("paint-order") === "stroke" && label.getAttribute("stroke") === "white") {
                covered++;
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
        return {issues,covered};
      },bank.slice(i,i+100));
      issues.push(...result.issues);
      covered += result.covered;
    }
    console.log(JSON.stringify({checked:2*bank.length, issues:issues.length, labelsWithHaloAtCrossings:covered, examples:issues.slice(0,12)}));
    assert.equal(issues.length,0,"SVG text must fit and remain legible at line crossings");
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
