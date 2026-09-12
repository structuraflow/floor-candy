/* Floor Candy — lean vanilla JS. No libraries.
   Everything here is progressive enhancement: the site works without it. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Conversion events ----------
     Vendor-neutral. Pushes to dataLayer and forwards to gtag when either is
     present, so GA4 or GTM can be installed later without touching this file.
     No analytics library is loaded here — see docs/TRACKING.md. */
  function track(name, params) {
    var payload = params || {};
    try {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push(Object.assign({ event: name }, payload));
      if (typeof window.gtag === 'function') window.gtag('event', name, payload);
    } catch (e) { /* tracking must never break the page */ }
  }

  // Any element carrying data-ev reports itself once clicked.
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('[data-ev]');
    if (!el) return;
    track(el.getAttribute('data-ev'), {
      link_text: (el.textContent || '').trim().slice(0, 60),
      link_url: el.getAttribute('href') || '',
      page_path: location.pathname
    });
  }, true);

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
    var reported = false;
    var report = function (how) {
      if (reported) return;
      reported = true;
      track('before_after_interaction', { method: how, label: handle.getAttribute('aria-label') || '' });
    };
    var dragging = false;
    var start = function (e) { dragging = true; el.classList.add('is-touched'); fromEvent(e); report(e.touches ? 'touch' : 'pointer'); };
    var move = function (e) { if (dragging) { fromEvent(e); if (e.cancelable) e.preventDefault(); } };
    var end = function () { dragging = false; };
    el.addEventListener('mousedown', start);
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', end);
    el.addEventListener('touchstart', start, { passive: true });
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('touchend', end);
    handle.addEventListener('keydown', function (e) {
      if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].indexOf(e.key) > -1) report('keyboard');
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

  /* ---------- Form engagement ----------
     One assessment_form_start per form, on the first real interaction. */
  function wireFormStart(el, formName) {
    if (!el) return;
    var started = false;
    var fire = function () {
      if (started) return;
      started = true;
      track('assessment_form_start', { form_name: formName, page_path: location.pathname });
    };
    el.addEventListener('focusin', function (e) {
      if (e.target.matches('input, select, textarea')) fire();
    });
    el.addEventListener('change', fire);
  }

  /* ---------- Multi-step assessment form ---------- */
  var form = document.getElementById('assessmentForm');
  if (form) {
    wireFormStart(form, 'assessment_full');
    var fullSending = false;
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
      if (fullSending) return;
      if (!validate(panels[idx])) return;
      fullSending = true;

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
          track('assessment_form_submit', { form_name: 'assessment_full', page_path: location.pathname });
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
          fullSending = false;
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

  /* ---------- Homepage quick-capture form ----------
     Single step, three fields. Same endpoint and attribution as the full
     assessment form; validated on blur and on submit. */
  var quick = document.getElementById('quickForm');
  if (quick) {
    wireFormStart(quick, 'assessment_quick');
    var quickSending = false;
    var qCheck = function (f) {
      var v = f.value.trim();
      if (!v) return 'This field is required.';
      if (f.type === 'tel' && v.replace(/[^\d]/g, '').length < 8) return 'Please enter a valid phone number.';
      return '';
    };
    var qPaint = function (f) {
      var slot = quick.querySelector('[data-err="' + f.name + '"]');
      var msg = qCheck(f);
      if (slot) slot.textContent = msg;
      f.setAttribute('aria-invalid', msg ? 'true' : 'false');
      return !msg;
    };
    quick.querySelectorAll('[required]').forEach(function (f) {
      f.addEventListener('blur', function () { qPaint(f); });
    });

    quick.addEventListener('submit', function (e) {
      e.preventDefault();
      if (quickSending) return;
      var ok = true, first = null;
      quick.querySelectorAll('[required]').forEach(function (f) {
        if (!qPaint(f) && ok) { ok = false; first = f; }
      });
      if (!ok) { if (first) first.focus({ preventScroll: true }); return; }
      quickSending = true;

      var btn = quick.querySelector('[data-submit]');
      var status = quick.querySelector('.form-status');
      var attr = attribution();
      Object.keys(attr).forEach(function (k) {
        if (quick.querySelector('[name="' + k + '"]')) return;
        var i = document.createElement('input');
        i.type = 'hidden'; i.name = k; i.value = attr[k];
        quick.appendChild(i);
      });

      var label = btn.textContent;
      btn.disabled = true; btn.textContent = 'Sending…';
      if (status) status.textContent = '';

      fetch(quick.getAttribute('action'), {
        method: 'POST', body: new FormData(quick), headers: { Accept: 'application/json' }
      })
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); })
        .then(function () {
          track('assessment_form_submit', { form_name: 'assessment_quick', page_path: location.pathname });
          var done = document.getElementById('quickSuccess');
          quick.hidden = true;
          if (done) {
            done.hidden = false;
            done.setAttribute('tabindex', '-1');
            done.focus({ preventScroll: true });
          }
        })
        .catch(function () {
          quickSending = false;
          btn.disabled = false; btn.textContent = label;
          if (status) {
            status.innerHTML = 'Could not send that. Please call ' +
              '<a href="tel:+61435193845">0435 193 845</a> and we\'ll pick it up from there.';
          }
        });
    });
  }


  /* ---------- Finish collection tabs ----------
     Roving tabindex, arrow-key navigation, one panel visible at a time. The
     panels are plain elements with [hidden], so with JS off every finish is
     still readable on the page. */
  (function finishTabs() {
    var list = document.querySelector('[role="tablist"]');
    if (!list) return;
    var tabs = [].slice.call(list.querySelectorAll('[role="tab"]'));
    if (tabs.length < 2) return;
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });

    var select = function (i, focus) {
      tabs.forEach(function (t, n) {
        var on = n === i;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        if (panels[n]) panels[n].hidden = !on;
      });
      if (focus) tabs[i].focus();
      track('finish_tab_view', { finish: tabs[i].textContent.trim() });
    };

    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i, false); });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight') n = (i + 1) % tabs.length;
        if (e.key === 'ArrowLeft') n = (i - 1 + tabs.length) % tabs.length;
        if (e.key === 'Home') n = 0;
        if (e.key === 'End') n = tabs.length - 1;
        if (n !== null) { select(n, true); e.preventDefault(); }
      });
    });
  })();

  /* ---------- Build-up diagram ----------
     Each process step lights the layer it creates. Nothing is hidden behind
     this — it is emphasis on a drawing that is complete without it. */
  (function buildUp() {
    var steps = [].slice.call(document.querySelectorAll('.bu-step'));
    var groups = [].slice.call(document.querySelectorAll('.bu-group'));
    if (!steps.length || !groups.length) return;

    var show = function (n) {
      steps.forEach(function (s) { s.classList.toggle('is-active', s.getAttribute('data-step') === n); });
      groups.forEach(function (g) { g.classList.toggle('is-active', g.getAttribute('data-layer') === n); });
    };

    if (!('IntersectionObserver' in window)) { groups.forEach(function (g) { g.classList.add('is-active'); }); return; }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) show(en.target.getAttribute('data-step'));
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    steps.forEach(function (s) { io.observe(s); });
    show('1');
  })();

  /* ---------- Current year ---------- */
  var y = document.getElementById('yr');
  if (y) y.textContent = new Date().getFullYear();
})();
