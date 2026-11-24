/* Note AI — site behaviour. No libraries, no network calls. */
(function () {
  "use strict";
  var CFG = window.SITE || {};
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  };
  var REWARD_KEY = "noteai-reward-20";

  /* Header: solid after scroll */
  var header = document.querySelector(".site-header");
  function onScroll() { if (header) header.classList.toggle("solid", window.scrollY > 24); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Mobile menu */
  var menuBtn = document.querySelector(".menu-btn");
  var menu = document.getElementById("mobile-menu");
  function setMenu(open) {
    document.documentElement.classList.toggle("menu-open", open);
    document.body.classList.toggle("menu-open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    if (open) { var first = menu.querySelector("a"); if (first) first.focus(); }
  }
  if (menuBtn && menu) {
    menuBtn.addEventListener("click", function () { setMenu(menuBtn.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menuBtn.getAttribute("aria-expanded") === "true") { setMenu(false); menuBtn.focus(); }
    });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    window.addEventListener("resize", function () { if (window.innerWidth > 980) setMenu(false); });
  }

  /* Laptop screen: scale fixed-size app to the frame */
  var fits = document.querySelectorAll(".screen-fit");
  function fit() {
    fits.forEach(function (el) {
      var w = el.parentElement.clientWidth;
      el.style.transform = "scale(" + (w / 1100) + ")";
    });
  }
  if (fits.length) {
    fit();
    if ("ResizeObserver" in window) new ResizeObserver(fit).observe(fits[0].parentElement);
    else window.addEventListener("resize", fit);
  }

  /* Live note typing inside the app frame (decorative, stops under reduced motion) */
  var typer = document.querySelector("[data-typer]");
  if (typer && !reduce) {
    var lines = JSON.parse(typer.getAttribute("data-typer"));
    var li = 0, ci = 0;
    (function tick() {
      var line = lines[li];
      typer.textContent = line.slice(0, ci);
      ci++;
      if (ci > line.length) { li = (li + 1) % lines.length; ci = 0; setTimeout(tick, 1800); }
      else setTimeout(tick, 38);
    })();
  }

  /* Accordions */
  document.querySelectorAll(".acc-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      if (panel) panel.setAttribute("aria-hidden", String(open));
    });
  });

  /* Tabs (notes examples) — click or arrow keys, never timed */
  document.querySelectorAll("[role=tablist]").forEach(function (list) {
    var tabs = Array.prototype.slice.call(list.querySelectorAll("[role=tab]"));
    function select(t, focus) {
      tabs.forEach(function (x) {
        var on = x === t;
        x.setAttribute("aria-selected", String(on));
        x.tabIndex = on ? 0 : -1;
        var p = document.getElementById(x.getAttribute("aria-controls"));
        if (p) p.hidden = !on;
      });
      if (focus) t.focus();
      list.dispatchEvent(new CustomEvent("tabchange", { detail: tabs.indexOf(t) }));
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var n = null;
        if (e.key === "ArrowRight") n = tabs[(i + 1) % tabs.length];
        if (e.key === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === "Home") n = tabs[0];
        if (e.key === "End") n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* Steps stack: tabs drive which card is in front */
  var stack = document.querySelector("[data-steps]");
  if (stack) {
    var cards = Array.prototype.slice.call(stack.querySelectorAll(".step-card"));
    var stepList = document.querySelector("[data-steps-tabs]");
    /* Carousel: the next card slides in from the right, the current one slides out left.
       The card that wraps round (left back to right) jumps there out of sight, then fades in. */
    function show(idx) {
      cards.forEach(function (c, i) {
        var pos = (i - idx + cards.length) % cards.length;
        var prev = c.getAttribute("data-pos");
        if (prev === "2" && pos === 1) {
          c.classList.add("jump");
          c.setAttribute("data-pos", "1");
          void c.offsetWidth;
          requestAnimationFrame(function () { c.classList.remove("jump"); });
        } else {
          c.setAttribute("data-pos", String(pos));
        }
        c.setAttribute("aria-hidden", pos === 0 ? "false" : "true");
        c.tabIndex = -1;
      });
    }
    show(0);
    /* Loops forever every 5 seconds (1 > 2 > 3 > 1 ...). Only the pause button stops it;
       it also rests while the section is off screen or the tab is hidden, and carries on when back. */
    var ctrl = document.querySelector(".step-ctrl");
    var pauseBtn = document.querySelector("[data-steps-pause]");
    var stepTabs = stepList ? Array.prototype.slice.call(stepList.querySelectorAll("[role=tab]")) : [];
    var cur = 0, timer = null, userPaused = false, focused = false, onScreen = false;
    function canRun() { return !userPaused && !focused && onScreen && !document.hidden; }
    function restart() {
      clearTimeout(timer);
      if (!ctrl) return;
      ctrl.classList.remove("run", "hold");
      void ctrl.offsetWidth;
      if (!canRun()) return;
      ctrl.classList.add("run");
      timer = setTimeout(function () { var n = stepTabs[(cur + 1) % stepTabs.length]; if (n) n.click(); }, 5000);
    }
    if (stepList) stepList.addEventListener("tabchange", function (e) { cur = e.detail; show(cur); restart(); });
    var zone = stack.closest("section");
    if (zone) {
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (en) { onScreen = en[0].isIntersecting; restart(); }, { threshold: .15 }).observe(zone);
      } else { onScreen = true; }
    }
    document.addEventListener("visibilitychange", restart);
    if (pauseBtn) pauseBtn.addEventListener("click", function () {
      userPaused = !userPaused;
      pauseBtn.setAttribute("aria-pressed", String(userPaused));
      pauseBtn.setAttribute("aria-label", userPaused ? "Play automatic steps" : "Pause automatic steps");
      restart();
    });
    restart();
    cards.forEach(function (c, i) {
      c.addEventListener("click", function () {
        var t = stepList && stepList.querySelectorAll("[role=tab]")[i];
        if (t) t.click();
      });
    });
  }

  /* Photo loop (inside the folio): fades every 4.5 s, dots to jump, pause button */
  document.querySelectorAll("[data-slideshow]").forEach(function (box) {
    var slides = Array.prototype.slice.call(box.querySelectorAll(".slide"));
    var dots = Array.prototype.slice.call(box.querySelectorAll(".slide-dot"));
    var pause = box.querySelector("[data-slide-pause]");
    var cur = 0, t = null, paused = false, seen = false;
    slides.forEach(function (im) { im.loading = "eager"; });
    function go(n) {
      cur = (n + slides.length) % slides.length;
      slides.forEach(function (s, i) { s.classList.toggle("on", i === cur); s.setAttribute("aria-hidden", String(i !== cur)); });
      dots.forEach(function (d, i) { if (i === cur) d.setAttribute("aria-current", "true"); else d.removeAttribute("aria-current"); });
      tick();
    }
    function tick() {
      clearTimeout(t);
      if (!paused && seen && !document.hidden) t = setTimeout(function () { go(cur + 1); }, 4500);
    }
    dots.forEach(function (d, i) { d.addEventListener("click", function () { go(i); }); });
    if (pause) pause.addEventListener("click", function () {
      paused = !paused;
      pause.setAttribute("aria-pressed", String(paused));
      pause.setAttribute("aria-label", paused ? "Play photos" : "Pause photos");
      tick();
    });
    if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { seen = en[0].isIntersecting; tick(); }, { threshold: .2 }).observe(box);
    else seen = true;
    document.addEventListener("visibilitychange", tick);
    go(0);
  });

  /* Product film: plays muted when in view, pauses when scrolled away.
     Visitors who prefer less motion get a play button instead of autoplay. */
  document.querySelectorAll("[data-film]").forEach(function (box) {
    var v = box.querySelector("video");
    var playBtn = box.querySelector("[data-film-play]");
    var soundBtn = box.querySelector("[data-film-sound]");
    var startBtn = box.querySelector("[data-film-start]");
    var userPaused = reduce, inView = false;
    function sync() {
      var paused = v.paused;
      playBtn.setAttribute("aria-pressed", String(paused));
      playBtn.setAttribute("aria-label", paused ? "Play video" : "Pause video");
    }
    function tryPlay() { var p = v.play(); if (p && p.catch) p.catch(function () { box.classList.add("idle"); }); }
    function update() {
      if (inView && !userPaused && !document.hidden) { if (v.preload === "none") v.preload = "auto"; tryPlay(); }
      else if (!v.paused) v.pause();
    }
    if (reduce) box.classList.add("idle");
    v.addEventListener("play", function () { box.classList.remove("idle"); sync(); });
    v.addEventListener("pause", sync);
    playBtn.addEventListener("click", function () { userPaused = !v.paused; if (userPaused) v.pause(); else tryPlay(); });
    startBtn.addEventListener("click", function () { userPaused = false; v.preload = "auto"; tryPlay(); });
    soundBtn.addEventListener("click", function () {
      v.muted = !v.muted;
      soundBtn.setAttribute("aria-pressed", String(!v.muted));
      soundBtn.setAttribute("aria-label", v.muted ? "Turn sound on" : "Turn sound off");
      if (!v.muted && v.paused) { userPaused = false; tryPlay(); }
    });
    if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { inView = en[0].isIntersecting; update(); }, { threshold: .35 }).observe(box);
    else { inView = true; update(); }
    document.addEventListener("visibilitychange", update);
    sync();
  });

    /* Colour swatches swap the product photo */
  document.querySelectorAll("[data-swatches]").forEach(function (group) {
    var img = document.getElementById(group.getAttribute("data-swatches"));
    var name = document.querySelector("[data-colour-name]");
    var btns = Array.prototype.slice.call(group.querySelectorAll(".swatch"));
    function pick(b, focus) {
      btns.forEach(function (x) { var on = x === b; x.setAttribute("aria-checked", String(on)); x.tabIndex = on ? 0 : -1; });
      if (focus) b.focus();
      if (!img) return;
      img.classList.add("swap");
      setTimeout(function () {
        img.src = b.getAttribute("data-src");
        img.srcset = b.getAttribute("data-srcset");
        img.alt = b.getAttribute("data-alt");
        img.classList.remove("swap");
      }, reduce ? 0 : 180);
      if (name) name.textContent = b.getAttribute("data-name");
    }
    btns.forEach(function (b, i) {
      b.addEventListener("click", function () { pick(b); });
      b.addEventListener("keydown", function (e) {
        var n = null;
        if (e.key === "ArrowRight" || e.key === "ArrowDown") n = btns[(i + 1) % btns.length];
        if (e.key === "ArrowLeft" || e.key === "ArrowUp") n = btns[(i - 1 + btns.length) % btns.length];
        if (n) { e.preventDefault(); pick(n, true); }
      });
    });
  });

  /* Assistant demo (canned answers, clearly labelled as an example) */
  var chat = document.querySelector("[data-chat]");
  if (chat) {
    var answers = JSON.parse(chat.getAttribute("data-chat"));
    var out = chat.querySelector(".bubble.ai");
    var q = chat.querySelector(".bubble.me");
    var promptBtns = Array.prototype.slice.call(document.querySelectorAll("[data-prompt]"));
    promptBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        promptBtns.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        var a = answers[b.getAttribute("data-prompt")];
        q.textContent = b.textContent;
        out.textContent = "…";
        setTimeout(function () { out.textContent = a; }, reduce ? 0 : 380);
      });
    });
  }

  /* Integrations hub: curved lines from the core to each icon */
  var hub = document.querySelector(".hub");
  function drawHub() {
    if (!hub) return;
    var svg = hub.querySelector("svg.lines");
    var core = hub.querySelector(".core");
    var box = hub.getBoundingClientRect();
    var c = core.getBoundingClientRect();
    var cx = c.left - box.left + c.width / 2, cy = c.top - box.top + c.height / 2;
    svg.setAttribute("viewBox", "0 0 " + box.width + " " + box.height);
    var d = "", pulses = "";
    hub.querySelectorAll(".node").forEach(function (n, i) {
      if (n.offsetParent === null) return;
      var r = n.getBoundingClientRect();
      var nx = r.left - box.left + r.width / 2, ny = r.top - box.top + r.height / 2;
      var mx = (cx + nx) / 2;
      var path = "M" + cx + "," + cy + " C" + mx + "," + cy + " " + mx + "," + ny + " " + nx + "," + ny;
      d += '<path class="hub-line" d="' + path + '" opacity="' + (n.classList.contains("faint") ? .35 : .8) + '"/>';
      if (!n.classList.contains("faint") && i % 2 === 0) pulses += '<path class="hub-pulse" d="' + path + '" style="animation-delay:-' + (i * .55) + 's"/>';
    });
    svg.innerHTML = d + (reduce ? "" : pulses);
  }
  if (hub) { drawHub(); window.addEventListener("resize", drawHub); window.addEventListener("load", drawHub); }

  /* Reward state shared by the scratch card and the pre-order form */
  function hasReward() { return store.get(REWARD_KEY) === "1"; }
  function markReward() {
    store.set(REWARD_KEY, "1");
    document.documentElement.classList.add("has-reward");
    var f = document.querySelector("input[name=reward]");
    if (f) f.value = CFG.reward + " scratch-card reward";
  }
  if (hasReward()) markReward();

  /* Scratch scratchCards (homepage section and the welcome pop-up). Revealing one reveals them all. */
  var scratchCards = [];
  function setupScratch(sc) {
    var canvas = sc.querySelector("canvas");
    var ctx = canvas.getContext("2d");
    var group = sc.closest("[data-scratch-group]") || sc.parentElement;
    var live = document.getElementById("scratch-live");
    var done = false, drawing = false, last = null, moves = 0;

    function paintFoil() {
      if (done) return;
      var r = sc.getBoundingClientRect();
      if (!r.width) return;
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(r.width * dpr);
      canvas.height = Math.round(r.height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var w = r.width, h = r.height;
      ctx.globalCompositeOperation = "source-over";
      var g = ctx.createLinearGradient(0, 0, w, h);
      g.addColorStop(0, "#2f6fe4"); g.addColorStop(.45, "#5b9af2"); g.addColorStop(.6, "#cfe2fb"); g.addColorStop(.75, "#5b9af2"); g.addColorStop(1, "#1f4fb8");
      ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
      for (var i = 0; i < w * h / 60; i++) {
        ctx.fillStyle = "rgba(255,255,255," + (Math.random() * .12).toFixed(3) + ")";
        ctx.fillRect(Math.random() * w, Math.random() * h, 1.2, 1.2);
      }
      ctx.strokeStyle = "rgba(255,255,255,.55)"; ctx.lineWidth = 1.5; ctx.setLineDash([5, 5]);
      ctx.beginPath(); ctx.moveTo(14, h * .22); ctx.lineTo(w / 2, h * .62); ctx.lineTo(w - 14, h * .22); ctx.stroke();
      ctx.setLineDash([]);
      ctx.strokeStyle = "rgba(255,255,255,.35)";
      ctx.strokeRect(10.5, 10.5, w - 21, h - 21);
      ctx.fillStyle = "#fff"; ctx.textAlign = "center";
      ctx.font = "600 13px Inter, system-ui, sans-serif";
      ctx.fillText((CFG.brand || "").toUpperCase() + " REWARDS", w / 2, h * .16);
      ctx.font = "500 " + Math.max(22, Math.round(w / 15)) + "px 'Inter Tight', Inter, system-ui, sans-serif";
      ctx.fillText("Scratch to reveal", w / 2, h * .8);
      ctx.font = "400 14px Inter, system-ui, sans-serif";
      ctx.fillStyle = "rgba(255,255,255,.85)";
      ctx.fillText("Use a finger or your mouse", w / 2, h * .8 + 26);
    }
    function point(e) { var r = canvas.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
    function scratchLine(a, b) {
      ctx.globalCompositeOperation = "destination-out";
      ctx.strokeStyle = "#000"; ctx.globalAlpha = 1;
      ctx.lineCap = "round"; ctx.lineJoin = "round";
      ctx.lineWidth = Math.max(36, canvas.getBoundingClientRect().width / 9);
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x + .01, b.y + .01); ctx.stroke();
    }
    function cleared() {
      var data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      var step = 24, total = 0, clear = 0;
      for (var i = 3; i < data.length; i += 4 * step) { total++; if (data[i] < 40) clear++; }
      return clear / total;
    }
    function burst() {
      if (reduce) return;
      var wrap = sc.querySelector(".confetti");
      var colours = ["#2f6fe4", "#8fb8f6", "#d9a46c", "#3b2f24", "#ffffff"];
      var html = "";
      for (var i = 0; i < 36; i++) {
        var ang = Math.random() * Math.PI * 2, dist = 120 + Math.random() * 160;
        html += '<i style="background:' + colours[i % colours.length] + ";--x:" + Math.cos(ang) * dist + "px;--y:" + Math.sin(ang) * dist + "px;--r:" + (Math.random() * 540 - 270) + "deg;animation-delay:" + Math.random() * .12 + 's"></i>';
      }
      wrap.innerHTML = html;
      setTimeout(function () { wrap.innerHTML = ""; }, 1500);
    }
    function reveal(silent) {
      if (done) return;
      done = true;
      sc.classList.add("done");
      markReward();
      if (!silent) {
        burst();
        if (live) live.textContent = "Revealed: " + CFG.reward + " off. You pay " + CFG.priceReward + " instead of " + CFG.price + ". Your reward is saved and added to your pre-order.";
        scratchCards.forEach(function (c) { if (c.reveal !== reveal) c.reveal(true); });
      }
    }
    canvas.addEventListener("pointerdown", function (e) {
      if (done) return;
      drawing = true; last = point(e);
      try { canvas.setPointerCapture(e.pointerId); } catch (x) {}
      scratchLine(last, last);
    });
    canvas.addEventListener("pointermove", function (e) {
      if (!drawing || done) return;
      var p = point(e);
      scratchLine(last, p); last = p;
      if (++moves % 8 === 0 && cleared() > .48) reveal();
    });
    function end() { if (drawing && !done && cleared() > .48) reveal(); drawing = false; }
    canvas.addEventListener("pointerup", end);
    canvas.addEventListener("pointercancel", end);
    var btn = group.querySelector("[data-reveal]");
    if (btn) btn.addEventListener("click", function () { reveal(); });
    return { reveal: reveal, paint: paintFoil, untouched: function () { return moves === 0; } };
  }
  document.querySelectorAll("[data-scratch]").forEach(function (sc) { scratchCards.push(setupScratch(sc)); });
  if (hasReward()) scratchCards.forEach(function (c) { c.reveal(true); });
  else {
    scratchCards.forEach(function (c) { c.paint(); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { scratchCards.forEach(function (c) { if (c.untouched()) c.paint(); }); });
    var rw;
    window.addEventListener("resize", function () { clearTimeout(rw); rw = setTimeout(function () { scratchCards.forEach(function (c) { if (c.untouched()) c.paint(); }); }, 150); });
  }

  /* Welcome pop-up: once per visitor, only if the reward isn't revealed yet */
  var promo = document.getElementById("promo");
  var PROMO_KEY = "noteai-promo-seen";
  if (promo && !hasReward() && store.get(PROMO_KEY) !== "1") {
    var promoCard = promo.querySelector(".promo-card");
    var lastFocus = null;
    var promoScratch = scratchCards.filter(function (c, i) { return promo.contains(document.querySelectorAll("[data-scratch]")[i]); })[0];
    function focusables() { return Array.prototype.slice.call(promoCard.querySelectorAll("a[href],button:not([disabled])")).filter(function (el) { return el.offsetParent !== null; }); }
    function onKey(e) {
      if (e.key === "Escape") { e.preventDefault(); closePromo(); return; }
      if (e.key === "Tab") {
        var f = focusables(); if (!f.length) return;
        var first = f[0], lastEl = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastEl.focus(); }
        else if (!e.shiftKey && document.activeElement === lastEl) { e.preventDefault(); first.focus(); }
      }
    }
    function openPromo() {
      if (hasReward()) return;
      lastFocus = document.activeElement;
      promo.hidden = false;
      document.documentElement.classList.add("promo-open");
      requestAnimationFrame(function () { promo.classList.add("is-open"); if (promoScratch) promoScratch.paint(); });
      store.set(PROMO_KEY, "1");
      document.addEventListener("keydown", onKey);
      promoCard.setAttribute("tabindex", "-1"); setTimeout(function () { promoCard.focus({ preventScroll: true }); }, 50);
    }
    function closePromo() {
      promo.classList.remove("is-open");
      document.documentElement.classList.remove("promo-open");
      document.removeEventListener("keydown", onKey);
      setTimeout(function () { promo.hidden = true; }, reduce ? 0 : 250);
      if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    }
    promo.querySelectorAll("[data-promo-close]").forEach(function (b) { b.addEventListener("click", closePromo); });
    setTimeout(openPromo, 1200);
  }

  /* Pre-order form: validate, then hand off to WhatsApp or email (no server) */
  var form = document.getElementById("preorder-form");
  if (form) {
    var shell = form.closest("[data-form-shell]");
    var params = new URLSearchParams(window.location.search);
    var pre = params.get("colour");
    if (pre) { var r = form.querySelector('input[name=colour][value="' + pre + '"]'); if (r) r.checked = true; }
    if (hasReward()) markReward();

    function setErr(field, msg) {
      var wrap = field.closest(".field");
      if (!wrap) return;
      var err = wrap.querySelector(".err");
      if (msg) { wrap.setAttribute("data-invalid", ""); if (err) err.textContent = msg; field.setAttribute("aria-invalid", "true"); }
      else { wrap.removeAttribute("data-invalid"); field.removeAttribute("aria-invalid"); }
    }
    function validate() {
      var ok = true, firstBad = null;
      var name = form.elements.name, email = form.elements.email, phone = form.elements.phone, consent = form.elements.consent;
      var colour = form.querySelector("input[name=colour]:checked");
      function bad(el, msg) { setErr(el, msg); ok = false; if (!firstBad) firstBad = el; }
      if (!name.value.trim()) bad(name, "Please add your full name."); else setErr(name);
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) bad(email, "Please add a valid email address, like name@company.co.za."); else setErr(email);
      var digits = phone.value.replace(/\D/g, "");
      if (digits.length < 9 || digits.length > 12) bad(phone, "Please add a phone number we can reach you on, like 082 123 4567."); else setErr(phone);
      var cf = form.querySelector("[data-colour-field]");
      if (!colour) { cf.setAttribute("data-invalid", ""); ok = false; if (!firstBad) firstBad = form.querySelector("input[name=colour]"); } else cf.removeAttribute("data-invalid");
      if (!consent.checked) bad(consent, "Please agree so we can contact you about your pre-order."); else setErr(consent);
      if (firstBad) firstBad.focus();
      return ok;
    }
    form.querySelectorAll("input,select,textarea").forEach(function (el) {
      el.addEventListener("input", function () { if (el.closest("[data-invalid]")) { el.closest("[data-invalid]").removeAttribute("data-invalid"); el.removeAttribute("aria-invalid"); } });
      el.addEventListener("change", function () { if (el.closest("[data-invalid]")) el.closest("[data-invalid]").removeAttribute("data-invalid"); });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) return;
      var colour = form.querySelector("input[name=colour]:checked").value;
      var reward = hasReward() ? "Yes, " + CFG.reward + " scratch-card reward" : "No";
      var price = hasReward() ? CFG.priceReward + " once-off (" + CFG.price + " RRP less " + CFG.reward + " reward)" : CFG.price + " once-off (RRP)";
      var data = {
        Name: form.elements.name.value.trim(),
        Email: form.elements.email.value.trim(),
        Phone: form.elements.phone.value.trim(),
        Colour: colour,
        Province: form.elements.province.value || "Not given",
        Price: price,
        Gift: CFG.gift,
        Reward: reward,
        Notes: form.elements.notes.value.trim() || "None"
      };
      var lines = ["Hi " + CFG.brand + " team, I'd like to place a pre-order.", ""];
      Object.keys(data).forEach(function (k) { lines.push(k + ": " + data[k]); });
      var msg = lines.join("\n");
      var wa = "https://wa.me/" + CFG.whatsapp + "?text=" + encodeURIComponent(msg);
      var mail = "mailto:" + CFG.email + "?subject=" + encodeURIComponent("Pre-order: " + data.Name + " (" + colour + ")") + "&body=" + encodeURIComponent(msg);
      shell.querySelector("[data-send-wa]").href = wa;
      shell.querySelector("[data-send-mail]").href = mail;
      var dl = shell.querySelector("[data-summary]");
      dl.innerHTML = "";
      ["Name", "Email", "Phone", "Colour", "Price"].forEach(function (k) {
        var dt = document.createElement("dt"); dt.textContent = k;
        var dd = document.createElement("dd"); dd.textContent = data[k];
        dl.appendChild(dt); dl.appendChild(dd);
      });
      shell.classList.add("sent");
      var h = shell.querySelector(".success h2");
      h.setAttribute("tabindex", "-1"); h.focus();
      window.scrollTo({ top: shell.getBoundingClientRect().top + window.scrollY - 100, behavior: reduce ? "auto" : "smooth" });
    });
    var again = shell.querySelector("[data-edit]");
    if (again) again.addEventListener("click", function () { shell.classList.remove("sent"); form.elements.name.focus(); });
  }

  /* Contact form: same hand-off pattern */
  var cform = document.getElementById("contact-form");
  if (cform) {
    var cshell = cform.closest("[data-form-shell]");
    cform.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true, first = null;
      [["cname", function (v) { return v.trim(); }, "Please add your name."],
       ["cemail", function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()); }, "Please add a valid email address."],
       ["cmsg", function (v) { return v.trim().length > 4; }, "Please tell us a little more."]].forEach(function (r) {
        var el = cform.elements[r[0]];
        if (!r[1](el.value)) { setE(el, r[2]); ok = false; if (!first) first = el; } else setE(el);
      });
      function setE(el, m) { var w = el.closest(".field"); if (m) { w.setAttribute("data-invalid", ""); w.querySelector(".err").textContent = m; el.setAttribute("aria-invalid", "true"); } else { w.removeAttribute("data-invalid"); el.removeAttribute("aria-invalid"); } }
      if (!ok) { first.focus(); return; }
      var msg = "Hi " + CFG.brand + " team,\n\n" + cform.elements.cmsg.value.trim() + "\n\n" + cform.elements.cname.value.trim() + "\n" + cform.elements.cemail.value.trim();
      cshell.querySelector("[data-send-wa]").href = "https://wa.me/" + CFG.whatsapp + "?text=" + encodeURIComponent(msg);
      cshell.querySelector("[data-send-mail]").href = "mailto:" + CFG.email + "?subject=" + encodeURIComponent("Question from " + cform.elements.cname.value.trim()) + "&body=" + encodeURIComponent(msg);
      cshell.classList.add("sent");
      var h = cshell.querySelector(".success h2"); h.setAttribute("tabindex", "-1"); h.focus();
    });
  }
})();
