// Reproduce representative contact sheets; opening them is a separate review.
const fs = require("node:fs");
const path = require("node:path");
const {gunzipSync} = require("node:zlib");
const {chromium} = require("playwright");

(async () => {
  const packed = fs.readFileSync("index.html","utf8").match(/atob\('([^']+)'/)[1];
  const html = gunzipSync(Buffer.from(packed,"base64")).toString("utf8");
  const bank = JSON.parse(html.split('id="bank">')[1].split("</script>")[0]);
  const lessons = JSON.parse(html.split('id="lessons">')[1].split("</script>")[0]);
  const dir = process.env.GEOMETRY_REVIEW_DIR || "candidate/review";
  fs.mkdirSync(dir,{recursive:true});
  const chosen = new Map();
  for (const q of bank) {
    const form = q.category + q.question.replace(/\d+(?:[./]\d+)?/g,"N");
    if (!chosen.has(form)) chosen.set(form,q);
  }
  const rows = [...new Map([...bank.slice(0,5),...chosen.values()].map(q=>[q.id,q])).values()];
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? {executablePath:process.env.CHROMIUM_PATH} : {});
  const manifest = {questions:[],lessons:[]};
  try {
    const page = await browser.newPage({viewport:{width:880,height:1200}});
    const style = '<meta charset="utf-8"><style>body{margin:0;font:16px sans-serif;background:#e5ebf3}main{display:grid;grid-template-columns:repeat(2,430px);gap:6px}article{background:white;padding:5px;overflow:hidden}h2{font:16px sans-serif;font-weight:bold;margin:6px}svg{display:block;width:420px;height:auto}</style>';
    for (let i=0;i<rows.length;i+=4) {
      const file = `questions-${i/4+1}.png`;
      await page.setContent(style+'<main>'+rows.slice(i,i+4).map(q=>`<article><h2>#${q.id} ${q.category} · ${q.subcategory}</h2>${q.questionSvg}${q.answerSvg}</article>`).join("")+'</main>');
      await page.locator("main").screenshot({path:path.join(dir,file)});
      manifest.questions.push(...rows.slice(i,i+4).map(q=>({id:q.id,sheet:file,question:q.question,solution:q.solution})));
    }
    const cards = Object.entries(lessons);
    for (let i=0;i<cards.length;i+=4) {
      const file = `lessons-${i/4+1}.png`;
      await page.setContent(style+'<main>'+cards.slice(i,i+4).map(([group,l])=>`<article><h2>${group}</h2><p>${l.condition}</p>${l.svg}<p>${l.rule}</p><ol>${l.steps.map(s=>`<li>${s}</li>`).join("")}</ol><p>${l.caution}</p></article>`).join("")+'</main>');
      await page.locator("main").screenshot({path:path.join(dir,file)});
      manifest.lessons.push(...cards.slice(i,i+4).map(([category])=>({category,sheet:file})));
    }
    fs.writeFileSync(path.join(dir,"manifest.json"),JSON.stringify(manifest,null,2));
    console.log(JSON.stringify({questionPairs:rows.length,sheets:Math.ceil(rows.length/4),teachingCards:cards.length}));
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
