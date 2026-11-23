#!/usr/bin/env python3
"""Genera UNA sola imagen con todos los productos de Rial Arte (para la feria, WhatsApp, etc.).

Uso:  python3 tools/catalogo_imagen.py                       # sin precios -> catalogo/catalogo-imagen.jpg
      python3 tools/catalogo_imagen.py --precios lista.csv   # con precios -> catalogo/catalogo-imagen-precios.jpg
El CSV (columnas Producto, Precio COP) NO se guarda en el repo: es un repositorio público.
Necesita Pillow y Google Chrome.
"""
import argparse
import csv
import html
import json
import subprocess
import sys
from math import ceil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = ROOT / "catalogo"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
COLS, W = 5, 2400
FOTO, ETQ, GAP, MARGEN = 400, 150, 36, 60
HEAD, FOOT = 400, 420

site = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
productos = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
esc = html.escape
ORDEN = ["Ropa tejida", "Hogar", "Bisutería", "Llaveros", "Accesorios"]
productos.sort(key=lambda p: ORDEN.index(p["categoria"]) if p["categoria"] in ORDEN else 99)  # estable

# Productos cuya foto es una prenda de cuerpo entero: se muestran completos, sin recortar
ENTERO = {"abrigo-multicolor-con-capucha", "conjunto-de-bebe-tejido", "conejo-amigurumi-con-zanahoria",
          "amigurumi-osos-y-conejo", "sueter-gatitos-y-flores"}


PRECIOS = {}


def cop(n):
    return "$" + f"{int(n):,}".replace(",", ".")


def tile(p):
    f = DOCS / "assets" / "img" / f"{p['fotos'][0]}-l.jpg"
    nueva = ROOT / "fotos-origen" / "feria" / f"{p['slug']}.jpg"   # foto nueva de la feria (tools/recortes_feria.py)
    if nueva.exists():
        f = nueva
    ajuste = "contain" if p["slug"] in ENTERO else "cover"
    precio = PRECIOS.get(p["nombre"])
    badge = f'<div class="pr">{cop(precio)}</div>' if precio else ""
    return (f'<div class="t"><div class="ph"><img style="object-fit:{ajuste}" src="{f.as_uri()}" alt="">{badge}</div>'
            f'<div class="tx"><span>{esc(p["categoria"])}</span><b>{esc(p["nombre"])}</b></div></div>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--precios', type=Path, help='CSV con columnas Producto y Precio COP')
    args = ap.parse_args()
    if args.precios:
        with open(args.precios, encoding='utf-8-sig') as fh:
            for r in csv.DictReader(fh):
                if str(r.get('Precio COP', '')).strip():
                    PRECIOS[r['Producto'].strip()] = int(str(r['Precio COP']).replace('.', '').replace('$', '').strip())
    nota = '<p class="nota">Precios unitarios en pesos colombianos (COP). No incluyen envío.</p>' if PRECIOS else ''
    nombre = 'catalogo-imagen-precios' if PRECIOS else 'catalogo-imagen'
    filas = ceil(len(productos) / COLS)
    ancho_t = (W - 2 * MARGEN - (COLS - 1) * GAP) // COLS
    alto = HEAD + filas * (FOTO + ETQ) + (filas - 1) * GAP + FOOT
    ig = site["instagram"].rstrip("/").split("/")[-1]
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--navy:#1f2a5a;--gold:#e8b838;--gold-soft:#f6e6b4;--cream:#fbf7ef;--muted:#666b80;--serif:'Cormorant Garamond',Georgia,serif;--sans:'Jost',sans-serif}}
html,body{{width:{W}px;height:{alto}px;font-family:var(--sans);color:var(--navy);overflow:hidden}}
body{{background:radial-gradient(circle at 90% 0%,var(--gold-soft),var(--cream) 38%);padding:0 {MARGEN}px;position:relative}}
.head{{height:{HEAD}px;display:flex;align-items:center;justify-content:center;gap:56px;text-align:left}}
.head img{{width:260px;height:260px}}
h1{{font-family:var(--serif);font-weight:600;font-size:150px;line-height:.95}}
.sub{{font-size:44px;letter-spacing:.1em;color:var(--muted);margin-top:18px}}
.sub2{{font-family:var(--serif);font-style:italic;font-size:54px;color:#c99a1c;margin-top:10px}}
.grid{{display:grid;grid-template-columns:repeat({COLS},{ancho_t}px);gap:{GAP}px}}
.t{{background:#fff;border-radius:34px;overflow:hidden;box-shadow:0 8px 26px rgba(31,42,90,.14);height:{FOTO + ETQ}px}}
.ph{{height:{FOTO}px;background:#f1ece0;position:relative}}
.pr{{position:absolute;right:18px;bottom:18px;background:var(--navy);color:#fff;font-weight:600;font-size:42px;padding:6px 26px;border-radius:40px;box-shadow:0 6px 16px rgba(0,0,0,.3);border:3px solid var(--gold)}}
.ph img{{width:100%;height:100%;display:block}}
.tx{{height:{ETQ}px;padding:20px 26px;display:flex;flex-direction:column;justify-content:center}}
.tx span{{align-self:flex-start;background:var(--gold-soft);color:#7a5a06;font-size:22px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:4px 16px;border-radius:30px;margin-bottom:10px}}
.tx b{{font-family:var(--serif);font-weight:600;font-size:38px;line-height:1.05}}
.foot{{position:absolute;left:{MARGEN}px;right:{MARGEN}px;bottom:50px;height:{FOOT - 90}px;background:var(--navy);border-radius:44px;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 90px}}
.foot h2{{font-family:var(--serif);font-weight:600;font-size:76px;line-height:1.05}}
.foot h2 em{{color:var(--gold)}}
.foot p{{font-size:46px;line-height:1.5;margin-top:14px}}
.foot p b{{font-weight:600;color:var(--gold)}}
.foot .nota{{font-size:40px;color:var(--gold-soft);font-style:italic;margin-top:10px}}
.foot .qr{{background:#fff;border-radius:26px;padding:16px;text-align:center}}
.foot .qr img{{width:210px;height:210px;display:block}}
.foot .qr small{{display:block;color:var(--navy);font-size:22px;font-weight:600;margin-top:6px}}
</style></head><body>
<div class="head"><img src="{(ROOT / 'emblema' / 'emblema-rial-arte-2000px-transparente.png').as_uri()}" alt="">
<div><h1>Rial Arte</h1><div class="sub">TEJIDO · CROCHET · BORDADO · BISUTERÍA</div><div class="sub2">Catálogo de productos hechos a mano</div></div></div>
<div class="grid">{''.join(tile(p) for p in productos)}</div>
<div class="foot"><div><h2>Pídelo por <em>WhatsApp</em></h2>
<p><b>{esc(site['whatsapp_visible'])}</b> · Instagram @{esc(ig)}<br>{esc(site['ciudad'])} · {esc(site['url_base'].replace('https://', ''))}</p>{nota}</div>
<div class="qr"><img src="{(ROOT / 'tarjeta' / 'qr-rial-arte.png').as_uri()}" alt=""><small>Catálogo web</small></div></div>
</body></html>"""
    OUT.mkdir(exist_ok=True)
    (OUT / f"{nombre}.html").write_text(doc, encoding="utf-8")
    png = OUT / f"{nombre}.png"
    if not Path(CHROME).exists():
        sys.exit("Falta Google Chrome")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={W},{alto}", "--virtual-time-budget=20000", f"--screenshot={png}",
                    (OUT / f"{nombre}.html").as_uri()], check=True, capture_output=True)
    with Image.open(png) as im:
        im.convert("RGB").save(OUT / f"{nombre}.jpg", quality=92, optimize=True)
    png.unlink()
    print(f"Imagen generada: {OUT / (nombre + '.jpg')} ({W}x{alto})")


if __name__ == "__main__":
    main()
