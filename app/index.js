import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'
import GeoJSON from 'ol/format/GeoJSON';
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import {Circle as CircleStyle, Fill, Stroke, Style} from 'ol/style';

import $, { data } from 'jquery'

import {transform} from 'ol/proj.js'

const map =	new Map({
	target: 'map',
	layers: [
		new TileLayer({
			source: new OSM()
		})
	],
	view: new View({
		center: transform([36.382177, 55.207178], 'EPSG:4326', 'EPSG:3857'),
		zoom: 12
	})
})

var profilePnt = new VectorSource({
	format: new GeoJSON(),
	loader: function(extent, resolution, projection) {
		$.ajax({
			url: "http://localhost/node",
			type: 'POST',
			data: JSON.stringify({
				table:'dat_Profiles',
				column: 'Geometry',
				query: 'ST_AsGeoJSON(ST_SetSRID(ST_MakePoint("dat_Profiles"."Lon", "dat_Profiles"."Lat"), 4326))'
			}),
			dataType: 'json',
			success : function(data) {
				console.log(data)
				var geodata = {}
				geodata["type"] = 'FeatureCollection'
				var features = []
				for (var i = 0; i < data.length ; i++) {
					var featobj = {}
					if (data[i].st_asgeojson) {

						featobj["type"] = "Feature"
						featobj["properties"] = {}

						featobj["geometry"] = JSON.parse(data[i].st_asgeojson)
						features.push(featobj)
					}
				}
				geodata["features"] = features
				console.log(geodata)
				var Vfeatures = profilePnt.getFormat().readFeatures(geodata, {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'})
				profilePnt.addFeatures(Vfeatures)
				console.log(profilePnt)
			}
		})
	}
})

const image = new CircleStyle({
	radius: 3,
	fill: new Fill({color: 'red'}),
	stroke: new Stroke({color: 'red', width: 1}),
});

var pnt_layer = new VectorLayer({
	source: profilePnt,
	style: new Style(
		{image: image}),
	declutter: true
});

map.addLayer(pnt_layer);

//window.onload = init

//function init() {

//	const format = new GeoJSON()

//	const feature = format.readFeature(geodata);

//	var profilePnt = new VectorLayer({
//		source: new VectorSource({feature})
//	});

//	 console.log(profilePnt)

//	new Map({
//		target: 'map',
//		layers: [
//			//profilePnt,
//			new TileLayer({
//				source: new OSM()
//			})
//		],
//		view: new View({
//			center: transform([36.382177, 55.207178], 'EPSG:4326', 'EPSG:3857'),
//			zoom: 12
//		})
//	})

//}


