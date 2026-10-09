"""Build ../brand-guide.html with the logo SVGs inlined. Run after build.py."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "..", "logo", "svg")
n = 0
def logo(name, h=None, w=None):
    global n; n += 1
    s = open(os.path.join(SVG, f"doublemint-{name}.svg")).read().strip()
    s = re.sub(r'id="([^"]+)"', lambda m: f'id="{m.group(1)}-{n}"', s)
    s = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{m.group(1)}-{n})', s)
    s = re.sub(r' width="\d+" height="\d+"', '', s, count=1)
    size = f'height:{h};width:auto' if h else f'width:{w};height:auto'
    return s.replace('<svg ', f'<svg style="{size};max-width:100%;display:block" ', 1)

colors = [
  ("Spearmint", "#A3E05A", "Primary accent. Highlights, prices, buttons, “MINT”.", "#0E1210"),
  ("Peppermint", "#4CAF50", "Second leaf. Supporting accent on dark.", "#0E1210"),
  ("Evergreen", "#2F7D4F", "Accent on light backgrounds; text-safe green.", "#FFFFFF"),
  ("Gloss Black", "#0E1210", "Main background. Like a fresh clear coat.", "#FFFFFF"),
  ("Graphite", "#1C221F", "Cards and panels on black.", "#FFFFFF"),
  ("Steel", "#9AA59E", "Secondary text on dark.", "#0E1210"),
  ("Foam", "#F3F7F0", "Light background, paper stock.", "#0E1210"),
]
swatches = "".join(f'''<div class="sw"><div class="chip" style="background:{hx};color:{fg}">{hx}</div>
<b>{nm}</b><span>{use}</span></div>''' for nm, hx, use, fg in colors)

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Doublemint Brand Guide</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0E1210;--panel:#1C221F;--line:#2a322d;--text:#fff;--muted:#9AA59E;--accent:#A3E05A;--foam:#F3F7F0;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 Inter,system-ui,sans-serif}}
main{{max-width:1080px;margin:0 auto;padding:0 16px 80px}}
header{{padding:72px 0 56px;border-bottom:1px solid var(--line)}}
h1{{font-weight:900;letter-spacing:-.02em;font-size:clamp(32px,6vw,56px);line-height:1.05;margin:40px 0 12px}}
h1 em{{font-style:normal;color:var(--accent)}}
h2{{font-size:13px;letter-spacing:.24em;text-transform:uppercase;color:var(--accent);margin:0 0 6px;font-weight:600}}
h3{{font-size:28px;font-weight:900;letter-spacing:-.01em;margin:0 0 16px}}
section{{padding:64px 0;border-bottom:1px solid var(--line)}}
p{{color:#d5ddd8;max-width:640px}}.muted{{color:var(--muted)}}
.grid{{display:grid;gap:16px}}.g2{{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}}
.g3{{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}}
.tile{{border-radius:16px;padding:40px 28px;display:flex;align-items:center;justify-content:center;min-height:200px;border:1px solid var(--line)}}
.dark{{background:var(--bg)}}.panel{{background:var(--panel)}}.light{{background:var(--foam)}}.lime{{background:#A3E05A}}.ever{{background:#2F7D4F}}
.cap{{font-size:13px;color:var(--muted);margin-top:8px}}
.sw .chip{{height:120px;border-radius:14px;display:flex;align-items:flex-end;padding:12px;font:600 13px Inter;letter-spacing:.04em;border:1px solid var(--line)}}
.sw b{{display:block;margin-top:10px}}.sw span{{font-size:14px;color:var(--muted)}}
.sw7{{grid-template-columns:repeat(auto-fit,minmax(124px,1fr))}}
.card>svg,.ig>svg{{align-self:flex-start}}.ig.ctr>svg{{align-self:center}}
.type-xl{{font-weight:900;font-size:clamp(40px,8vw,88px);letter-spacing:-.02em;line-height:1}}
.spaced{{letter-spacing:.42em;text-transform:uppercase;font-weight:600;color:var(--muted)}}
.do,.dont{{border-radius:16px;padding:20px;border:1px solid var(--line);background:var(--panel)}}
.do h4,.dont h4{{margin:0 0 10px;font-size:14px;letter-spacing:.12em;text-transform:uppercase}}
.do h4{{color:var(--accent)}}.dont h4{{color:#ff8a7a}}
ul{{margin:0;padding-left:18px;color:#d5ddd8}}li{{margin:4px 0}}
.card{{aspect-ratio:3.5/2;border-radius:12px;padding:22px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 20px 50px rgba(0,0,0,.4)}}
.card .n{{font-weight:700;font-size:15px}}.card .r{{font-size:12px;color:var(--muted)}}
.card .ph{{font-weight:600;font-size:14px;letter-spacing:.02em}}
.ig{{aspect-ratio:1;border-radius:12px;padding:28px;display:flex;flex-direction:column;justify-content:space-between;background:var(--bg);border:1px solid var(--line)}}
.price{{display:grid;grid-template-columns:1fr auto auto auto;gap:6px 18px;align-items:baseline;font-size:14px}}
.price .h{{color:var(--muted);font-size:11px;letter-spacing:.14em;text-transform:uppercase}}
.price .v{{font-weight:900;color:var(--accent);font-size:18px}}
.clear{{position:relative;padding:36px;outline:1px dashed #A3E05A88;outline-offset:-1px}}
.spec{{font-size:14px;color:var(--muted)}}
.bigtag{{font-weight:900;font-size:clamp(24px,4vw,36px);line-height:1.15;letter-spacing:-.01em}}
.bigtag span{{color:var(--accent)}}
</style></head><body><main>

<header>
{logo("horizontal-dark", h="72px")}
<h1>Fresh look.<br><em>Clean finish.</em></h1>
<p>Brand guidelines for Doublemint Detailing. The new identity drops the busy cartoon badge for one simple mark that reads at any size, on a business card, a shirt, a van door or an Instagram avatar.</p>
</header>

<section>
<h2>01 · The mark</h2><h3>Two leaves and one shine</h3>
<div class="grid g2">
<div class="tile dark">{logo("mark-dark", h="180px")}</div>
<div><p>Two mint leaves are the <b>double mint</b>. The sparkle between them is the shine on a freshly detailed car. The leaves are two different greens for two levels of service, inside and out.</p>
<p>The shape is flat and symmetrical on purpose. It has no gradients, glow, bevels or clip-art, so it prints in one color, embroiders cleanly and can be cut from vinyl.</p></div>
</div>
</section>

<section>
<h2>02 · Logo lockups</h2><h3>Use the right version</h3>
<div class="grid g2">
<div><div class="tile dark">{logo("horizontal-dark", w="100%")}</div><div class="cap">Primary · horizontal on dark</div></div>
<div><div class="tile light">{logo("horizontal-light", w="100%")}</div><div class="cap">Horizontal on light</div></div>
<div><div class="tile dark">{logo("stacked-dark", h="170px")}</div><div class="cap">Stacked · square spaces, shirts, signage</div></div>
<div><div class="tile light">{logo("stacked-light", h="170px")}</div><div class="cap">Stacked on light</div></div>
<div><div class="tile ever">{logo("horizontal-white", w="100%")}</div><div class="cap">One-color white · photos, green, vinyl</div></div>
<div><div class="tile lime">{logo("horizontal-black", w="100%")}</div><div class="cap">One-color black · stamps, receipts, lime</div></div>
</div>
<div class="grid g3" style="margin-top:16px">
<div><div class="tile panel">{logo("app-icon", h="140px")}</div><div class="cap">App / social avatar</div></div>
<div class="tile panel" style="flex-direction:column;align-items:flex-start;justify-content:center">
<div class="spec"><b style="color:#fff">Clear space</b><br>Leave empty space around the logo at least the height of the “D” in DOUBLEMINT.</div>
<div class="spec" style="margin-top:14px"><b style="color:#fff">Minimum size</b><br>Horizontal: 120&nbsp;px / 1.25&nbsp;in wide.<br>Mark alone: 24&nbsp;px / 0.3&nbsp;in.</div></div>
<div class="tile dark"><div class="clear">{logo("mark-dark", h="90px")}</div></div>
</div>
</section>

<section>
<h2>03 · Color</h2><h3>Black, chrome and mint</h3>
<p>Mostly Gloss Black with Spearmint as the accent. That keeps the look you already have on the flyer, just calmer. Aim for about 70% black, 20% neutrals and 10% green.</p>
<div class="grid sw7" style="margin-top:24px">{swatches}</div>
</section>

<section>
<h2>04 · Typography</h2><h3>Inter, used two ways</h3>
<div class="grid g2">
<div class="tile panel" style="flex-direction:column;align-items:flex-start">
<div class="type-xl">DETAILING</div><div class="cap">Inter Display Black · headlines, prices, logo</div></div>
<div class="tile panel" style="flex-direction:column;align-items:flex-start">
<div class="spaced">Professional Services</div>
<p style="margin:14px 0 0">Inter Regular / Medium for body text, service lists and contact details. It is free on Google Fonts and works in Canva.</p>
<div class="cap">Inter SemiBold, +0.4em tracking · labels, taglines</div></div>
</div>
<p class="muted" style="margin-top:20px">Stick to these two styles. Leave out script fonts, italic sports fonts, 3D text and outlines.</p>
</section>

<section>
<h2>05 · Voice</h2><h3>Confident, clean, friendly</h3>
<div class="grid g3">
<div class="tile panel"><div class="bigtag">Fresh look.<br><span>Clean finish.</span></div></div>
<div class="tile panel"><div class="bigtag">Detailed<br><span>twice as fresh.</span></div></div>
<div class="tile panel"><div class="bigtag">Quality you see.<br><span>Details you feel.</span></div></div>
</div>
<p style="margin-top:20px">Keep it short and plain. Use real prices and real photos of your own work. Leave out the hype words (“ultimate”, “insane”) and use one exclamation mark at most.</p>
</section>

<section>
<h2>06 · Do &amp; don’t</h2><h3>Keep the logo intact</h3>
<div class="grid g2">
<div class="do"><h4>Do</h4><ul>
<li>Use the files in <code>logo/</code> exactly as supplied</li>
<li>Use the white version over photos</li>
<li>Put the logo on Gloss Black, Foam or Evergreen</li>
<li>Scale it proportionally</li></ul></div>
<div class="dont"><h4>Don’t</h4><ul>
<li>Add glow, gradients, shadows, bevels or outlines</li>
<li>Put cars, sprayers or bubbles back around it</li>
<li>Stretch it, rotate it or recolor the leaves</li>
<li>Put the color logo on a busy photo</li></ul></div>
</div>
</section>

<section>
<h2>07 · In use</h2><h3>How it looks out in the world</h3>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(min(420px,100%),1fr))">
<div class="card" style="background:#0E1210;border:1px solid var(--line)">{logo("horizontal-dark", h="44px")}
<div><div class="n">Exterior · Interior · Full Detail</div><div class="ph" style="margin-top:8px">862 238 0550 <span class="muted">·</span> 219 786 9863</div><div class="r">Appointments recommended · walk-ins welcome</div></div></div>
<div class="card" style="background:#A3E05A;color:#0E1210">{logo("mark-black", h="44px")}
<div><div class="n" style="font-size:22px;font-weight:900">Fresh look.<br>Clean finish.</div><div class="r" style="color:#0E1210;opacity:.7;margin-top:6px">Doublemint Detailing</div></div></div>
<div class="ig">{logo("stacked-dark", h="90px")}
<div class="price"><span class="h">Package</span><span class="h">Car</span><span class="h">SUV</span><span class="h">Truck</span>
<span>Exterior</span><span class="v">$60</span><span class="v">$80</span><span class="v">$100</span>
<span>Interior</span><span class="v">$200</span><span class="v">$240</span><span class="v">$240</span>
<span>Full detail</span><span class="v">$230</span><span class="v">$260</span><span class="v">$280</span></div></div>
<div class="ig ctr" style="background:#2F7D4F;border:0;align-items:center;justify-content:center">{logo("stacked-white", h="160px")}</div>
</div>
</section>

<p class="muted" style="margin-top:40px;font-size:14px">The logo files are in <code>brand/logo/svg</code> (for print and web) and <code>brand/logo/png</code> (transparent, high resolution). To regenerate them, run <code>brand/source/build.py</code>.</p>
</main></body></html>
'''
open(os.path.join(HERE, "..", "brand-guide.html"), "w").write(html)
