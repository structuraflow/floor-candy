/* Floor Candy homepage (v2) behaviour. No dependencies.
   main.js owns the menu drawer, the mobile bar hide and click tracking (window.fcTrack).
   home.js owns the before/after sliders ([data-cmp]) and single-open FAQ.
   This file owns: service areas, finish picker, the 4-step quote form, lead magnet,
   postcode checker, the prep photo swap and the block reveal. */

/* =====================================================================
   SERVICE AREAS: edit here. Core towns get a yes, Newcastle/Hunter get
   "selected projects", anything else is asked to send the postcode.
   Matching ignores case and accepts a postcode or a town name.
   ===================================================================== */
var FC_AREAS = {
  core: { "2430": "Taree", "2428": "Forster, Tuncurry, Blueys Beach and Pacific Palms", "2427": "Harrington" },
  coreNames: ["taree", "forster", "tuncurry", "harrington", "blueys beach", "pacific palms", "old bar", "mid north coast"],
  selectedNames: ["newcastle", "hunter", "the hunter", "maitland"],
  selectedRange: [2280, 2339] // Newcastle and the Hunter postcodes
};

(function () {
  "use strict";
  var EMAIL = "floorcandyepoxy@gmail.com";
  var WA = "61435193845";
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var track = function (n, p) { if (typeof window.fcTrack === "function") window.fcTrack(n, p); };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };


  /* ------------------------------------------------- motion 1: block reveal */
  var hero = $(".hero");
  if (hero) requestAnimationFrame(function () { hero.classList.add("is-ready"); });
  var blks = $$(".blk");
  if (blks.length && !reduced && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -10% 0px" });
    blks.forEach(function (b) { io.observe(b); });
  } else {
    blks.forEach(function (b) { b.classList.add("is-in"); });
  }

  /* ---------------------------------------- prep: sticky photo follows the step */
  var steps = $$(".steps li");
  var photos = $$(".prep-frame img");
  var cap = $("[data-cap]");
  if (steps.length && photos.length && "IntersectionObserver" in window) {
    var showStep = function (li) {
      steps.forEach(function (s) { s.classList.toggle("on", s === li); });
      var n = li.getAttribute("data-photo");
      photos.forEach(function (p) { p.classList.toggle("on", p.getAttribute("data-ph") === n); });
      if (cap) cap.textContent = li.getAttribute("data-caption");
    };
    var sio = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) showStep(en.target); });
    }, { rootMargin: "-45% 0px -45% 0px" });
    steps.forEach(function (s) { sio.observe(s); });
  }

  /* ------------------------------------------------------------ quote form */
  var form = $("#fc-quote");
  if (!form) return;
  var stepEls = $$(".qstep", form);
  var now = $("[data-now]", form);
  var segs = $$(".qsegs i", form);
  var back = $("[data-back]", form);
  var next = $("[data-next]", form);
  var submit = $("[data-submit]", form);
  var errEl = $("[data-err]", form);
  var magnet = $("[data-magnet]", form);
  var done = $("[data-done]", form);
  var cur = 1, total = stepEls.length;

  function show(n, focus) {
    cur = n;
    stepEls.forEach(function (s) { s.hidden = Number(s.getAttribute("data-step")) !== n; });
    now.textContent = ("0" + n).slice(-2);
    segs.forEach(function (sg, k) { sg.classList.toggle("is-on", k < n); });
    back.hidden = n === 1;
    next.hidden = n === total;
    submit.hidden = n !== total;
    errEl.textContent = "";
    magnet.hidden = true;
    if (focus) {
      var first = $(".qstep:not([hidden]) input", form);
      var legend = $(".qstep:not([hidden]) legend", form);
      if (legend) { legend.setAttribute("tabindex", "-1"); legend.focus({ preventScroll: true }); }
      var top = form.getBoundingClientRect().top;
      if (top < 0 || top > window.innerHeight * 0.6) form.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
      if (n === total && first) setTimeout(function () { first.focus(); }, 60);
    }
    track("quote_step", { step: n });
  }

  function valid(n) {
    var s = $('.qstep[data-step="' + n + '"]', form);
    var groups = {};
    var bad = null;
    $$("input", s).forEach(function (i) {
      if (i.type === "radio") { if (i.required) groups[i.name] = true; return; }
      i.removeAttribute("aria-invalid");
      var v = i.value.trim();
      var ok = !(i.required && !v) && !(v && i.pattern && !new RegExp(i.pattern).test(v));
      if (!ok && !bad) { bad = i.getAttribute("data-msg") || ("Please add your " + (s.querySelector('label[for="' + i.id + '"]') || {}).textContent.toLowerCase() + "."); i.setAttribute("aria-invalid", "true"); i.focus(); }
      else if (!ok) i.setAttribute("aria-invalid", "true");
    });
    Object.keys(groups).forEach(function (name) {
      if (!bad && !form.querySelector('input[name="' + name + '"]:checked')) bad = "Pick one option to continue.";
    });
    errEl.textContent = bad || "";
    return !bad;
  }

  next.addEventListener("click", function () { if (valid(cur)) show(cur + 1, true); });
  back.addEventListener("click", function () { show(cur - 1, true); });

  /* Single-question steps advance on tap. Step 2 advances once size and timing are both picked,
     except "Just researching", which offers the guide instead of pushing them on. */
  form.addEventListener("change", function (e) {
    if (e.target.type !== "radio") return;
    errEl.textContent = "";
    if (e.target.name === "finish") syncPicker(e.target.value);
    if (cur === 1 || cur === 3) { setTimeout(function () { if (valid(cur)) show(cur + 1, true); }, 220); return; }
    if (cur === 2) {
      var size = form.querySelector('[name="approx_size"]:checked');
      var when = form.querySelector('[name="timing"]:checked');
      if (size && when) setTimeout(function () { if (cur === 2) show(3, true); }, 260);
    }
  });

  function answers() {
    var fd = new FormData(form);
    var lines = [
      "Floor Candy quote request",
      "Finish: " + (fd.get("finish") || "-"),
      "Size: " + (fd.get("approx_size") || "-"),
      "When: " + (fd.get("timing") || "-"),
      "Floor: " + (fd.get("floor_type") || "-"),
      "Name: " + (fd.get("name") || "-"),
      "Mobile: " + (fd.get("mobile") || "-"),
      "Postcode: " + (fd.get("postcode") || "-")
    ];
    return lines.join("\n");
  }

  function finish(sent) {
    var body = answers();
    $("[data-wa]", form).href = "https://wa.me/" + WA + "?text=" + encodeURIComponent(body);
    $("[data-mail]", form).href = "mailto:" + EMAIL + "?subject=" + encodeURIComponent("Quote request") + "&body=" + encodeURIComponent(body);
    if (!sent) {
      $("[data-done-h]", form).textContent = "Almost there. Send your answers to Jarrod.";
      $("[data-done-p]", form).textContent = "We couldn’t send the form from here. Your answers are filled in below: tap WhatsApp or email and hit send.";
    }
    $$(".qbar, [data-steps], .qnav, [data-err]", form).forEach(function (el) { el.hidden = true; el.style.display = "none"; });
    done.hidden = false;
    done.focus();
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!valid(cur)) return;
    var pu = form.querySelector('[name="page_url"]'); if (pu) pu.value = location.href;
    submit.disabled = true;
    submit.textContent = "Sending…";
    /* TODO — connect to Jarrod's real form endpoint / CRM when confirmed.
       (a) POST to the existing Formspree form (form action). (b) Success screen offers the
       answers pre-filled on WhatsApp and by mailto. If the POST fails, (b) is the fallback. */
    var ok = function () { track("generate_lead", { form: "interactive_quote" }); if (typeof window.fbq === "function") window.fbq("track", "Lead"); finish(true); };
    var fail = function () { track("lead_fallback", { form: "interactive_quote" }); finish(false); };
    if (!window.fetch || location.protocol === "file:") return fail();
    fetch(form.action, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
      .then(function (r) { r.ok ? ok() : fail(); })
      .catch(fail);
  });

  /* ------------------------------------------- lead magnet for "Just researching" */
  /* TODO — the 2026 Garage Floor Cost & Finish Guide does not exist yet. Requests reach
     Jarrod (Formspree, else mailto) so he can send it by hand until it is written. */
  var mEmail = $("#m-email");
  var mErr = $("[data-magnet-err]");
  $("[data-magnet-skip]").addEventListener("click", function () {
    magnet.hidden = true;
    if (form.querySelector('[name="approx_size"]:checked')) show(3, true);
    else errEl.textContent = "Pick a rough size to continue.";
  });
  $("[data-magnet-send]").addEventListener("click", function () {
    var v = mEmail.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) { mErr.textContent = "Enter an email address so we can send it."; mEmail.focus(); return; }
    mErr.textContent = "";
    var thanks = function () { magnet.innerHTML = "<h3>Thanks — Jarrod will email you the guide.</h3><p>Ready for a price later? Your answers are saved: just tap Next.</p>"; };
    var mail = function () { location.href = "mailto:" + EMAIL + "?subject=" + encodeURIComponent("Please send the 2026 Garage Floor Cost & Finish Guide") + "&body=" + encodeURIComponent("Please email the guide to: " + v); thanks(); };
    track("guide_request");
    if (!window.fetch) return mail();
    var fd = new FormData();
    fd.append("email", v); fd.append("_subject", "Guide request: 2026 Garage Floor Cost & Finish Guide"); fd.append("form_type", "guide_request");
    fetch(form.action, { method: "POST", body: fd, headers: { Accept: "application/json" } })
      .then(function (r) { r.ok ? thanks() : mail(); }).catch(mail);
  });

  /* -------------------------------------------------------- finish picker */
  var picks = $$(".fin");
  var finStatus = $(".fin-status");
  function syncPicker(val) {
    picks.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-finish") === val)); });
  }
  picks.forEach(function (b) {
    b.addEventListener("click", function () {
      var val = b.getAttribute("data-finish");
      var radio = form.querySelector('input[name="finish"][value="' + val + '"]');
      if (radio) radio.checked = true;
      syncPicker(val);
      if (cur === 1) show(2, false);
      if (finStatus) finStatus.innerHTML = val + " saved to your quote. <a class=\"tlink\" href=\"#quote\">Continue to your price</a>";
      track("finish_pick", { finish: val });
    });
  });

  /* ------------------------------------------------------ postcode checker */
  var pc = $("[data-pc]");
  if (pc) {
    var out = $("[data-pc-out]", pc);
    var inp = $("#pc-in", pc);
    pc.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = inp.value.trim();
      if (!v) { out.textContent = "Type your postcode or suburb first."; inp.focus(); return; }
      var key = v.toLowerCase().replace(/\s+nsw$/, "").trim();
      var n = /^\d{4}$/.test(key) ? Number(key) : null;
      var hit = false;
      var sms = function (lead) {
        out.textContent = lead + " ";
        var a = document.createElement("a");
        a.href = "sms:0435193845?&body=" + encodeURIComponent("Hi Jarrod, do you cover " + v + "?");
        a.textContent = "Text Jarrod " + v;
        out.appendChild(a);
      };
      if (n !== null && FC_AREAS.core[key]) { hit = true; out.textContent = "Yes, " + key + " (" + FC_AREAS.core[key] + ") is one of our core areas."; }
      else if (n === null && FC_AREAS.coreNames.indexOf(key) > -1) { hit = true; out.textContent = "Yes, " + v.replace(/\b\w/g, function (c) { return c.toUpperCase(); }) + " is one of our core areas."; }
      else if ((n !== null && n >= FC_AREAS.selectedRange[0] && n <= FC_AREAS.selectedRange[1]) || FC_AREAS.selectedNames.indexOf(key) > -1) {
        sms("We take selected projects in Newcastle and the Hunter, depending on job size and timing. Send Jarrod the details and he will confirm.");
      } else {
        sms("Send us your postcode and Jarrod will confirm. Jobs outside our core areas are decided by job size and timing.");
      }
      track("postcode_check", { matched: hit });
    });
  }

  /* ------------------------------------------- reviews: clamp long text + Read more */
  $$("[data-clamp]").forEach(function (q) {
    q.classList.add("is-clamped");
    var btn = q.parentNode.querySelector("[data-more]");
    if (btn && q.scrollHeight > q.clientHeight + 2) {
      btn.hidden = false;
      btn.addEventListener("click", function () {
        var clamped = q.classList.toggle("is-clamped");
        btn.textContent = clamped ? "Read more" : "Show less";
      });
    } else { q.classList.remove("is-clamped"); }
  });

  /* ------------------------------------------------ simple one-page quote form */
  /* Same Formspree form as the interactive quote, same thanks message, same WhatsApp/email fallback. */
  var sq = $("#fc-simple");
  if (sq) {
    var sqErr = $("[data-sq-err]", sq);
    var sqSend = $("[data-sq-send]", sq);
    var sqDone = $("[data-sq-done]", sq);
    var sqBody = function () {
      var fd = new FormData(sq);
      return ["Floor Candy quote request", "Name: " + (fd.get("name") || "-"), "Mobile: " + (fd.get("mobile") || "-"),
        "Postcode: " + (fd.get("postcode") || "-"), "What needs doing: " + (fd.get("job_details") || "-")].join("\n");
    };
    var sqFinish = function (sent) {
      var body = sqBody();
      $("[data-sq-wa]", sq).href = "https://wa.me/" + WA + "?text=" + encodeURIComponent(body);
      $("[data-sq-mail]", sq).href = "mailto:" + EMAIL + "?subject=" + encodeURIComponent("Quote request") + "&body=" + encodeURIComponent(body);
      if (!sent) {
        $("[data-sq-h]", sq).textContent = "Almost there. Send your details to Jarrod.";
        $("[data-sq-p]", sq).textContent = "We couldn’t send the form from here. Your details are filled in below: tap WhatsApp or email and hit send.";
      }
      $("[data-sq-fields]", sq).hidden = true;
      sqDone.hidden = false;
      sqDone.focus();
    };
    sq.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = null;
      $$("input:not([type=hidden]):not([name=_gotcha]), textarea", sq).forEach(function (i) {
        i.removeAttribute("aria-invalid");
        var v = i.value.trim();
        var ok = !(i.required && !v) && !(v && i.pattern && !new RegExp(i.pattern).test(v));
        if (!ok) { i.setAttribute("aria-invalid", "true"); if (!bad) { bad = i.getAttribute("data-msg") || ("Please add your " + sq.querySelector('label[for="' + i.id + '"]').textContent.toLowerCase() + "."); i.focus(); } }
      });
      sqErr.textContent = bad || "";
      if (bad) return;
      $('[name="page_url"]', sq).value = location.href;
      sqSend.disabled = true;
      sqSend.textContent = "Sending…";
      var ok = function () { track("generate_lead", { form: "simple_quote" }); if (typeof window.fbq === "function") window.fbq("track", "Lead"); sqFinish(true); };
      var fail = function () { track("lead_fallback", { form: "simple_quote" }); sqFinish(false); };
      if (!window.fetch || location.protocol === "file:") return fail();
      fetch(sq.action, { method: "POST", body: new FormData(sq), headers: { Accept: "application/json" } })
        .then(function (r) { r.ok ? ok() : fail(); })
        .catch(fail);
    });
  }

  show(1, false);
})();
