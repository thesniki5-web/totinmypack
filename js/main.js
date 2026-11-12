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

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
      document.body.classList.toggle("nav-open", !open);
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        document.body.classList.remove("nav-open");
      });
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && toggle && toggle.getAttribute("aria-expanded") === "true") {
      toggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
      document.body.classList.remove("nav-open");
      toggle.focus();
    }
  });

  function thumbUrl(id) {
    return "https://i.ytimg.com/vi/" + id + "/maxresdefault.jpg";
  }

  function openPlayer(id, title, kind) {
    if (!dialog || !frame) return;
    lastFocus = document.activeElement;
    var safeTitle = title || "YouTube video";
    var src =
      "https://www.youtube-nocookie.com/embed/" +
      encodeURIComponent(id) +
      "?autoplay=1&rel=0&modestbranding=1";
    frame.innerHTML =
      '<iframe src="' +
      src +
      '" title="' +
      safeTitle.replace(/"/g, "&quot;") +
      '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>';
    if (caption) caption.textContent = safeTitle;
    if (fallback) {
      fallback.innerHTML =
        '<a href="https://www.youtube.com/watch?v=' +
        encodeURIComponent(id) +
        '" rel="noopener noreferrer">Watch on YouTube</a>';
    }
    dialog.dataset.kind = kind === "short" ? "short" : "film";
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
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
    openPlayer(card.getAttribute("data-video-id"), card.getAttribute("data-title"), card.getAttribute("data-kind"));
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var card = e.target.closest("[data-video-id]");
    if (!card || e.target !== card) return;
    e.preventDefault();
    openPlayer(card.getAttribute("data-video-id"), card.getAttribute("data-title"), card.getAttribute("data-kind"));
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
      img.src = "https://i.ytimg.com/vi/" + id + "/hqdefault.jpg";
    });
  });
})();
