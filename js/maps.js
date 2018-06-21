var map;

function show(feature, layer) {
    return feature.properties.show_on_map;
}

function addTooltip(feature, layer) {
    if (feature.properties && feature.properties.name) {
        layer.bindTooltip('<b>'+feature.properties.name+'</b>');
    }
}

function show(feature, layer){
    return feature.properties.show_on_map;
}

function addFeature(feature){
   L.geoJson(feature, {
	filter: show,
        onEachFeature: addTooltip,
        filter: show,
    }).addTo(map);
}

function addData() {
    $.getJSON('places.geojson', function(data) {
        let i = 0;
        var add_feat = setInterval(function() {
            let feat = data.features[i++];
            addFeature(feat);
            if (i >= data.features.length) clearInterval(add_feat);
        }, 30);
    });
}

window.onload = function() {
    map = L.map('map').setView([23.26, 0], 3);
    L.control.fullscreen({
        position: 'topleft',
        title: 'Go Fullscreen!',
    }).addTo(map);
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
         maxZoom: 19,
         subdomains: ['a', 'b', 'c'],
	 attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);
    map.whenReady(addData);
};
