// Exports brand/new-logo/*.svg to transparent PNGs. Run: node brand/source/export_new_logo_png.js
const fs = require("fs"), path = require("path");
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
const dir = path.join(__dirname, "..", "new-logo");
(async () => {
  const b = await chromium.launch();
  for (const f of fs.readdirSync(dir).filter((f) => f.endsWith(".svg"))) {
    const icon = f.includes("icon");
    const [w, h] = icon ? [1024, 1024] : [2400, 900];
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.setContent(`<style>html,body{margin:0;background:transparent}</style><img src="file://${path.join(dir, f)}" width="${w}" height="${h}">`);
    await p.waitForTimeout(200);
    await p.screenshot({ path: path.join(dir, f.replace(".svg", ".png")), omitBackground: true });
    await p.close();
  }
  await b.close();
})();
