// Renders each flyer to PNG (and the letter menu to PDF).
// Run: node flyers/render.js   (needs Playwright + Chromium)
const path = require("path");
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
const jobs = [
  ["price-menu", 816, 1056, 3, true],
  ["social-post", 1080, 1080, 1],
  ["story", 1080, 1920, 1],
];
(async () => {
  const browser = await chromium.launch();
  for (const [name, w, h, scale, pdf] of jobs) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
    await page.goto("file://" + path.join(__dirname, name + ".html"), { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(__dirname, "export", name + ".png") });
    if (pdf) await page.pdf({ path: path.join(__dirname, "export", name + ".pdf"), width: "8.5in", height: "11in", printBackground: true });
    await page.close();
  }
  await browser.close();
})();
