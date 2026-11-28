#!/usr/bin/env python3
"""Genera una tarjeta regalo de Rial Arte con código único y la anota en el registro.

Se usa DESPUÉS de verificar el pago:
  python3 tools/tarjeta_regalo.py 15000 --para "María" --de "Carlos"
  python3 tools/tarjeta_regalo.py 20000                       # sin nombres
  python3 tools/tarjeta_regalo.py --redimir RA-15-ABCD-EFGH   # marca el código como redimido
  python3 tools/tarjeta_regalo.py --estado                    # lista todas las tarjetas

Crea  <carpeta>/Tarjeta RA-15-XXXX-XXXX ($15.000).png  (para enviar por WhatsApp)
y agrega una fila en  <carpeta>/Registro de tarjetas regalo.csv.
El registro y las tarjetas NO van al repositorio (es público): se guardan en Drive.
Necesita Pillow y Google Chrome.
"""
import argparse
import csv
import html
import json
import secrets
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CARPETA = Path("/Users/ceapalaciosal/Library/CloudStorage/GoogleDrive-ceapalaciosal@gmail.com/"
               "Mi unidad/Emprendimiento Mama/Tarjetas regalo")
COLS = ["Codigo", "Valor COP", "Para", "De", "Fecha compra", "Vence", "Estado", "Fecha redencion", "Notas"]
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # sin 0/O/1/I para evitar confusiones
VIGENCIA_MESES = 6
site = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
esc = html.escape


def cop(n):
    return "$" + f"{int(n):,}".replace(",", ".")


def sumar_meses(d: date, m: int) -> date:
    y, mes = divmod(d.month - 1 + m, 12)
    dia = min(d.day, [31, 29 if (d.year + y) % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes])
    return date(d.year + y, mes + 1, dia)


def leer(reg: Path):
    if not reg.exists():
        return []
    with open(reg, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def escribir(reg: Path, filas):
    with open(reg, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(filas)


def codigo_nuevo(monto, existentes):
    while True:
        c = "RA-%02d-%s-%s" % (monto // 1000, "".join(secrets.choice(ALFABETO) for _ in range(4)),
                               "".join(secrets.choice(ALFABETO) for _ in range(4)))
        if c not in existentes:
            return c


def dibujar(codigo, monto, para, de, vence, destino: Path):
    emblema = ROOT / "emblema" / "emblema-rial-arte-2000px-transparente.png"
    qr = ROOT / "tarjeta" / "qr-rial-arte.png"
    dedicatoria = ""
    if para or de:
        dedicatoria = "<p class='ded'>" + (f"Para <b>{esc(para)}</b>" if para else "") + \
                      (" · " if para and de else "") + (f"De <b>{esc(de)}</b>" if de else "") + "</p>"
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<style>*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--navy:#1f2a5a;--gold:#e8b838;--gold-soft:#f6e6b4;--serif:'Cormorant Garamond',Georgia,serif;--sans:'Jost',sans-serif}}
html,body{{width:1600px;height:1000px;background:#fbf7ef;font-family:var(--sans)}}
.c{{position:absolute;inset:30px;border-radius:48px;color:#fff;overflow:hidden;border:6px solid var(--gold);
background:radial-gradient(circle at 88% 8%,rgba(232,184,56,.55),transparent 42%),linear-gradient(135deg,#1f2a5a,#2d3a78 75%)}}
.c::before{{content:"";position:absolute;inset:22px;border:3px dashed rgba(246,230,180,.55);border-radius:30px}}
.em{{position:absolute;left:80px;top:70px;width:210px}}
.tag{{position:absolute;left:330px;top:100px;text-transform:uppercase;letter-spacing:.3em;font-size:32px;color:var(--gold-soft);font-weight:600}}
.nom{{position:absolute;left:330px;top:150px;font-family:var(--serif);font-style:italic;font-size:54px}}
.monto{{position:absolute;left:80px;top:330px;font-family:var(--serif);font-weight:600;font-size:230px;line-height:1;color:var(--gold)}}
.ded{{position:absolute;left:84px;top:590px;font-size:44px;color:var(--gold-soft)}}
.ded b{{color:#fff;font-weight:600}}
.cod{{position:absolute;left:80px;bottom:130px;font-size:30px;letter-spacing:.2em;color:var(--gold-soft)}}
.cod b{{display:block;font-size:64px;letter-spacing:.14em;color:#fff;margin-top:6px;font-weight:600}}
.pie{{position:absolute;left:84px;bottom:62px;font-size:26px;color:#cfd4ee}}
.q{{position:absolute;right:80px;bottom:80px;background:#fff;border-radius:28px;padding:16px;text-align:center;color:var(--navy);font-weight:600;font-size:22px}}
.q img{{width:230px;height:230px;display:block;margin-bottom:6px}}
.how{{position:absolute;right:80px;top:80px;width:520px;text-align:right;font-size:30px;line-height:1.4;color:var(--gold-soft)}}
.how b{{color:#fff}}</style></head><body><div class="c">
<img class="em" src="{emblema.as_uri()}" alt="">
<p class="tag">Tarjeta regalo</p><p class="nom">Rial Arte · hecho a mano</p>
<p class="monto">{cop(monto)}</p>{dedicatoria}
<p class="cod">CÓDIGO<b>{esc(codigo)}</b></p>
<p class="pie">Válida hasta el {vence.strftime('%d/%m/%Y')} · de un solo uso · no canjeable por dinero</p>
<p class="how">Para redimirla escribe a<br><b>WhatsApp {esc(site['whatsapp_visible'])}</b><br>con tu código o entra a<br><b>{esc(site['url_base'].replace('https://', ''))}</b></p>
<div class="q"><img src="{qr.as_uri()}" alt="">Catálogo web</div>
</div></body></html>"""
    h = destino.with_suffix(".html")
    h.write_text(doc, encoding="utf-8")
    png = destino.with_suffix(".tmp.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1600,1000", "--virtual-time-budget=15000", f"--screenshot={png}", h.as_uri()],
                   check=True, capture_output=True)
    with Image.open(png) as im:
        im.convert("RGB").save(destino, optimize=True)
    png.unlink()
    h.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("monto", nargs="?", type=int, help="10000, 15000, 20000 u otro valor")
    ap.add_argument("--para")
    ap.add_argument("--de")
    ap.add_argument("--carpeta", type=Path, default=CARPETA)
    ap.add_argument("--redimir", metavar="CODIGO")
    ap.add_argument("--estado", action="store_true")
    a = ap.parse_args()
    a.carpeta.mkdir(parents=True, exist_ok=True)
    reg = a.carpeta / "Registro de tarjetas regalo.csv"
    filas = leer(reg)

    if a.estado:
        for f in filas:
            print(f"{f['Codigo']}  {cop(f['Valor COP']):>9}  {f['Estado']:<9} vence {f['Vence']}  {f['Para']}")
        print(f"{len(filas)} tarjetas")
        return
    if a.redimir:
        c = a.redimir.strip().upper()
        for f in filas:
            if f["Codigo"] == c:
                if f["Estado"] == "Redimida":
                    sys.exit(f"¡Ojo! {c} ya fue redimida el {f['Fecha redencion']}")
                if date.fromisoformat(f["Vence"]) < date.today():
                    sys.exit(f"{c} está vencida desde el {f['Vence']}")
                f["Estado"], f["Fecha redencion"] = "Redimida", date.today().isoformat()
                escribir(reg, filas)
                print(f"OK: {c} ({cop(f['Valor COP'])}) marcada como redimida")
                return
        sys.exit(f"No encuentro el código {c}: no es una tarjeta válida")
    if not a.monto:
        ap.error("indica el valor (por ejemplo 15000)")
    if not Path(CHROME).exists():
        sys.exit("Falta Google Chrome")

    hoy = date.today()
    vence = sumar_meses(hoy, VIGENCIA_MESES)
    codigo = codigo_nuevo(a.monto, {f["Codigo"] for f in filas})
    destino = a.carpeta / f"Tarjeta {codigo} ({cop(a.monto)}).png"
    dibujar(codigo, a.monto, a.para, a.de, vence, destino)
    filas.append({"Codigo": codigo, "Valor COP": a.monto, "Para": a.para or "", "De": a.de or "",
                  "Fecha compra": hoy.isoformat(), "Vence": vence.isoformat(), "Estado": "Activa",
                  "Fecha redencion": "", "Notas": ""})
    escribir(reg, filas)
    print(f"Tarjeta creada: {destino}\nCódigo {codigo} · {cop(a.monto)} · vence {vence.isoformat()}\nRegistro: {reg}")


if __name__ == "__main__":
    main()
