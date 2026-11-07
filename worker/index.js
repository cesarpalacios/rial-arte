// Cloudflare Worker: proxy del sitio de Rial Arte que, en la página de inicio,
// cambia la foto de la vista previa (og:image) por una foto aleatoria del catálogo
// en cada petición. El resto de rutas se sirven tal cual desde GitHub Pages.
const ORIGIN = "https://cesarpalacios.github.io/rial-arte";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const res = await fetch(ORIGIN + url.pathname + url.search, { cf: { cacheTtl: 300 } });
    const esInicio = url.pathname === "/" || url.pathname === "/index.html";
    const esHtml = (res.headers.get("content-type") || "").includes("text/html");
    if (!esInicio || !esHtml) return res;

    let foto = null;
    try {
      const lista = await (await fetch(ORIGIN + "/fotos.json", { cf: { cacheTtl: 300 } })).json();
      foto = lista[Math.floor(Math.random() * lista.length)];
    } catch (e) { /* si falla, se deja la foto por defecto */ }
    if (!foto) return res;

    const salida = new HTMLRewriter()
      .on('meta[property="og:image"]', { element(el) { el.setAttribute("content", `${ORIGIN}/${foto.img}`); } })
      .on('meta[property="og:image:alt"]', { element(el) { el.setAttribute("content", foto.n); } })
      .on('meta[property="og:url"]', { element(el) { el.setAttribute("content", url.origin + "/"); } })
      .transform(res);
    const headers = new Headers(salida.headers);
    headers.set("Cache-Control", "no-store");
    return new Response(salida.body, { status: salida.status, headers });
  },
};
