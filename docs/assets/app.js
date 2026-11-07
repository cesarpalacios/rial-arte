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

// Galería "Momentos": ampliar foto al tocarla
(function () {
  var items = document.querySelectorAll('.momento');
  if (!items.length) return;
  function cerrar() { var l = document.querySelector('.lightbox'); if (l) l.remove(); }
  items.forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      cerrar();
      var l = document.createElement('div');
      l.className = 'lightbox';
      l.setAttribute('role', 'dialog');
      l.innerHTML = '<img alt=""><p></p>';
      l.querySelector('img').src = a.getAttribute('data-full');
      l.querySelector('img').alt = a.getAttribute('data-cap');
      l.querySelector('p').textContent = a.getAttribute('data-cap');
      l.addEventListener('click', cerrar);
      document.body.appendChild(l);
    });
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') cerrar(); });
})();
