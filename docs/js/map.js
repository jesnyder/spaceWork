var cities = L.layerGroup();
var fdaLocs = L.layerGroup();
var cdcStats = L.layerGroup();
var pubs = L.layerGroup();


var mbAttr = 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>';
var mbUrl = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw';
var streets = L.tileLayer(mbUrl, {id: 'mapbox/streets-v11', tileSize: 512, zoomOffset: -1, attribution: mbAttr});

var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		//attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	});


//var map = L.map('map').setView([37.8, -96], 4);
var map = L.map('map', {
		center: [0, 0],
		zoom:2,
		minZoom: 2,
		maxZoom: 18,
		zoomSnap: 0.25,
		layers: [osm]
	});

	var baseLayers = {
		'OpenStreetMap': osm,
		'Streets': streets
	};

	var overlays = {
		'Pubs': pubs,
	};

	var layerControl = L.control.layers(baseLayers, overlays).addTo(map);

	var satellite = L.tileLayer(mbUrl, {id: 'mapbox/satellite-v9', tileSize: 512, zoomOffset: -1, attribution: mbAttr});
	layerControl.addBaseLayer(satellite, 'Satellite');


	var tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'
	}).addTo(map);

	// control that shows state info on hover
	var info = L.control();

	info.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'info');
		this.update();
		return this._div;
	};




	function style(feature) {
		return {
			weight: 0,
			opacity: 1,
			color: 'white',
			dashArray: '3',
			fillOpacity: 0.7,
			fillColor: feature.properties['Arthritis-Crude Prevalence']['color']
		};
	}


	function highlightFeature(e) {
		var layer = e.target;

		layer.setStyle({
			weight: 5,
			color: '#666',
			dashArray: '',
			fillOpacity: 0.7
		});

		if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
			layer.bringToFront();
		}

		info.update(layer.feature.properties);
	}


	function resetHighlight(e) {
		geojson_counties.resetStyle(e.target);
		info.update();
	}


	function zoomToFeature(e) {
		map.fitBounds(e.target.getBounds());
	}


	function onEachFeature(feature, layer) {
		layer.on({
			mouseover: highlightFeature,
			mouseout: resetHighlight,
			click: zoomToFeature
		});
	}


	function onEachFacility(feature, layer) {
			var website = feature.properties.website;

			var popupContent = '<b>' +
					feature.properties.name + '</b><br>' + '<a href="' + feature.properties.website + '" target="_blank" rel="noopener">' + feature.properties.website + '</a>'  + '<br>' + feature.properties.city + ', ' + feature.properties.state + '</p>';
			if (feature.properties && feature.properties.popupContent) {
				popupContent += feature.properties.popupContent;
			}
			layer.bindPopup(popupContent);
		}




function onEachPub(feature, layer) {

						var aff = feature.properties.aff;
				    var url = feature.properties.url;
				    var title = feature.properties.title;

						map.createPane('popUpPane');
				    map.getPane('popUpPane').style.zIndex = 999;

				    var popupContent = '<p><b>'
				         + feature.properties.title
				         + '</b><br>'
				         + feature.properties.aff
				         + '<br> Cited by: '
								 + feature.properties.cited
				         + '<br>'
				         + '<a href="' + feature.properties.url + '" target="_blank" rel="noopener">'
				         + feature.properties.url + '</a>'
				         + '</p>';

				    if (feature.properties && feature.properties.popupContent) {
				            popupContent += feature.properties.popupContent;
				          }
				     layer.bindPopup(popupContent);
				  }


function pubStyle (feature) {
						    return feature.properties && feature.properties.style;
								}

function pubToLayer(feature, latlng) {

				var paneName = feature.properties.paneName;
				var zindex = feature.properties.zindex;
				//console.log('paneName = ')
				//console.log(paneName)
				//console.log('zindex = ')
				//console.log(zindex)

					map.createPane(paneName);
			    map.getPane(paneName).style.zIndex = zindex + 200;
			    return L.circleMarker(latlng, {
			      radius: feature.properties.radius,
			      opacity:0.8,
			      fillOpacity: 0.8,
			      fillColor: feature.properties.color,
			      color: 'black',
			      weight: 1,
			      pane: paneName,
			    });
			  }



	/*
	global statesData
	var geojson_counties = L.geoJson(cdc_stats, {
		style: style,
		onEachFeature: onEachFeature
	}).addTo(map).addTo(cdcStats);


	/* global statesData
	var geojson_facility = L.geoJson(facilityData, {
		style: style,
		onEachFeature: onEachFacility
	}).addTo(map).addTo(fdaLocs);
	*/

	/* global statesData */
	var pubs = L.geoJson(microgravity_space_biology, {
		style: pubStyle,
		onEachFeature: onEachPub,
		pointToLayer: pubToLayer,
	}).addTo(map).addTo(pubs);

console.log('microgravity_space_biology = ')
console.log(microgravity_space_biology)


	/* cite source of information
	map.attributionControl.addAttribution('| <a href="https://www.cdc.gov/arthritis/data_statistics/state-data-current.htm" target="_blank" rel="noopener">CDC Arthritis Statistics</a> | <a href="https://datadashboard.fda.gov/ora/cd/inspections.htm" target="_blank" rel="noopener"> FDA Inspection Record </a>' );
*/
