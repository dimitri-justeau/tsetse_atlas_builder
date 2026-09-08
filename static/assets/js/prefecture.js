var offset = $('#sidebar-container li').first().position().top;
$('#sidebar-container').scrollTop($('#' + current).position().top - offset);

var map = L.map(
    'map', {
        zoomSnap: 0.25,
        zoomDelta: 0.25
    }).setView([10.0, -11.1], 7.5);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var prefecture_path = asset_root + "/geojson/" + current + ".geojson";
var prefecture_geojson = null;

fetch(prefecture_path)
    .then(response => response.json())
    .then(data => {
        prefecture_geojson = L.geoJSON(data).addTo(map);
        map.fitBounds(prefecture_geojson.getBounds());
        if (prefecture_geojson != null) {
            prefecture_geojson.bringToFront();
        }
    })
    .catch(error => console.error('Erreur lors du chargement du fichier GeoJSON :', error));

var prefecture_traps_path = asset_root + "/geojson/" + current + "_traps.geojson";
var prefecture_traps_geojson = null;

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

fetch(prefecture_traps_path)
    .then(response => response.json())
    .then(data => {
        prefecture_traps_geojson = L.geoJSON(data, {
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
        prefecture_traps_geojson.bringToFront();
    })
    .catch(error => console.error('Erreur lors du chargement du fichier GeoJSON :', error));

new PureCounter();