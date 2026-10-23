# Doublemint Detailing — Brand Kit

Open **`brand-guide.html`** in a browser for the full guidelines (logo, color, type, voice, usage).

## Logo files

| File | Use it for |
|---|---|
| `logo/*/doublemint-stacked-*` | **Primary.** Wheel over the name: shirts, flyers, signs, price sheets |
| `logo/*/doublemint-horizontal-dark` | Wide spaces on black: website header, banners, van side |
| `logo/*/doublemint-horizontal-light` | White/light paper, invoices, letterhead |
| `logo/*/doublemint-mark-*` | Wheel only: stickers, windshield decals, watermark |
| `logo/*/doublemint-*-white` / `-black` | One color: vinyl decals, stamps, over photos |
| `logo/*/doublemint-app-icon` | Instagram / Facebook / Google profile picture |

`svg/` scales to any size (print, signs, vinyl). `png/` files are high-res with transparent backgrounds (Canva, social media).

## Classic logo (car swoosh)

`logo/classic/` is a clean vector redraw of the original car + brush-lettering logo: same layout, car, sparkles, and the original lettering traced from `source/original.jpg`, with smooth strokes and solid fills.

| File | Use it for |
|---|---|
| `doublemint-classic-dark` | On black, background included (social posts, banners) |
| `doublemint-classic-transparent` | White + mint, no background: over dark photos, black shirts |
| `doublemint-classic-light` | Black + green, no background: white paper, invoices |
| `doublemint-classic-white` / `-black` | One color: vinyl, stamps, embroidery |

Each comes as `.svg` (any size) and a 3000px-wide `.png`. Rebuild with `python3 source/trace_text.py` (re-traces the lettering) then `python3 source/classic.py`.

## Other mark options

`logo/options/` has the same logo with a **windshield + wiper** or a **steering wheel** instead of the wheel (see `options-comparison.png`). To switch the main files to one of them: `DM_MARK=windshield python3 source/build.py` (or `steering`).

## Palette

| Name | Hex | Role |
|---|---|---|
| Spearmint | `#A3E05A` | Primary accent |
| Peppermint | `#4CAF50` | Secondary accent on dark |
| Evergreen | `#2F7D4F` | Accent on light, text-safe green |
| Gloss Black | `#0E1210` | Main background |
| Graphite | `#1C221F` | Panels / cards |
| Steel | `#9AA59E` | Secondary text |
| Foam | `#F3F7F0` | Light background |

## Type

[Inter](https://fonts.google.com/specimen/Inter), free on Google Fonts and Canva.
Inter Display Black Italic for headlines and prices, Inter Regular/Medium for body, Inter SemiBold with wide tracking for labels.

## Regenerating

```
pip install fonttools
python3 source/build.py   # logo SVGs
python3 source/guide.py   # brand-guide.html
```
