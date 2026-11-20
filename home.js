/* Floor Candy homepage behaviour (Nov 2026 revamp). No dependencies.
   main.js still owns the menu, quote form, attribution and tracking.
   Everything here is progressive: without it the page is complete and static. */
(function () {
  "use strict";
  var root = document.documentElement;
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* ------------------------------------------------ before/after compare
     Adapted from ibelick/motion-primitives Image Comparison (MIT, (c) 2024 ibelick).
     Pointer drag on the frame (vertical scroll still works on touch), plus a
     visually hidden range input for keyboard and screen readers. */
  function Compare(el) {
    var range = el.querySelector(".cmp-range");
    var dragging = false, anim = null;
    var self = this;

    function set(v) {
      v = Math.max(0, Math.min(100, v));
      el.style.setProperty("--pos", v + "%");
      if (range) {
        range.value = Math.round(v);
        range.setAttribute("aria-valuetext", Math.round(100 - v) + "% finished floor showing");
      }
    }
    function fromEvent(e) {
      var r = el.getBoundingClientRect();
      return ((e.clientX - r.left) / r.width) * 100;
    }
    function stopAnim() { if (anim) { cancelAnimationFrame(anim); anim = null; } }

    el.addEventListener("pointerdown", function (e) {
      if (e.button !== 0) return;
      stopAnim();
      dragging = true;
      el.classList.add("is-dragging");
      try { el.setPointerCapture(e.pointerId); } catch (x) {}
      set(fromEvent(e));
    });
    el.addEventListener("pointermove", function (e) { if (dragging) set(fromEvent(e)); });
    var end = function () { dragging = false; el.classList.remove("is-dragging"); };
    el.addEventListener("pointerup", end);
    el.addEventListener("pointercancel", end);
    if (range) range.addEventListener("input", function () { stopAnim(); set(Number(range.value)); });

    /* One-off sweep: before, across to after, then settle in the middle. */
    self.sweep = function (from, mid, to, ms) {
      stopAnim();
      var t0 = null;
      var ease = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
      function frame(ts) {
        if (t0 === null) t0 = ts;
        var p = Math.min(1, (ts - t0) / ms);
        var v = p < 0.62 ? from + (mid - from) * ease(p / 0.62)
                         : mid + (to - mid) * ease((p - 0.62) / 0.38);
        set(v);
        anim = p < 1 ? requestAnimationFrame(frame) : null;
      }
      anim = requestAnimationFrame(frame);
    };
    set(range ? Number(range.value) : 50);
  }

  var compares = [];
  Array.prototype.forEach.call(document.querySelectorAll("[data-cmp]"), function (el) {
    var c = new Compare(el);
    compares.push(c);
    if (el.hasAttribute("data-cmp-sweep") && !reduced) {
      el.style.setProperty("--pos", "97%");
      setTimeout(function () { c.sweep(97, 6, 50, 2600); }, 750);
    }
  });

  if (reduced || !("IntersectionObserver" in window)) {
    root.classList.remove("can-anim");
  } else {
    /* ------------------------------------------- statement word reveal
       After the Motion "scroll word reveal" example: words start faint and
       come up in reading order. Runs once on entry, no pinning. */
    Array.prototype.forEach.call(document.querySelectorAll("[data-words]"), function (el) {
      var i = 0;
      (function wrap(node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (n) {
          if (n.nodeType === 3) {
            var frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach(function (part) {
              if (!part) return;
              if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
              var s = document.createElement("span");
              s.className = "w";
              s.textContent = part;
              s.style.transitionDelay = (i++ * 55) + "ms";
              frag.appendChild(s);
            });
            node.replaceChild(frag, n);
          } else if (n.nodeType === 1) { wrap(n); }
        });
      })(el);
      new IntersectionObserver(function (es, io) {
        if (!es[0].isIntersecting) return;
        el.classList.add("is-in");
        io.disconnect();
      }, { rootMargin: "0px 0px -25% 0px" }).observe(el);
    });

    /* ------------------------------------------------------ fade-ups */
    var rv = document.querySelectorAll(".rv");
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("is-in");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    Array.prototype.forEach.call(rv, function (el, n) {
      var sib = el.parentNode ? Array.prototype.indexOf.call(el.parentNode.children, el) : 0;
      el.style.transitionDelay = Math.min(sib, 4) * 80 + "ms";
      io.observe(el);
    });
  }

  /* ------------------------------------------------- magnetic buttons
     After Hirael Magnetic Button (MIT, Mohammad Shehadeh). Mouse only,
     never with reduced motion. */
  if (finePointer && !reduced) {
    Array.prototype.forEach.call(document.querySelectorAll("[data-magnetic]"), function (b) {
      var k = 0.22;
      b.addEventListener("pointermove", function (e) {
        var r = b.getBoundingClientRect();
        b.style.setProperty("--mx", ((e.clientX - (r.left + r.width / 2)) * k).toFixed(1) + "px");
        b.style.setProperty("--my", ((e.clientY - (r.top + r.height / 2)) * k).toFixed(1) + "px");
      });
      b.addEventListener("pointerleave", function () {
        b.style.setProperty("--mx", "0px");
        b.style.setProperty("--my", "0px");
      });
    });
  }

  /* ------------------------------------------- services dropdown (desktop) */
  var dd = document.querySelector(".dd");
  if (dd) {
    document.addEventListener("click", function (e) { if (dd.open && !dd.contains(e.target)) dd.open = false; });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && dd.open) { dd.open = false; dd.querySelector("summary").focus(); }
    });
  }

  /* ---------------------------------------------- FAQ: one open at a time */
  var faqs = document.querySelectorAll(".faq details");
  Array.prototype.forEach.call(faqs, function (d) {
    d.addEventListener("toggle", function () {
      if (!d.open) return;
      Array.prototype.forEach.call(faqs, function (o) { if (o !== d && o.open) o.open = false; });
    });
  });

  /* ---------------- quote form: step 2 advances once size and timing are picked */
  var form = document.getElementById("home-quote");
  if (form) {
    var step2 = form.querySelector('.qstep[data-step="2"]');
    var next = form.querySelector("[data-next]");
    if (step2 && next) {
      step2.addEventListener("change", function (e) {
        if (e.target.type !== "radio") return;
        var size = step2.querySelector('[name="approx_size"]:checked');
        var when = step2.querySelector('[name="timing"]:checked');
        if (size && when && !step2.hidden) setTimeout(function () { if (!step2.hidden) next.click(); }, 250);
      });
    }
  }
})();
