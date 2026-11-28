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
- **Catálogo PDF**: `python3 tools/catalogo.py` (requiere Google Chrome) genera `docs/catalogo-rial-arte.pdf`.
- **QR y tarjeta de presentación**: `python3 tools/qr.py` genera `tarjeta/` (QR, imagen para el celular y PDF imprimible).
- **Emblema sin cinta (solo símbolo)**: `python3 tools/emblema.py` genera `emblema/`. Catálogo como imágenes: `pdftoppm -r 200 -jpeg docs/catalogo-rial-arte.pdf pagina`.
- **Catálogo en una sola imagen**: `python3 tools/catalogo_imagen.py` genera `catalogo/catalogo-imagen.jpg`.
- **Vista previa aleatoria**: ver `worker/PUBLICAR.md`.
- **Google Sites**: Insertar → Insertar con código/Insertar desde la Web → URL de GitHub Pages (ver guía en `GOOGLE-SITES.md`).

## Tarjetas regalo
Sección `#regalo` del sitio (valores en `data/site.json` → `tarjetas_regalo`, por defecto 10.000 / 15.000 / 20.000). Quien compra escribe por WhatsApp; **después de verificar el pago** se genera la tarjeta con código único:

```bash
python3 tools/tarjeta_regalo.py 15000 --para "María" --de "Carlos"   # crea la imagen y anota en el registro
python3 tools/tarjeta_regalo.py --redimir RA-15-XXXX-XXXX            # al usarla: la marca como redimida
python3 tools/tarjeta_regalo.py --estado                             # lista de tarjetas
```
Las tarjetas y el registro CSV quedan en Drive (`Emprendimiento Mama/Tarjetas regalo/`), nunca en el repo.
