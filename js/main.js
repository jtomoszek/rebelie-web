/* REBELIE — navigace, lightbox, odhalování při scrollu, marquee */
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
  /* CSS clamp() neví, jak je text široký, takže dlouhé i krátké nadpisy
     vycházejí různě. Tohle dopočítá velikost tak, aby nejdelší řádek
     přesně vyplnil rodičovský sloupec. Bez JS zůstane v platnosti clamp(). */
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
    if (!widest) { el.style.fontSize = ''; return; }

    el.style.fontSize = (REF * avail / widest) + 'px';
  }

  function fitAll() { fitTargets.forEach(fitText); }

  if (fitTargets.length) {
    fitAll();
    // písma z Google Fonts dorazí až po prvním vykreslení — přeměřit
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(fitAll);
    }
    var fitTimer;
    window.addEventListener('resize', function () {
      clearTimeout(fitTimer);
      fitTimer = setTimeout(fitAll, 120);
    });
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
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]'));
  if (!items.length) return;

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
  var index = 0;
  var lastFocused = null;

  function show(i) {
    index = (i + items.length) % items.length;
    var el = items[index];
    var full = el.getAttribute('data-full') || el.querySelector('img').src;
    var img = el.querySelector('img');
    lbImg.src = full;
    lbImg.alt = img ? img.alt : '';
    lbCounter.textContent = (index + 1) + ' / ' + items.length;
  }

  function open(i) {
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

  items.forEach(function (el, i) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      open(i);
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
})();
