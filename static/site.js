(function () {
  // Mobilmenu
  var btn = document.querySelector('.nav-toggle'), nav = document.getElementById('site-nav');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // Indholdsfortegnelse åben på desktop, lukket på mobil
  var toc = document.querySelector('.toc[data-open-desktop]');
  if (toc && window.matchMedia('(min-width: 981px)').matches) toc.open = true;
  if (toc) toc.addEventListener('click', function (e) {
    if (e.target.tagName === 'A' && window.matchMedia('(max-width: 980px)').matches) toc.open = false;
  });

  // Sticky CTA på mobil efter lidt scroll
  var sticky = document.querySelector('.sticky-cta');
  if (sticky) {
    var onScroll = function () { sticky.hidden = window.scrollY < 700; };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }

  // Prisfinder på forsiden
  var sel = document.getElementById('finder-select'), dataEl = document.getElementById('finder-data');
  if (sel && dataEl) {
    var data = JSON.parse(dataEl.textContent), out = document.querySelector('.finder-result');
    var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    sel.addEventListener('change', function () {
      var d = data[sel.value];
      if (!d) { out.innerHTML = ''; return; }
      var h = '';
      if (d.price) h += '<p class="finder-note">Typisk pris for ' + esc(d.name.toLowerCase()) + '</p><p class="finder-price">' + esc(d.price) + '</p><p class="finder-note">' + esc(d.note) + '</p>';
      else h += '<p class="finder-note">Få konkrete priser på ' + esc(d.name.toLowerCase()) + ' fra håndværkere i dit område.</p>';
      h += '<div class="finder-actions"><a class="btn btn-cta" href="' + esc(d.aff) + '" rel="sponsored nofollow noopener" target="_blank">Få 3 gratis tilbud</a>';
      if (d.guide) h += '<a class="textlink" href="' + esc(d.guide) + '">Læs guiden først</a>';
      h += '</div><p class="cta-ad">Annonce. Linket går til 3byggetilbud.dk.</p>';
      out.innerHTML = h;
    });
  }
})();
