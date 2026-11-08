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

var region_path = root + "/" + asset_root + "/geojson/regions.geojson";
var regions_geojson = null;
var all_traps_path = root + "/" + asset_root + "/geojson/all_traps.geojson";
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

fetch(all_traps_path)
    .then(response => response.json())
    .then(data => {
        function tooltip(feature, layer) {
            layer.bindTooltip(String("<b>" + feature.properties.code + "</b>: " + feature.properties.total_tsetse) +' mouches');
            layer.on({
                click: function(e) {
                    window.location.href = root + "/" + "traps/" + feature.properties.code + ".html";
                }
            });
        }
        let classes = [0, 1, 5, 10, 15]
        let colorRamp = [
            chroma("#ffffff").alpha(0.7),
            chroma("#fecc5c").alpha(0.7),
            chroma("#fd8d3c").alpha(0.7),
            chroma("#f03b20").alpha(0.7),
            chroma("#bd0026").alpha(0.7)
        ]
        if (data.features.length <= 5) {
            classes = [0, 1, 10]
            colorRamp = [
                chroma("#ffffff").alpha(0.7),
                chroma("#feb24c").alpha(0.7),
                chroma("#f03b20").alpha(0.7)
            ]
        }
        all_traps_geojson = L.dataClassification(data, {
            // required:
            mode: 'manual',
            classes: classes,
            field: 'total_tsetse',
            colorRamp: colorRamp,
            legendTemplate: {
                highest: '{low} mouches et plus',
                middle: '{low} à {high} mouches',
                lowest: 'Pas de capture',
            },
            legendTitle: 'Nombre de mouches capturées',
            onEachFeature: tooltip,
        }).addTo(map);
        all_traps_geojson.bringToFront();
    })
    .catch(error => console.error('Erreur lors du chargement du fichier GeoJSON :', error));
