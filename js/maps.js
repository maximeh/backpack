import L, {Map, TileLayer, Marker, GeoJSON} from 'leaflet';

let map;
const places = [];  // {year, layer}, in first-visit order
let selectedYear = null;

function show(feature, layer) {
  return feature.properties.show_on_map;
}

function addTooltip(feature, layer) {
  if (feature.properties && feature.properties.name) {
    const visited = feature.properties.visited;
    const when = visited ? '<br>' + new Date(visited).toLocaleDateString('en', {month: 'short', year: 'numeric', timeZone: 'UTC'}) : '';
    layer.bindTooltip('<b>' + feature.properties.name + '</b>' + when);
  }
}

function markerBounce(event) {
  event.target.bounce({height: 50});
}

function addClickBounce(feature, latlng) {
  const marker = new Marker(latlng, {bounceOnAdd: true});
  // Only the first drop bounces; the year filter re-adds markers quietly.
  marker.once('add', () => { marker.options.bounceOnAdd = false; });
  marker.on('click', markerBounce);
  return marker;
}

function addFeature(feature) {
  const layer = new GeoJSON(feature, {
    onEachFeature: addTooltip,
    pointToLayer: addClickBounce,
  }).addTo(map);
  const year = (feature.properties.visited || '').slice(0, 4) || null;
  places.push({year, layer});
}

function selectYear(year, counts) {
  selectedYear = year === selectedYear ? null : year;
  for (const place of places) {
    const visible = selectedYear === null || place.year === selectedYear;
    if (visible && !map.hasLayer(place.layer)) place.layer.addTo(map);
    if (!visible) place.layer.remove();
  }
  for (const column of document.querySelectorAll('#years button')) {
    column.setAttribute('aria-pressed', column.dataset.year === selectedYear);
  }
  showSummary(counts);
}

function showSummary(counts, hoveredYear) {
  const year = hoveredYear || selectedYear;
  const years = Object.keys(counts).sort();
  document.getElementById('summary').textContent = year
    ? `${year}: ${counts[year] || 0} new places`
    : `${places.length} places, ${years[0]}–${years[years.length - 1]}`;
}

// One column per year of first visits; a click shows only that year.
function addYearChart() {
  const counts = {};
  for (const place of places) if (place.year) counts[place.year] = (counts[place.year] || 0) + 1;
  const years = Object.keys(counts).sort();
  if (!years.length) return;
  const most = Math.max(...Object.values(counts));
  const chart = document.getElementById('years');
  for (let y = Number(years[0]); y <= Number(years[years.length - 1]); y++) {
    const year = String(y);
    const count = counts[year] || 0;
    const column = document.createElement('button');
    column.dataset.year = year;
    column.setAttribute('aria-pressed', 'false');
    column.setAttribute('aria-label', `${year}: ${count} new places`);
    column.innerHTML = `<span class="bar" style="height:${100 * count / most}%"></span><span class="label">${year.slice(2)}</span>`;
    column.addEventListener('click', () => selectYear(year, counts));
    column.addEventListener('mouseenter', () => showSummary(counts, year));
    column.addEventListener('mouseleave', () => showSummary(counts));
    chart.appendChild(column);
  }
  document.getElementById('timeline').hidden = false;
  showSummary(counts);
}

function addData() {
  fetch('places.geojson')
    .then(response => response.json())
    .then(data => {
      // Drop the markers in the order of the first visit; undated places go last.
      const features = data.features.filter(show);
      features.sort((a, b) => (a.properties.visited || '9999').localeCompare(b.properties.visited || '9999'));
      let i = 0;
      const addFeat = setInterval(function() {
        if (i < features.length) addFeature(features[i++]);
        if (i >= features.length) {
          clearInterval(addFeat);
          addYearChart();
        }
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
