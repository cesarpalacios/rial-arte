# Publicar en Google Sites

Google Sites no permite subir HTML propio directamente, pero sí **incrustar una página web por URL**. Por eso el sitio vive en GitHub Pages y Google Sites lo muestra a pantalla completa.

1. Entra a <https://sites.google.com> y crea un sitio en blanco con la cuenta de Google que quieras como dueña.
2. Ponle un nombre (por ejemplo, "Rial Arte") y borra el título y los bloques de texto por defecto.
3. Menú de la derecha → **Insertar** → **Insertar con código** (Embed) → pestaña **Por URL**.
4. Pega la URL de GitHub Pages (la misma que figura como `url_base` en `data/site.json`) y pulsa **Insertar** → **Insertar**.
5. Estira el bloque a todo el ancho y alto de la página (arrastra las esquinas). Para que ocupe todo el alto, usa un diseño de página con una sola sección.
6. Ajusta el tema a un color neutro/crema y oculta el título del encabezado si quieres que se vea solo el catálogo.
7. **Publicar** (arriba a la derecha) → elige una dirección, por ejemplo `sites.google.com/view/rial-arte`.

Notas:
- Cuando se actualice el repositorio, el sitio de Google se actualiza solo, porque solo apunta a la URL.
- Si algún día se compra un dominio propio, GitHub Pages lo soporta directamente y Google Sites deja de ser necesario.
