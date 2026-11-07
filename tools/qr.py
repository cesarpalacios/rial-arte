#!/usr/bin/env python3
"""Genera el QR de Rial Arte y la tarjeta de presentación.

Uso:  python3 tools/qr.py
Crea en tarjeta/:
  - qr-rial-arte.png          QR solo (con el logo al centro), para imprimir o poner donde sea
  - tarjeta-celular.png       tarjeta vertical para mostrar desde el celular
  - tarjeta-impresa.pdf       tarjeta de presentación 90x55 mm (frente y reverso)
Necesita Pillow, reportlab y Google Chrome.
"""
import html
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tarjeta"
DOCS = ROOT / "docs"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
site = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
URL = site["url_base"]
NAVY = (31, 42, 90)
esc = html.escape


def qr_png(path: Path, px=1400, quiet=4):
    qr = QRCode(None, QRErrorCorrectLevel.H)  # corrección alta: tolera el logo al centro
    qr.addData(URL)
    qr.make()
    n = qr.getModuleCount()
    cell = px // (n + 2 * quiet)
    size = cell * (n + 2 * quiet)
    img = Image.new("RGB", (size, size), "white")
    d = ImageDraw.Draw(img)
    for r in range(n):
        for c in range(n):
            if qr.isDark(r, c):
                x, y = (c + quiet) * cell, (r + quiet) * cell
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=NAVY)
    logo = Image.open(DOCS / "assets" / "logo.png").convert("RGBA")
    lado = int(size * 0.2)
    logo.thumbnail((lado, lado), Image.LANCZOS)
    pad = int(lado * 0.14)
    caja = Image.new("RGBA", (logo.width + 2 * pad, logo.height + 2 * pad), (255, 255, 255, 255))
    caja.alpha_composite(logo, (pad, pad))
    img.paste(caja.convert("RGB"), ((size - caja.width) // 2, (size - caja.height) // 2))
    img.save(path, optimize=True)
    return n


def chrome(args):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--virtual-time-budget=15000", *args], check=True, capture_output=True)


FUENTES = ('<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500'
           '&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">')
BASE_CSS = """*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
:root{--navy:#1f2a5a;--gold:#e8b838;--gold-soft:#f6e6b4;--cream:#fbf7ef;--muted:#666b80;--sans:'Jost',sans-serif;--serif:'Cormorant Garamond',Georgia,serif}
body{font-family:var(--sans);color:var(--navy)}"""


def tarjeta_celular():
    tel, ig = site["whatsapp_visible"], site["instagram"].rstrip("/").split("/")[-1]
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">{FUENTES}<style>{BASE_CSS}
html,body{{width:1080px;height:1920px}}
body{{background:radial-gradient(circle at 85% 6%,var(--gold-soft),var(--cream) 55%);display:flex;flex-direction:column;align-items:center;padding:70px 70px 60px;text-align:center}}
.logo{{width:260px}}
h1{{font-family:var(--serif);font-weight:600;font-size:88px;line-height:1.05;margin-top:22px}}
.serv{{font-size:36px;letter-spacing:.06em;color:var(--muted);margin-top:18px}}
.qrbox{{margin-top:50px;background:#fff;border-radius:60px;padding:40px;border:10px solid var(--gold);box-shadow:0 30px 70px rgba(31,42,90,.22)}}
.qrbox img{{width:640px;height:640px;display:block}}
.scan{{font-family:var(--serif);font-style:italic;font-size:60px;margin-top:44px;line-height:1.1}}
.scan em{{color:#c99a1c}}
.ct{{margin-top:36px;font-size:40px;line-height:1.6}}
.ct b{{font-weight:600}}
.ct small{{display:block;color:var(--muted);font-size:32px}}</style></head><body>
<img class="logo" src="{(DOCS / 'assets/logo.png').as_uri()}" alt="">
<h1>Rosa Irlanda<br>Alarcón Laverde</h1>
<p class="serv">Tejido · Crochet · Bordado · Bisutería</p>
<div class="qrbox"><img src="{(OUT / 'qr-rial-arte.png').as_uri()}" alt="QR"></div>
<p class="scan">Escanéame y conoce<br>mi <em>catálogo</em></p>
<p class="ct"><b>WhatsApp {esc(tel)}</b><br>Instagram @{esc(ig)}<small>Sogamoso, Boyacá · {esc(URL.replace('https://', ''))}</small></p>
</body></html>"""
    (OUT / "tarjeta-celular.html").write_text(doc, encoding="utf-8")
    chrome(["--force-device-scale-factor=1", "--window-size=1080,1920",
            f"--screenshot={OUT / 'tarjeta-celular.png'}", (OUT / "tarjeta-celular.html").as_uri()])


def tarjeta_impresa():
    tel, ig = site["whatsapp_visible"], site["instagram"].rstrip("/").split("/")[-1]
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">{FUENTES}<style>{BASE_CSS}
@page{{size:90mm 55mm;margin:0}}
.c{{width:90mm;height:55mm;overflow:hidden;page-break-after:always;break-after:page;display:flex;align-items:center;justify-content:center;position:relative}}
.f{{background:radial-gradient(circle at 90% 0%,var(--gold-soft),var(--cream) 60%);padding:5mm 6mm;gap:5mm;justify-content:flex-start}}
.f .logo{{width:22mm;flex:none}}
.f h1{{font-family:var(--serif);font-size:14.5pt;line-height:1.05;font-weight:600}}
.f .s{{font-size:6pt;letter-spacing:.07em;color:var(--muted);margin:1.2mm 0 2.4mm}}
.f p{{font-size:6.8pt;line-height:1.55}}
.f b{{font-weight:600}}
.b{{background:var(--navy);color:#fff;flex-direction:column;text-align:center}}
.b .q{{background:#fff;padding:2.2mm;border-radius:3mm;border:.8mm solid var(--gold)}}
.b .q img{{width:34mm;height:34mm;display:block}}
.b p{{font-family:var(--serif);font-style:italic;font-size:10pt;margin-top:2.2mm}}
.b p em{{color:var(--gold)}}</style></head><body>
<div class="c f"><img class="logo" src="{(DOCS / 'assets/logo.png').as_uri()}" alt="">
<div><h1>Rosa Irlanda<br>Alarcón Laverde</h1><div class="s">TEJIDO · CROCHET · BORDADO · BISUTERÍA</div>
<p><b>WhatsApp {esc(tel)}</b><br>@{esc(ig)}<br>Sogamoso, Boyacá</p></div></div>
<div class="c b"><div class="q"><img src="{(OUT / 'qr-rial-arte.png').as_uri()}" alt=""></div><p>Escanéame y conoce mi <em>catálogo</em></p></div>
</body></html>"""
    (OUT / "tarjeta-impresa.html").write_text(doc, encoding="utf-8")
    chrome(["--no-pdf-header-footer", f"--print-to-pdf={OUT / 'tarjeta-impresa.pdf'}",
            (OUT / "tarjeta-impresa.html").as_uri()])


def main():
    if not Path(CHROME).exists():
        sys.exit("Falta Google Chrome")
    OUT.mkdir(exist_ok=True)
    n = qr_png(OUT / "qr-rial-arte.png")
    print(f"QR de {n}x{n} módulos apuntando a {URL}")
    tarjeta_celular()
    tarjeta_impresa()
    for f in ("qr-rial-arte.png", "tarjeta-celular.png", "tarjeta-impresa.pdf"):
        print("  ", OUT / f, f"{(OUT / f).stat().st_size / 1e3:.0f} KB")


if __name__ == "__main__":
    main()
