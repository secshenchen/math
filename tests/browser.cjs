const assert = require("node:assert/strict");
const {readFileSync,writeFileSync} = require("node:fs");
const {resolve} = require("node:path");
const {pathToFileURL} = require("node:url");
const {chromium, webkit, devices} = require("playwright");

async function main() {
  const engine = process.env.GEOMETRY_BROWSER === "webkit" ? webkit : chromium;
  const browser = await engine.launch(engine === chromium && process.env.CHROMIUM_PATH
    ? {executablePath:process.env.CHROMIUM_PATH} : {});
  try {
    const device = process.env.GEOMETRY_DEVICE;
    const context = await browser.newContext({...(devices[device] ?? {viewport:{width:1365,height:900}}), offline:engine === chromium});
    const page = await context.newPage();
    const errors = [], remote = [];
    page.on("pageerror", error => errors.push(error.message));
    const localDocument = "https://geometry.test/index.html";
    page.on("request", request => {
      if (engine === webkit && request.url() === localDocument && request.resourceType() === "document") return;
      if (/^https?:/.test(request.url())) remote.push(request.url());
    });
    page.on("dialog", dialog => dialog.accept());
    const packed = resolve("index.html");
    if (engine === webkit) {
      // WebKit on the Linux runner cannot navigate to the local file.
      // Fulfill the document from disk and prohibit all network traffic.
      const url = localDocument;
      await page.route("**/*", route => route.request().url() === url && route.request().resourceType() === "document"
        ? route.fulfill({contentType:"text/html; charset=utf-8",body:readFileSync(packed)})
        : route.abort());
      await page.goto(url);
    } else {
      await page.goto(pathToFileURL(packed).href);
    }
    const input = id => page.locator("#" + id);
    async function credentials(name, pass, action) {
      await input("username").fill(name);
      await input("password").fill(pass);
      if (action === "register") await input("confirmPassword").fill(pass);
      await input(action).click();
    }
    await input("login").waitFor({state:"visible"});
    async function auditAccessibility() {
      if (engine !== chromium || !process.env.GEOMETRY_AXE) return;
      await page.addScriptTag({content:readFileSync(require.resolve("axe-core/axe.min.js"),"utf8")});
      const violations = await page.evaluate(async () => (await window.axe.run({
        runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa"]},
      })).violations.map(({id,nodes}) => ({id,targets:nodes.map(node => node.target)})));
      assert.deepEqual(violations,[]);
    }
    await auditAccessibility();
    await page.keyboard.press("Tab");
    assert.ok(await page.evaluate(() => document.activeElement?.matches("input, button, a")));
    assert.equal(await page.locator("html").getAttribute("lang"),"zh-CN");
    await credentials("local-test-a","test-a-1234","register");
    await input("workspace").waitFor({state:"visible"});
    assert.equal(await input("drawing").locator("svg").count(),1);
    assert.ok(await input("drawing").locator("svg title").textContent());
    const graphic = input("drawing").locator("svg");
    assert.equal(await graphic.getAttribute("role"),"img");
    assert.match(await graphic.ariaSnapshot(), /img "第1题 · 长方形与正方形 · 题图"/);
    assert.match(await input("response").ariaSnapshot(), /textbox "答案"/);
    await auditAccessibility();
    assert.equal(await input("solutionSvg").locator("svg").count(),0);
    const topics = await input("category").locator("option").evaluateAll(nodes => nodes.map(n => n.value).filter(Boolean));
    for (const category of topics) {
      await input("category").selectOption(category);
      await input("learn").click();
      assert.match(await input("lessonTitle").textContent(),new RegExp(category));
      assert.equal(await input("lessonDrawing").locator("svg").count(),1);
      assert.ok((await input("lessonSteps").locator("li").count()) >= 2);
      assert.ok(await input("lessonCondition").textContent());
      assert.equal(await page.evaluate(() => document.activeElement.id),"lessonTitle");
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),true);
    }
    await input("filter").selectOption("wrong");
    await input("category").selectOption("平行四边形");
    assert.equal(await input("problem").isVisible(),false);
    await input("learn").click();
    assert.match(await input("lessonTitle").textContent(),/平行四边形/);
    await input("filter").selectOption("");
    await input("category").selectOption("");
    await input("resume").click();
    const openChapters = page.getByText("展开章节", {exact:true});
    const firstChapter = input("chapters").getByRole("button", {name:/长方形与正方形/});
    if (devices[device]?.hasTouch) {
      await openChapters.tap();
      await firstChapter.tap();
    } else {
      await openChapters.click();
      await firstChapter.click();
    }
    await input("resume").click();
    assert.match(await input("problemStatus").textContent(), /未作答/);
    await input("entry").fill("84cm²");
    await input("response").locator("button").click();
    assert.match(await input("feedback").textContent(), /正确/);
    assert.match(await input("problemStatus").textContent(), /已答对/);
    await input("solution").locator("summary").click();
    await input("solutionSvg").locator("svg").waitFor();
    await input("next").click();
    assert.equal(await page.evaluate(() => document.activeElement.id),"title","Next must announce the new problem through focus");
    await input("entry").fill("1");
    await input("response").locator("button").click();
    assert.match(await input("feedback").textContent(), /错误/);
    await input("favorite").click();
    await input("mastered").click();
    await input("filter").selectOption("wrong");
    assert.match(await input("matches").textContent(), /^1 /);
    await input("resume").click();
    await input("search").fill("5000");
    assert.match(await input("title").textContent(), /5000/);
    await page.reload();
    await input("workspace").waitFor({state:"visible"});
    assert.match(await input("title").textContent(), /5000/);
    await input("logout").click();
    await credentials("local-test-a","incorrect","signIn");
    await page.getByText("用户名或密码错误。").waitFor();
    await credentials("local-test-b","test-b-1234","register");
    await input("workspace").waitFor({state:"visible"});
    assert.match(await input("summary").textContent(), /完成 0\/5000/);
    await input("logout").click();
    await credentials("local-test-a","test-a-1234","signIn");
    await input("workspace").waitFor({state:"visible"});
    assert.match(await input("summary").textContent(), /完成 2\/5000/);
    await input("category").selectOption("平行四边形");
    await input("random").click();
    assert.match(await input("title").textContent(), /平行四边形/);
    const download = page.waitForEvent("download");
    await input("download").click();
    const exported = await download;
    const file = await exported.path();
    const backup = JSON.parse(readFileSync(file,"utf8"));
    assert.ok(Date.parse(backup.marks["1"].answered));
    await input("clear").click();
    assert.match(await input("summary").textContent(), /完成 0/);
    await input("uploadFile").setInputFiles(file);
    await page.waitForFunction(() => document.getElementById("summary").textContent.includes("完成 2/"));
    const imported = page.waitForEvent("download");
    await input("download").click();
    const restored = JSON.parse(readFileSync(await (await imported).path(),"utf8"));
    assert.equal(restored.marks["1"].answered,backup.marks["1"].answered);
    await input("uploadFile").setInputFiles({name:"large.json",mimeType:"application/json",buffer:Buffer.alloc(2000001,32)});
    assert.match(await input("importMessage").textContent(),/文件过大/);
    assert.deepEqual(await page.evaluate(() => JSON.parse(localStorage.getItem("math-geometry-v1-progress:local-test-a"))),restored);
    const legacy = await page.evaluate(() => {
      const old = JSON.parse(document.getElementById("migration").textContent);
      const versions = [[undefined, old.indexOf(0)+1]];
      for (const [version, element] of [[2,"retired"],[3,"retired3"],[4,"retired4"],[5,"retired5"],[6,"retired6"],[7,"retired7"],[8,"retired8"]]) {
        versions.push([version,JSON.parse(document.getElementById(element).textContent)[0]]);
      }
      return versions;
    });
    for (const [version, retired] of legacy) {
      assert.ok(retired > 5);
      const old = {version, last:retired, marks:{"1":{favorite:true}, [retired]:{mastered:true}}};
      await page.evaluate(old => localStorage.setItem("math-geometry-v1-progress:local-test-a",JSON.stringify(old)),old);
      await page.reload();
      await input("workspace").waitFor({state:"visible"});
      const {current, previous} = await page.evaluate(version => {
        const read = key => JSON.parse(localStorage.getItem("math-geometry-v1-"+key));
        return {current:read("progress:local-test-a"),
                previous:read((version === null ? "previous-progress:" : "previous-progress-v"+version+":")+"local-test-a")};
      },version ?? null);
      assert.deepEqual(current,{version:9,last:1,marks:{"1":{favorite:true}}});
      assert.deepEqual(previous,JSON.parse(JSON.stringify(old)));
    }
    const v7 = {version:7,last:2,marks:{"2":{favorite:true},[legacy.at(-1)[1]]:{mastered:true}}};
    await input("uploadFile").setInputFiles({name:"v7.json",mimeType:"application/json",buffer:Buffer.from(JSON.stringify(v7))});
    await page.waitForFunction(() => document.getElementById("title").textContent.includes("第 2 题"));
    assert.deepEqual(await page.evaluate(() => JSON.parse(localStorage.getItem("math-geometry-v1-progress:local-test-a"))),
      {version:9,last:2,marks:{"2":{favorite:true}}});
    await input("search").fill("1");
    await page.evaluate(() => { window.print = () => document.body.dataset.printed = "yes"; });
    await input("print").click();
    assert.equal(await page.locator("body").getAttribute("data-printed"), "yes");
    if (engine === chromium) {
      await page.emulateMedia({media:"print"});
      assert.equal(await input("knowledge").isVisible(),false);
      assert.equal(await input("drawing").locator("svg").isVisible(),true);
      assert.equal(await input("solutionSvg").locator("svg").count(),0);
      const pdf = await page.pdf({format:"A4"});
      assert.equal(pdf.subarray(0,4).toString(), "%PDF");
      if (process.env.GEOMETRY_PDF_DIR) writeFileSync(resolve(process.env.GEOMETRY_PDF_DIR,"question.pdf"),pdf);
      await page.emulateMedia({media:"screen"});
      await input("solution").locator("summary").click();
      await input("solutionSvg").locator("svg").waitFor();
      await page.emulateMedia({media:"print"});
      const answerPdf = await page.pdf({format:"A4"});
      if (process.env.GEOMETRY_PDF_DIR) writeFileSync(resolve(process.env.GEOMETRY_PDF_DIR,"answer.pdf"),answerPdf);
      await page.emulateMedia({media:"screen"});
    }
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await input("remove").click();
    await input("login").waitFor({state:"visible"});
    assert.equal(await page.evaluate(() => localStorage.getItem("math-geometry-v1-previous-progress-v7:local-test-a")),null);
    await credentials("local-test-a","test-a-1234","signIn");
    await page.getByText("用户名或密码错误。").waitFor();
    await credentials("local-test-b","test-b-1234","register");
    await page.getByText("用户名已存在。").waitFor();
    assert.deepEqual(remote, []);
    assert.deepEqual(errors, []);
    console.log("Offline browser smoke test passed.");
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
