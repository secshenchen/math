# Math Geometry｜几何模型专项练习

[打开 GitHub Pages](https://secshenchen.github.io/math/) · [下载离线 HTML](https://raw.githubusercontent.com/secshenchen/math/main/index.html)

12 个专题、5000 道题。每题包括题目图和答案图，题库内嵌共 10000 份 SVG。支持本地账户、答题批改、解析、随机出题、错题重练、收藏和打印。

下载根目录 `index.html` 后，用新版浏览器打开即可使用。页面需要支持 DecompressionStream 的浏览器。本地虚拟账户需要 Web Crypto 和可用的本地存储。账户和进度只能在建立它们的浏览器环境中读取，可以用学习记录导入和导出在设备间转移进度。请勿复用真实账户密码。

## 构建与验证

    python3 build.py
    python3 tools/package_candidate.py
    cmp index.html candidate/offline.html
    python3 -m unittest discover -s tests -v
    node tests/test_grading.cjs
    node tests/browser.cjs

浏览器测试依赖 Playwright，仅开发和持续集成时使用。根目录是与 `candidate/offline.html` 字节一致的完整离线应用。旧版入口可通过 Git 历史恢复。

## 审校范围
批量统计见 `candidate/AUDIT.json`，可用 `python3 tools/audit_bank.py` 重建。旧版记录按题干匹配转移；本次替换掉的题目记录将从新版进度中移除。

自动化检查覆盖题库数量、数学复算、SVG 解析、外轮廓和顶点标签间距。仍有部分细分题型、结构重复、难度分布和逐图视觉审查待完善。移动端兼容性依据 WebKit 模拟测试，真机 Safari 本地文件的表现取决于系统打开方式和浏览器存储设置。

本次补入平行四边形一半模型的四种约定构图、互补夹角、沙漏、金字塔及五种跨模型组合。模型名称用于本站分类，具体构图由题干定义。挑战题占 25%。`AUDIT.json` 中的题干形式按数字归一化统计，同类推理的数字变体仍有保留。

图形的自动验收包括 XML、顶点与渲染后的文字边界。若两题共享几何构图和条件，图下附各自的题干，题号以外的 SVG 正文可据此区分。自动验收和新模型的抽样目视检查有各自的验收范围。iPhone、iPad WebKit 模拟及 axe 扫描由 CI 运行，真机 Safari、VoiceOver 与逐图人工审校单独记录。
