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
      if (!menuOpen && y > 240 && y > lastY + 4) header.classList.add('hide');
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

  /* ---------- personal gallery ---------- */
  var items = (window.PERSONAL_GALLERY || []).filter(function (i) { return i && i.src; });
  document.querySelectorAll('[data-nav="personal"]').forEach(function (a) { a.hidden = !items.length; });
  var teaser = document.getElementById('personalTeaser');
  if (teaser && items.length) {
    teaser.hidden = false;
    var strip = teaser.querySelector('.strip');
    items.slice(0, 4).forEach(function (it) {
      var a = document.createElement('a');
      a.href = base + (it.full || it.src); a.setAttribute('data-lightbox', 'teaser');
      var img = document.createElement('img'); img.src = base + it.src; img.alt = it.alt || it.caption || ''; img.loading = 'lazy';
      a.appendChild(img); strip.appendChild(a);
    });
  }
  var grid = document.getElementById('masonry');
  if (grid) {
    var filters = document.getElementById('filters');
    var empty = document.getElementById('emptyGallery');
    if (!items.length) { if (empty) empty.hidden = false; if (filters) filters.hidden = true; }
    var cats = [], figs = [];
    items.forEach(function (it) {
      var cat = it.category || 'Personal';
      if (cats.indexOf(cat) === -1) cats.push(cat);
      var fig = document.createElement('figure'); fig.setAttribute('data-cat', cat);
      var frame = document.createElement('div'); frame.className = 'frame';
      var a = document.createElement('a'); a.href = base + (it.full || it.src); a.setAttribute('data-lightbox', 'personal');
      var img = document.createElement('img'); img.src = base + it.src; img.loading = 'lazy'; img.alt = it.alt || it.caption || '';
      if (it.width && it.height) { img.width = it.width; img.height = it.height; }
      a.appendChild(img); frame.appendChild(a); fig.appendChild(frame);
      var when = '';
      if (it.taken) {
        var dt = new Date(it.taken + 'T12:00:00');
        if (!isNaN(dt)) when = dt.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      }
      if (it.caption || when) {
        var c = document.createElement('figcaption');
        if (it.caption) c.appendChild(document.createTextNode(it.caption));
        if (when) { var w = document.createElement('span'); w.className = 'when'; w.textContent = when; c.appendChild(w); }
        fig.appendChild(c);
      }
      fig._ratio = (it.width && it.height) ? it.height / it.width : 1;
      figs.push(fig);
    });
    /* row-major masonry: each item goes to the shortest column, so reading order
       left-to-right matches the sorted order (newest first) */
    var lastCols = 0;
    var layout = function (force) {
      var w = grid.clientWidth || window.innerWidth;
      var n = w >= 980 ? 3 : (w >= 560 ? 2 : 1);
      if (!force && n === lastCols) return;
      lastCols = n;
      grid.innerHTML = '';
      var cols = [], hs = [];
      for (var k = 0; k < n; k++) { var c = document.createElement('div'); c.className = 'col'; grid.appendChild(c); cols.push(c); hs.push(0); }
      figs.forEach(function (f) {
        if (f.hidden) return;
        var j = hs.indexOf(Math.min.apply(null, hs));
        cols[j].appendChild(f); hs[j] += f._ratio + 0.12;
      });
    };
    layout(true);
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { layout(false); }, 120); });
    if (filters && cats.length > 1) {
      var counts = { All: items.length };
      items.forEach(function (it) { var k = it.category || 'Personal'; counts[k] = (counts[k] || 0) + 1; });
      ['All'].concat(cats).forEach(function (c, i) {
        var b = document.createElement('button'); b.type = 'button'; b.textContent = c + ' ';
        var n = document.createElement('span'); n.className = 'count'; n.textContent = counts[c]; b.appendChild(n);
        b.setAttribute('aria-pressed', i === 0 ? 'true' : 'false');
        b.addEventListener('click', function () {
          filters.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
          b.setAttribute('aria-pressed', 'true');
          figs.forEach(function (f) { f.hidden = !(c === 'All' || f.getAttribute('data-cat') === c); });
          layout(true);
        });
        filters.appendChild(b);
      });
    } else if (filters) { filters.hidden = true; }
  }

  /* ---------- lightbox ---------- */
  var dlg = document.getElementById('lightbox');
  if (dlg && typeof dlg.showModal === 'function') {
    var lbImg = dlg.querySelector('img'), lbCap = dlg.querySelector('.lb-cap');
    var group = [], index = 0;
    var captionFor = function (a) {
      var fig = a.closest('figure'); var cap = fig && fig.querySelector('figcaption');
      if (!cap) { var im = a.querySelector('img'); return im ? im.alt : ''; }
      var num = cap.querySelector('b'); var all = cap.textContent.trim();
      return num ? num.textContent + '  ' + all.slice(num.textContent.length).trim() : all;
    };
    var show = function (i) {
      index = (i + group.length) % group.length;
      var a = group[index]; var im = a.querySelector('img');
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
    dlg.addEventListener('click', function (e) {
      var step = e.target.closest('[data-step]');
      if (step) { show(index + Number(step.getAttribute('data-step'))); return; }
      if (e.target.closest('[data-close]') || e.target === dlg || e.target.classList.contains('lb-inner')) dlg.close();
    });
    document.addEventListener('keydown', function (e) {
      if (!dlg.open || group.length < 2) return;
      if (e.key === 'ArrowRight') show(index + 1);
      if (e.key === 'ArrowLeft') show(index - 1);
    });
    dlg.addEventListener('close', function () { lbImg.removeAttribute('src'); });
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
