# Vista previa aleatoria con Cloudflare Workers (gratis)

Al compartir un enlace por WhatsApp, la tarjeta con la foto la arma WhatsApp leyendo la etiqueta `og:image` de la página. GitHub Pages solo entrega archivos fijos, así que esa foto no puede cambiar. Este Worker se pone delante del sitio y, cada vez que alguien (o WhatsApp) abre la página de inicio, cambia esa etiqueta por una foto distinta del catálogo.

## Pasos (una sola vez, unos 5 minutos)

1. Crea una cuenta gratuita en <https://dash.cloudflare.com/sign-up> (solo correo y contraseña; no pide tarjeta).
2. Menú izquierdo → **Workers & Pages** → **Create** → **Create Worker**.
3. Ponle nombre, por ejemplo `rial-arte`, y pulsa **Deploy**.
4. Pulsa **Edit code**, borra todo y pega el contenido de `worker/index.js`. Pulsa **Deploy**.
5. Tu enlace nuevo será `https://rial-arte.<tu-usuario>.workers.dev`. Ese es el que se comparte por WhatsApp y el que va en Google Sites (Insertar → Por URL).

## Cosas a saber

- El sitio se ve igual: el Worker solo reenvía el contenido de GitHub Pages.
- WhatsApp guarda la vista previa de cada enlace durante un tiempo. En un mismo chat puede seguir viéndose la foto anterior; en chats nuevos o para otras personas saldrá otra. Para forzar una foto nueva en el mismo chat, agrega al final `?x=1`, `?x=2`, etc.
- Si cambias el catálogo, el Worker se entera solo (lee `fotos.json`, que genera `tools/build.py`); no hay que volver a pegar el código.
- Plan gratuito de Cloudflare: 100.000 peticiones al día, de sobra para este sitio.
