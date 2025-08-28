import L, {Map, TileLayer, Marker, GeoJSON} from 'leaflet';

let map;

function show(feature, layer) {
  return feature.properties.show_on_map;
}

function addTooltip(feature, layer) {
  if (feature.properties && feature.properties.name) {
    layer.bindTooltip('<b>'+feature.properties.name+'</b>');
  }
}

function markerBounce(event) {
  event.target.bounce({height: 50});
}

function addClickBounce(feature, latlng) {
  const marker = new Marker(latlng, {bounceOnAdd: true}).addTo(map);
  marker.on('click', markerBounce);
  return marker;
}

function addFeature(feature) {
  new GeoJSON(feature, {
    filter: show,
    onEachFeature: addTooltip,
    pointToLayer: addClickBounce,
  }).addTo(map);
}

function addData() {
  fetch('places.geojson')
    .then(response => response.json())
    .then(data => {
      let i = 0;
      const addFeat = setInterval(function() {
        const feat = data.features[i++];
        addFeature(feat);
        if (i >= data.features.length) clearInterval(addFeat);
      }, 30);
    })
    .catch(error => console.error('Error loading places.geojson:', error));
}

window.onload = function() {
  map = new Map('map').setView([23.26, 0], 3);
  new TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    subdomains: ['a', 'b', 'c'],
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);
  map.whenReady(addData);
};
