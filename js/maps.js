import {Map, TileLayer, Marker, GeoJSON} from 'leaflet';

let map;
const UNKNOWN_VISIT = 'unknown';  // places_log.UNKNOWN_VISIT

// Sort key for the first visit: dated places first, then unknown and undated ones.
function visitKey(feature) {
  const visited = feature.properties.visited;
  return visited && visited !== UNKNOWN_VISIT ? visited : '9999';
}

function firstVisitLabel(visited) {
  if (!visited) return '';
  if (visited === UNKNOWN_VISIT) return '<br>Date unknown';
  return '<br>' + new Date(visited).toLocaleDateString('en', {month: 'short', year: 'numeric', timeZone: 'UTC'});
}

function show(feature) {
  return feature.properties.show_on_map;
}

function addTooltip(feature, layer) {
  if (feature.properties && feature.properties.name) {
    layer.bindTooltip('<b>' + feature.properties.name + '</b>' + firstVisitLabel(feature.properties.visited));
  }
}

function markerBounce(event) {
  event.target.bounce({height: 50});
}

function addClickBounce(feature, latlng) {
  const marker = new Marker(latlng, {bounceOnAdd: true});
  marker.on('click', markerBounce);
  return marker;
}

function addFeature(feature) {
  new GeoJSON(feature, {
    onEachFeature: addTooltip,
    pointToLayer: addClickBounce,
  }).addTo(map);
}

function addData() {
  fetch('places.geojson')
    .then(response => response.json())
    .then(data => {
      // Drop the markers in the order of the first visit.
      const features = data.features.filter(show);
      features.sort((a, b) => visitKey(a).localeCompare(visitKey(b)));
      let i = 0;
      const addFeat = setInterval(function() {
        if (i < features.length) addFeature(features[i++]);
        if (i >= features.length) clearInterval(addFeat);
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
