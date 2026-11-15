/* Floor Candy — site behaviour.
   No dependencies. Everything degrades without JS. */
(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");

  /* ------------------------------------------------------------------ nav */
  var burger = document.querySelector(".burger");
  var drawer = document.getElementById("drawer");

  if (burger && drawer) {
    var setNav = function (open) {
      burger.setAttribute("aria-expanded", String(open));
      drawer.hidden = !open;
      document.body.classList.toggle("nav-open", open);
    };
    burger.addEventListener("click", function () {
      setNav(burger.getAttribute("aria-expanded") !== "true");
    });
    drawer.addEventListener("click", function (e) {
      if (e.target.closest("a")) setNav(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && burger.getAttribute("aria-expanded") === "true") {
        setNav(false);
        burger.focus();
      }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth >= 1000 && burger.getAttribute("aria-expanded") === "true") setNav(false);
    });
  }

  /* -------------------------------------------------- before/after slider */
  Array.prototype.forEach.call(document.querySelectorAll(".ba"), function (ba) {
    var range = ba.querySelector('input[type="range"]');
    var after = ba.querySelector(".ba-after");
    var handle = ba.querySelector(".ba-handle");
    if (!range || !after || !handle) return;

    var paint = function () {
      var v = Number(range.value);
      // clip, don't resize — setting width would squash the after image
      after.style.clipPath = "inset(0 0 0 " + v + "%)";
      handle.style.left = v + "%";
    };
    range.addEventListener("input", paint);
    paint();
  });

  /* ------------------------------------------------------- hero video */
  /* Enhancement only. The poster image is the LCP and is never blocked by this.
     A 3MB background loop is not worth serving on a metered or slow connection,
     so it is gated rather than assumed. */
  (function () {
    var v = document.querySelector("[data-hero-video]");
    if (!v) return;

    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) return;
    /* The loop is 9:16, art-directed for phones like the portrait poster. On a
       landscape hero it was stretched and blurry, and cost desktop 0.5MB. */
    if (window.matchMedia && !window.matchMedia("(max-width: 860px)").matches) return;

    var c = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (c) {
      if (c.saveData) return;
      if (/^(slow-)?2g$/.test(c.effectiveType || "") || c.effectiveType === "3g") return;
    }

    var start = function () {
      v.src = v.getAttribute("data-src");
      v.addEventListener("canplay", function () {
        var p = v.play();
        if (p && p.catch) p.catch(function () { /* autoplay refused: keep the still */ });
        v.setAttribute("data-ready", "");
      }, { once: true });
      v.load();
    };

    /* Wait until the page is idle so the video never competes with the poster. */
    if ("requestIdleCallback" in window) requestIdleCallback(start, { timeout: 2500 });
    else setTimeout(start, 1200);
  })();

  /* ------------------------------------------------------- quote form(s) */
  var PARAMS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"];

  function storedParams() {
    var out = {};
    var qs = new URLSearchParams(window.location.search);
    PARAMS.forEach(function (k) {
      var v = qs.get(k);
      if (v) {
        try { sessionStorage.setItem("fc_" + k, v); } catch (e) { /* private mode */ }
      }
      if (!v) {
        try { v = sessionStorage.getItem("fc_" + k); } catch (e) { v = null; }
      }
      if (v) out[k] = v;
    });
    return out;
  }

  Array.prototype.forEach.call(document.querySelectorAll("form[data-quote]"), function (form) {
    /* Stamp hidden attribution fields so the CRM receives them on submit. */
    var attrib = storedParams();
    Object.keys(attrib).forEach(function (k) {
      var input = form.querySelector('[name="' + k + '"]');
      if (!input) {
        input = document.createElement("input");
        input.type = "hidden";
        input.name = k;
        form.appendChild(input);
      }
      input.value = attrib[k];
    });

    var pageField = form.querySelector('[name="page_url"]');
    if (pageField) pageField.value = window.location.href;
    var refField = form.querySelector('[name="referrer"]');
    if (refField) refField.value = document.referrer || "";

    var status = form.querySelector(".form-status");

    form.addEventListener("submit", function (e) {
      /* Clear previous errors. */
      Array.prototype.forEach.call(form.querySelectorAll(".err"), function (n) { n.remove(); });
      Array.prototype.forEach.call(form.querySelectorAll('[aria-invalid="true"]'), function (n) {
        n.removeAttribute("aria-invalid");
      });

      var firstBad = null;
      Array.prototype.forEach.call(form.querySelectorAll("[required]"), function (field) {
        if (field.checkValidity()) return;
        field.setAttribute("aria-invalid", "true");
        var msg = document.createElement("span");
        msg.className = "err";
        msg.textContent = field.validationMessage || "Please complete this field.";
        (field.closest(".field") || field.parentNode).appendChild(msg);
        if (!firstBad) firstBad = field;
      });

      if (firstBad) {
        e.preventDefault();
        firstBad.focus();
        firstBad.scrollIntoView({ block: "center", behavior: "smooth" });
        if (status) {
          status.dataset.state = "err";
          status.textContent = "Please check the highlighted fields.";
        }
        return;
      }

      var endpoint = form.getAttribute("action");
      if (!endpoint || !window.fetch || !window.FormData) return; /* native POST */
      e.preventDefault();
      if (form.dataset.sending) return; /* no double leads on a slow connection */
      form.dataset.sending = "1";

      var btn = form.querySelector('button[type="submit"]');
      var label = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      if (status) { status.dataset.state = ""; status.textContent = "Sending your details…"; }

      var fail = function () {
        delete form.dataset.sending;
        if (btn) { btn.disabled = false; btn.textContent = label; }
        if (status) {
          status.dataset.state = "err";
          status.innerHTML =
            "Sorry, that didn\u2019t send. Please call " +
            '<a href="tel:+61435193845">0435 193 845</a> or email ' +
            '<a href="mailto:floorcandyepoxy@gmail.com">floorcandyepoxy@gmail.com</a>.';
        }
        track("form_error", { form_id: form.id || "quote" });
      };

      fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) return fail();
          track("generate_lead", { form_id: form.id || "quote", page_path: window.location.pathname });
          form.reset();
          if (btn) btn.textContent = "Sent";
          if (status) {
            status.dataset.state = "ok";
            status.innerHTML =
              "Thanks \u2014 your details are with Jarrod, who will be in touch shortly. " +
              'Got photos of the floor? Text them to <a href="sms:+61435193845">0435 193 845</a>.';
            status.setAttribute("tabindex", "-1");
            status.focus();
          }
        })
        .catch(fail);
    });

    /* Fires once, on the first real interaction: the denominator for drop-off. */
    form.addEventListener("focusin", function () {
      if (form.dataset.started) return;
      form.dataset.started = "1";
      track("form_start", { form_id: form.id || "quote" });
    });
  });

  /* ------------------------------------------------------------ tracking */
  /* Vendor-neutral. Pushes to dataLayer and calls gtag when either exists.
     No analytics library is loaded by this site — see docs/TRACKING.md */
  function track(name, params) {
    try {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push(Object.assign({ event: name }, params || {}));
      if (typeof window.gtag === "function") window.gtag("event", name, params || {});
    } catch (e) { /* never break the page for analytics */ }
  }
  window.fcTrack = track;

  document.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    var where = { link_url: href, page_path: window.location.pathname };
    if (href.indexOf("tel:") === 0) track("click_call", where);
    else if (href.indexOf("sms:") === 0) track("click_sms", where);
    else if (href.indexOf("mailto:") === 0) track("click_email", where);
    else if (href.indexOf("wa.me") !== -1) track("click_whatsapp", where);
    else if (href === "/contact" || href === "#quote") track("quote_cta_click", where);
  });
})();
