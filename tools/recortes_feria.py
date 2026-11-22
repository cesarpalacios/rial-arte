#!/usr/bin/env python3
"""Recorta cada producto de las fotos nuevas de la feria (cuadrado centrado en el producto).

Uso: python3 tools/recortes_feria.py "/ruta/a/Productos "
Escribe fotos-origen/feria/<slug>.jpg (1400 px) que usa tools/catalogo_imagen.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fotos-origen" / "feria"
ELEGIDAS = {  # slug del producto -> foto original
    "aretes-aro-cristales-blancos": "IMG20261122125134",
    "aretes-flores-lilas-crochet": "IMG20261122125208",
    "aretes-gota-azul-crochet": "IMG20261122125333",
    "aretes-gota-chaquira-azul-lila": "IMG20261122125442",
    "aretes-aro-chaquira-multicolor": "IMG20261122125705",
    "aretes-flor-lila-perla-crochet": "IMG20261122125805",
    "aretes-flor-azul-dorado-crochet": "IMG20261122125819",
}


def recorte(im: Image.Image, margen=1.5, lado_out=1400) -> Image.Image:
    """Cuadrado centrado en el producto: se detecta por saturación (el fondo de tela es gris)."""
    import cv2
    pequena = im.copy()
    pequena.thumbnail((900, 900))
    rgb = np.asarray(pequena.convert("RGB"))
    hsv = cv2.cvtColor(cv2.GaussianBlur(rgb, (0, 0), 2.0), cv2.COLOR_RGB2HSV).astype(float)
    sat = hsv[..., 1]
    borde = np.concatenate([sat[:15].ravel(), sat[-15:].ravel(), sat[:, :15].ravel(), sat[:, -15:].ravel()])
    # el producto (cartón beige, hilos, chaquira) es más saturado que la tela gris del fondo
    mask = sat > np.median(borde) + 35
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    ys, xs = np.where(mask)
    x0, x1 = np.percentile(xs, [1, 99])
    y0, y1 = np.percentile(ys, [1, 99])
    esc = im.size[0] / pequena.size[0]
    cx, cy = (x0 + x1) / 2 * esc, (y0 + y1) / 2 * esc
    lado = max(x1 - x0, y1 - y0) * esc * margen
    lado = min(max(lado, 1200), min(im.size))
    l = int(min(max(cx - lado / 2, 0), im.size[0] - lado))
    t = int(min(max(cy - lado / 2, 0), im.size[1] - lado))
    return im.crop((l, t, l + int(lado), t + int(lado))).resize((lado_out, lado_out), Image.LANCZOS)


def main():
    src = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, nombre in ELEGIDAS.items():
        with Image.open(src / f"{nombre}.jpg") as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            recorte(im).save(OUT / f"{slug}.jpg", quality=90, optimize=True)
        print("ok", slug)


if __name__ == "__main__":
    main()
