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
    'map', {
        zoomSnap: 0.25,
        zoomDelta: 0.25
    }).setView([10.0, -11.1], 7.5);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var region_path = asset_root + "/geojson/regions.geojson";
var regions_geojson = null;
var all_traps_path = asset_root + "/geojson/all_traps.geojson";
var all_traps_geojson = null;

fetch(region_path)
    .then(response => response.json())
    .then(data => {
        regions_geojson = L.geoJSON(data).addTo(map);
        map.fitBounds(regions_geojson.getBounds());
        if (all_traps_geojson != null) {
            all_traps_geojson.bringToFront();
        }
    })
    .catch(error => console.error('Erreur lors du chargement du fichier GeoJSON :', error));

function getColor(feature) {
    var d = feature.properties.total_tsetse;
    if (d > 0) {
        return '#2ecc71';
    } else {// Green
        return '#f39c12'; // Orange
    }
}

function getRadius(feature) {
    var d = feature.properties.total_tsetse;
    return 8 + 0.3*d;
}

fetch(all_traps_path)
    .then(response => response.json())
    .then(data => {
        all_traps_geojson = L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                var dynamicOptions = {
                    radius: getRadius(feature),
                    fillColor: getColor(feature),
                    color: "#000",
                    weight: 1,
                    fillOpacity: 0.9
                };
                return L.circleMarker(latlng, dynamicOptions);
            }
        }).addTo(map);
        all_traps_geojson.bringToFront();
    })
    .catch(error => console.error('Erreur lors du chargement du fichier GeoJSON :', error));

new PureCounter();