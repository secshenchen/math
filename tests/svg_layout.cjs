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
    for (let i=0;i<bank.length;i+=100) {
      issues.push(...await page.evaluate(batch => {
        const issues = [];
        const holder = document.createElement("div");
        document.body.append(holder);
        for (const question of batch) for (const field of ["questionSvg","answerSvg"]) {
          holder.innerHTML = question[field];
          const svg = holder.firstElementChild;
          const {width,height} = svg.viewBox.baseVal;
          for (const label of svg.querySelectorAll("text")) {
            const b = label.getBBox();
            if (b.x < -.5 || b.y < -.5 || b.x+b.width > width+.5 || b.y+b.height > height+.5) {
              issues.push({id:question.id,field,text:label.textContent, bounds:[b.x,b.y,b.width,b.height]});
            }
          }
        }
        holder.remove();
        return issues;
      },bank.slice(i,i+100)));
    }
    console.log(JSON.stringify({checked:2*bank.length, overflow:issues.length, examples:issues.slice(0,12)}));
    assert.equal(issues.length,0,"SVG text must fit its viewBox");
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
