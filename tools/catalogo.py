#!/usr/bin/env python3
"""Genera el catálogo digital en PDF (A4) de Rial Arte.

Uso:  python3 tools/catalogo.py
Lee data/site.json, data/products.json y las fotos de docs/assets/img.
Crea catalogo/catalogo.html y lo imprime a PDF con Google Chrome (headless).
Resultado: docs/catalogo-rial-arte.pdf
"""
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
IMG = DOCS / "assets" / "img"
OUT_HTML = ROOT / "catalogo" / "catalogo.html"
OUT_PDF = DOCS / "catalogo-rial-arte.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

site = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
productos = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
esc = lambda s: html.escape(s, quote=True)
U = lambda p: (DOCS / p).as_uri()


def wa(producto=None):
    if producto:
        msg = (f"Hola, estoy interesado en este producto de Rial Arte: {producto['nombre']}. "
               f"¿Me das más información? {site['url_base']}producto/{producto['slug']}/")
    else:
        msg = "Hola, vi el catálogo de Rial Arte y quisiera más información."
    return f"https://wa.me/{site['whatsapp']}?text={quote(msg)}"


def foto(p, tam="m"):
    return f"assets/img/{p['fotos'][0]}-{tam}.jpg"


def es_vertical(p):
    with Image.open(DOCS / foto(p)) as im:
        return im.size[1] / im.size[0] > 1.1


def tarjeta(p):
    clase = "card vert" if es_vertical(p) else "card"
    return f"""<a class="{clase}" href="{esc(wa(p))}">
  <div class="ph"><img src="{U(foto(p))}" alt=""></div>
  <div class="tx"><span class="chip">{esc(p['categoria'])}</span>
  <h3>{esc(p['nombre'])}</h3><p>{esc(p['resumen'])}</p>
  <span class="ask">Pedir por WhatsApp →</span></div></a>"""


def tile_encargo():
    return f"""<a class="tile gold" href="{esc(wa())}"><b>¿Algo a tu medida?</b>
  <span>También tejemos y bordamos por encargo. Cuéntanos tu idea.</span><u>Escríbenos por WhatsApp</u></a>"""


def tile_ig():
    return f"""<a class="tile navy" href="{esc(site['instagram'])}"><b>Síguela en Instagram</b>
  <span>@rosairlandaalarconlaverde</span><u>Ver más trabajos</u></a>"""


def pagina_cat(titulo, subtitulo, items, cols, relleno, num):
    celdas = "".join(tarjeta(p) for p in items) + "".join(relleno)
    return f"""<section class="page cat cols{cols}">
  <header class="ph-head"><div><p class="eyebrow">Catálogo</p><h2>{esc(titulo)}</h2><p class="sub">{esc(subtitulo)}</p></div>
  <img src="{U('assets/logo.png')}" alt="" class="mini"></header>
  <div class="grid">{celdas}</div>
  <footer class="pie"><span>Rial Arte · {esc(site['whatsapp_visible'])}</span><span>{num}</span></footer></section>"""


def por_cat(*cats):
    return [p for c in cats for p in productos if p["categoria"] == c]


def main():
    sm = site["sobre_mi"]
    hero = [p for p in productos if p.get("destacado")][:3]
    portada = f"""<section class="page cover">
  <div class="cv-arts">
    <div class="arch a1"><img src="{U(foto(hero[0], 'l'))}" alt=""></div>
    <div class="arch a2"><img src="{U(foto(hero[1], 'l'))}" alt=""></div>
    <div class="arch a3"><img src="{U(foto(hero[2], 'l'))}" alt=""></div>
  </div>
  <div class="cv-text">
    <img src="{U('assets/logo.png')}" alt="Rial Arte" class="cv-logo">
    <p class="eyebrow">Catálogo digital · 2026</p>
    <h1>Hecho a mano,<br><em>puntada a puntada</em></h1>
    <p class="lead">Tejido · Crochet · Bordado · Bisutería</p>
    <a class="btn" href="{esc(wa())}">Escríbenos por WhatsApp · {esc(site['whatsapp_visible'])}</a>
    <p class="loc">{esc(site['ciudad'])}</p>
  </div></section>"""

    parrafos = "".join(f"<p>{esc(t)}</p>" for t in sm["parrafos"])
    momentos = site.get("momentos", {}).get("fotos", [])[:2]
    strip = "".join(
        f'<figure><img src="{U("assets/img/" + m["foto"] + "-m.jpg")}" alt=""><figcaption>{esc(m["texto"])}</figcaption></figure>'
        for m in momentos)
    sobre = f"""<section class="page about">
  <header class="ph-head"><div><p class="eyebrow">Sobre mí</p><h2>{esc(sm['nombre'])}</h2></div>
  <img src="{U('assets/logo.png')}" alt="" class="mini"></header>
  <div class="ab-body">
    <div class="ab-photo"><img src="{U('assets/' + sm['foto'])}" alt=""></div>
    <div class="ab-text">{parrafos}<blockquote>“{esc(sm['cita'])}”</blockquote></div>
  </div>
  <div class="strip">{strip}</div>
  <footer class="pie"><span>Rial Arte · {esc(site['whatsapp_visible'])}</span><span>2</span></footer></section>"""

    paginas = [
        pagina_cat("Ropa tejida", "Prendas únicas tejidas a mano", por_cat("Ropa tejida"), 2, [tile_encargo()], 3),
        pagina_cat("Hogar", "Toallas bordadas y cojines para decorar y regalar", por_cat("Hogar"), 2, [tile_encargo()], 4),
        pagina_cat("Bisutería", "Aretes en crochet, chaquira y macramé", por_cat("Bisutería"), 3,
                   [tile_encargo(), tile_ig()], 5),
        pagina_cat("Llaveros y accesorios", "Pequeños detalles para regalar", por_cat("Llaveros", "Accesorios"), 2,
                   [tile_ig()], 6),
    ]

    cierre = f"""<section class="page closing">
  <img src="{U('assets/logo.png')}" alt="Rial Arte" class="cv-logo">
  <h2>¿Cómo comprar?</h2>
  <ol class="steps">
    <li><b>1</b><h3>Elige</h3><p>Escoge los productos que más te gusten de este catálogo.</p></li>
    <li><b>2</b><h3>Escríbenos</h3><p>Toca “Pedir por WhatsApp” en el producto: el mensaje sale escrito.</p></li>
    <li><b>3</b><h3>Acordamos</h3><p>Hablamos de tallas, colores, precio, pago y envío directamente.</p></li>
  </ol>
  <a class="btn big" href="{esc(wa())}">WhatsApp {esc(site['whatsapp_visible'])}</a>
  <p class="contact">Instagram <a href="{esc(site['instagram'])}">@rosairlandaalarconlaverde</a><br>
  Web <a href="{esc(site['url_base'])}">{esc(site['url_base'].replace('https://', ''))}</a><br>
  {esc(site['ciudad'])}</p>
  <p class="thanks">Gracias por apoyar el trabajo hecho a mano.</p></section>"""

    css = (ROOT / "catalogo" / "catalogo.css").read_text(encoding="utf-8")
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Catálogo Rial Arte</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css}</style></head><body>{portada}{sobre}{''.join(paginas)}{cierre}</body></html>"""
    OUT_HTML.write_text(doc, encoding="utf-8")

    if not Path(CHROME).exists():
        sys.exit("No encuentro Google Chrome para generar el PDF")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=15000", f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri()],
                   check=True, capture_output=True)
    print(f"PDF generado: {OUT_PDF} ({OUT_PDF.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
