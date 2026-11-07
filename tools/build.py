#!/usr/bin/env python3
"""Genera el sitio estático de Rial Arte en ./docs

Uso:
    python3 tools/build.py --fotos "/ruta/a/RIAL-ARTE"        # optimiza fotos + genera HTML
    python3 tools/build.py                                    # solo regenera HTML (usa fotos ya optimizadas)

Los datos viven en data/site.json y data/products.json.
"""
import argparse
import html
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
IMG = DOCS / "assets" / "img"
CATEGORIAS = ["Ropa tejida", "Hogar", "Llaveros", "Bisutería", "Accesorios"]


def optimizar_fotos(origenes: list, productos: list, extras=()) -> None:
    from PIL import Image, ImageOps

    IMG.mkdir(parents=True, exist_ok=True)
    usadas = {f for p in productos for f in p["fotos"]} | set(extras)
    for nombre in sorted(usadas):
        src = next((o / f"{nombre}{ext}" for o in origenes
                    for ext in (".JPG", ".jpg", ".jpeg", ".png") if (o / f"{nombre}{ext}").exists()), None)
        if not src:
            sys.exit(f"No encuentro la foto {nombre} en {origenes}")
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            for etiqueta, lado in (("l", 1400), ("m", 640)):
                c = im.copy()
                c.thumbnail((lado, lado), Image.LANCZOS)
                c.save(IMG / f"{nombre}-{etiqueta}.jpg", "JPEG", quality=82, optimize=True,
                       progressive=True)
    logo = next((l for o in origenes for l in o.glob("Logo.png")), None)
    if logo:
        with Image.open(logo) as im:
            im.save(DOCS / "assets" / "logo.png", optimize=True)
            im.resize((64, 55), Image.LANCZOS).save(DOCS / "assets" / "favicon.png")
    print(f"Fotos optimizadas: {len(usadas)}")


def tamanio(nombre: str, etiqueta: str):
    from PIL import Image
    with Image.open(IMG / f"{nombre}-{etiqueta}.jpg") as im:
        return im.size


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def wa_link(site: dict, producto: dict | None = None, pagina: str = "") -> str:
    if producto:
        url = site["url_base"] + f"producto/{producto['slug']}/"
        msg = (f"Hola, estoy interesado en este producto de Rial Arte: "
               f"{producto['nombre']}. ¿Me das más información? {url}")
    else:
        msg = "Hola, vi tu página de Rial Arte y quisiera más información."
    return f"https://wa.me/{site['whatsapp']}?text={quote(msg)}"


WA_PATH = ("M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z")
WA_ICON = f'<svg viewBox="0 0 24 24" aria-hidden="true" width="22" height="22" fill="currentColor"><path d="{WA_PATH}"/></svg>'


def head(site, titulo, desc, rel, canonical, imagen, extra=""):
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<link rel="icon" href="{rel}assets/favicon.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(site['url_base'] + imagen)}">
<meta property="og:locale" content="es_CO">
<meta name="theme-color" content="#1f2a5a">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/style.css">
{extra}
</head>"""


def header(site, rel):
    return f"""<header class="topbar">
  <a class="brand" href="{rel or './'}" aria-label="Rial Arte, inicio">
    <img src="{rel}assets/logo.png" alt="" width="60" height="52"><span>{esc(site['nombre'])}</span>
  </a>
  <nav aria-label="Principal">
    <a href="{rel}index.html#catalogo">Catálogo</a>
    <a href="{rel}index.html#sobre-mi">Sobre mí</a>
    <a href="{rel}index.html#momentos">Momentos</a>
    <a href="{rel}index.html#redes">Redes</a>
    <a href="{rel}index.html#como-comprar">Cómo comprar</a>
    <a class="nav-wa" href="{wa_link(site)}" target="_blank" rel="noopener">{WA_ICON}<span>WhatsApp</span></a>
  </nav>
</header>"""


def footer(site, rel):
    ig = (f'<a href="{esc(site["instagram"])}" target="_blank" rel="noopener">Instagram</a>'
          if site.get("instagram") else "")
    return f"""<footer class="footer">
  <img src="{rel}assets/logo.png" alt="Rial Arte" width="130" height="112">
  <p class="footer-lema">{esc(site['lema'])}</p>
  <p class="footer-links"><a href="{wa_link(site)}" target="_blank" rel="noopener">WhatsApp {esc(site['whatsapp_visible'])}</a> {ig}</p>
  <p class="footer-small">© {esc(site['nombre'])} · Hecho a mano en {esc(site['ciudad'])}</p>
</footer>
<a class="wa-float" href="{wa_link(site)}" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">{WA_ICON}</a>"""


def card(p, rel):
    foto = p["fotos"][0]
    w, h = tamanio(foto, "m")
    clase = "card-media portrait" if w / h < 1.1 else "card-media"
    return f"""<a class="card" data-cat="{esc(p['categoria'])}" href="{rel}producto/{p['slug']}/">
  <div class="{clase}" style="--bg:url('{rel}assets/img/{foto}-m.jpg')">
    <img src="{rel}assets/img/{foto}-m.jpg" alt="{esc(p['nombre'])}" width="{w}" height="{h}" loading="lazy">
  </div>
  <div class="card-body">
    <span class="chip">{esc(p['categoria'])}</span>
    <h3>{esc(p['nombre'])}</h3>
    <p>{esc(p['resumen'])}</p>
    <span class="card-cta">Ver detalles <b aria-hidden="true">→</b></span>
  </div>
</a>"""


def pagina_inicio(site, productos):
    rel = ""
    destacados = [p for p in productos if p.get("destacado")]
    fotos_js = json.dumps([{"s": p["slug"], "n": p["nombre"], "f": p["fotos"][0]} for p in productos],
                          ensure_ascii=False)
    hero = [p["fotos"][0] for p in destacados[:3]] or [productos[0]["fotos"][0]] * 3
    cats = "".join(
        f'<button class="filtro" data-cat="{esc(c)}">{esc(c)}</button>'
        for c in CATEGORIAS if any(p["categoria"] == c for p in productos))
    sm = site["sobre_mi"]
    def _p(t):
        t = esc(t)
        for k, u in sm.get("enlaces", {}).items():
            t = t.replace(esc(k), f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(k)}</a>')
        return f"<p>{t}</p>"
    parrafos = "".join(_p(t) for t in sm["parrafos"])
    foto_sm = (f'<img src="assets/{esc(sm["foto"])}" alt="{esc(sm["nombre"])}" loading="lazy">'
               if sm.get("foto") else
               f'<div class="sm-logo"><img src="assets/logo.png" alt="Logo Rial Arte" width="220" height="189"></div>')
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "LocalBusiness", "name": site["nombre"],
        "description": site["descripcion"], "url": site["url_base"],
        "image": site["url_base"] + "assets/logo.png",
        "telephone": "+" + site["whatsapp"]}, ensure_ascii=False)
    vd = site.get("video")
    video_html = ""
    if vd:
        video_html = (f'<section id="video" class="section video"><div class="section-head">'
                      f'<p class="eyebrow">Video</p><h2>{esc(vd["titulo"])}</h2><p>{esc(vd["texto"])}</p></div>'
                      f'<div class="video-wrap"><video controls playsinline preload="none" poster="{esc(vd["poster"])}">'
                      f'<source src="{esc(vd["archivo"])}" type="video/mp4">Tu navegador no puede reproducir el video.'
                      f'</video></div></section>')
    mo = site.get("momentos")
    momentos_html = ""
    if mo and mo.get("fotos"):
        items = ""
        for m in mo["fotos"]:
            w, h = tamanio(m["foto"], "m")
            items += (f'<a class="momento" href="assets/img/{m["foto"]}-l.jpg" data-full="assets/img/{m["foto"]}-l.jpg" '
                      f'data-cap="{esc(m["texto"])}"><img src="assets/img/{m["foto"]}-m.jpg" alt="{esc(m["texto"])}" '
                      f'width="{w}" height="{h}" loading="lazy"><span>{esc(m["texto"])}</span></a>')
        momentos_html = (f'<section id="momentos" class="section momentos"><div class="section-head">'
                         f'<p class="eyebrow">Galería</p><h2>{esc(mo["titulo"])}</h2><p>{esc(mo["texto"])}</p></div>'
                         f'<div class="galeria-momentos">{items}</div></section>')
    rd = site.get("redes")
    redes_html = ""
    ig_btn = (f'<p class="ig-cta"><a class="btn btn-ghost" href="{esc(site["instagram"])}" target="_blank" rel="noopener">Ver su Instagram</a></p>'
              if site.get("instagram") else "")
    if rd and rd.get("posts"):
        embeds = "".join(
            f'<blockquote class="instagram-media" data-instgrm-permalink="{esc(u)}" data-instgrm-version="14">'
            f'<a href="{esc(u)}" target="_blank" rel="noopener">Ver publicación en Instagram</a></blockquote>'
            for u in rd["posts"])
        redes_html = (f'<section id="redes" class="section redes"><div class="section-head">'
                      f'<p class="eyebrow">Redes</p><h2>{esc(rd["titulo"])}</h2><p>{esc(rd["texto"])}</p></div>'
                      f'<div class="embeds">{embeds}</div>{ig_btn}</section>'
                      '<script async src="https://www.instagram.com/embed.js"></script>')
    out = head(site, f"{site['nombre']} · {site['lema']}", site["descripcion"], rel,
               site["url_base"], f"assets/img/{hero[0]}-l.jpg",
               f'<script type="application/ld+json">{jsonld}</script>')
    out += f"""
<body>
{header(site, rel)}
<main>
<section class="hero">
  <div class="hero-text">
    <p class="eyebrow">Tejido · Crochet · Bordado · Bisutería</p>
    <h1>Piezas únicas hechas <em>a mano</em>, puntada a puntada</h1>
    <p class="lead">{esc(site['descripcion'])}</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="#catalogo">Ver catálogo</a>
      <a class="btn btn-ghost" href="{wa_link(site)}" target="_blank" rel="noopener">{WA_ICON} Escribir por WhatsApp</a>
    </div>
  </div>
  <div class="hero-art" id="hero-art">
    <a class="arch a1" href="producto/{destacados[0]['slug'] if destacados else productos[0]['slug']}/"><img src="assets/img/{hero[0]}-l.jpg" alt=""></a>
    <a class="arch a2" href="producto/{destacados[1 % len(destacados)]['slug'] if destacados else productos[0]['slug']}/"><img src="assets/img/{hero[1 % len(hero)]}-m.jpg" alt=""></a>
    <a class="arch a3" href="producto/{destacados[2 % len(destacados)]['slug'] if destacados else productos[0]['slug']}/"><img src="assets/img/{hero[2 % len(hero)]}-m.jpg" alt=""></a>
  </div>
  <script>
  /* Cada visita muestra tres fotos distintas del catálogo, elegidas al azar */
  (function(){{var f={fotos_js};var a=document.querySelectorAll('#hero-art .arch');
  for(var i=f.length-1;i>0;i--){{var j=Math.floor(Math.random()*(i+1)),t=f[i];f[i]=f[j];f[j]=t;}}
  a.forEach(function(el,k){{var p=f[k];if(!p)return;el.href='producto/'+p.s+'/';el.setAttribute('aria-label',p.n);
  var im=el.querySelector('img');im.alt=p.n;im.src='assets/img/'+p.f+(k===0?'-l':'-m')+'.jpg';}});}})();
  </script>
</section>

<section class="valores" aria-label="Por qué Rial Arte">
  <div><b>Hecho a mano</b><span>Cada pieza se teje y se borda sin prisa</span></div>
  <div><b>Pieza única</b><span>Colores y detalles que no encuentras en tiendas</span></div>
  <div><b>Trato directo</b><span>Hablas con quien la hace, por WhatsApp</span></div>
</section>

<section id="catalogo" class="section">
  <div class="section-head">
    <p class="eyebrow">Catálogo</p>
    <h2>Nuestros productos</h2>
    <p>Toca un producto para ver sus fotos y detalles. Si te enamora, te escribimos por WhatsApp.</p>
  </div>
  <div class="filtros" role="group" aria-label="Filtrar por categoría">
    <button class="filtro active" data-cat="todos">Todos</button>{cats}
  </div>
  <div class="grid">
{chr(10).join(card(p, rel) for p in productos)}
  </div>
</section>

<section id="sobre-mi" class="section sobre">
  <div class="sobre-foto">{foto_sm}</div>
  <div class="sobre-texto">
    <p class="eyebrow">{esc(sm['titulo'])}</p>
    <h2>{esc(sm['nombre'])}</h2>
    {parrafos}
    <blockquote>“{esc(sm['cita'])}”</blockquote>
  </div>
</section>

{video_html}
{momentos_html}
{redes_html}
<section id="como-comprar" class="section como">
  <div class="section-head">
    <p class="eyebrow">Comprar es fácil</p>
    <h2>Cómo comprar</h2>
  </div>
  <ol class="pasos">
    <li><span>1</span><h3>Elige</h3><p>Recorre el catálogo y abre el producto que te guste.</p></li>
    <li><span>2</span><h3>Escríbenos</h3><p>Toca “Comprar por WhatsApp”: el mensaje ya sale escrito con el producto.</p></li>
    <li><span>3</span><h3>Acordamos</h3><p>Hablamos de tallas, colores, precio, pago y envío directamente.</p></li>
  </ol>
  <div class="cta-final">
    <h2>¿Buscas algo a tu medida?</h2>
    <p>También tejemos y bordamos por encargo. Cuéntanos tu idea.</p>
    <a class="btn btn-primary" href="{wa_link(site)}" target="_blank" rel="noopener">{WA_ICON} Hablemos por WhatsApp</a>
  </div>
</section>
</main>
{footer(site, rel)}
<script src="assets/app.js"></script>
</body>
</html>
"""
    return out


def pagina_producto(site, p, productos):
    rel = "../../"
    fotos = p["fotos"]
    principal = fotos[0]
    w, h = tamanio(principal, "l")
    url = site["url_base"] + f"producto/{p['slug']}/"
    thumbs = ""
    if len(fotos) > 1:
        thumbs = '<div class="thumbs" role="tablist" aria-label="Más fotos">' + "".join(
            f'<button class="thumb{" active" if i == 0 else ""}" data-src="{rel}assets/img/{f}-l.jpg" '
            f'aria-label="Foto {i + 1}"><img src="{rel}assets/img/{f}-m.jpg" alt="" loading="lazy"></button>'
            for i, f in enumerate(fotos)) + "</div>"
    detalles = "".join(f"<li>{esc(d)}</li>" for d in p["detalles"])
    relacionados = [q for q in productos if q["categoria"] == p["categoria"] and q["slug"] != p["slug"]]
    relacionados += [q for q in productos if q["categoria"] != p["categoria"] and q["slug"] != p["slug"]]
    relacionados = relacionados[:3]
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Product", "name": p["nombre"],
        "description": p["descripcion"], "category": p["categoria"],
        "image": [site["url_base"] + f"assets/img/{f}-l.jpg" for f in fotos],
        "brand": {"@type": "Brand", "name": site["nombre"]}, "url": url}, ensure_ascii=False)
    out = head(site, f"{p['nombre']} · {site['nombre']}", p["resumen"], rel, url,
               f"assets/img/{principal}-l.jpg", f'<script type="application/ld+json">{jsonld}</script>')
    out += f"""
<body class="detalle-page">
{header(site, rel)}
<main class="detalle">
  <nav class="migas" aria-label="Ruta"><a href="{rel}index.html">Inicio</a> / <a href="{rel}index.html#catalogo">Catálogo</a> / <span>{esc(p['nombre'])}</span></nav>
  <div class="detalle-grid">
    <div class="galeria">
      <div class="galeria-main"><img id="foto-principal" src="{rel}assets/img/{principal}-l.jpg" alt="{esc(p['nombre'])}" width="{w}" height="{h}"></div>
      {thumbs}
    </div>
    <div class="info">
      <span class="chip">{esc(p['categoria'])}</span>
      <h1>{esc(p['nombre'])}</h1>
      <p class="precio">Precio: consúltalo por WhatsApp</p>
      <p class="desc">{esc(p['descripcion'])}</p>
      <ul class="detalles">{detalles}</ul>
      <a class="btn btn-primary btn-xl" href="{wa_link(site, p)}" target="_blank" rel="noopener">{WA_ICON} Comprar por WhatsApp</a>
      <p class="nota">Al tocar el botón se abre WhatsApp con este mensaje ya escrito: “Hola, estoy interesado en este producto…”. Tallas, colores y envío se acuerdan por el chat.</p>
    </div>
  </div>
  <section class="relacionados">
    <h2>También te puede gustar</h2>
    <div class="grid">
{chr(10).join(card(q, rel) for q in relacionados)}
    </div>
  </section>
</main>
{footer(site, rel)}
<script src="{rel}assets/app.js"></script>
</body>
</html>
"""
    return out


def sitemap(site, productos):
    urls = [site["url_base"]] + [site["url_base"] + f"producto/{p['slug']}/" for p in productos]
    cuerpo = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{cuerpo}\n</urlset>\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fotos", type=Path, nargs="+", help="Carpeta(s) con las fotos originales")
    args = ap.parse_args()

    site = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
    productos = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    if args.fotos:
        optimizar_fotos(args.fotos + [ROOT / "fotos-origen"], productos,
                        [m["foto"] for m in site.get("momentos", {}).get("fotos", [])])

    prod_dir = DOCS / "producto"
    if prod_dir.exists():
        shutil.rmtree(prod_dir)
    (DOCS / "index.html").write_text(pagina_inicio(site, productos), encoding="utf-8")
    for p in productos:
        d = prod_dir / p["slug"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(pagina_producto(site, p, productos), encoding="utf-8")
    fotos = [{"n": p["nombre"], "s": p["slug"], "img": f"assets/img/{f}-l.jpg"}
             for p in productos for f in p["fotos"]]
    (DOCS / "fotos.json").write_text(json.dumps(fotos, ensure_ascii=False), encoding="utf-8")
    (DOCS / "sitemap.xml").write_text(sitemap(site, productos), encoding="utf-8")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site['url_base']}sitemap.xml\n")
    (DOCS / ".nojekyll").write_text("")
    print(f"Sitio generado: {len(productos)} productos")


if __name__ == "__main__":
    main()
