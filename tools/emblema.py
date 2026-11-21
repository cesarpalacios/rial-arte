#!/usr/bin/env python3
"""Genera el emblema de Rial Arte SIN la cinta con el nombre (solo el símbolo).

El logo original tiene una cinta con "Rial Arte" que tapa la parte baja del círculo.
Aquí se quita la cinta y se reconstruye el círculo (anillo plateado + fondo dorado) reflejando
la parte alta, que no tiene dibujo. Resultado en emblema/ (PNG transparente, PNG fondo blanco, JPG).

Uso: python3 tools/emblema.py
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "emblema"
CX, CY, R = 205.77, 163.65, 167.83   # círculo exterior del logo (ajustado a mínimos cuadrados)
Y0 = 248                              # el dibujo termina ~y=244; desde aquí se reconstruye


def main():
    OUT.mkdir(exist_ok=True)
    a = np.array(Image.open(ROOT / "docs" / "assets" / "logo.png").convert("RGBA"))
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot(xx - CX, yy - CY)
    al = a[..., 3:4].astype(float) / 255
    base = (a[..., :3] * al + 255 * (1 - al)).astype(np.uint8)

    R_IN = R - 19.5   # el anillo plateado mide ~19 px; dentro está el dorado
    # perfil radial del dorado (incluye la sombra interior junto al anillo), medido arriba, donde no hay dibujo
    col = base[:60, int(CX) - 6:int(CX) + 7].astype(float).mean(axis=1)
    ds = CY - np.arange(60)
    orden = np.argsort(ds)
    ds, col = ds[orden], col[orden]
    prof = lambda dist: np.stack([np.interp(np.clip(dist, 118, R_IN), ds, col[:, c]) for c in range(3)], axis=-1)

    work = base.copy().astype(float)
    # 1) Anillo plateado: la parte alta reflejada hacia abajo
    YR = 205  # el anillo se refleja desde aquí (ahí no hay dibujo ni cinta)
    mirror = base.copy()
    for y in range(YR, h):
        mirror[y] = base[max(int(round(2 * CY - y)), 0)]
    zona = (yy >= Y0) & (d < R + 3)
    anillo = (yy >= YR) & (d < R + 3) & (d >= R_IN - 1)
    peso = np.clip((yy - YR) / 24.0, 0, 1)[..., None]   # fundido gradual en vez de corte seco
    work[anillo] = ((1 - peso) * base + peso * mirror)[anillo]
    # 2) Fondo dorado: se prolonga hacia abajo la fila limpia y se le aplica el perfil radial (sombra interior)
    # fila de referencia: se descartan columnas con tinta o halo blanco del dibujo y se interpola
    fila = base[Y0 - 3:Y0 + 1].astype(float).mean(axis=0)
    hsv = cv2.cvtColor(base[Y0 - 3:Y0 + 1].astype(np.uint8), cv2.COLOR_RGB2HSV).astype(float)
    bueno = ((hsv[..., 1] > 110) & (hsv[..., 2] > 190)).all(axis=0)
    bueno = ~(cv2.dilate((~bueno).astype(np.uint8)[None, :], np.ones((1, 9), np.uint8))[0] > 0)
    xs = np.arange(w)
    dentro = np.hypot(xs - CX, (Y0 - 1) - CY) < R_IN
    validos = bueno & dentro
    fila = np.stack([np.interp(xs, xs[validos], fila[validos, c]) for c in range(3)], axis=-1)
    fila = cv2.GaussianBlur(fila[None].astype(np.float32), (0, 0), sigmaX=5)[0].astype(float)
    dref = np.hypot(xs - CX, (Y0 - 1) - CY)
    ref = fila / prof(dref)
    oro = zona & (d < R_IN - 1)
    vals = ref[xx[oro]] * prof(d[oro])
    work[oro] = np.clip(vals, 0, 255)
    # 3) Suavizar la unión del anillo con el dorado
    sua = cv2.GaussianBlur(work, (0, 0), sigmaX=1.2)
    borde = zona & (np.abs(d - R_IN) < 2.5)
    work[borde] = sua[borde]
    # 4) Costura horizontal: inpaint fino
    mask = np.zeros((h, w), np.uint8)
    mask[(yy >= Y0 - 1) & (yy <= Y0 + 3) & (d < R + 3)] = 255
    res = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(work.astype(np.uint8), cv2.COLOR_RGB2BGR), mask, 3, cv2.INPAINT_TELEA),
                       cv2.COLOR_BGR2RGB)

    alpha = np.clip(R + 0.5 - d, 0, 1)
    rgba = Image.fromarray(np.dstack([res, (alpha * 255).astype(np.uint8)]), "RGBA")
    box = (int(CX - R) - 2, int(CY - R) - 2, int(CX + R) + 3, int(CY + R) + 3)
    # lienzo cuadrado: el recorte puede salirse del original por arriba
    lado = box[2] - box[0]
    lienzo = Image.new("RGBA", (lado, box[3] - box[1]), (0, 0, 0, 0))
    lienzo.paste(rgba, (-box[0], -box[1]))
    base_img = lienzo.crop((0, 0, lado, lado))

    for px in (2000,):
        g = base_img.resize((px, px), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=2))
        g.save(OUT / f"emblema-rial-arte-{px}px-transparente.png", optimize=True)
        blanco = Image.new("RGB", g.size, "white")
        blanco.paste(g, mask=g.split()[3])
        blanco.save(OUT / f"emblema-rial-arte-{px}px-fondo-blanco.png", optimize=True)
        blanco.save(OUT / f"emblema-rial-arte-{px}px-fondo-blanco.jpg", quality=95)
    print("Emblema generado en", OUT)


if __name__ == "__main__":
    sys.exit(main())
