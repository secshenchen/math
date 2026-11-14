import base64
import gzip
from pathlib import Path

payload = Path("candidate/index.html").read_bytes()
packed = base64.b64encode(gzip.compress(payload, mtime=0)).decode()
prefix = """<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Math Geometry 离线候选版</title><p id="status">正在加载离线题库…</p><script>
(async () => {
  try {
    const bytes = Uint8Array.from(atob('"""
suffix = """'), ch => ch.charCodeAt(0));
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    const html = await new Response(stream).text();
    document.open();
    document.write(html);
    document.close();
  } catch {
    document.getElementById('status').textContent = '加载失败，请使用支持 DecompressionStream 的新版浏览器。';
  }
})();
</script></html>
"""
assert gzip.decompress(base64.b64decode(packed)) == payload
Path("candidate/offline.html").write_text(prefix + packed + suffix, encoding="utf-8")
