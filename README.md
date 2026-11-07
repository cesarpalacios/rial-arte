# Rial Arte

Catálogo web de **Rial Arte**: tejidos, crochet y bordados hechos a mano. Cada producto tiene su página con fotos y detalles, y un botón **Comprar por WhatsApp** que abre el chat con un mensaje ya escrito ("Hola, estoy interesado en este producto…") para cerrar la venta directamente.

Sitio estático (HTML + CSS + JS), sin dependencias de ejecución, publicado con GitHub Pages desde `docs/`.

## Editar contenido

Todo el contenido está en dos archivos:

| Archivo | Qué contiene |
|---|---|
| `data/site.json` | Nombre, lema, **número de WhatsApp**, redes, sección **Sobre mí** (historia) |
| `data/products.json` | Productos: nombre, categoría, descripción, detalles y fotos |

Para regenerar el sitio después de editar:

```bash
python3 tools/build.py                                   # solo HTML
python3 tools/build.py --fotos "/ruta/a/RIAL-ARTE"       # HTML + optimizar fotos (requiere Pillow)
```

Probar en local:

```bash
cd docs && python3 -m http.server 8000   # http://localhost:8000
```

## Agregar un producto

1. Añade un objeto en `data/products.json` (copia uno existente). `fotos` son los nombres de archivo sin extensión; la primera es la portada.
2. Ejecuta `python3 tools/build.py --fotos "/ruta/a/RIAL-ARTE"`.
3. Haz commit y push; GitHub Pages se actualiza solo.

## Publicación

- **GitHub Pages**: Settings → Pages → rama `main`, carpeta `/docs`.
- **Google Sites**: Insertar → Insertar con código/Insertar desde la Web → URL de GitHub Pages (ver guía en `GOOGLE-SITES.md`).
