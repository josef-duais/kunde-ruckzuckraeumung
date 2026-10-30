/* Ruckzuckräumung – gemeinsames Script (alle Seiten). Vanilla JS, keine Abhängigkeiten. */
(function () {
  "use strict";

  /* ---------- Scroll bei Seitenwechsel auf y=0 (außer bei Sprungmarken) */
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  if (!location.hash) window.scrollTo(0, 0);

  /* ---------- Navigation */
  var root = document.documentElement;
  var burger = document.querySelector(".nav-burger");
  function setNav(open) {
    root.classList.toggle("nav-open", open);
    if (burger) {
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "Menü schließen" : "Menü öffnen");
    }
    document.body.style.overflow = open ? "hidden" : "";
  }
  if (burger) burger.addEventListener("click", function () { setNav(!root.classList.contains("nav-open")); });
  document.querySelectorAll(".sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest(".has-sub");
      var open = !li.classList.contains("open");
      document.querySelectorAll(".has-sub.open").forEach(function (o) {
        if (o !== li) { o.classList.remove("open"); o.querySelector(".sub-toggle").setAttribute("aria-expanded", "false"); }
      });
      li.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
  });
  document.querySelectorAll(".nav a").forEach(function (a) { a.addEventListener("click", function () { setNav(false); }); });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    setNav(false);
    document.querySelectorAll(".has-sub.open").forEach(function (o) { o.classList.remove("open"); });
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".has-sub")) document.querySelectorAll(".has-sub.open").forEach(function (o) {
      o.classList.remove("open"); o.querySelector(".sub-toggle").setAttribute("aria-expanded", "false");
    });
  });

  /* ---------- Formular: Leistung per ?leistung=… vorbelegen */
  var pre = new URLSearchParams(location.search).get("leistung");
  if (pre) document.querySelectorAll('select[name="Leistung"]').forEach(function (s) {
    Array.prototype.forEach.call(s.options, function (o) { if (o.text.toLowerCase() === pre.toLowerCase()) s.value = o.value || o.text; });
  });

  /* ---------- Angebots-Buttons: auf Seiten mit eigenem Formular direkt dorthin (Formular-Quelle bleibt erhalten) */
  if (document.getElementById("anfrage")) {
    document.querySelectorAll("a[data-cta]").forEach(function (a) { a.setAttribute("href", "#anfrage"); });
  }

  /* ---------- Lightbox: Fotos öffnen als Popup auf derselben Seite (Pfeile, Esc, Wischen) */
  var lbLinks = Array.prototype.slice.call(document.querySelectorAll("a[data-lightbox]"));
  if (lbLinks.length) {
    var lb = document.createElement("div");
    lb.className = "lb";
    lb.setAttribute("role", "dialog");
    lb.setAttribute("aria-modal", "true");
    lb.setAttribute("aria-label", "Bildansicht");
    lb.hidden = true;
    lb.innerHTML = '<button type="button" class="lb-close" aria-label="Schließen">&times;</button>' +
      '<button type="button" class="lb-prev" aria-label="Vorheriges Bild">&#8249;</button>' +
      '<figure class="lb-fig"><img alt=""><figcaption></figcaption></figure>' +
      '<button type="button" class="lb-next" aria-label="Nächstes Bild">&#8250;</button>';
    document.body.appendChild(lb);
    var lbImg = lb.querySelector("img"), lbCap = lb.querySelector("figcaption"), lbIdx = 0, lastFocus = null;
    function lbShow(i) {
      lbIdx = (i + lbLinks.length) % lbLinks.length;
      var a = lbLinks[lbIdx], img = a.querySelector("img"), fig = a.closest("figure"), cap = fig && fig.querySelector("figcaption");
      lbImg.src = a.getAttribute("href");
      lbImg.alt = img ? img.alt : "";
      lbCap.textContent = cap ? cap.textContent : (img ? img.alt : "");
    }
    function lbOpen(i) {
      lastFocus = document.activeElement;
      lbShow(i);
      lb.hidden = false;
      document.body.style.overflow = "hidden";
      lb.querySelector(".lb-close").focus();
    }
    function lbClose() {
      lb.hidden = true;
      lbImg.removeAttribute("src");
      document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    }
    lbLinks.forEach(function (a, i) {
      a.addEventListener("click", function (e) { e.preventDefault(); lbOpen(i); });
    });
    lb.querySelector(".lb-close").addEventListener("click", lbClose);
    lb.querySelector(".lb-prev").addEventListener("click", function () { lbShow(lbIdx - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { lbShow(lbIdx + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) lbClose(); });
    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") lbClose();
      else if (e.key === "ArrowLeft") lbShow(lbIdx - 1);
      else if (e.key === "ArrowRight") lbShow(lbIdx + 1);
    });
    var touchX = null;
    lb.addEventListener("touchstart", function (e) { touchX = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (touchX === null) return;
      var dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 50) lbShow(lbIdx + (dx < 0 ? 1 : -1));
      touchX = null;
    });
  }

  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- Cookie-Consent (Opt-in). Drittanbieter laden erst nach Einwilligung. */
  var KEY = "rz-consent-v1";
  var CATS = ["functional", "statistics", "marketing"];
  var banner = document.getElementById("cc-banner");
  var dialog = document.getElementById("cc-dialog");

  function read() {
    try { var v = JSON.parse(localStorage.getItem(KEY)); return v && v.v === 1 ? v : null; } catch (e) { return null; }
  }
  function store(choice) {
    var data = { v: 1, ts: new Date().toISOString() };
    CATS.forEach(function (c) { data[c] = !!choice[c]; });
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) { /* privater Modus */ }
    return data;
  }

  // Template-Inhalt einsetzen; <script>-Tags neu erzeugen, damit sie ausgeführt werden.
  function inject(tpl, target) {
    var frag = tpl.content.cloneNode(true);
    frag.querySelectorAll("script").forEach(function (old) {
      var s = document.createElement("script");
      Array.prototype.forEach.call(old.attributes, function (a) { s.setAttribute(a.name, a.value); });
      s.text = old.text;
      old.replaceWith(s);
    });
    target.appendChild(frag);
  }

  function apply(consent) {
    if (!consent) return;
    document.querySelectorAll(".consent-embed[data-consent]").forEach(function (box) {
      if (!consent[box.dataset.consent] || box.classList.contains("is-loaded")) return;
      var tpl = box.querySelector("template");
      if (tpl) inject(tpl, box);
      box.classList.add("is-loaded");
    });
    var chat = document.getElementById("chat-snippet");
    if (chat && consent[chat.dataset.consent] && !chat.dataset.loaded) {
      chat.dataset.loaded = "1";
      if (chat.content.querySelector("script, iframe, div")) {
        inject(chat, document.body);
        root.classList.add("chat-loaded");
      }
    }
    // GHL form_embed.js nur einmal auf Body-Ebene laden, falls GHL-iframes vorhanden sind
    if (consent.functional && document.querySelector('iframe[src*="leadconnectorhq"], iframe[src*="msgsndr"]') && !document.getElementById("ghl-form-embed")) {
      var s = document.createElement("script");
      s.id = "ghl-form-embed";
      s.src = "https://link.msgsndr.com/js/form_embed.js";
      s.async = true;
      document.body.appendChild(s);
    }
  }

  function decide(choice) {
    var c = store(choice);
    if (banner) banner.hidden = true;
    if (dialog && dialog.open) dialog.close();
    apply(c);
  }
  function all(val) { var o = {}; CATS.forEach(function (c) { o[c] = val; }); return o; }

  function openSettings() {
    if (!dialog) return;
    var c = read() || {};
    dialog.querySelectorAll("input[data-cat]").forEach(function (i) { i.checked = !!c[i.dataset.cat]; });
    if (typeof dialog.showModal === "function") dialog.showModal(); else dialog.setAttribute("open", "");
  }

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-cc], [data-cookie-settings], [data-consent-accept]");
    if (!t) return;
    if (t.hasAttribute("data-cookie-settings")) { e.preventDefault(); openSettings(); return; }
    if (t.hasAttribute("data-consent-accept")) {
      var cur = read() || all(false);
      cur[t.getAttribute("data-consent-accept")] = true;
      decide(cur);
      return;
    }
    var action = t.getAttribute("data-cc");
    if (action === "accept") decide(all(true));
    else if (action === "reject") decide(all(false));
    else if (action === "settings") openSettings();
    else if (action === "save") {
      var o = {};
      dialog.querySelectorAll("input[data-cat]").forEach(function (i) { o[i.dataset.cat] = i.checked; });
      decide(o);
    }
  });

  var saved = read();
  if (saved) apply(saved);
  else if (banner) banner.hidden = false;
})();
