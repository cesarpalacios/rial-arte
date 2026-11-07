// Filtro del catálogo
(function () {
  var botones = document.querySelectorAll('.filtro');
  var tarjetas = document.querySelectorAll('.grid .card');
  botones.forEach(function (b) {
    b.addEventListener('click', function () {
      botones.forEach(function (x) { x.classList.toggle('active', x === b); });
      var cat = b.getAttribute('data-cat');
      tarjetas.forEach(function (t) {
        t.hidden = cat !== 'todos' && t.getAttribute('data-cat') !== cat;
      });
    });
  });
})();

// Galería de la página de producto
(function () {
  var principal = document.getElementById('foto-principal');
  if (!principal) return;
  document.querySelectorAll('.thumb').forEach(function (t) {
    t.addEventListener('click', function () {
      principal.src = t.getAttribute('data-src');
      document.querySelectorAll('.thumb').forEach(function (x) { x.classList.toggle('active', x === t); });
    });
  });
})();
