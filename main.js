/* Floor Candy — lean vanilla JS. No libraries.
   Everything here is progressive enhancement: the site works without it. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Header scroll state ---------- */
  var hdr = document.querySelector('.hdr');
  if (hdr) {
    var stuck = false;
    var onScroll = function () {
      var s = window.scrollY > 24;
      if (s !== stuck) { stuck = s; hdr.classList.toggle('is-stuck', s); }
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- Mobile drawer ---------- */
  var burger = document.getElementById('burger');
  var drawer = document.getElementById('drawer');
  if (burger && drawer) {
    var setOpen = function (open) {
      burger.setAttribute('aria-expanded', String(open));
      drawer.classList.toggle('is-open', open);
      document.documentElement.style.overflow = open ? 'hidden' : '';
      if (open) {
        var first = drawer.querySelector('a');
        if (first) first.focus({ preventScroll: true });
      }
    };
    burger.addEventListener('click', function () {
      setOpen(burger.getAttribute('aria-expanded') !== 'true');
    });
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') {
        setOpen(false); burger.focus();
      }
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var revealables = document.querySelectorAll('[data-reveal]');
  if (revealables.length) {
    if (reduced || !('IntersectionObserver' in window)) {
      revealables.forEach(function (el) { el.classList.add('is-in'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
      revealables.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---------- Hero video: only load when it exists and conditions allow ---------- */
  var hv = document.getElementById('heroVideo');
  if (hv) {
    var src = hv.getAttribute('data-src');
    var conn = navigator.connection || {};
    var saveData = conn.saveData === true;
    var slow = /(^|-)2g$/.test(conn.effectiveType || '');
    var small = window.matchMedia('(max-width: 860px)').matches;
    if (src && !reduced && !saveData && !slow && !small) {
      // Poster stays as LCP; video is attached after load so it never blocks.
      var attach = function () {
        hv.src = src;
        hv.load();
        var p = hv.play();
        if (p && p.catch) p.catch(function () { hv.remove(); });
        hv.addEventListener('playing', function () { hv.classList.add('is-playing'); }, { once: true });
        hv.addEventListener('error', function () { hv.remove(); });
      };
      if (document.readyState === 'complete') setTimeout(attach, 240);
      else window.addEventListener('load', function () { setTimeout(attach, 240); });
    } else {
      hv.remove();
    }
  }

  /* ---------- Before/after slider (only initialised where genuine matched pairs exist) ---------- */
  document.querySelectorAll('[data-ba]').forEach(function (el) {
    var handle = el.querySelector('.ba-handle');
    if (!handle) return;
    var set = function (pct) {
      pct = Math.max(0, Math.min(100, pct));
      el.style.setProperty('--pos', pct + '%');
      handle.setAttribute('aria-valuenow', String(Math.round(pct)));
    };
    var fromEvent = function (e) {
      var r = el.getBoundingClientRect();
      var x = (e.touches ? e.touches[0].clientX : e.clientX) - r.left;
      set((x / r.width) * 100);
    };
    var dragging = false;
    var start = function (e) { dragging = true; fromEvent(e); };
    var move = function (e) { if (dragging) { fromEvent(e); if (e.cancelable) e.preventDefault(); } };
    var end = function () { dragging = false; };
    el.addEventListener('mousedown', start);
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', end);
    el.addEventListener('touchstart', start, { passive: true });
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('touchend', end);
    handle.addEventListener('keydown', function (e) {
      var cur = parseFloat(el.style.getPropertyValue('--pos')) || 50;
      if (e.key === 'ArrowLeft') { set(cur - 4); e.preventDefault(); }
      if (e.key === 'ArrowRight') { set(cur + 4); e.preventDefault(); }
      if (e.key === 'Home') { set(0); e.preventDefault(); }
      if (e.key === 'End') { set(100); e.preventDefault(); }
    });
    set(50);
  });

  /* ---------- Attribution capture (UTM / GCLID / referrer) ---------- */
  var STORE = 'fc_attr';
  (function captureAttribution() {
    try {
      var qs = new URLSearchParams(location.search);
      var keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid', 'msclkid'];
      var found = {};
      keys.forEach(function (k) { if (qs.get(k)) found[k] = qs.get(k); });
      var existing = JSON.parse(sessionStorage.getItem(STORE) || '{}');
      if (!existing.landing_page) found.landing_page = location.pathname;
      if (!existing.referrer) found.referrer = document.referrer || 'direct';
      if (Object.keys(found).length) {
        sessionStorage.setItem(STORE, JSON.stringify(Object.assign(existing, found)));
      }
    } catch (e) { /* storage unavailable — non-fatal */ }
  })();

  function attribution() {
    try { return JSON.parse(sessionStorage.getItem(STORE) || '{}'); }
    catch (e) { return {}; }
  }

  /* ---------- Multi-step assessment form ---------- */
  var form = document.getElementById('assessmentForm');
  if (form) {
    var panels = Array.prototype.slice.call(form.querySelectorAll('.fs'));
    var bar = form.querySelector('.steps-bar');
    var counter = bar ? bar.querySelector('span') : null;
    var ticks = bar ? Array.prototype.slice.call(bar.querySelectorAll('i')) : [];
    var idx = 0;

    var paint = function () {
      panels.forEach(function (p, i) { p.hidden = i !== idx; });
      ticks.forEach(function (t, i) { t.classList.toggle('is-done', i <= idx); });
      if (counter) counter.textContent = 'Step ' + (idx + 1) + ' of ' + panels.length;
      var h = panels[idx].querySelector('.fs-title');
      if (h) h.focus({ preventScroll: true });
    };

    var validate = function (panel) {
      var ok = true;
      panel.querySelectorAll('[required]').forEach(function (f) {
        var slot = panel.querySelector('[data-err="' + f.name + '"]');
        var bad = false, msg = '';
        if (f.type === 'radio') {
          bad = !form.querySelector('input[name="' + f.name + '"]:checked');
          msg = 'Please choose an option.';
        } else if (!f.value.trim()) {
          bad = true; msg = 'This field is required.';
        } else if (f.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value)) {
          bad = true; msg = 'Please enter a valid email address.';
        } else if (f.type === 'tel' && f.value.replace(/[^\d]/g, '').length < 8) {
          bad = true; msg = 'Please enter a valid phone number.';
        }
        if (slot) slot.textContent = bad ? msg : '';
        if (f.type !== 'radio') f.setAttribute('aria-invalid', bad ? 'true' : 'false');
        if (bad && ok) { ok = false; (f.type === 'radio' ? f : f).focus({ preventScroll: true }); }
      });
      return ok;
    };

    form.addEventListener('click', function (e) {
      var next = e.target.closest('[data-next]');
      var prev = e.target.closest('[data-prev]');
      if (next) {
        e.preventDefault();
        if (!validate(panels[idx])) return;
        if (idx < panels.length - 1) { idx++; paint(); }
      }
      if (prev) { e.preventDefault(); if (idx > 0) { idx--; paint(); } }
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validate(panels[idx])) return;

      var btn = form.querySelector('[data-submit]');
      var status = form.querySelector('.form-status');
      var endpoint = form.getAttribute('action');

      // Merge captured attribution into the payload
      var attr = attribution();
      Object.keys(attr).forEach(function (k) {
        if (form.querySelector('[name="' + k + '"]')) return;
        var i = document.createElement('input');
        i.type = 'hidden'; i.name = k; i.value = attr[k];
        form.appendChild(i);
      });

      var data = new FormData(form);
      btn.disabled = true;
      var label = btn.textContent;
      btn.textContent = 'Sending…';
      if (status) status.textContent = '';

      fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.json().catch(function () { return {}; });
        })
        .then(function () {
          var ok = document.getElementById('formSuccess');
          if (ok) {
            form.hidden = true;
            ok.hidden = false;
            ok.setAttribute('tabindex', '-1');
            ok.focus({ preventScroll: true });
            ok.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' });
          }
        })
        .catch(function () {
          btn.disabled = false;
          btn.textContent = label;
          if (status) {
            status.innerHTML = 'Something went wrong sending your request. Please call ' +
              '<a href="tel:+61435193845">0435 193 845</a> or email ' +
              '<a href="mailto:admin@floorcandyepoxy.com">admin@floorcandyepoxy.com</a> and we\'ll pick it up from there.';
          }
        });
    });

    paint();
  }

  /* ---------- Current year ---------- */
  var y = document.getElementById('yr');
  if (y) y.textContent = new Date().getFullYear();
})();
