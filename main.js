/* ═══════════════════════════════════════════════
   FLOOR CANDY — Shared JS
   ═══════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── PAGE LOADER ── */
  const loader = document.querySelector('.loader');
  if (loader) {
    window.addEventListener('load', () => {
      setTimeout(() => loader.classList.add('done'), 1600);
    });
  }

  /* ── CUSTOM CURSOR ── */
  const cursor = document.querySelector('.cursor');
  if (cursor && window.matchMedia('(hover: hover)').matches) {
    let mx = -100, my = -100;
    document.addEventListener('mousemove', e => {
      mx = e.clientX; my = e.clientY;
      cursor.style.left = mx + 'px';
      cursor.style.top  = my + 'px';
    });
    document.querySelectorAll('a, button, .masonry-item, .work-item, .svc-tease-card, .filter-btn, .hamburger').forEach(el => {
      el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
    });
  }

  /* ── SCROLL PROGRESS BAR ── */
  const bar = document.querySelector('.scroll-bar');
  function updateBar() {
    if (!bar) return;
    const docH = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (docH > 0 ? (window.scrollY / docH) * 100 : 0) + '%';
  }

  /* ── STICKY NAV ── */
  const nav = document.querySelector('nav');
  function updateNav() {
    if (!nav) return;
    nav.classList.toggle('scrolled', window.scrollY > 60);
  }

  /* ── HERO VIDEO AUTOPLAY ── */
  const heroVideo = document.getElementById('heroVideo');
  if (heroVideo) {
    heroVideo.play().catch(() => {
      document.addEventListener('touchstart', () => heroVideo.play(), { once: true });
    });
  }

  /* ── PARALLAX HERO ── */
  const heroBg = document.querySelector('.hero-bg');
  function parallax() {
    if (!heroBg || window.innerWidth < 768) return;
    heroBg.style.transform = `translateY(${window.scrollY * 0.3}px)`;
  }

  window.addEventListener('scroll', () => {
    updateBar();
    updateNav();
    parallax();
  }, { passive: true });

  updateNav();
  updateBar();

  /* ── MOBILE MENU ── */
  const ham = document.getElementById('ham');
  const mobMenu = document.getElementById('mobMenu');
  if (ham && mobMenu) {
    ham.addEventListener('click', () => {
      ham.classList.toggle('open');
      mobMenu.classList.toggle('open');
      document.body.style.overflow = mobMenu.classList.contains('open') ? 'hidden' : '';
    });
    mobMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        ham.classList.remove('open');
        mobMenu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  /* ── ACTIVE NAV LINK ── */
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mob-menu a').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (
      (href === 'index.html' && (path === '' || path === 'index.html')) ||
      (href !== 'index.html' && path.includes(href.replace('.html', '')))
    ) {
      a.classList.add('active');
    }
  });

  /* ── REVEAL ON SCROLL ── */
  const reveals = document.querySelectorAll('.reveal');
  const revealObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('in');
        revealObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
  reveals.forEach(el => revealObs.observe(el));

  /* ── COUNTER ANIMATION ── */
  const counters = document.querySelectorAll('.ctr');
  const ctrObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target;
      const target = +el.dataset.target;
      const dur = 1800;
      const step = target / (dur / 16);
      let cur = 0;
      const tick = setInterval(() => {
        cur += step;
        if (cur >= target) { el.textContent = target; clearInterval(tick); }
        else { el.textContent = Math.floor(cur); }
      }, 16);
      ctrObs.unobserve(el);
    });
  }, { threshold: 0.5 });
  counters.forEach(el => ctrObs.observe(el));

  /* ── FAQ ACCORDION ── */
  document.querySelectorAll('.faq-q').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.parentElement;
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });

  /* ── GALLERY FILTER ── */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const masonryItems = document.querySelectorAll('.masonry-item');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.dataset.filter;
      masonryItems.forEach(item => {
        const show = cat === 'all' || item.dataset.cat === cat;
        item.style.display = show ? 'block' : 'none';
      });
    });
  });

  /* ── LIGHTBOX ── */
  const lightbox = document.getElementById('lightbox');
  if (lightbox) {
    const lbImg    = lightbox.querySelector('.lb-img');
    const lbCap    = lightbox.querySelector('.lb-caption');
    const lbClose  = lightbox.querySelector('.lb-close');
    const lbPrev   = lightbox.querySelector('.lb-prev');
    const lbNext   = lightbox.querySelector('.lb-next');
    let items = [], idx = 0;

    function openLb(i) {
      idx = i;
      lbImg.src = items[i].src;
      lbCap.textContent = items[i].caption;
      lightbox.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function closeLb() {
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
    }
    function showPrev() { openLb((idx - 1 + items.length) % items.length); }
    function showNext() { openLb((idx + 1) % items.length); }

    document.querySelectorAll('.masonry-item').forEach((item, i) => {
      const img = item.querySelector('img');
      const cap = item.querySelector('.masonry-caption');
      items.push({ src: img ? img.src : '', caption: cap ? cap.textContent : '' });
      item.addEventListener('click', () => openLb(i));
    });

    if (lbClose) lbClose.addEventListener('click', closeLb);
    if (lbPrev)  lbPrev.addEventListener('click', showPrev);
    if (lbNext)  lbNext.addEventListener('click', showNext);
    lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLb(); });
    document.addEventListener('keydown', e => {
      if (!lightbox.classList.contains('open')) return;
      if (e.key === 'Escape') closeLb();
      if (e.key === 'ArrowLeft') showPrev();
      if (e.key === 'ArrowRight') showNext();
    });
  }

  /* ── CONTACT FORM ── */
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async e => {
      e.preventDefault();
      const btn = contactForm.querySelector('button[type="submit"]');
      btn.textContent = 'Sending…';
      btn.disabled = true;
      try {
        const res = await fetch(contactForm.action, {
          method: 'POST',
          body: new FormData(contactForm),
          headers: { Accept: 'application/json' }
        });
        if (res.ok) {
          contactForm.style.display = 'none';
          document.getElementById('formSuccess').style.display = 'block';
        } else {
          btn.textContent = 'Try Again';
          btn.disabled = false;
        }
      } catch {
        btn.textContent = 'Try Again';
        btn.disabled = false;
      }
    });
  }

  /* ── BEFORE / AFTER SLIDER ── */
  const baSlider = document.getElementById('baSlider');
  if (baSlider) {
    const baBefore  = baSlider.querySelector('.ba-before');
    const baDivider = document.getElementById('baDivider');
    let dragging = false;
    let pct = 50;

    function baSetPos(clientX) {
      const rect = baSlider.getBoundingClientRect();
      pct = Math.max(0, Math.min(100, ((clientX - rect.left) / rect.width) * 100));
      baBefore.style.clipPath  = `inset(0 ${100 - pct}% 0 0)`;
      baDivider.style.left = pct + '%';
    }

    baSlider.addEventListener('mousedown',  e => { dragging = true; baSetPos(e.clientX); e.preventDefault(); });
    window.addEventListener('mousemove',    e => { if (dragging) baSetPos(e.clientX); });
    window.addEventListener('mouseup',      ()  => { dragging = false; });
    baSlider.addEventListener('touchstart', e => { dragging = true; baSetPos(e.touches[0].clientX); }, { passive: true });
    window.addEventListener('touchmove',    e => { if (dragging) baSetPos(e.touches[0].clientX); }, { passive: true });
    window.addEventListener('touchend',     ()  => { dragging = false; });
  }

  /* ── COST ESTIMATOR ── */
  const estSqmInput = document.getElementById('estSqm');
  const estRangeInput = document.getElementById('estRange');
  const estLowEl  = document.getElementById('estLow');
  const estHighEl = document.getElementById('estHigh');
  const estNoteEl = document.getElementById('estNote');
  const estOpts   = document.querySelectorAll('.est-opt');

  if (estSqmInput && estOpts.length) {
    let rateMin = 65, rateMax = 90;

    estOpts.forEach(btn => {
      btn.addEventListener('click', () => {
        estOpts.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        rateMin = +btn.dataset.rate;
        rateMax = +btn.dataset.max;
        calcEst();
      });
    });

    function calcEst() {
      const sqm = parseFloat(estSqmInput.value) || parseFloat(estRangeInput.value) || 0;
      if (!sqm || sqm <= 0) {
        estLowEl.textContent = '—'; estHighEl.textContent = '—';
        if (estNoteEl) estNoteEl.style.display = 'block';
        return;
      }
      if (estNoteEl) estNoteEl.style.display = 'none';
      estLowEl.textContent  = '$' + Math.round(sqm * rateMin).toLocaleString('en-AU');
      estHighEl.textContent = '$' + Math.round(sqm * rateMax).toLocaleString('en-AU');
    }

    estSqmInput.addEventListener('input', () => {
      const v = parseFloat(estSqmInput.value);
      if (estRangeInput && v >= 10 && v <= 500) estRangeInput.value = v;
      calcEst();
    });
    if (estRangeInput) {
      estRangeInput.addEventListener('input', () => {
        estSqmInput.value = estRangeInput.value;
        calcEst();
      });
    }
    calcEst();
  }

  /* ── FINISH SELECTOR ── */
  const finishSwatches = document.querySelectorAll('.finish-swatch');
  const finishPreviewImg = document.getElementById('finishPreview');
  const finishLabelEl = document.getElementById('finishLabel');

  if (finishSwatches.length && finishPreviewImg) {
    finishSwatches.forEach(sw => {
      sw.addEventListener('click', () => {
        finishSwatches.forEach(s => s.classList.remove('active'));
        sw.classList.add('active');
        finishPreviewImg.style.opacity = '0';
        setTimeout(() => {
          finishPreviewImg.src = sw.dataset.img;
          if (finishLabelEl) finishLabelEl.textContent = sw.dataset.name;
          finishPreviewImg.style.opacity = '1';
        }, 220);
      });
    });
  }

})();
