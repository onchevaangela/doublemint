# Doublemint Detailing — Brand Kit

Open **`brand-guide.html`** in a browser for the full guidelines (logo, color, type, voice, usage).

## Logo files

| File | Use it for |
|---|---|
| `logo/*/doublemint-horizontal-dark` | **Primary.** Website header, flyers, anything on black |
| `logo/*/doublemint-horizontal-light` | White/light paper, invoices, letterhead |
| `logo/*/doublemint-stacked-*` | Square spaces: shirts, signs, the top of a price sheet |
| `logo/*/doublemint-mark-*` | Icon only: stickers, embroidery, watermark |
| `logo/*/doublemint-*-white` / `-black` | One color: vinyl decals, stamps, over photos |
| `logo/*/doublemint-app-icon` | Instagram / Facebook / Google profile picture |

`svg/` scales to any size (print, signs, vinyl). `png/` files are high-res with transparent backgrounds (Canva, social media).

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
Inter Display Black for headlines and prices, Inter Regular/Medium for body, Inter SemiBold with wide tracking for labels.

## Regenerating

```
pip install fonttools
python3 source/build.py   # logo SVGs
python3 source/guide.py   # brand-guide.html
```
