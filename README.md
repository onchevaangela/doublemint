# Double Mint Detailing

Website, booking, flyers and brand files.

**Going live:** follow [SETUP-GUIDE.md](SETUP-GUIDE.md) (Cloudflare hosting + Google Calendar booking).

| Folder | What's in it |
|---|---|
| `index.html`, `assets/` | The website. Prices, phones and services are in `assets/js/config.js`. |
| `booking/` | Online booking: requests go on one Google Calendar, owners confirm or decline, customers get emails at each step. |
| `flyers/` | Flyers as editable HTML + ready-to-use exports in `flyers/export/` (letter price menu PNG/PDF, Instagram post, story). Re-export: `node flyers/render.js` |
| `brand/logo-official/` | **The official logo** (transparent PNG). `dark` = white text for black backgrounds, `light` = black text for white paper, `icon` = car + sparkles for profile pictures, `dm` / `dm-icon` = the DM monogram (cut from the logo itself). |
| `brand/logo/` | Older logo concepts. Not in use. |

## Publish the site for free

GitHub → this repo → Settings → Pages → *Deploy from a branch* → `main` / root. The site appears at
`https://onchevaangela.github.io/doublemint/` (a custom domain can be added on the same page).
