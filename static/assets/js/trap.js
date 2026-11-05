$('.sidebar-toggle').on('click', function (e) {
  $('.app').toggleClass('is-collapsed');
  e.preventDefault();
});
/**
 * Wait untill sidebar fully toggled (animated in/out)
 * then trigger window resize event in order to recalculate
 * masonry layout widths and gutters.
 */
$('#sidebar-toggle').click(function (e) {
  e.preventDefault();
  setTimeout(function () {
    window.dispatchEvent(window.EVENT);
  }, 300);
});

var map = L.map(
    'map_trap', {
        zoomSnap: 0.25,
        zoomDelta: 0.25
    }).setView([10.0, -11.1], 7.5);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var trap_path = root + "/" + asset_root + "/geojson/traps/" + current + ".geojson";
var trap_geojson = null;

fetch(trap_path)
    .then(response => response.json())
    .then(data => {
        function tooltip(feature, layer) {
            layer.bindTooltip(String("<b>" + feature.properties.code + "</b>: " + feature.properties.total_tsetse) +' mouches');
        }
        trap_geojson = L.geoJSON(data, {
            onEachFeature: tooltip,
        }).addTo(map);
        trap_geojson.bringToFront();
        map.fitBounds(trap_geojson.getBounds());
    })
    .catch(error => console.error('Erreur lors du chargement du fichier GeoJSON :', error));

new PureCounter();