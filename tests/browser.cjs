const assert = require("node:assert/strict");
const {resolve} = require("node:path");
const {pathToFileURL} = require("node:url");
const {chromium, webkit, devices} = require("playwright");

async function main() {
  const engine = process.env.GEOMETRY_BROWSER === "webkit" ? webkit : chromium;
  const browser = await engine.launch(engine === chromium && process.env.CHROMIUM_PATH
    ? {executablePath:process.env.CHROMIUM_PATH} : {});
  try {
    const device = process.env.GEOMETRY_DEVICE;
    const context = await browser.newContext({...(devices[device] ?? {viewport:{width:390,height:844}}), offline:true});
    const page = await context.newPage();
    const errors = [], remote = [];
    page.on("pageerror", error => errors.push(error.message));
    page.on("request", request => { if (/^https?:/.test(request.url())) remote.push(request.url()); });
    page.on("dialog", dialog => dialog.accept());
    await page.goto(pathToFileURL(resolve("candidate/offline.html")).href);
    const input = id => page.locator("#" + id);
    async function credentials(name, pass, action) {
      await input("username").fill(name);
      await input("password").fill(pass);
      if (action === "register") await input("confirmPassword").fill(pass);
      await input(action).click();
    }
    await input("login").waitFor({state:"visible"});
    await credentials("local-test-a","test-a-1234","register");
    await input("workspace").waitFor({state:"visible"});
    assert.equal(await input("drawing").locator("svg").count(),1);
    assert.equal(await input("solutionSvg").locator("svg").count(),0);
    await input("entry").fill("84cm²");
    await input("response").locator("button").click();
    assert.match(await input("feedback").textContent(), /正确/);
    await input("solution").locator("summary").click();
    await input("solutionSvg").locator("svg").waitFor();
    await input("next").click();
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
    await input("clear").click();
    assert.match(await input("summary").textContent(), /完成 0/);
    await input("uploadFile").setInputFiles(file);
    await page.waitForFunction(() => document.getElementById("summary").textContent.includes("完成 2/"));
    await input("search").fill("1");
    await page.evaluate(() => { window.print = () => document.body.dataset.printed = "yes"; });
    await input("print").click();
    assert.equal(await page.locator("body").getAttribute("data-printed"), "yes");
    if (engine === chromium) {
      const pdf = await page.pdf({format:"A4"});
      assert.equal(pdf.subarray(0,4).toString(), "%PDF");
    }
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.deepEqual(remote, []);
    assert.deepEqual(errors, []);
    console.log("Offline browser smoke test passed.");
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
