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

  /* ------------------------------------------------------- quote form(s) */
  var PARAMS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"];

  function ss(op, k, v) {
    try {
      if (op === "get") return sessionStorage.getItem(k);
      if (op === "set") sessionStorage.setItem(k, v);
      if (op === "del") sessionStorage.removeItem(k);
    } catch (e) { return null; }
  }
  function ls(op, k, v) {
    try {
      if (op === "get") return localStorage.getItem(k);
      if (op === "set") localStorage.setItem(k, v);
      if (op === "del") localStorage.removeItem(k);
    } catch (e) { return null; }
  }

  function storedParams() {
    var out = {};
    var qs = new URLSearchParams(window.location.search);
    PARAMS.forEach(function (k) {
      var v = qs.get(k);
      if (v) ss("set", "fc_" + k, v);
      else v = ss("get", "fc_" + k);
      if (v) out[k] = v;
    });
    return out;
  }
  /* First page of the visit, kept for the whole session. */
  if (!ss("get", "fc_landing")) ss("set", "fc_landing", window.location.href);

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0;
      return (c === "x" ? r : (r & 3 | 8)).toString(16);
    });
  }

  function setHidden(form, name, value) {
    var input = form.querySelector('[name="' + name + '"]');
    if (!input) {
      input = document.createElement("input");
      input.type = "hidden";
      input.name = name;
      form.appendChild(input);
    }
    input.value = value;
  }

  function fieldMsg(field) {
    if (field.validity.valueMissing) {
      return field.type === "radio" ? "Please pick one." : "Please fill this in.";
    }
    if (field.validity.patternMismatch && field.dataset.msg) return field.dataset.msg;
    if (field.validity.typeMismatch && field.type === "email") return "That email doesn’t look right.";
    return field.validationMessage || "Please check this.";
  }

  function clearErr(field) {
    var host = field.closest(".field") || field.closest("fieldset");
    if (!host) return;
    var e = host.querySelector(".err");
    if (e) e.remove();
    field.removeAttribute("aria-invalid");
  }

  function showErr(field) {
    var host = field.closest(".field") || field.closest("fieldset");
    clearErr(field);
    field.setAttribute("aria-invalid", "true");
    var msg = document.createElement("span");
    msg.className = "err";
    msg.textContent = fieldMsg(field);
    if (field.id) { msg.id = field.id + "-err"; field.setAttribute("aria-describedby", msg.id); }
    host.appendChild(msg);
  }

  /* Validate a container. Radios are checked once per group. */
  function validate(scope) {
    var bad = null, seen = {};
    Array.prototype.forEach.call(scope.querySelectorAll("[required], [pattern], [type=email]"), function (f) {
      if (f.type === "radio") {
        if (seen[f.name]) return;
        seen[f.name] = 1;
      }
      if (f.checkValidity()) { clearErr(f); f.closest(".field") && f.value && f.closest(".field").classList.add("is-ok"); return; }
      showErr(f);
      if (!bad) bad = f;
    });
    return bad;
  }

  Array.prototype.forEach.call(document.querySelectorAll("form[data-quote]"), function (form) {
    var attrib = storedParams();
    Object.keys(attrib).forEach(function (k) { setHidden(form, k, attrib[k]); });
    setHidden(form, "page_url", window.location.href);
    setHidden(form, "referrer", document.referrer || "");
    setHidden(form, "landing_page", ss("get", "fc_landing") || window.location.href);
    setHidden(form, "headline_variant", ss("get", "fc_h") || "a");

    var status = form.querySelector(".form-status");
    var steps = Array.prototype.slice.call(form.querySelectorAll(".qstep"));
    var stepped = form.hasAttribute("data-steps") && steps.length > 1;
    var KEY = "fc_quote_progress";
    var current = 1;
    var backBtn = form.querySelector("[data-back]");
    var nextBtn = form.querySelector("[data-next]");
    var submitBtn = form.querySelector('button[type="submit"]');
    var nowEl = form.querySelector("[data-step-now]");
    var bar = form.querySelector(".qprog-bar");

    /* ---- save + restore progress (refresh keeps answers) ---- */
    function save() {
      var data = {};
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.type === "hidden" || el.name === "_gotcha") return;
        if ((el.type === "radio" || el.type === "checkbox") && !el.checked) return;
        data[el.name] = el.value;
      });
      data._step = current;
      ls("set", KEY, JSON.stringify(data));
    }
    function restore() {
      var raw = ls("get", KEY);
      if (!raw) return 1;
      var data;
      try { data = JSON.parse(raw); } catch (e) { return 1; }
      Object.keys(data).forEach(function (k) {
        if (k === "_step") return;
        Array.prototype.forEach.call(form.querySelectorAll('[name="' + k + '"]'), function (el) {
          if (el.type === "radio" || el.type === "checkbox") el.checked = el.value === data[k];
          else el.value = data[k];
        });
      });
      return Math.min(Number(data._step) || 1, steps.length);
    }

    function show(n, focus) {
      current = n;
      steps.forEach(function (st) {
        var on = Number(st.getAttribute("data-step")) === n;
        st.hidden = !on;
        st.classList.toggle("is-in", on);
      });
      if (nowEl) nowEl.textContent = String(n);
      if (bar) bar.style.transform = "scaleX(" + (n / steps.length) + ")";
      if (backBtn) backBtn.hidden = n === 1;
      if (nextBtn) nextBtn.hidden = n === 1 || n === steps.length;
      if (submitBtn) submitBtn.hidden = n !== steps.length;
      if (focus) {
        var leg = steps[n - 1].querySelector("legend");
        if (leg) { leg.setAttribute("tabindex", "-1"); leg.focus({ preventScroll: true }); }
        var top = form.getBoundingClientRect().top;
        if (top < 0 || top > window.innerHeight * 0.4) {
          form.scrollIntoView({ block: "start", behavior: "smooth" });
        }
      }
      track("form_step", { form_id: form.id, step: n });
      save();
    }

    function next() {
      var bad = validate(steps[current - 1]);
      if (bad) { bad.focus(); return; }
      if (current < steps.length) show(current + 1, true);
    }

    if (stepped) {
      form.classList.add("is-stepped");
      /* ?type=Double+garage from the entry cards on other pages: pre-pick step 1. */
      var pre = new URLSearchParams(window.location.search).get("type");
      var start = restore();
      if (pre) {
        Array.prototype.forEach.call(form.querySelectorAll('[name="floor_type"]'), function (r) {
          if (r.value === pre) r.checked = true;
        });
        start = Math.max(start, 2);
      }
      show(start, false);

      /* Step 1 cards advance on tap. */
      Array.prototype.forEach.call(form.querySelectorAll('[name="floor_type"]'), function (r) {
        r.addEventListener("change", function () {
          track("form_floor_type", { form_id: form.id, floor_type: r.value });
          setTimeout(function () { show(2, true); }, 250);
        });
      });
      if (nextBtn) nextBtn.addEventListener("click", next);
      if (backBtn) backBtn.addEventListener("click", function () { show(Math.max(1, current - 1), true); });
      /* Enter in a text field moves to the next step instead of submitting early. */
      form.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && e.target.tagName === "INPUT" && current < steps.length) {
          e.preventDefault();
          next();
        }
      });
    }

    /* Inline validation: on blur, and errors clear as soon as the field is fixed. */
    form.addEventListener("focusout", function (e) {
      var f = e.target;
      if (!f.name || f.type === "radio" || f.type === "hidden") return;
      if (!f.value && !f.required) { clearErr(f); return; }
      var host = f.closest(".field");
      if (f.checkValidity()) { clearErr(f); if (host && f.value) host.classList.add("is-ok"); }
      else { showErr(f); if (host) host.classList.remove("is-ok"); }
    });
    form.addEventListener("input", function (e) {
      var f = e.target;
      if (f.getAttribute("aria-invalid") === "true" && f.checkValidity()) {
        clearErr(f);
        var host = f.closest(".field");
        if (host) host.classList.add("is-ok");
      }
      save();
    });
    form.addEventListener("change", function (e) {
      if (e.target.type === "radio") clearErr(e.target);
      save();
    });

    form.addEventListener("submit", function (e) {
      var firstBad = validate(form);
      if (firstBad) {
        e.preventDefault();
        if (stepped) {
          var st = firstBad.closest(".qstep");
          var n = st ? Number(st.getAttribute("data-step")) : current;
          if (n !== current) show(n, true);
        }
        firstBad.focus();
        if (status) { status.dataset.state = "err"; status.textContent = "Please check the highlighted field."; }
        return;
      }

      var eventId = uuid();
      setHidden(form, "event_id", eventId);
      var nameField = form.querySelector('[name="name"]');
      var heardField = form.querySelector('[name="heard_about"]');
      var lead = {
        name: nameField ? nameField.value.trim().split(/\s+/)[0] : "",
        event_id: eventId,
        heard: heardField ? heardField.value : "",
        floor_type: (form.querySelector('[name="floor_type"]:checked') || {}).value || ""
      };

      var endpoint = form.getAttribute("action");
      if (!endpoint || !window.fetch || !window.FormData) return; /* native POST */
      e.preventDefault();
      if (form.dataset.sending) return; /* no double leads on a slow connection */
      form.dataset.sending = "1";

      var label = submitBtn ? submitBtn.textContent : "";
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "Sending…"; }
      if (status) { status.dataset.state = ""; status.textContent = "Sending your details…"; }

      var fail = function () {
        delete form.dataset.sending;
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = label; }
        if (status) {
          status.dataset.state = "err";
          status.innerHTML =
            "Sorry, that didn’t send. Please call " +
            '<a href="tel:+61435193845">0435 193 845</a> or email ' +
            '<a href="mailto:floorcandyepoxy@gmail.com">floorcandyepoxy@gmail.com</a>.';
        }
        track("form_error", { form_id: form.id || "quote" });
      };

      fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) return fail();
          track("form_submit", { form_id: form.id || "quote", floor_type: lead.floor_type });
          ss("set", "fc_lead", JSON.stringify(lead));
          ls("del", KEY);
          window.location.assign("/thank-you");
        })
        .catch(fail);
    });

    form.addEventListener("focusin", function () {
      if (form.dataset.started) return;
      form.dataset.started = "1";
      track("form_start", { form_id: form.id || "quote" });
    });
  });

  /* ---------------------------------------------------------- thank-you */
  (function () {
    var nameEl = document.querySelector("[data-ty-name]");
    if (!nameEl) return;
    var lead = null;
    try { lead = JSON.parse(ss("get", "fc_lead") || "null"); } catch (e) { lead = null; }
    if (!lead) return; /* direct visit or refresh: no conversion fired */
    if (lead.name) nameEl.textContent = "Thanks " + lead.name + ", your quote request is in.";

    /* Fire the conversion once per lead, never on refresh. */
    if (!lead.fired) {
      if (typeof window.fbq === "function") window.fbq("track", "Lead", {}, { eventID: lead.event_id });
      track("generate_lead", { event_id: lead.event_id, floor_type: lead.floor_type });
      lead.fired = true;
      ss("set", "fc_lead", JSON.stringify(lead));
    }

    var box = document.querySelector("[data-ty-heard]");
    var endpoint = (document.querySelector('meta[name="fc-endpoint"]') || {}).content;
    if (!box || lead.heard || !endpoint || !window.fetch) return;
    box.hidden = false;
    box.addEventListener("click", function (e) {
      var b = e.target.closest("[data-heard]");
      if (!b) return;
      var fd = new FormData();
      fd.append("heard_about", b.getAttribute("data-heard"));
      fd.append("event_id", lead.event_id);
      fd.append("_subject", "Follow-up: how they heard about Floor Candy");
      fetch(endpoint, { method: "POST", body: fd, headers: { Accept: "application/json" } });
      lead.heard = b.getAttribute("data-heard");
      ss("set", "fc_lead", JSON.stringify(lead));
      Array.prototype.forEach.call(box.querySelectorAll("button"), function (x) { x.disabled = true; });
      b.classList.add("is-picked");
      box.querySelector("[data-ty-heard-done]").hidden = false;
    });
  })();

  /* ---------------------------------------------------- mobile quote bar */
  (function () {
    var bar = document.querySelector(".mobar");
    var quote = document.getElementById("quote");
    var link = document.querySelector("[data-quote-link]");
    if (quote && link) link.setAttribute("href", "#quote");
    if (!bar || !quote || !("IntersectionObserver" in window)) return;
    /* Hide the bar while the hero buttons or a form are on screen:
       it would repeat the hero buttons or cover the form's own buttons. */
    var watch = [quote, document.querySelector(".hero-cta"), document.getElementById("send")].filter(Boolean);
    var seen = new Set();
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) seen.add(e.target); else seen.delete(e.target); });
      bar.classList.toggle("is-hidden", seen.size > 0);
    }, { threshold: 0.15 });
    watch.forEach(function (el) { io.observe(el); });
  })();

  /* ------------------------------------------------------- scroll reveal */
  /* Transform + opacity only, never on the hero (LCP), skipped for reduced motion. */
  (function () {
    var items = document.querySelectorAll(".reveal");
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!items.length || reduced || !("IntersectionObserver" in window)) return;
    document.documentElement.classList.add("can-reveal");
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        var group = en.target.parentNode;
        var idx = Array.prototype.indexOf.call(group.children, en.target);
        en.target.style.transitionDelay = Math.min(idx, 6) * 70 + "ms";
        en.target.classList.add("is-in");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    Array.prototype.forEach.call(items, function (el) { io.observe(el); });
  })();

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
    var fbContact = function () { if (typeof window.fbq === "function") window.fbq("track", "Contact"); };
    if (/^(tel:|sms:)|wa\.me/.test(href)) fbContact();
    if (href.indexOf("tel:") === 0) track("click_call", where);
    else if (href.indexOf("sms:") === 0) track("click_sms", where);
    else if (href.indexOf("mailto:") === 0) track("click_email", where);
    else if (href.indexOf("wa.me") !== -1) track("click_whatsapp", where);
    else if (href.indexOf("/contact") === 0 || href === "#quote") track("quote_cta_click", where);
  });
})();
