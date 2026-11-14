const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("web/app.js","utf8");
const grade = vm.runInNewContext(source.slice(source.indexOf("function rational"), source.indexOf('el("response").onsubmit')) + "\nequivalent");
const area = {answer:"84", unit:"cm²", answerType:"number"};
const half = {answer:"1/2", unit:"", answerType:"number"};
const ratio = {answer:"2:3", unit:"", answerType:"ratio"};
assert.equal(grade("84cm²", area),true);
assert.equal(grade("84 平方厘米", area),true);
assert.equal(grade("84cm", area),null);
assert.equal(grade("85", area),false);
assert.equal(grade("0.5", half),true);
assert.equal(grade("1/0", half),null);
assert.equal(grade("4：6", ratio),true);
assert.equal(grade("0:3", ratio),null);
console.log("8 grading cases passed");
