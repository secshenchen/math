"use strict";
const el = id => document.getElementById(id);
const bank = JSON.parse(el("bank").textContent);
const lessons = JSON.parse(el("lessons").textContent);
const namespace = "math-geometry-v1-";
const enc = new TextEncoder();
const read = (key, fallback) => JSON.parse(localStorage.getItem(namespace + key) ?? JSON.stringify(fallback));
const save = (key, value) => localStorage.setItem(namespace + key, JSON.stringify(value));
const hex = bytes => Array.from(bytes, n => n.toString(16).padStart(2, "0")).join("");
let account = null, data, shown = bank, cursor = 0, current;
const fresh = () => ({version:9, last:1, marks:{}});
const retireByVersion = {2:"retired",3:"retired3",4:"retired4",5:"retired5",6:"retired6",7:"retired7",8:"retired8"};
function migrateProgress(old) {
  if (old.version === 9) return old;
  if (Object.hasOwn(retireByVersion, old.version)) {
    const retired = new Set(JSON.parse(el(retireByVersion[old.version]).textContent));
    return {version:9, last:retired.has(old.last) ? 1 : old.last,
            marks:Object.fromEntries(Object.entries(old.marks).filter(([id]) => !retired.has(Number(id))))};
  }
  if (old.version !== undefined) throw Error("学习记录版本不受支持。");
  const map = JSON.parse(el("migration").textContent);
  const converted = fresh();
  converted.last = map[old.last-1] || 1;
  for (const [id, record] of Object.entries(old.marks)) {
    const replacement = map[Number(id)-1];
    if (replacement) converted.marks[replacement] = record;
  }
  return converted;
}
const mark = () => data.marks[current.id] ??= {};
const persist = () => save("progress:" + account, data);
async function verifier(password, salt) {
  if (!globalThis.crypto?.subtle) throw Error("当前环境不支持安全的本地密码验证。请使用支持 Web Crypto 的本地浏览器或 HTTPS 页面。");
  const key = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits"]);
  return hex(new Uint8Array(await crypto.subtle.deriveBits({name:"PBKDF2", salt:enc.encode(salt), iterations:600000, hash:"SHA-256"}, key, 256)));
}
function activate(name) {
  const previousProgress = read("progress:" + name, fresh());
  data = migrateProgress(previousProgress);
  if (Object.hasOwn(retireByVersion, previousProgress.version)) {
    save("previous-progress-v" + previousProgress.version + ":" + name,previousProgress);
  }
  if (previousProgress.version === undefined && !read("previous-progress:" + name,null)) {
    save("previous-progress:" + name,previousProgress);
  }
  save("active", name);
  account = name;
  el("login").hidden = true;
  el("workspace").hidden = false;
  el("who").textContent = name;
  const color = read("profile:" + name, {}).color;
  el("avatar").style.backgroundColor = /^#[0-9a-f]{6}$/i.test(color ?? "") ? color : "#2457a6";
  el("avatar").textContent = Array.from(name)[0] ?? "";
  resetFilters();
}
el("credentials").addEventListener("submit", async event => {
  event.preventDefault();
  const name = el("username").value.trim(), password = el("password").value;
  const registering = event.submitter?.id === "register";
  const buttons = ["signIn","register"].map(el);
  buttons.forEach(button => button.disabled = true);
  try {
    if (!name) throw Error("请输入用户名。");
    const key = "profile:" + name;
    const profile = read(key, null);
    if (registering) {
      if (profile) throw Error("用户名已存在。");
      if (password.length < 6 || password !== el("confirmPassword").value) throw Error("密码至少 6 个字符，两次输入须一致。");
      const salt = hex(crypto.getRandomValues(new Uint8Array(16)));
      save(key, {salt, digest:await verifier(password,salt), color:el("avatarColor").value});
    } else if (!profile || await verifier(password, profile.salt) !== profile.digest) {
      throw Error("用户名或密码错误。");
    }
    el("credentials").reset();
    el("authMessage").textContent = "";
    activate(name);
  } catch (error) { el("authMessage").textContent = error.message; }
  finally { buttons.forEach(button => button.disabled = false); }
});
function exit() {
  localStorage.removeItem(namespace + "active");
  account = null;
  el("workspace").hidden = true;
  el("login").hidden = false;
}
const counts = new Map();
for (const q of bank) counts.set(q.category,(counts.get(q.category) ?? 0)+1);
for (const [group, count] of counts) {
  const label = group + "（" + count + "）";
  el("category").add(new Option(label,group));
  const button = Object.assign(document.createElement("button"), {type:"button", textContent:label});
  button.onclick = () => { filters.forEach(id => el(id).value = ""); el("category").value = group; select(); el("title").focus(); };
  el("chapters").append(button);
}
const filters = ["category","level","filter","search"];
function resetFilters() {
  filters.forEach(id => el(id).value = "");
  select(data.last);
}
function select(id) {
  const [category, level, filter, raw] = filters.map(id => el(id).value.trim());
  const search = raw.toLowerCase();
  shown = bank.filter(q => {
    const record = data.marks[q.id] ?? {};
    return (!category || q.category === category) && (!level || q.difficulty === level)
      && (!filter || (filter === "wrong" ? record.correct === false : filter === "new" ? record.correct === undefined : record[filter]))
      && (!search || (/^\d+$/.test(search) ? String(q.id) === search : (q.question + q.category + q.subcategory).toLowerCase().includes(search)));
  });
  cursor = Math.max(0,shown.findIndex(q => q.id === id));
  render();
}
for (const id of filters) el(id).addEventListener("input", () => select());
function stats() {
  const marks = Object.values(data.marks);
  const correct = marks.filter(m => m.correct === true).length, wrong = marks.filter(m => m.correct === false).length;
  const mastered = marks.filter(m => m.mastered).length, favorite = marks.filter(m => m.favorite).length;
  const accuracy = correct + wrong ? Math.round(correct * 100/(correct + wrong)) : 0;
  const ids = el("category").value ? bank.filter(q => q.category === el("category").value) : bank;
  const completed = ids.filter(q => typeof data.marks[q.id]?.correct === "boolean").length;
  el("summary").textContent = `完成 ${correct+wrong}/${bank.length} · 正确率 ${accuracy}% · 错题 ${wrong} · 收藏 ${favorite} · 掌握 ${mastered}（${(100*mastered/bank.length).toFixed(1)}%） · 当前专题 ${completed}/${ids.length}`;
}
const formulas = {
  "长方形与正方形":"长方形面积＝长×宽，周长＝2×(长＋宽)。正方形面积＝边长²。",
  "平行四边形":"面积＝底×对应的高。对角线把平行四边形分成两个全等三角形。",
  "梯形":"面积＝(上底＋下底)×高÷2。",
  "三角形基础":"面积＝底×对应的高÷2。作高时，垂足可以落在底边的延长线上。",
  "三角形边角关系":"三角形内角和＝180°。任意两边之和大于第三边。",
  "等积模型":"同底等高的三角形面积相等。同高时，面积比等于底边比。",
  "一半模型":"三角形的中线平分面积。两边中点连线平行于第三边，长度为其一半。",
  "风筝模型":"凸四边形对角线相交后，四个区域中，相对两块的面积乘积相等。",
  "蝴蝶模型":"梯形的两翼等积。上下两块三角形的面积比等于两底比的平方。",
  "鸟头模型":"两三角形共用一个夹角时，可逐次固定一条边，利用共同高换算面积比。",
  "燕尾模型":"从共同底边或共同高入手，通过分点比例逐步换算面积。",
  "综合几何模型":"先找平行线、中点和公共高，确定可直接换算的面积，再合并结果。"
};
function showProblemStatus(record) {
  el("problemStatus").textContent = [
    current.subcategory,
    record.correct === true ? "已答对" : record.correct === false ? "待重练" : "未作答",
    record.mastered ? "已掌握" : ""
  ].filter(Boolean).join(" · ");
}
function render() {
  current = shown[cursor];
  el("matches").textContent = `${shown.length} 道题`;
  el("problem").hidden = !current;
  el("empty").hidden = !!current;
  stats();
  showLesson(current?.category || el("category").value);
  if (!current) return;
  el("title").textContent = `第 ${current.id} 题 · ${current.category} · ${current.difficulty}`;
  el("prompt").textContent = current.question;
  el("formula").textContent = formulas[current.category];
  el("drawing").innerHTML = current.questionSvg;
  el("solution").open = false;
  el("solutionSvg").replaceChildren();
  el("entry").value = "";
  el("feedback").textContent = "";
  el("previous").disabled = cursor === 0;
  el("next").disabled = cursor === shown.length-1;
  const record = data.marks[current.id] ?? {};
  showProblemStatus(record);
  for (const [id,label] of [["favorite","收藏"],["mastered","掌握"]]) {
    el(id).textContent = record[id] ? "取消" + label : "标记" + label;
    el(id).setAttribute("aria-pressed", !!record[id]);
  }
  data.last = current.id;
  persist();
}
function showLesson(category) {
  const lesson = lessons[category];
  el("knowledge").hidden = !lesson;
  el("learn").disabled = !lesson;
  if (!lesson) return;
  el("lessonTitle").textContent = category + " · " + lesson.title;
  el("lessonCondition").textContent = lesson.condition;
  el("lessonRule").textContent = lesson.rule;
  el("lessonDrawing").innerHTML = lesson.svg;
  el("lessonSteps").replaceChildren(...lesson.steps.map(s => Object.assign(document.createElement("li"),{textContent:s})));
  el("lessonCaution").textContent = lesson.caution;
}
function rational(str) {
  if (!/^[+-]?(?:\d{1,70}(?:[./]\d{1,70})?|\.\d{1,70})$/.test(str)) return null;
  if (str.includes("/")) {
    const [a,b] = str.split("/").map(BigInt);
    return b ? [a,b] : null;
  }
  const fraction = str.split(".")[1] ?? "";
  return [BigInt(str.replace(".","")),10n ** BigInt(fraction.length)];
}
function equivalent(input, q) {
  const normalize = str => str.normalize("NFKC").trim().replace(/\s+/g,"");
  let value = normalize(input);
  if (q.answerType === "text") {
    if (!value) return null;
    return [q.answer, ...(q.alternatives ?? [])].some(answer => normalize(answer) === value);
  }
  const unit = value.match(/(?:cm2|[^\d./:+-]+)$/iu)?.[0];
  if (unit) {
    const normalized = ({"平方厘米":"cm2","厘米":"cm","度":"°"})[unit] ?? unit.toLowerCase();
    if (normalized !== q.unit.normalize("NFKC")) return null;
    value = value.slice(0,-unit.length);
  }
  if (q.answerType === "ratio") {
    const parts = value.split(":").map(rational);
    if (parts.length !== 2 || parts.some(part => !part || part[0] <= 0n)) return null;
    const [a,b] = parts, [c,d] = q.answer.split(":").map(BigInt);
    return a[0]*b[1]*d === a[1]*b[0]*c;
  }
  const a = rational(value), b = rational(q.answer);
  if (!a || !b) return null;
  if (q.requiresUnit && !unit) return "missing-unit";
  const difference = a[0]*b[1]-b[0]*a[1];
  const tolerance = q.tolerance ? rational(q.tolerance) : null;
  if (!tolerance) return difference === 0n;
  const magnitude = difference < 0n ? -difference : difference;
  return magnitude*tolerance[1] <= tolerance[0]*a[1]*b[1];
}
el("response").onsubmit = event => {
  event.preventDefault();
  const answer = equivalent(el("entry").value, current);
  el("feedback").textContent = answer === "missing-unit" ? "请补充答案单位。" : answer === null ? "输入格式或单位无效。" : answer ? "回答正确。" : "回答错误，可以重试或查看解析。";
  if (typeof answer === "boolean") {
    Object.assign(mark(),{correct:answer, answered:new Date().toISOString()});
    persist();
    stats();
    showProblemStatus(mark());
  }
};
el("solution").ontoggle = () => {
  if (!current || !el("solution").open) { el("solutionSvg").replaceChildren(); return; }
  el("result").textContent = [current.answer,current.unit].join(" ");
  el("steps").replaceChildren(...current.solution.map(s => Object.assign(document.createElement("li"),{textContent:s})));
  el("solutionSvg").innerHTML = current.answerSvg;
};
el("next").onclick = () => { if (cursor+1<shown.length) { cursor++; render(); el("title").focus(); } };
el("previous").onclick = () => { if (cursor>0) { cursor--; render(); el("title").focus(); } };
el("random").onclick = () => { if (shown.length) { cursor = Math.floor(Math.random()*shown.length); render(); el("title").focus(); } };
el("resume").onclick = () => { resetFilters(); el("title").focus(); };
el("learn").onclick = () => { el("knowledge").open = true; el("lessonTitle").focus(); };
for (const id of ["favorite","mastered"]) el(id).onclick = () => { const record = mark(); record[id] = !record[id]; persist(); select(current.id); };
el("logout").onclick = exit;
el("print").onclick = () => window.print();
el("clear").onclick = () => { if (confirm("清空当前账户的全部学习记录？")) { data = fresh(); persist(); resetFilters(); } };
el("remove").onclick = () => { if (confirm("删除当前账户及学习记录？")) { localStorage.removeItem(namespace+"profile:"+account); localStorage.removeItem(namespace+"progress:"+account); localStorage.removeItem(namespace+"previous-progress:"+account); for (const version of Object.keys(retireByVersion)) localStorage.removeItem(namespace+"previous-progress-v"+version+":"+account); exit(); } };
el("download").onclick = () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data)],{type:"application/json"}));
  Object.assign(document.createElement("a"),{href:url,download:"geometry-progress.json"}).click();
  setTimeout(() => URL.revokeObjectURL(url),1000);
};
el("upload").onclick = () => el("uploadFile").click();
el("uploadFile").onchange = async event => {
  const file = event.target.files[0];
  event.target.value = "";
  el("importMessage").textContent = "";
  if (!file) return;
  if (file.size>2000000) { el("importMessage").textContent = "文件过大，请选择不超过 2 MB 的学习记录；原进度未修改。"; return; }
  const owner = account;
  try {
    let incoming = JSON.parse(await file.text());
    if (!incoming.marks || typeof incoming.marks !== "object" || Array.isArray(incoming.marks)) throw Error();
    incoming = migrateProgress(incoming);
    const clean = fresh();
    if (Number.isInteger(incoming.last) && bank[incoming.last-1]) clean.last = incoming.last;
    for (const [id, record] of Object.entries(incoming.marks)) {
      if (!/^[1-9]\d*$/.test(id) || !bank[Number(id)-1] || !record || typeof record !== "object") throw Error();
      clean.marks[id] = Object.fromEntries(["correct","mastered","favorite"].filter(k => typeof record[k] === "boolean").map(k => [k,record[k]]));
      if (typeof record.answered === "string" && Number.isFinite(Date.parse(record.answered))) {
        clean.marks[id].answered = new Date(record.answered).toISOString();
      }
    }
    if (account === owner && confirm("用导入文件替换当前账户的学习记录？")) { data=clean; persist(); resetFilters(); }
  } catch { alert("学习记录文件无效。"); }
};
try {
  const active = read("active",null);
  if (active && read("profile:"+active,null)) activate(active);
} catch { el("authMessage").textContent = "当前浏览器无法读取本地账户数据。"; }
