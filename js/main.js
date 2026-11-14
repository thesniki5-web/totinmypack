(function () {
  "use strict";

  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".site-nav");
  var dialog = document.getElementById("player-dialog");
  var frame = dialog ? dialog.querySelector(".player-frame") : null;
  var caption = dialog ? dialog.querySelector(".player-caption") : null;
  var fallback = dialog ? dialog.querySelector(".youtube-fallback") : null;
  var lastFocus = null;

  function onScroll() {
    if (!header) return;
    header.classList.toggle("is-stuck", window.scrollY > 24);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  function isMobileNav() {
    return window.matchMedia("(max-width: 880px)").matches;
  }

  function setMobileMenuOpen(open) {
    if (!toggle || !nav) return;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    nav.classList.toggle("is-open", open);
    document.body.classList.toggle("nav-open", open);
    if (isMobileNav()) {
      document.querySelectorAll(".has-sub").forEach(function (item) {
        var btn = item.querySelector(":scope > .nav-label");
        if (!btn) return;
        btn.setAttribute("aria-expanded", String(open));
        item.classList.toggle("is-open", open);
      });
    }
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      setMobileMenuOpen(!open);
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setMobileMenuOpen(false);
      });
    });
  }

  document.querySelectorAll(".has-sub").forEach(function (item) {
    var btn = item.querySelector(":scope > .nav-label");
    if (!btn) return;

    function setSubOpen(open) {
      btn.setAttribute("aria-expanded", String(open));
      item.classList.toggle("is-open", open);
    }

    btn.addEventListener("click", function () {
      if (isMobileNav()) {
        setSubOpen(true);
        return;
      }
      setSubOpen(btn.getAttribute("aria-expanded") !== "true");
    });
    item.addEventListener("mouseenter", function () {
      if (!isMobileNav()) setSubOpen(true);
    });
    item.addEventListener("mouseleave", function () {
      if (!isMobileNav()) setSubOpen(false);
    });
    item.addEventListener("focusin", function () {
      if (!isMobileNav()) setSubOpen(true);
    });
    item.addEventListener("focusout", function (e) {
      if (item.contains(e.relatedTarget)) return;
      if (!isMobileNav()) setSubOpen(false);
    });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (toggle && toggle.getAttribute("aria-expanded") === "true") {
      setMobileMenuOpen(false);
      toggle.focus();
      return;
    }
    document.querySelectorAll(".has-sub > .nav-label[aria-expanded='true']").forEach(function (btn) {
      btn.setAttribute("aria-expanded", "false");
      var item = btn.closest(".has-sub");
      if (item) item.classList.remove("is-open");
    });
  });

  function thumbUrl(id) {
    return "https://i.ytimg.com/vi/" + id + "/maxresdefault.jpg";
  }

  function openPlayer(id, title, kind, start) {
    if (!dialog || !frame) return;
    lastFocus = document.activeElement;
    var safeTitle = title || "YouTube video";
    var startSec = parseInt(start, 10);
    if (!(startSec > 0)) startSec = 0;
    var src =
      "https://www.youtube-nocookie.com/embed/" +
      encodeURIComponent(id) +
      "?autoplay=1&rel=0&modestbranding=1";
    if (startSec) src += "&start=" + startSec;
    frame.innerHTML =
      '<iframe src="' +
      src +
      '" title="' +
      safeTitle.replace(/"/g, "&quot;") +
      '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>';
    if (caption) caption.textContent = safeTitle;
    if (fallback) {
      var watch =
        "https://www.youtube.com/watch?v=" + encodeURIComponent(id);
      if (startSec) watch += "&t=" + startSec;
      fallback.innerHTML =
        '<a href="' +
        watch +
        '" rel="noopener noreferrer" data-goatcounter-click="out: youtube.com/' +
        id +
        '" data-goatcounter-title="Watch on YouTube">Watch on YouTube</a>';
      if (window.goatcounter && window.goatcounter.bind_events) {
        window.goatcounter.bind_events();
      }
    }
    dialog.dataset.kind = kind === "short" ? "short" : "film";
    if (typeof dialog.showModal === "function") {
      if (!dialog.open) dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
    var closeBtn = dialog.querySelector(".player-close");
    if (closeBtn) closeBtn.focus();
  }

  function closePlayer() {
    if (!dialog) return;
    if (frame) frame.innerHTML = "";
    if (typeof dialog.close === "function" && dialog.open) {
      dialog.close();
    } else {
      dialog.removeAttribute("open");
    }
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  if (dialog) {
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) closePlayer();
    });
    dialog.addEventListener("close", function () {
      if (frame) frame.innerHTML = "";
    });
    var closeBtn = dialog.querySelector(".player-close");
    if (closeBtn) closeBtn.addEventListener("click", closePlayer);
  }

  document.addEventListener("click", function (e) {
    var card = e.target.closest("[data-video-id]");
    if (!card) return;
    e.preventDefault();
    openPlayer(
      card.getAttribute("data-video-id"),
      card.getAttribute("data-title"),
      card.getAttribute("data-kind"),
      card.getAttribute("data-start")
    );
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var card = e.target.closest("[data-video-id]");
    if (!card || e.target !== card) return;
    e.preventDefault();
    openPlayer(
      card.getAttribute("data-video-id"),
      card.getAttribute("data-title"),
      card.getAttribute("data-kind"),
      card.getAttribute("data-start")
    );
  });

  var filterBar = document.querySelector("[data-filters]");
  if (filterBar) {
    var cards = Array.prototype.slice.call(document.querySelectorAll("[data-filter-item]"));
    var status = document.querySelector("[data-filter-status]");
    filterBar.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-filter]");
      if (!btn) return;
      filterBar.querySelectorAll("[data-filter]").forEach(function (b) {
        b.classList.toggle("is-active", b === btn);
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      var key = btn.getAttribute("data-filter");
      var shown = 0;
      cards.forEach(function (card) {
        var match = key === "all" || card.getAttribute("data-group") === key || card.getAttribute("data-kind") === key;
        card.classList.toggle("is-hidden", !match);
        if (match) shown += 1;
      });
      if (status) {
        status.textContent = shown + (shown === 1 ? " film shown." : " films shown.");
      }
    });
  }

  // Swap broken/placeholder thumbs if a maxres image is missing (defensive).
  document.querySelectorAll('img[data-fallback]').forEach(function (img) {
    img.addEventListener("error", function () {
      var id = img.getAttribute("data-fallback");
      if (!id) return;
      img.removeAttribute("data-fallback");
      img.removeAttribute("srcset");
      img.src = "https://i.ytimg.com/vi/" + id + "/hqdefault.jpg";
    });
  });

  // Outbound clicks not already marked with data-goatcounter-click (for example
  // Leaflet attribution). GoatCounter binds the marked links itself.
  function goatOutboundPath(href) {
    var url;
    try {
      url = new URL(href, window.location.href);
    } catch (err) {
      return "out: link";
    }
    var host = (url.hostname || "").replace(/^www\./, "").toLowerCase();
    var path = url.pathname || "";
    if (host === "youtube.com" || host === "m.youtube.com" || host === "youtu.be" || host === "youtube-nocookie.com") {
      var vid = "";
      if (host === "youtu.be") {
        vid = path.replace(/^\//, "").split("/")[0] || "";
      } else {
        vid = url.searchParams.get("v") || "";
        var parts = path.split("/").filter(Boolean);
        if (!vid && parts.length > 1 && (parts[0] === "embed" || parts[0] === "shorts" || parts[0] === "live" || parts[0] === "v")) {
          vid = parts[1];
        } else if (!vid && parts[0] && parts[0].charAt(0) === "@") {
          return "out: youtube.com/" + parts[0];
        } else if (!vid && parts.indexOf("playlist") !== -1) {
          return "out: youtube.com/playlist";
        }
      }
      if (vid) return "out: youtube.com/" + vid;
      return "out: youtube.com";
    }
    var label = host || "link";
    if (path && path !== "/") {
      var short = path.replace(/\/$/, "");
      if (short.length > 48) short = short.slice(0, 45) + "...";
      label = host + short;
    }
    return "out: " + label;
  }

  function trackOutbound(e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a || a.getAttribute("data-goatcounter-click")) return;
    var href = a.getAttribute("href");
    if (!href || !/^https?:/i.test(href)) return;
    var dest;
    try {
      dest = new URL(href, window.location.href);
    } catch (err) {
      return;
    }
    if (dest.origin === window.location.origin) return;
    if (!window.goatcounter || !window.goatcounter.count) return;
    var path = goatOutboundPath(href);
    var title = (a.getAttribute("data-goatcounter-title") || a.getAttribute("title") || a.textContent || path).trim();
    if (title.length > 200) title = title.slice(0, 200);
    window.goatcounter.count({ path: path, title: title, event: true });
  }

  document.addEventListener("click", trackOutbound);
  document.addEventListener("auxclick", trackOutbound);
})();
