# Math Geometry 开发候选版

本目录包含自包含的离线候选应用。根目录入口仍为仓库现有版本。

运行构建与自动化检查。

    python3 build.py
    python3 -m unittest discover -s tests -v
    node --check web/app.js
    node tests/test_grading.cjs

候选题库含 5000 个连续题号、12 个专题配额、5000 份题目 SVG 和 5000 份答案 SVG。批量测试覆盖文本完全重复、必需字段、SVG XML 解析、视口、标签锚点及显式答案标签。构建还比较了部分面积题的公式结果和坐标面积。

正式验收仍需补齐全部细分题型、减少数值变体的结构重复、按真实推理难度重标、逐题独立审校、检查标签碰撞和导出打印，并跑完浏览器功能清单。当前账户与进度功能属于候选实现，浏览器兼容性待核验。

GitHub 上的候选入口为 `candidate/offline.html`。先执行上面的构建命令，再执行
`python3 tools/package_candidate.py`，可生成相同的 gzip 内嵌版。解压后的页面与
`candidate/index.html` 字节一致。浏览器需支持 DecompressionStream。源码与测试
可重建未压缩版本。

本轮加入共同底边等积、平行四边形中点分割及梯形蝴蝶与中点组合。
4,995 道生成题已通过坐标和答案一致性复算，原 5 道样例继续由独立用例核对。
数字归一后的措辞形式为 57 种，最大一组 400 道。细分题型覆盖、结构重复、
SVG 标签遮挡和其他图文标注检查仍待完成。浏览器脚本覆盖断网条件下的注册、
账户隔离、答题和小屏检查。本地 Chromium 因进程套接字权限无法启动。
