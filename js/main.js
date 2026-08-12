/* REBELIE — navigace, nadpisy na šířku, lightbox, odhalování při scrollu */
(function () {
  'use strict';

  /* --- Mobilní menu ----------------------------------------------------- */
  var burger = document.querySelector('.nav__burger');
  var menu = document.querySelector('.mobile-menu');

  if (burger && menu) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', String(!open));
      menu.setAttribute('data-open', String(!open));
      document.body.style.overflow = open ? '' : 'hidden';
    });

    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        burger.setAttribute('aria-expanded', 'false');
        menu.setAttribute('data-open', 'false');
        document.body.style.overflow = '';
      }
    });
  }

  /* --- Nadpisy roztažené přesně na šířku sloupce ------------------------ */
  /* CSS clamp() neví, jak je text široký, takže „rebelie" a „co porota
     nepřehlédla" by při stejném nastavení vyšly úplně jinak. Tohle dopočítá
     velikost tak, aby nejdelší řádek přesně vyplnil rodičovský sloupec —
     na mobilu i na ultraširokém monitoru. Bez JS platí clamp() z CSS. */
  var MIN_PX = 28;    // pod tím už by nadpis nepůsobil jako nadpis
  var MAX_PX = 460;   // strop pro velmi široké monitory

  var fitTargets = Array.prototype.slice.call(document.querySelectorAll('[data-fit]'));

  function fitText(el) {
    var parent = el.parentElement;
    if (!parent) return;

    var ps = getComputedStyle(parent);
    var avail = parent.clientWidth
      - parseFloat(ps.paddingLeft || 0)
      - parseFloat(ps.paddingRight || 0);
    if (avail <= 0) return;

    var REF = 200; // referenční velikost pro změření
    el.style.fontSize = REF + 'px';

    var range = document.createRange();
    range.selectNodeContents(el);

    // getClientRects() vrací jeden obdélník na řádek, takže <br> je ošetřené
    var rects = range.getClientRects();
    var widest = 0;
    for (var i = 0; i < rects.length; i++) {
      if (rects[i].width > widest) widest = rects[i].width;
    }
    // Nulová šířka textu znamená, že stránka ještě není vykreslená
    // (skryté okno, náhledový panel). Vrátit CSS zálohu a nechat
    // pozdější resize/RO, ať to přeměří — nesmí se tu nic „zamknout".
    if (!widest) { el.style.fontSize = ''; return; }

    var size = REF * avail / widest;
    el.style.fontSize = Math.max(MIN_PX, Math.min(MAX_PX, size)) + 'px';
  }

  function fitAll() { fitTargets.forEach(fitText); }

  if (fitTargets.length) {
    fitAll();

    // Písma z Google Fonts dorazí až po prvním vykreslení — přeměřit,
    // jinak by velikost seděla na náhradní písmo.
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(fitAll);
    }

    // ResizeObserver chytí i změny, které resize okna nehlásí — přepnutí
    // mřížky hero sekce, otočení telefonu, zobrazení posuvníku.
    if (window.ResizeObserver) {
      var ro = new ResizeObserver(function () { fitAll(); });
      fitTargets.forEach(function (el) {
        if (el.parentElement) ro.observe(el.parentElement);
      });
    }

    // resize okna navíc vždy — pojistka pro případ, kdy RO proběhl
    // ve chvíli, kdy okno ještě nemělo rozměry (skrytá karta, náhled).
    var fitTimer;
    window.addEventListener('resize', function () {
      clearTimeout(fitTimer);
      fitTimer = setTimeout(fitAll, 120);
    });
    window.addEventListener('pageshow', fitAll);
  }

  /* --- Odhalování prvků při scrollu ------------------------------------- */
  var revealables = document.querySelectorAll('[data-reveal]');
  if (revealables.length) {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var delay = entry.target.getAttribute('data-reveal-delay') || 0;
            setTimeout(function () { entry.target.classList.add('is-visible'); }, Number(delay));
            io.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

      revealables.forEach(function (el) { io.observe(el); });
    } else {
      revealables.forEach(function (el) { el.classList.add('is-visible'); });
    }
  }

  /* --- Marquee: zdvojení obsahu pro plynulou smyčku ---------------------- */
  document.querySelectorAll('.marquee').forEach(function (m) {
    var track = m.querySelector('.marquee__track');
    if (!track) return;
    var clone = track.cloneNode(true);
    clone.setAttribute('aria-hidden', 'true');
    m.appendChild(clone);
  });

  /* --- Lightbox --------------------------------------------------------- */
  /* Pracuje nad polem položek {full, alt}. Díky tomu ho umí otevřít jak
     dlaždice v galerii, tak obálka akce, jejíž fotky nejsou v HTML,
     ale v datech (jinak by na stránce viselo 300 skrytých obrázků). */

  var galleryItems = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]'));
  var eventCovers = Array.prototype.slice.call(document.querySelectorAll('[data-udalost]'));
  if (!galleryItems.length && !eventCovers.length) return;

  var udalosti = {};
  var dataTag = document.getElementById('udalosti-data');
  if (dataTag) {
    // Uvnitř bloku zůstává značka pro generátor (<!--UDALOSTI-DATA-->).
    // JSON komentáře nezná, takže se před parsováním musí odstranit.
    var raw = dataTag.textContent.replace(/<!--[\s\S]*?-->/g, '').trim();
    try { udalosti = raw ? JSON.parse(raw) : {}; } catch (err) { udalosti = {}; }
  }

  var lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Zvětšená fotografie');
  lb.innerHTML =
    '<img class="lightbox__img" alt="">' +
    '<button class="lightbox__close" type="button" aria-label="Zavřít">✕</button>' +
    '<button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Předchozí">←</button>' +
    '<button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Další">→</button>' +
    '<p class="lightbox__counter"></p>';
  document.body.appendChild(lb);

  var lbImg = lb.querySelector('.lightbox__img');
  var lbCounter = lb.querySelector('.lightbox__counter');
  var lbTitle = null;
  var seznam = [];
  var index = 0;
  var lastFocused = null;

  function show(i) {
    if (!seznam.length) return;
    index = (i + seznam.length) % seznam.length;
    var polozka = seznam[index];
    lbImg.src = polozka.full;
    lbImg.alt = polozka.alt || '';
    lbCounter.textContent = (lbTitle ? lbTitle + ' — ' : '') +
      (index + 1) + ' / ' + seznam.length;

    // předstih: načíst sousední fotky, aby listování neproblikávalo
    [index + 1, index - 1].forEach(function (j) {
      var s = seznam[(j + seznam.length) % seznam.length];
      if (s) { var im = new Image(); im.src = s.full; }
    });
  }

  function open(items, i, nadpis) {
    if (!items || !items.length) return;
    seznam = items;
    lbTitle = nadpis || null;
    lastFocused = document.activeElement;
    show(i);
    lb.setAttribute('data-open', 'true');
    document.body.style.overflow = 'hidden';
    lb.querySelector('.lightbox__close').focus();
  }

  function close() {
    lb.removeAttribute('data-open');
    lbImg.src = '';
    document.body.style.overflow = '';
    if (lastFocused) lastFocused.focus();
  }

  // dlaždice v galeriích (bodypainting, oblečení, obrazy, ukázky)
  var galerieSeznam = galleryItems.map(function (el) {
    var img = el.querySelector('img');
    return {
      full: el.getAttribute('data-full') || (img && img.src),
      alt: img ? img.alt : ''
    };
  });

  galleryItems.forEach(function (el, i) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      open(galerieSeznam, i);
    });
  });

  // obálky akcí — fotky se berou z dat
  eventCovers.forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      var slug = el.getAttribute('data-udalost');
      var u = udalosti[slug];
      if (!u) return;
      open(u.fotky.map(function (soubor, i) {
        return {
          full: 'img/udalosti/' + slug + '/' + soubor,
          alt: u.nazev + ' — fotografie ' + (i + 1)
        };
      }), 0, u.nazev);
    });
  });

  lb.querySelector('.lightbox__close').addEventListener('click', close);
  lb.querySelector('.lightbox__nav--prev').addEventListener('click', function () { show(index - 1); });
  lb.querySelector('.lightbox__nav--next').addEventListener('click', function () { show(index + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });

  document.addEventListener('keydown', function (e) {
    if (lb.getAttribute('data-open') !== 'true') return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(index - 1);
    if (e.key === 'ArrowRight') show(index + 1);
  });

  // listování prstem na mobilu
  var touchX = null;
  lb.addEventListener('touchstart', function (e) {
    touchX = e.changedTouches[0].clientX;
  }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 45) show(index + (dx < 0 ? 1 : -1));
    touchX = null;
  }, { passive: true });
})();
