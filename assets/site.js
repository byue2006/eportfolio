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
    doc.setAttribute('data-theme', on ? 'light' : (window.byTheme ? window.byTheme() : 'dark'));
    if (window.byThemeLabel) window.byThemeLabel();
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
    if (t && t.closest && t.closest('.stage')) return;  // keys belong to the 3D viewer / video player
    if (e.key === 'p' || e.key === 'P') { set(!doc.classList.contains('present')); return; }
    if (!doc.classList.contains('present')) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'PageDown' || (e.key === ' ' && !e.shiftKey)) { e.preventDefault(); go(1); }
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp' || (e.key === ' ' && e.shiftKey)) { e.preventDefault(); go(-1); }
  });
  if (doc.classList.contains('present')) setTimeout(function () { say('Present mode: <kbd>←</kbd><kbd>→</kbd> move between sections, <kbd>P</kbd> turns it off'); }, 400);
})();

/* ---------- 3D models and video ---------- */
(function () {
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function full(el) {
    if (document.fullscreenElement) { document.exitFullscreen(); return; }
    if (el.requestFullscreen) el.requestFullscreen(); else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    else { var v = el.querySelector('video'); if (v && v.webkitEnterFullscreen) v.webkitEnterFullscreen(); }
  }
  function pauseOthers(me) {
    Array.prototype.forEach.call(document.querySelectorAll('.vid:not(.loop) video'), function (v) { if (v !== me) v.pause(); });
    Array.prototype.forEach.call(document.querySelectorAll('.vid iframe'), function (f) { if (f !== me) f.closest('.vid').reset(); });
  }

  Array.prototype.forEach.call(document.querySelectorAll('.m3d'), function (fig) {
    var mv = fig.querySelector('model-viewer'); if (!mv) return;
    var stage = fig.querySelector('.stage'), home = mv.getAttribute('camera-orbit');
    var spin = fig.querySelector('[data-act="rotate"]');
    function setSpin(on) { mv.autoRotate = on; if (!on) mv.removeAttribute('auto-rotate'); spin.setAttribute('aria-pressed', on ? 'true' : 'false'); }
    if (reduce) setSpin(false);
    mv.addEventListener('progress', function (e) { fig.style.setProperty('--p', e.detail.totalProgress); });
    mv.addEventListener('load', function () { fig.classList.add('is-loaded'); });
    mv.addEventListener('camera-change', function (e) { if (e.detail.source === 'user-interaction') fig.classList.add('is-touched'); });
    mv.addEventListener('pointerdown', function () { setSpin(false); });
    fig.querySelector('.ctl').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var a = b.getAttribute('data-act');
      if (a === 'rotate') setSpin(!mv.autoRotate);
      else if (a === 'in' || a === 'out') {
        var o = mv.getCameraOrbit();
        mv.cameraOrbit = o.theta + 'rad ' + o.phi + 'rad ' + (o.radius * (a === 'in' ? 0.8 : 1.25)) + 'm';
      } else if (a === 'reset') { mv.cameraOrbit = home; mv.cameraTarget = 'auto auto auto'; mv.fieldOfView = 'auto'; mv.resetTurntableRotation && mv.resetTurntableRotation(0); }
      else if (a === 'full') full(stage);
    });
  });

  Array.prototype.forEach.call(document.querySelectorAll('.vid'), function (fig) {
    var stage = fig.querySelector('.stage'), v = fig.querySelector('video'), start = fig.querySelector('.start');
    var fb = fig.querySelector('[data-act="full"]');
    if (fb) fb.addEventListener('click', function () { full(stage); });
    if (fig.classList.contains('loop')) {
      var btn = fig.querySelector('[data-act="pause"]'), wanted = !reduce;
      function sync() {
        var playing = !v.paused;
        btn.setAttribute('aria-label', playing ? 'Pause video' : 'Play video'); btn.title = btn.getAttribute('aria-label');
        btn.innerHTML = playing ? '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M8 5v14M16 5v14"/></svg>'
                                : '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg>';
      }
      v.addEventListener('play', sync); v.addEventListener('pause', sync); sync();
      btn.addEventListener('click', function () { wanted = v.paused; if (wanted) v.play(); else v.pause(); });
      if ('IntersectionObserver' in window) new IntersectionObserver(function (es) {
        es.forEach(function (en) {
          if (en.isIntersecting && wanted) { v.preload = 'auto'; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
          else if (!en.isIntersecting) v.pause();
        });
      }, { threshold: 0.35 }).observe(fig);
      return;
    }
    fig.reset = function () {  // YouTube: swap the player back for the poster
      var f = stage.querySelector('iframe'); if (f) f.remove(); fig.classList.remove('is-playing');
    };
    start.addEventListener('click', function () {
      var id = start.getAttribute('data-yt');
      pauseOthers(null);
      fig.classList.add('is-playing'); stage.removeAttribute('data-cursor');
      if (id) {
        var f = document.createElement('iframe');
        f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0&playsinline=1';
        f.title = start.getAttribute('aria-label').replace(/^Play video: /, '');
        f.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture'; f.allowFullscreen = true;
        f.referrerPolicy = 'strict-origin-when-cross-origin';
        stage.appendChild(f); f.focus();
        return;
      }
      v.controls = true; v.preload = 'auto'; v.focus();
      var p = v.play(); if (p && p.catch) p.catch(function () {});
    });
    if (v) v.addEventListener('play', function () { pauseOthers(v); });
  });
})();

/* ---------- theme switch: dark by default; a visitor's choice is remembered ---------- */
(function () {
  var doc = document.documentElement, meta = document.querySelector('meta[name="theme-color"]');
  window.byTheme = function () { var t = null; try { t = localStorage.getItem('by-theme'); } catch (e) {} return t === 'light' ? 'light' : 'dark'; };
  window.byThemeLabel = function () {
    var dark = doc.getAttribute('data-theme') === 'dark', t = dark ? 'Switch to light theme' : 'Switch to dark theme';
    Array.prototype.forEach.call(document.querySelectorAll('.theme-btn'), function (b) { b.setAttribute('aria-label', t); b.title = t; });
    if (meta) meta.content = dark ? '#0b0c0d' : '#f5f5f2';
  };
  document.addEventListener('click', function (e) {
    if (!e.target.closest || !e.target.closest('.theme-btn')) return;
    var next = doc.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    doc.setAttribute('data-theme', next);
    try { localStorage.setItem('by-theme', next); } catch (err) {}
    window.byThemeLabel();
  });
  window.byThemeLabel();
})();

/* Animated card posters (Smaller work). Each card runs a small physics loop while hovered (or focused, or on screen on
   touch devices): an RK4 orbit with drag (ISS), a spring-loaded snap-fit you push with the cursor, and a shuttle that
   banks toward the cursor through a starfield. Pointer input is smoothed (critically damped), so motion eases instead of
   jumping. Nothing runs under prefers-reduced-motion; at rest every card shows a still frame. */
(function () {
  var els = document.querySelectorAll('.media.anim[data-anim]');
  if (!els.length) return;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var canHover = window.matchMedia && matchMedia('(hover: hover)').matches;
  var NS = 'http://www.w3.org/2000/svg';
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ease(cur, tgt, rate, dt) { return cur + (tgt - cur) * (1 - Math.exp(-rate * dt)); }

  var SIMS = {
    /* ---- ISS: gravity + exponential-atmosphere drag, integrated with RK4 (the same method as the project) ---- */
    iss: function (el, st) {
      var svg = el.querySelector('svg'), stn = svg.querySelector('.iss-st'), dot = svg.querySelector('.iss-dot'),
          flare = svg.querySelector('.iss-flare'), segs = svg.querySelectorAll('.iss-trail line'), alt = el.querySelector('.alt');
      var CX = 250, CY = 200, R0 = 138, RA = 91, MU = Math.pow(2 * Math.PI * R0 / 1.7, 2) * R0, K = 0.00034, H = 17.5;
      var s, trail = [], boom = 0, acc = 0, rest = -40 * Math.PI / 180;
      function reset(a) { var v = Math.sqrt(MU / R0); s = [R0 * Math.sin(a), -R0 * Math.cos(a), v * Math.cos(a), v * Math.sin(a)]; trail = []; }
      function f(y) {
        var r = Math.sqrt(y[0] * y[0] + y[1] * y[1]), g = -MU / (r * r * r), sp = Math.sqrt(y[2] * y[2] + y[3] * y[3]),
            d = K * Math.exp(-(r - RA) / H) * sp;
        return [y[2], y[3], g * y[0] - d * y[2], g * y[1] - d * y[3]];
      }
      function rk4(h) {
        var k1 = f(s), y2 = [], y3 = [], y4 = [], i;
        for (i = 0; i < 4; i++) y2[i] = s[i] + h / 2 * k1[i];
        var k2 = f(y2); for (i = 0; i < 4; i++) y3[i] = s[i] + h / 2 * k2[i];
        var k3 = f(y3); for (i = 0; i < 4; i++) y4[i] = s[i] + h * k3[i];
        var k4 = f(y4); for (i = 0; i < 4; i++) s[i] += h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
      }
      reset(rest);
      return {
        step: function (dt) {
          var live = st.on || st.auto;
          if (boom > 0) { boom -= dt / 0.9; if (boom <= 0) { boom = 0; reset(Math.random() * Math.PI * 2); } return true; }
          if (!live) return false;
          var h = 1 / 240, n = Math.ceil(dt / h);
          for (var i = 0; i < n; i++) {
            rk4(dt / n);
            acc += dt / n;
            if (acc >= 1 / 60) { acc = 0; trail.push([s[0], s[1]]); if (trail.length > segs.length + 1) trail.shift(); }
            if (s[0] * s[0] + s[1] * s[1] < RA * RA) { boom = 1; break; }
          }
          return true;
        },
        draw: function () {
          var r = Math.sqrt(s[0] * s[0] + s[1] * s[1]), heat = clamp((R0 - r) / (R0 - RA), 0, 1);
          stn.setAttribute('transform', 'translate(' + (CX + s[0]).toFixed(1) + ' ' + (CY + s[1]).toFixed(1) + ')');
          var hot = Math.pow(heat, 2.2);
          dot.style.fill = 'rgb(' + Math.round(237 + 3 * hot) + ',' + Math.round(237 - 99 * hot) + ',' + Math.round(235 - 160 * hot) + ')';
          var fl = boom > 0 ? Math.sin(boom * Math.PI) : hot * 0.35;
          flare.setAttribute('opacity', fl.toFixed(3));
          flare.setAttribute('r', (9 + 19 * (boom > 0 ? 1 - boom : hot)).toFixed(1));
          dot.setAttribute('opacity', boom > 0 ? boom.toFixed(3) : 1);
          var n = trail.length;
          for (var i = 0; i < segs.length; i++) {
            var a = trail[n - 2 - i], b = trail[n - 1 - i], ln = segs[i];
            if (!a || !b || boom > 0.6) { ln.setAttribute('opacity', 0); continue; }
            var k = 1 - i / segs.length;
            ln.setAttribute('x1', (CX + a[0]).toFixed(1)); ln.setAttribute('y1', (CY + a[1]).toFixed(1));
            ln.setAttribute('x2', (CX + b[0]).toFixed(1)); ln.setAttribute('y2', (CY + b[1]).toFixed(1));
            ln.setAttribute('opacity', (0.55 * k * k * (boom > 0 ? boom : 1)).toFixed(3));
            ln.setAttribute('stroke-width', (0.6 + 3.2 * k).toFixed(2));
          }
          if (alt) alt.textContent = boom > 0 ? '120' : Math.round(120 + clamp((r - RA) / (R0 - RA), 0, 1) * 300);
        }
      };
    },

    /* ---- Snap-fit: the cube follows the cursor on a spring; the arms ride the tabs, then spring back (and ring) ---- */
    snap: function (el, st) {
      var svg = el.querySelector('svg'), cube = svg.querySelector('.cube'), arms = svg.querySelectorAll('.arm'),
          strains = svg.querySelectorAll('.arm-strain'), rings = svg.querySelectorAll('.snapring'), eps = svg.querySelector('.eps');
      var x = 0, v = 0, th = 0, w = 0, dir = -1, contact = false, ring = 0, autoT = 0;
      var OUT = 280, INNER = 43, OUTER = 212, RAMP = 22, MAXD = -4.5;
      return {
        step: function (dt) {
          var target = 0;
          if (st.on) target = clamp((st.tx + 0.55) / 1.4, 0, 1) * OUT;                    // cursor left = push in, right = pull out
          else if (st.auto) { autoT += dt; target = Math.floor(autoT / 1.9) % 2 ? OUT : 0; }
          var n = Math.ceil(dt / (1 / 240)), h = dt / n;
          for (var i = 0; i < n; i++) {
            var a = 160 * (target - x) - 2 * Math.sqrt(160) * 0.82 * v;                 // slightly underdamped spring
            v += a * h; x += v * h;
            if (Math.abs(v) > 3) dir = v < 0 ? -1 : 1;
            var amt = 0;
            if (x > INNER && x < OUTER) amt = dir < 0 ? Math.min(1, (OUTER - x) / RAMP) : Math.min(1, (x - INNER) / RAMP);
            if (amt > 0) { var g = MAXD * amt; w = (g - th) / h; th = g; contact = true; }
            else {
              if (contact) { contact = false; ring = 1; }
              var aa = -1100 * th - 2 * Math.sqrt(1100) * 0.11 * w;                        // the arm snaps back and rings down
              w += aa * h; th += w * h;
            }
          }
          ring = Math.max(0, ring - dt * 2.4);
          return Math.abs(x - target) > 0.3 || Math.abs(v) > 0.5 || Math.abs(th) > 0.02 || Math.abs(w) > 0.2 || ring > 0;
        },
        draw: function () {
          cube.setAttribute('transform', 'translate(' + x.toFixed(2) + ' 0)');
          for (var i = 0; i < arms.length; i++) arms[i].setAttribute('transform', 'rotate(' + th.toFixed(3) + ' 122 107)');
          var sv = clamp(-th / -MAXD, 0, 1);
          for (i = 0; i < strains.length; i++) strains[i].setAttribute('opacity', sv.toFixed(3));
          for (i = 0; i < rings.length; i++) { rings[i].setAttribute('opacity', (ring * 0.95).toFixed(3)); rings[i].setAttribute('r', (6 + (1 - ring) * 26).toFixed(1)); }
          eps.style.opacity = (0.5 + 0.5 * sv).toFixed(3);
        }
      };
    },

    /* ---- Vanguard: throttle spools up, three plumes flicker, stars stream past, the ship banks toward the cursor ---- */
    fly: function (el, st) {
      var cv = el.querySelector('canvas'), ctx = cv.getContext('2d'), ship = el.querySelector('.ship'),
          plumes = el.querySelectorAll('.plume'), thrEl = el.querySelector('.thr');
      var stars = [], thr = 0, t = 0, W = 0, Hh = 0, dx = Math.cos(15 * Math.PI / 180), dy = Math.sin(15 * Math.PI / 180);
      for (var i = 0; i < 70; i++) stars.push({ x: Math.random(), y: Math.random(), z: 0.25 + Math.random() * 0.75 });
      function size() {
        var r = cv.getBoundingClientRect(), d = Math.min(2, window.devicePixelRatio || 1);
        if (Math.round(r.width * d) !== cv.width || Math.round(r.height * d) !== cv.height) {
          cv.width = Math.round(r.width * d); cv.height = Math.round(r.height * d);
        }
        W = cv.width; Hh = cv.height;
      }
      return {
        step: function (dt) {
          t += dt;
          var want = (st.on || st.auto) ? 0.78 + 0.22 * clamp((st.sx + 1) / 2, 0, 1) : 0;   // cursor toward the plume side = more thrust
          thr = ease(thr, want, want > thr ? 2.6 : 3.4, dt);
          var sp = 0.025 + 0.85 * thr;
          for (var i = 0; i < stars.length; i++) {
            var p = stars[i];
            p.x += dx * sp * p.z * dt; p.y += dy * sp * p.z * dt * 1.25;
            if (p.x > 1.05 || p.y > 1.05) { if (Math.random() < 0.5) { p.x = -0.05; p.y = Math.random(); } else { p.x = Math.random(); p.y = -0.05; } }
          }
          return thr > 0.004 || st.on || st.auto;
        },
        draw: function () {
          size();
          ctx.clearRect(0, 0, W, Hh);
          var sp = 0.025 + 0.85 * thr;
          ctx.lineCap = 'round';
          for (var i = 0; i < stars.length; i++) {
            var p = stars[i], x = p.x * W, y = p.y * Hh, len = (2 + sp * p.z * 90) * (W / 500);
            ctx.strokeStyle = 'rgba(255,255,255,' + (0.18 + 0.5 * p.z).toFixed(3) + ')';
            ctx.lineWidth = (0.6 + p.z) * (W / 500);
            ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - dx * len, y - dy * len); ctx.stroke();
          }
          var bank = st.sy * 4 + Math.sin(t * 1.4) * 0.8 * thr, lift = st.sy * 2.2 + Math.sin(t * 1.1) * 0.9 * thr;
          ship.style.transform = 'translate(' + (-st.sx * 1.6 - thr * 1.2).toFixed(2) + '%,' + lift.toFixed(2) + '%) rotate(' + bank.toFixed(2) + 'deg)';
          for (var j = 0; j < plumes.length; j++) {
            var fl = 0.86 + 0.09 * Math.sin(t * 37 + j * 2.1) + 0.06 * Math.sin(t * 61 + j * 1.3) + 0.05 * Math.sin(t * 13 + j);
            plumes[j].style.transform = 'rotate(var(--na)) scaleX(' + (thr * fl).toFixed(3) + ') scaleY(' + (0.75 + 0.25 * thr).toFixed(3) + ')';
            plumes[j].style.opacity = Math.min(1, thr * 1.4).toFixed(3);
          }
          if (thrEl) thrEl.textContent = Math.round(thr * 100);
        }
      };
    }
  };

  els.forEach(function (el) {
    var kind = el.getAttribute('data-anim'), card = el.closest('.card') || el;
    var st = { on: false, auto: false, tx: 0, ty: 0, sx: 0, sy: 0, vx: 0, vy: 0, raf: 0, last: 0 };
    var sim = SIMS[kind] && SIMS[kind](el, st);
    if (!sim) return;
    sim.draw();
    if (reduce) return;
    function loop(now) {
      var dt = st.last ? Math.min(0.05, (now - st.last) / 1000) : 1 / 60; st.last = now;
      // critically damped follow of the pointer (smooth, no overshoot), like a lerp but frame-rate independent
      var k = 60, c = 2 * Math.sqrt(k);
      st.vx += (k * (st.tx - st.sx) - c * st.vx) * dt; st.sx += st.vx * dt;
      st.vy += (k * (st.ty - st.sy) - c * st.vy) * dt; st.sy += st.vy * dt;
      el.style.setProperty('--px', st.sx.toFixed(4)); el.style.setProperty('--py', st.sy.toFixed(4));
      var busy = sim.step(dt);
      sim.draw();
      var moving = Math.abs(st.tx - st.sx) > 0.002 || Math.abs(st.ty - st.sy) > 0.002 || Math.abs(st.vx) + Math.abs(st.vy) > 0.004;
      if (st.on || st.auto || busy || moving) st.raf = requestAnimationFrame(loop);
      else { st.raf = 0; st.last = 0; }
    }
    function kick() { if (!st.raf) st.raf = requestAnimationFrame(loop); }
    function point(e) {
      var r = el.getBoundingClientRect();
      st.tx = clamp((e.clientX - r.left) / r.width * 2 - 1, -1, 1); st.ty = clamp((e.clientY - r.top) / r.height * 2 - 1, -1, 1);
      el.style.setProperty('--mx', (e.clientX - r.left).toFixed(0) + 'px'); el.style.setProperty('--my', (e.clientY - r.top).toFixed(0) + 'px');
    }
    card.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse' || e.pointerType === 'pen') { st.on = true; point(e); kick(); } });
    card.addEventListener('pointermove', function (e) { if (st.on) { point(e); kick(); } });
    card.addEventListener('pointerleave', function () { st.on = false; st.tx = 0; st.ty = 0; kick(); });
    card.addEventListener('focusin', function () { st.auto = true; kick(); });
    card.addEventListener('focusout', function () { st.auto = false; kick(); });
    if (!canHover && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { st.auto = es[0].isIntersecting; kick(); }, { threshold: 0.55 }).observe(card);
    }
  });
})();
