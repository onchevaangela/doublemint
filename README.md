# Double Mint Detailing

Website, booking, flyers and brand files.

| Folder | What's in it |
|---|---|
| `index.html`, `assets/` | The website. Prices, phones and services are in `assets/js/config.js`. |
| `booking/` | Online booking that adds appointments to one Google Calendar (works in Apple Calendar too). **Setup: [`booking/README.md`](booking/README.md)** |
| `flyers/` | Flyers as editable HTML + ready-to-use exports in `flyers/export/` (letter price menu PNG/PDF, Instagram post, story). Re-export: `node flyers/render.js` |
| `brand/new-logo/` | Vector (SVG) + transparent PNG recreation of the new brush logo. `full` has the black brush backing, `dark` for black backgrounds, `light` for white, `white`/`black` one-color, `icon` for profile pictures. |
| `brand/logo/` | Older logo concepts (superseded by the new logo). |

## Publish the site for free

GitHub → this repo → Settings → Pages → *Deploy from a branch* → `main` / root. The site appears at
`https://onchevaangela.github.io/doublemint/` (a custom domain can be added on the same page).
