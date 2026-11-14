(function () {
  var mount = document.getElementById("restaurant-map") || document.getElementById("hotel-map");
  var dataEl = document.getElementById("restaurant-map-data") || document.getElementById("hotel-map-data");
  if (!mount || !dataEl) return;
  var isHotel = mount.id === "hotel-map";
  var listKey = isHotel ? "hotels" : "restaurants";
  var cardPrefix = isHotel ? "hotel-" : "restaurant-";
  var focusSelector = isHotel ? "[data-hotel-focus]" : "[data-restaurant-focus]";
  var focusAttr = isHotel ? "data-hotel-focus" : "data-restaurant-focus";

  var started = false;
  var readyResolve = null;
  var readyPromise = null;
  var showRestaurantOnMap = null;

  function whenMapReady() {
    if (showRestaurantOnMap) return Promise.resolve(showRestaurantOnMap);
    if (!readyPromise) {
      readyPromise = new Promise(function (resolve) {
        readyResolve = function (fn) {
          showRestaurantOnMap = fn;
          resolve(fn);
        };
      });
      init();
    }
    return readyPromise;
  }

  document.addEventListener("click", function (ev) {
    var el = ev.target.closest(focusSelector);
    if (!el) return;
    ev.preventDefault();
    var id = el.getAttribute(focusAttr);
    whenMapReady().then(function (show) {
      show(id);
    });
  });
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

  function markerSizeForZoom(z) {
    if (z < 6) return 12;
    if (z < 7) return 16;
    if (z < 8) return 22;
    if (z < 10) return 28;
    return 36;
  }

  function markerIcon(num, size) {
    size = size || 36;
    var inner;
    if (size < 16) {
      inner =
        '<span class="trip-marker-num is-dot" style="width:' +
        size +
        "px;height:" +
        size +
        'px"></span>';
    } else {
      var fs = size >= 28 ? "0.72rem" : "0.55rem";
      inner =
        '<span class="trip-marker-num" style="width:' +
        size +
        "px;height:" +
        size +
        "px;font-size:" +
        fs +
        '">' +
        num +
        "</span>";
    }
    return window.L.divIcon({
      className: "trip-marker",
      html: inner,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
      popupAnchor: [0, -Math.round(size / 2) - 2]
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
    mapDiv.className = "trip-map-canvas restaurant-map-canvas";
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

      var bounds = [];
      var markers = {};
      var mapped = [];

      (data[listKey] || []).forEach(function (place, index) {
        if (place.lat == null || place.lng == null) return;
        var latlng = [place.lat, place.lng];
        bounds.push(latlng);
        var number = place.number != null ? place.number : index + 1;
        var marker = L.marker(latlng, {
          icon: markerIcon(number, 12),
          title: place.name,
          keyboard: true,
          riseOnHover: true
        }).addTo(map);

        var popup = document.createElement("div");
        popup.className = "trip-popup";
        var heading = document.createElement("p");
        heading.className = "trip-popup-name";
        heading.textContent = place.name;
        popup.appendChild(heading);
        if (place.place) {
          var loc = document.createElement("p");
          loc.className = "trip-popup-place";
          loc.textContent = place.place;
          popup.appendChild(loc);
        }
        if (place.cuisine) {
          var cuisine = document.createElement("p");
          cuisine.className = "trip-popup-place";
          cuisine.textContent = place.cuisine;
          popup.appendChild(cuisine);
        }
        if (place.teddy_note) {
          var note = document.createElement("p");
          note.className = "trip-popup-start";
          note.textContent = place.teddy_note;
          popup.appendChild(note);
        }
        if (place.website) {
          var link = document.createElement("a");
          link.className = "btn btn-ghost trip-popup-watch";
          link.href = place.website;
          link.rel = "noopener noreferrer";
          link.target = "_blank";
          link.textContent = "Website";
          popup.appendChild(link);
        }
        if (place.video_id) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "btn btn-gold trip-popup-watch";
          btn.setAttribute("data-video-id", place.video_id);
          btn.setAttribute("data-title", place.video_title || place.name);
          btn.setAttribute("data-kind", place.video_kind || "film");
          if (place.start_seconds > 0) {
            btn.setAttribute("data-start", String(place.start_seconds));
          }
          btn.textContent =
            place.start_seconds > 0
              ? "Watch from " + formatTime(place.start_seconds)
              : "Watch the film";
          popup.appendChild(btn);
        }
        marker.bindPopup(popup, { maxWidth: 280 });
        marker.on("click", function () {
          var hits = overlappingStops(place);
          if (hits.length > 1 && canSeparate(hits)) {
            map.closePopup();
            zoomToSeparate(hits);
            return;
          }
          highlight(place);
          revealMarker(marker);
        });
        markers[place.id] = marker;
        mapped.push(place);
      });

      var fitOpts = {
        padding: [36, 36],
        paddingBottomRight: [16, 36],
        animate: false
      };
      if (bounds.length) {
        fitOpts.maxZoom = data.maxZoom || 12;
        map.fitBounds(bounds, fitOpts);
      } else {
        var empty = data.default_bounds || [
          [24.5, -125],
          [49.4, 28.3]
        ];
        fitOpts.maxZoom = 4;
        map.fitBounds(empty, fitOpts);
      }

      var appliedMarkerSize = 0;

      function overlappingStops(place) {
        var marker = markers[place.id];
        if (!marker) return [place];
        var size = markerSizeForZoom(map.getZoom());
        var pt = map.latLngToLayerPoint(marker.getLatLng());
        var hits = [];
        mapped.forEach(function (s) {
          var m = markers[s.id];
          if (!m) return;
          var p = map.latLngToLayerPoint(m.getLatLng());
          var dx = p.x - pt.x;
          var dy = p.y - pt.y;
          if (Math.sqrt(dx * dx + dy * dy) < size) hits.push(s);
        });
        return hits;
      }

      function minSeparation(hits, zTry) {
        var minPx = Infinity;
        var i, j;
        for (i = 0; i < hits.length; i++) {
          for (j = i + 1; j < hits.length; j++) {
            var p1 = map.project(markers[hits[i].id].getLatLng(), zTry);
            var p2 = map.project(markers[hits[j].id].getLatLng(), zTry);
            var d = p1.distanceTo(p2);
            if (d < minPx) minPx = d;
          }
        }
        return minPx;
      }

      function canSeparate(hits) {
        return minSeparation(hits, 18) >= markerSizeForZoom(18) + 10;
      }

      function zoomToSeparate(hits) {
        var z = map.getZoom();
        var maxZ = 18;
        var target = Math.min(z + 2, maxZ);
        var zTry;
        for (zTry = z + 1; zTry <= maxZ; zTry++) {
          target = zTry;
          if (minSeparation(hits, zTry) >= markerSizeForZoom(zTry) + 10) break;
        }
        var area = L.latLngBounds(
          hits.map(function (s) {
            return markers[s.id].getLatLng();
          })
        );
        map.setView(area.getCenter(), target, { animate: true });
      }

      function updateMarkerSizes() {
        var size = markerSizeForZoom(map.getZoom());
        if (size === appliedMarkerSize) return;
        appliedMarkerSize = size;
        mapped.forEach(function (place) {
          var m = markers[place.id];
          var number = place.number != null ? place.number : mapped.indexOf(place) + 1;
          if (m) m.setIcon(markerIcon(number, size));
        });
      }

      function highlight(place) {
        document.querySelectorAll(".restaurant-card.is-active, .hotel-card.is-active").forEach(function (el) {
          el.classList.remove("is-active");
        });
        if (!place) return;
        var card = document.getElementById(cardPrefix + place.id);
        if (card) card.classList.add("is-active");
      }

      function reduceMotion() {
        return (
          window.matchMedia &&
          window.matchMedia("(prefers-reduced-motion: reduce)").matches
        );
      }

      function focusPopup(marker) {
        var popup = marker.getPopup();
        var el = popup && popup.getElement();
        if (!el) return;
        var target =
          el.querySelector(".trip-popup-name") ||
          el.querySelector(".leaflet-popup-content");
        if (!target) return;
        if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
        try {
          target.focus({ preventScroll: true });
        } catch (err) {
          target.focus();
        }
      }

      function revealMarker(marker, zoom) {
        map.invalidateSize();
        var ll = marker.getLatLng();
        var targetZoom = Math.max(map.getZoom(), zoom || 16);
        var already =
          map.getZoom() === targetZoom &&
          map.getCenter().equals(ll, 0.00005);
        function open() {
          marker.openPopup();
          focusPopup(marker);
        }
        if (already) {
          open();
          return;
        }
        map.once("moveend", open);
        map.setView(ll, targetZoom, { animate: !reduceMotion() });
        window.setTimeout(function () {
          if (!marker.isPopupOpen()) open();
        }, 900);
      }

      function showRestaurant(id) {
        var marker = markers[id];
        var place = null;
        mapped.forEach(function (s) {
          if (s.id === id) place = s;
        });
        if (!marker || !place) return;
        highlight(place);
        mount.scrollIntoView({
          behavior: reduceMotion() ? "auto" : "smooth",
          block: "center"
        });
        window.setTimeout(function () {
          revealMarker(marker, 16);
        }, reduceMotion() ? 50 : 450);
      }

      updateMarkerSizes();
      map.on("zoomend", updateMarkerSizes);

      map.invalidateSize();
      setTimeout(function () {
        map.invalidateSize();
        updateMarkerSizes();
      }, 250);

      if (readyResolve) readyResolve(showRestaurant);
    }).catch(function () {
      mount.innerHTML =
        '<p class="trip-map-fallback">The map could not be loaded. The list is below.</p>';
      if (readyResolve) readyResolve(function () {});
    });
  }

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            io.disconnect();
            whenMapReady();
          }
        });
      },
      { rootMargin: "240px 0px" }
    );
    io.observe(mount);
  } else {
    whenMapReady();
  }
})();
