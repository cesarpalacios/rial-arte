# SEO de Rial Arte

## Ya implementado (se regenera con `python3 tools/build.py`)
- Título y descripción únicos por página, con palabras clave (tejidos, crochet, bordado, bisutería, Sogamoso, Boyacá).
- URL canónica, `hreflang es-CO`, `robots` con `max-image-preview:large`.
- Open Graph y Twitter Cards (vista previa al compartir).
- Datos estructurados (JSON-LD): WebSite, LocalBusiness con dirección en Sogamoso/Boyacá, lista de productos (ItemList), Product y BreadcrumbList en cada producto.
- `sitemap.xml` con fecha, prioridad y fotos de cada producto; `robots.txt` apuntando al sitemap; `404.html` con noindex.
- Una página real por producto (no solo JavaScript), un solo `h1` por página, texto alternativo en las fotos, carga diferida de imágenes, sitio rápido y adaptable a celular.

## Pasos manuales para que Google la indexe (una sola vez)
1. Entra a <https://search.google.com/search-console> con la cuenta de Google de la dueña.
2. **Agregar propiedad → Prefijo de URL** → `https://cesarpalacios.github.io/rial-arte/`
3. Verificar con la opción **Etiqueta HTML**: copia la línea `<meta name="google-site-verification" content="...">` y pásasela a quien mantiene el sitio para ponerla en `tools/build.py` (o en `data/site.json`). Después pulsa Verificar.
4. Menú **Sitemaps** → escribe `sitemap.xml` → Enviar.
5. Menú **Inspección de URLs** → pega la URL del sitio → **Solicitar indexación**. Repite con 3 o 4 productos.
6. Opcional: <https://www.bing.com/webmasters> (importa la propiedad desde Google Search Console).

La indexación suele tardar entre unos días y un par de semanas.

## Para posicionar mejor
- Pon el enlace del sitio en la biografía de Instagram y en los mensajes de WhatsApp Business.
- Crea el perfil gratuito de **Google Business Profile** (Sogamoso, Boyacá) con el mismo teléfono y enlace.
- Añade precios (cuando estén) y reseñas de clientes; Google las muestra en los resultados.
- Con un dominio propio (por ejemplo rialarte.com) el posicionamiento mejora. GitHub Pages lo soporta.
- Google Sites incrusta el sitio en un marco (iframe): para Google cuenta el contenido de GitHub Pages, no el de la página de Google Sites. Comparte siempre la URL de GitHub Pages.
