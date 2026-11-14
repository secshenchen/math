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

自动化检查覆盖题库数量、数学复算、SVG 解析、外轮廓和顶点标签间距。仍有部分细分题型、结构重复、难度分布和逐图视觉审查待完善。移动端兼容性依据 WebKit 模拟测试，真机 Safari 本地文件的表现取决于系统打开方式和浏览器存储设置。
