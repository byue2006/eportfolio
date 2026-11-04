/* Brian Yue · portfolio · shared behavior for every page.
   Everything here is progressive: the site works with JS off. */
(function () {
  var doc = document.documentElement;
  var body = document.body;
  var base = body.getAttribute('data-base') || '';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ---------- header: solid after scroll, hides on scroll down ---------- */
  var header = document.querySelector('.site-header');
  var progress = document.querySelector('.progress');
  var lastY = window.scrollY, ticking = false;
  function onScroll() {
    var y = window.scrollY;
    if (header) {
      header.classList.toggle('scrolled', y > 12);
      var menuOpen = body.classList.contains('menu-open');
      if (!menuOpen && !doc.classList.contains('present') && y > 240 && y > lastY + 4) header.classList.add('hide');
      else if (y < lastY - 4 || y < 240) header.classList.remove('hide');
    }
    if (progress) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
    }
    lastY = y;
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();

  /* ---------- mobile menu ---------- */
  var menuBtn = document.querySelector('.menu-btn');
  var menu = document.getElementById('menu');
  function setMenu(open) {
    if (!menu || !menuBtn) return;
    menu.classList.toggle('open', open);
    body.classList.toggle('menu-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menuBtn.querySelector('span').textContent = open ? 'Close' : 'Menu';
    if (open) { header.classList.remove('hide'); menu.removeAttribute('inert'); }
    else menu.setAttribute('inert', '');
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.classList.contains('open')) setMenu(false); });
  }

  /* ---------- headline word reveal ---------- */
  document.querySelectorAll('.split').forEach(function (el) {
    var i = 0;
    function wrap(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var w = document.createElement('span'); w.className = 'w';
            var s = document.createElement('span'); s.textContent = part; s.style.setProperty('--i', i++);
            w.appendChild(s); frag.appendChild(w);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1 && child.tagName !== 'BR') {
          wrap(child);
        }
      });
    }
    el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
    wrap(el);
    el.querySelectorAll('.w').forEach(function (w) { w.setAttribute('aria-hidden', 'true'); });
  });

  /* ---------- reveal on scroll ---------- */
  var revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- marquee: second copy for a seamless loop (kept out of the page text) ---------- */
  document.querySelectorAll('.marquee-track').forEach(function (track) {
    var ul = track.querySelector('ul');
    if (ul && track.children.length === 1) { var copy = ul.cloneNode(true); copy.setAttribute('aria-hidden', 'true'); track.appendChild(copy); }
  });

  /* ---------- hero crosshair with coordinate readout ---------- */
  var hero = document.querySelector('.hero');
  var xh = hero && hero.querySelector('.xhair');
  if (xh && finePointer && !reduce) {
    var xl = xh.querySelector('.xl'), yl = xh.querySelector('.yl'), ro = xh.querySelector('.ro');
    var hx = 0, hy = 0, raf = 0;
    hero.addEventListener('pointermove', function (e) {
      var r = hero.getBoundingClientRect();
      hx = e.clientX - r.left; hy = e.clientY - r.top;
      xh.classList.add('live');
      if (!raf) raf = requestAnimationFrame(function () {
        xl.style.transform = 'translateY(' + hy + 'px)';
        yl.style.transform = 'translateX(' + hx + 'px)';
        ro.style.transform = 'translate(' + hx + 'px,' + hy + 'px)';
        ro.textContent = 'X ' + String(Math.round(hx)).padStart(4, '0') + '  Y ' + String(Math.round(hy)).padStart(4, '0');
        raf = 0;
      });
    });
  }

  /* ---------- custom cursor on cards ---------- */
  if (finePointer && !reduce) {
    var cur = document.createElement('div');
    cur.className = 'cursor'; cur.setAttribute('aria-hidden', 'true');
    body.appendChild(cur);
    var mx = -200, my = -200, cx = -200, cy = -200, sc = 0, target = 0;
    document.addEventListener('pointermove', function (e) {
      mx = e.clientX; my = e.clientY;
      var t = e.target.closest && e.target.closest('[data-cursor]');
      if (t) { cur.textContent = t.getAttribute('data-cursor'); target = 1; } else target = 0;
    }, { passive: true });
    document.addEventListener('pointerleave', function () { target = 0; });
    (function loop() {
      cx += (mx - cx) * 0.2; cy += (my - cy) * 0.2; sc += (target - sc) * 0.18;
      cur.style.transform = 'translate3d(' + cx.toFixed(1) + 'px,' + cy.toFixed(1) + 'px,0) scale(' + sc.toFixed(3) + ')';
      requestAnimationFrame(loop);
    })();
  }

  /* ---------- table of contents scroll-spy (project pages) ---------- */
  var tocLinks = document.querySelectorAll('.toc a');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove('active'); });
          var a = map[en.target.id]; if (a) a.classList.add('active');
        }
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) spy.observe(s); });
  }

  /* ---------- copy email ---------- */
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    var hint = btn.querySelector('.hint');
    var original = hint ? hint.textContent : '';
    btn.addEventListener('click', function () {
      var text = btn.getAttribute('data-copy');
      function done() {
        btn.classList.add('done'); if (hint) hint.textContent = 'Copied';
        setTimeout(function () { btn.classList.remove('done'); if (hint) hint.textContent = original; }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { location.href = 'mailto:' + text; });
      } else { location.href = 'mailto:' + text; }
    });
  });

  /* ---------- local time in footer ---------- */
  var clock = document.querySelector('[data-clock]');
  if (clock && window.Intl) {
    var fmt = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York', timeZoneName: 'short' });
    var tick = function () { clock.textContent = 'Durham, NC · ' + fmt.format(new Date()); };
    tick(); setInterval(tick, 30000);
  }

  /* ---------- personal: categories (personal/categories.js) + photos (personal/gallery.js) ---------- */
  var items = (window.PERSONAL_GALLERY || []).filter(function (i) { return i && i.src; });
  var slug = function (t) { return String(t || 'personal').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); };
  var cats = (window.PERSONAL_CATEGORIES || []).map(function (c) { var o = {}; for (var k in c) o[k] = c[k]; o.key = slug(c.key || c.title); return o; });
  items.forEach(function (it) {
    var k = slug(it.category);
    if (!cats.some(function (c) { return c.key === k; })) cats.push({ key: k, title: it.category || 'Personal', blurb: '' });
  });
  cats.forEach(function (c) {
    c.items = items.filter(function (it) { return slug(it.category) === c.key; });
    c.live = c.items.length > 0 || !!c.blurb;
  });
  var hasPersonal = cats.some(function (c) { return c.live; });
  document.querySelectorAll('[data-nav="personal"]').forEach(function (a) { a.hidden = !hasPersonal; });
  var el = function (tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  /* line icons for tiles without photos, drawn like the site's diagrams */
  var ICONS = {
    volleyball: '<circle cx="50" cy="50" r="38"/><path d="M50 12c-6 14-6 30 0 38M50 50c-9 6-25 10-38 6M50 50c9 6 17 18 18 32"/><path d="M27 20c10 4 18 14 23 30M88 46c-12 6-26 6-38 4M24 80c4-12 14-24 26-30"/>',
    basketball: '<circle cx="50" cy="50" r="38"/><path d="M12 50h76M50 12v76"/><path d="M23 23c10 9 15 18 15 27s-5 18-15 27M77 23c-10 9-15 18-15 27s5 18 15 27"/>',
    music: '<path d="M36 60 H86 a5 5 0 0 1 0 10 H30"/><path d="M30 70 l-6 -3 v6 z"/><path d="M46 60 V70 M80 60 V70"/><path d="M36 60 H24 a11 11 0 0 1 0 -22 H52"/><path d="M52 36.5 C63 36 71 31 78 21 V55 C71 45 63 40 52 39.5"/><path d="M60 39.5 V60"/>',
    photography: '<rect x="14" y="30" width="72" height="48" rx="6"/><path d="M36 30l5-9h18l5 9"/><circle cx="50" cy="54" r="14"/><circle cx="50" cy="54" r="6"/>'
  };
  var countText = function (c) { return c.items.length ? c.items.length + (c.items.length === 1 ? ' photo' : ' photos') : 'Coming soon'; };
  var coverOf = function (c) {
    if (!c.items.length) return null;
    if (c.cover) { var m = c.items.filter(function (it) { return (it.orig || '').indexOf(c.cover) !== -1; })[0]; if (m) return m; }
    return c.items[0];
  };

  /* home page teaser */
  var teaser = document.getElementById('personalTeaser');
  if (teaser && hasPersonal && !teaser.hasAttribute('data-prerendered')) {
    teaser.hidden = false;
    var chips = teaser.querySelector('.pchips');
    if (chips) cats.forEach(function (c) {
      var a = el('a', 'pill', c.title); a.href = base + 'personal.html#' + c.key;
      if (!c.live) { a.removeAttribute('href'); a.classList.add('soon'); }
      chips.appendChild(a);
    });
    var strip = teaser.querySelector('.strip');
    items.slice(0, 4).forEach(function (it) {
      var a = el('a'); a.href = base + (it.full || it.src); a.setAttribute('data-lightbox', 'teaser');
      var img = el('img'); img.src = base + it.src; img.alt = it.alt || it.caption || ''; img.loading = 'lazy';
      a.appendChild(img); strip.appendChild(a);
    });
    if (!items.length) strip.hidden = true;
  }

  /* personal page */
  var tiles = document.getElementById('ptiles');
  var sections = document.getElementById('psections');
  var layouts = [];
  if (tiles && sections && sections.hasAttribute('data-prerendered')) {
    sections.querySelectorAll('.masonry').forEach(function (grid) {
      var figs = Array.prototype.slice.call(grid.querySelectorAll('figure')).map(function (f) {
        var im = f.querySelector('img'); var w = im && +im.getAttribute('width'), h = im && +im.getAttribute('height');
        f._ratio = (w && h) ? h / w : 1; return f;
      });
      layouts.push({ grid: grid, figs: figs, n: 0 });
    });
  } else if (tiles && sections) {
    cats.forEach(function (c, i) {
      var num = String(i + 1).padStart(2, '0');
      /* tile */
      var t = el(c.live ? 'a' : 'div', 'ptile' + (c.items.length ? '' : ' type'));
      if (c.live) { t.href = '#' + c.key; t.setAttribute('data-cursor', 'Open'); }
      var media = el('div', 'ptile-media');
      var cov = coverOf(c);
      if (cov) { var im = el('img'); im.src = base + cov.src; im.alt = ''; im.loading = 'lazy'; media.appendChild(im); }
      else if (ICONS[c.key]) { media.innerHTML = '<svg class="ptile-icon" viewBox="0 0 100 100" aria-hidden="true">' + ICONS[c.key] + '</svg>'; }
      t.appendChild(media);
      var meta = el('div', 'ptile-meta');
      var top = el('div', 'ptile-top');
      top.appendChild(el('span', 'num', num));
      top.appendChild(el('span', 'n', countText(c)));
      meta.appendChild(top);
      meta.appendChild(el('span', 't', c.title));
      t.appendChild(meta);
      tiles.appendChild(t);
      if (!c.live) return;
      /* section */
      var sec = el('section', 'pcat'); sec.id = c.key; sec.setAttribute('data-reveal', '');
      var head = el('div', 'pcat-head');
      var left = el('div');
      left.appendChild(el('p', 'label', c.items.length ? num + ' · ' + countText(c) : num));
      left.appendChild(el('h2', null, c.title));
      head.appendChild(left);
      var right = el('div', 'pcat-blurb');
      if (c.blurb) right.appendChild(el('p', null, c.blurb));
      if (c.link && c.link.href) {
        var l = el('a', 'pill'); l.href = base + c.link.href; l.textContent = (c.link.text || 'More') + ' ';
        l.appendChild(el('span', 'arrow', '→')); right.appendChild(l);
      }
      head.appendChild(right);
      sec.appendChild(head);
      if (c.items.length) {
        var grid = el('div', 'masonry');
        var figs = c.items.map(function (it) {
          var fig = el('figure');
          var frame = el('div', 'frame');
          var a = el('a'); a.href = base + (it.full || it.src); a.setAttribute('data-lightbox', 'p-' + c.key);
          var img = el('img'); img.src = base + it.src; img.loading = 'lazy'; img.alt = it.alt || it.caption || '';
          if (it.width && it.height) { img.width = it.width; img.height = it.height; }
          a.appendChild(img); frame.appendChild(a); fig.appendChild(frame);
          var when = '';
          if (it.taken) { var dt = new Date(it.taken + 'T12:00:00'); if (!isNaN(dt)) when = dt.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }); }
          if (it.caption || when) {
            var cap = el('figcaption');
            if (it.caption) cap.appendChild(document.createTextNode(it.caption));
            if (when) cap.appendChild(el('span', 'when', when));
            fig.appendChild(cap);
          }
          fig._ratio = (it.width && it.height) ? it.height / it.width : 1;
          return fig;
        });
        sec.appendChild(grid);
        layouts.push({ grid: grid, figs: figs, n: 0 });
      } else {
        sec.appendChild(el('p', 'pcat-soon', 'Photos coming soon.'));
      }
      sections.appendChild(sec);
    });
  }
  if (layouts.length || (sections && tiles)) {
    /* row-major masonry: each photo goes to the shortest column, so reading order
       left to right follows the sorted order */
    var layoutAll = function (force) {
      layouts.forEach(function (L) {
        var w = L.grid.clientWidth || window.innerWidth;
        var n = w >= 980 ? 3 : (w >= 560 ? 2 : 1);
        if (!force && n === L.n) return;
        L.n = n; L.grid.innerHTML = '';
        var cols = [], hs = [];
        for (var k = 0; k < n; k++) { var col = el('div', 'col'); L.grid.appendChild(col); cols.push(col); hs.push(0); }
        L.figs.forEach(function (f) { var j = hs.indexOf(Math.min.apply(null, hs)); cols[j].appendChild(f); hs[j] += f._ratio + 0.12; });
      });
    };
    layoutAll(true);
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { layoutAll(false); }, 120); });
    if ('IntersectionObserver' in window && !reduce) {
      var io2 = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io2.unobserve(en.target); } }); }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
      sections.querySelectorAll('[data-reveal]').forEach(function (s) { io2.observe(s); });
    } else { sections.querySelectorAll('[data-reveal]').forEach(function (s) { s.classList.add('in'); }); }
    var hashEl = location.hash && document.getElementById(location.hash.slice(1));
    if (hashEl) setTimeout(function () { hashEl.scrollIntoView(); }, 60);
  }

  /* ---------- lightbox ---------- */
  var dlg = document.getElementById('lightbox');
  if (dlg && typeof dlg.showModal === 'function') {
    var lbImg = dlg.querySelector('img'), lbCap = dlg.querySelector('.lb-cap');
    var group = [], index = 0;
    var captionFor = function (a) {
      if (a.getAttribute('data-caption')) return a.getAttribute('data-caption');
      var fig = a.closest('figure'); var cap = fig && fig.querySelector('figcaption');
      if (!cap) { var im = a.querySelector('img'); return im ? im.alt : ''; }
      var num = cap.querySelector('b'); var all = cap.textContent.trim();
      return num ? num.textContent + '  ' + all.slice(num.textContent.length).trim() : all;
    };
    var show = function (i) {
      index = (i + group.length) % group.length;
      var a = group[index]; var im = a.querySelector('img');
      dlg.classList.remove('zoomed'); dlg.classList.add('no-zoom');
      lbImg.onload = function () { dlg.classList.toggle('no-zoom', lbImg.naturalWidth < lbImg.clientWidth * 1.2); };
      lbImg.src = a.getAttribute('href'); lbImg.alt = im ? im.alt : '';
      lbCap.textContent = captionFor(a);
      dlg.querySelectorAll('[data-step]').forEach(function (b) { b.hidden = group.length < 2; });
    };
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a[data-lightbox]');
      if (!a || !a.getAttribute('href') || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      var name = a.getAttribute('data-lightbox');
      group = Array.prototype.filter.call(document.querySelectorAll('a[data-lightbox="' + name + '"]'), function (x) {
        return x.getAttribute('href') && !x.closest('[hidden]');
      });
      show(group.indexOf(a)); dlg.showModal();
    });
    lbImg.addEventListener('click', function (e) {
      e.stopPropagation();
      if (dlg.classList.contains('no-zoom')) return;
      if (dlg.classList.contains('zoomed')) { dlg.classList.remove('zoomed'); return; }
      var r = lbImg.getBoundingClientRect();
      var fx = (e.clientX - r.left) / r.width, fy = (e.clientY - r.top) / r.height;
      dlg.classList.add('zoomed');
      dlg.scrollLeft = fx * lbImg.naturalWidth - e.clientX;
      dlg.scrollTop = fy * lbImg.naturalHeight - e.clientY;
    });
    dlg.addEventListener('click', function (e) {
      var step = e.target.closest('[data-step]');
      if (step) { show(index + Number(step.getAttribute('data-step'))); return; }
      if (e.target.closest('[data-close]') || (!dlg.classList.contains('zoomed') && (e.target === dlg || e.target.classList.contains('lb-inner')))) dlg.close();
    });
    document.addEventListener('keydown', function (e) {
      if (!dlg.open || group.length < 2) return;
      if (e.key === 'ArrowRight') show(index + 1);
      if (e.key === 'ArrowLeft') show(index - 1);
    });
    dlg.addEventListener('close', function () { lbImg.removeAttribute('src'); dlg.classList.remove('zoomed'); });
  }
})();

/* organization logos: if a logo file exists, show it instead of the typeset name */
(function () {
  document.querySelectorAll('img[data-logo]').forEach(function (img) {
    var org = img.closest('.org');
    var ok = function () { if (img.naturalWidth && org) org.classList.add('has-logo'); };
    if (img.complete) ok(); else img.addEventListener('load', ok);
  });
})();

/* ---------- present mode, for screen sharing in interviews ----------
   Press P (or open any page with ?present). Stops all motion, enlarges text, keeps the
   menu visible, forces the light theme, and makes the arrow keys move section by section.
   It stays on across pages until you press P again (or open ?present=0). */
(function () {
  var doc = document.documentElement, KEY = 'by-present';
  var store = function (on) { try { on ? sessionStorage.setItem(KEY, '1') : sessionStorage.removeItem(KEY); } catch (e) {} };
  var toast = document.createElement('div'); toast.className = 'present-toast'; toast.setAttribute('role', 'status');
  document.body.appendChild(toast);
  var tt;
  var say = function (html) { toast.innerHTML = html; toast.classList.add('show'); clearTimeout(tt); tt = setTimeout(function () { toast.classList.remove('show'); }, 3200); };
  var set = function (on) {
    doc.classList.toggle('present', on);
    if (on) doc.setAttribute('data-theme', 'light'); else doc.removeAttribute('data-theme');
    store(on);
    say(on ? 'Present mode on: <kbd>←</kbd><kbd>→</kbd> move between sections, <kbd>P</kbd> turns it off'
           : 'Present mode off');
  };
  var stops = function () {
    var els = Array.prototype.slice.call(document.querySelectorAll(
      'main > section, main > div > .p-lead, .p-body .glance, .p-sec, .pcat, .next, .site-footer'));
    return els.filter(function (el) { return el.offsetParent !== null && !el.closest('[hidden]'); });
  };
  var go = function (dir) {
    var header = document.querySelector('.site-header');
    var off = (header ? header.offsetHeight : 0) + 16;
    var list = stops().map(function (el) { return { el: el, top: el.getBoundingClientRect().top - off }; })
                      .sort(function (a, b) { return a.top - b.top; });
    var target = null;
    if (dir > 0) { for (var i = 0; i < list.length; i++) if (list[i].top > 24) { target = list[i]; break; } }
    else { for (var j = list.length - 1; j >= 0; j--) if (list[j].top < -24) { target = list[j]; break; } }
    if (!target) { window.scrollTo({ top: dir > 0 ? document.documentElement.scrollHeight : 0, behavior: 'smooth' }); return; }
    window.scrollTo({ top: window.scrollY + target.top, behavior: 'smooth' });
  };
  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey || e.defaultPrevented) return;
    var t = e.target; if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    var lb = document.getElementById('lightbox'); if (lb && lb.open) return;
    if (e.key === 'p' || e.key === 'P') { set(!doc.classList.contains('present')); return; }
    if (!doc.classList.contains('present')) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'PageDown' || (e.key === ' ' && !e.shiftKey)) { e.preventDefault(); go(1); }
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp' || (e.key === ' ' && e.shiftKey)) { e.preventDefault(); go(-1); }
  });
  if (doc.classList.contains('present')) setTimeout(function () { say('Present mode: <kbd>←</kbd><kbd>→</kbd> move between sections, <kbd>P</kbd> turns it off'); }, 400);
})();
