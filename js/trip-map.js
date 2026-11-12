(function () {
  var mount = document.getElementById("trip-map");
  var dataEl = document.getElementById("trip-map-data");
  if (!mount || !dataEl) return;

  var started = false;
  var leafletCss = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
  var leafletJs = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
  var leafletIntegrityCss =
    "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=";
  var leafletIntegrityJs =
    "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=";

  function loadCss(href, integrity) {
    return new Promise(function (resolve, reject) {
      if (document.querySelector('link[href="' + href + '"]')) {
        resolve();
        return;
      }
      var link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      link.crossOrigin = "";
      if (integrity) link.integrity = integrity;
      link.onload = function () { resolve(); };
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }

  function loadJs(src, integrity) {
    return new Promise(function (resolve, reject) {
      if (window.L) {
        resolve();
        return;
      }
      var script = document.createElement("script");
      script.src = src;
      script.crossOrigin = "";
      if (integrity) script.integrity = integrity;
      script.onload = function () { resolve(); };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function formatTime(sec) {
    sec = Math.floor(Number(sec) || 0);
    var m = Math.floor(sec / 60);
    var s = sec % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  function markerIcon(num, spur) {
    return window.L.divIcon({
      className: "trip-marker" + (spur ? " is-spur" : ""),
      html: '<span class="trip-marker-num">' + num + "</span>",
      iconSize: [36, 36],
      iconAnchor: [18, 18],
      popupAnchor: [0, -20]
    });
  }

  function init() {
    if (started) return;
    started = true;
    var data;
    try {
      data = JSON.parse(dataEl.textContent);
    } catch (err) {
      mount.textContent = "The map could not be loaded.";
      return;
    }

    mount.innerHTML = "";
    var mapDiv = document.createElement("div");
    mapDiv.className = "trip-map-canvas";
    mapDiv.setAttribute("role", "presentation");
    mount.appendChild(mapDiv);

    Promise.all([
      loadCss(leafletCss, leafletIntegrityCss),
      loadJs(leafletJs, leafletIntegrityJs)
    ]).then(function () {
      var L = window.L;
      var map = L.map(mapDiv, {
        scrollWheelZoom: false,
        attributionControl: true
      });
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }).addTo(map);

      if (data.route && data.route.length) {
        L.polyline(data.route, {
          color: "#d4b37a",
          weight: 4,
          opacity: 0.9,
          lineJoin: "round",
          lineCap: "round"
        }).addTo(map);
      }
      if (data.spur && data.spur.length) {
        L.polyline(data.spur, {
          color: "#d4b37a",
          weight: 3,
          opacity: 0.75,
          dashArray: "8 7",
          lineJoin: "round"
        }).addTo(map);
      }

      var bounds = [];
      var markers = {};
      var popups = {};
      var origins = {};
      var tourStops = [];
      var currentIndex = -1;

      (data.stops || []).forEach(function (stop) {
        if (!stop.on_map || stop.lat == null || stop.lon == null) return;
        var latlng = [stop.lat, stop.lon];
        bounds.push(latlng);
        var marker = L.marker(latlng, {
          icon: markerIcon(stop.number, stop.spur),
          title: stop.name,
          keyboard: true,
          riseOnHover: true
        }).addTo(map);

        var primary = (stop.videos && stop.videos[0]) || null;
        var popup = document.createElement("div");
        popup.className = "trip-popup";
        if (stop.photo) {
          var pic = document.createElement("img");
          pic.className = "trip-popup-photo";
          pic.src = stop.photo;
          pic.alt = stop.name;
          pic.width = 480;
          pic.height = 270;
          popup.appendChild(pic);
        }
        var heading = document.createElement("p");
        heading.className = "trip-popup-name";
        heading.textContent = stop.number + ". " + stop.name;
        popup.appendChild(heading);
        if (stop.place) {
          var place = document.createElement("p");
          place.className = "trip-popup-place";
          place.textContent = stop.place;
          popup.appendChild(place);
        }
        if (stop.start_seconds > 0) {
          var at = document.createElement("p");
          at.className = "trip-popup-start";
          at.textContent = "Starts at " + formatTime(stop.start_seconds);
          popup.appendChild(at);
        }
        if (stop.then_and_now && stop.then_and_now.text) {
          var thenBox = document.createElement("div");
          thenBox.className = "trip-popup-then";
          var thenLabel = document.createElement("p");
          thenLabel.className = "trip-popup-then-label";
          thenLabel.textContent = "Then and now";
          thenBox.appendChild(thenLabel);
          var thenText = document.createElement("p");
          thenText.textContent = stop.then_and_now.text;
          thenBox.appendChild(thenText);
          if (stop.then_and_now.source_url && stop.then_and_now.source_name) {
            var thenSrc = document.createElement("p");
            thenSrc.className = "trip-popup-then-source";
            thenSrc.appendChild(document.createTextNode("Source: "));
            var thenLink = document.createElement("a");
            thenLink.href = stop.then_and_now.source_url;
            thenLink.rel = "noopener noreferrer";
            thenLink.target = "_blank";
            thenLink.textContent = stop.then_and_now.source_name;
            thenSrc.appendChild(thenLink);
            thenBox.appendChild(thenSrc);
          }
          popup.appendChild(thenBox);
        }
        if (primary) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "btn btn-gold trip-popup-watch";
          btn.setAttribute("data-video-id", primary.id);
          btn.setAttribute("data-title", primary.title);
          btn.setAttribute("data-kind", primary.kind);
          if (stop.start_seconds > 0) {
            btn.setAttribute("data-start", String(stop.start_seconds));
          }
          btn.textContent = "Watch the film";
          popup.appendChild(btn);
        }
        marker.bindPopup(popup, { maxWidth: stop.photo ? 320 : 280 });
        marker.on("click", function () {
          goToStop(indexOfStop(stop.id), { play: true, fromMarker: true });
        });
        markers[stop.id] = marker;
        popups[stop.id] = popup;
        origins[stop.id] = latlng;
        tourStops.push(stop);
      });

      if (bounds.length) {
        var maxZoom = data.maxZoom || 9;
        map.fitBounds(bounds, { padding: [36, 36], maxZoom: maxZoom });
      }

      function offsetOverlappingPins() {
        var ids = Object.keys(markers);
        if (!ids.length || !map) return;
        var items = ids.map(function (id) {
          return { id: id, latlng: L.latLng(origins[id][0], origins[id][1]) };
        });
        var pts = items.map(function (it) {
          return map.latLngToLayerPoint(it.latlng);
        });
        var parent = items.map(function (_, i) { return i; });
        function find(i) {
          if (parent[i] !== i) parent[i] = find(parent[i]);
          return parent[i];
        }
        function union(a, b) {
          a = find(a);
          b = find(b);
          if (a !== b) parent[b] = a;
        }
        var minSep = 44;
        var i, j;
        for (i = 0; i < items.length; i++) {
          for (j = i + 1; j < items.length; j++) {
            var dx = pts[i].x - pts[j].x;
            var dy = pts[i].y - pts[j].y;
            if (Math.sqrt(dx * dx + dy * dy) < minSep) union(i, j);
          }
        }
        var groups = {};
        for (i = 0; i < items.length; i++) {
          var root = find(i);
          (groups[root] = groups[root] || []).push(i);
        }
        Object.keys(groups).forEach(function (key) {
          var idxs = groups[key];
          if (idxs.length === 1) {
            markers[items[idxs[0]].id].setLatLng(items[idxs[0]].latlng);
            return;
          }
          var cx = 0, cy = 0;
          idxs.forEach(function (k) { cx += pts[k].x; cy += pts[k].y; });
          cx /= idxs.length;
          cy /= idxs.length;
          var n = idxs.length;
          var radius = Math.max(28, 20 / Math.sin(Math.PI / n));
          idxs.forEach(function (k, idx) {
            var angle = (Math.PI * 2 * idx) / n - Math.PI / 2;
            var point = L.point(
              cx + Math.cos(angle) * radius,
              cy + Math.sin(angle) * radius
            );
            markers[items[k].id].setLatLng(map.layerPointToLatLng(point));
          });
        });
      }


      offsetOverlappingPins();
      map.on("zoomend", offsetOverlappingPins);

      var tour = document.getElementById("trip-tour");
      var prevBtn = document.getElementById("trip-tour-prev");
      var nextBtn = document.getElementById("trip-tour-next");
      var statusEl = document.getElementById("trip-tour-status");
      var playerTour = document.getElementById("player-tour");
      var playerPrev = document.getElementById("player-tour-prev");
      var playerNext = document.getElementById("player-tour-next");
      var playerStatus = document.getElementById("player-tour-status");

      function indexOfStop(id) {
        for (var i = 0; i < tourStops.length; i++) {
          if (tourStops[i].id === id) return i;
        }
        return -1;
      }

      function highlight(stop) {
        document.querySelectorAll(".trip-stop.is-active").forEach(function (el) {
          el.classList.remove("is-active");
        });
        if (!stop) return;
        var row = document.getElementById("stop-" + stop.id);
        if (row) row.classList.add("is-active");
      }

      function statusText(stop, index) {
        if (!stop || index < 0) return "Step through the stops";
        var n = stop.number != null ? stop.number : index + 1;
        return n + " of " + tourStops.length + " · " + stop.name;
      }

      function updateTourUi() {
        var stop = currentIndex >= 0 ? tourStops[currentIndex] : null;
        var text = statusText(stop, currentIndex);
        var prevDisabled = currentIndex <= 0;
        var nextDisabled =
          tourStops.length === 0 ||
          (currentIndex >= 0 && currentIndex >= tourStops.length - 1);
        if (statusEl) statusEl.textContent = text;
        if (prevBtn) prevBtn.disabled = prevDisabled;
        if (nextBtn) nextBtn.disabled = nextDisabled;
        if (playerStatus) playerStatus.textContent = text;
        if (playerPrev) playerPrev.disabled = prevDisabled;
        if (playerNext) playerNext.disabled = nextDisabled;
        if (playerTour) {
          if (currentIndex >= 0) playerTour.removeAttribute("hidden");
          else playerTour.setAttribute("hidden", "");
        }
      }

      function goToStop(index, opts) {
        opts = opts || {};
        if (index < 0 || index >= tourStops.length) return;
        var stop = tourStops[index];
        currentIndex = index;
        highlight(stop);
        updateTourUi();
        var marker = markers[stop.id];
        if (marker && !opts.fromMarker) {
          map.panTo(marker.getLatLng());
          marker.openPopup();
        }
        if (opts.play) {
          var popup = popups[stop.id];
          var watchBtn = popup ? popup.querySelector(".trip-popup-watch") : null;
          if (watchBtn) watchBtn.click();
        }
      }

      function goNext() {
        var next = currentIndex < 0 ? 0 : currentIndex + 1;
        goToStop(next, { play: true });
      }

      function goPrev() {
        goToStop(currentIndex - 1, { play: true });
      }

      if (tour && tourStops.length) {
        tour.removeAttribute("hidden");
        updateTourUi();
        if (prevBtn) prevBtn.addEventListener("click", goPrev);
        if (nextBtn) nextBtn.addEventListener("click", goNext);
      }
      if (playerPrev) playerPrev.addEventListener("click", goPrev);
      if (playerNext) playerNext.addEventListener("click", goNext);

      document.querySelectorAll("[data-stop-focus]").forEach(function (el) {
        el.addEventListener("click", function () {
          var id = el.getAttribute("data-stop-focus");
          var idx = indexOfStop(id);
          if (idx >= 0) {
            goToStop(idx, { play: false });
            return;
          }
          var marker = markers[id];
          if (!marker) return;
          map.panTo(marker.getLatLng());
          marker.openPopup();
        });
      });

      document.querySelectorAll("[data-stop-play]").forEach(function (el) {
        el.addEventListener("click", function () {
          var id = el.getAttribute("data-stop-play");
          var idx = indexOfStop(id);
          if (idx >= 0) goToStop(idx, { play: true });
        });
      });

      map.invalidateSize();
      setTimeout(function () {
        map.invalidateSize();
        offsetOverlappingPins();
      }, 250);
    }).catch(function () {
      mount.innerHTML =
        '<p class="trip-map-fallback">The map could not be loaded. The stops are listed below.</p>';
    });
  }

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            io.disconnect();
            init();
          }
        });
      },
      { rootMargin: "240px 0px" }
    );
    io.observe(mount);
  } else {
    init();
  }
})();
