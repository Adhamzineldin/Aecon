var lineLayer;
var lineLayer2;
var arrowLayer;
var markerLayer;
var selectedMarkerLayer;

var currentFunction;
var marker;
var cancelActionFunction;
var currentMapFunction;

var geoJSON = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": { color: '#99cc99' },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    13.397215604782104,
                    52.522044249266486,
                    50
                ],
                [
                    13.39659333229065,
                    52.52177659937554,
                    55
                ],
                [
                    13.3958101272583,
                    52.52186146415167,
                    40
                ],
                [
                    13.394308090209961,
                    52.522037721239755,
                    30
                ],
                [
                    13.394136428833008,
                    52.52194632876386,
                    55
                ],
                [
                    13.394672870635986,
                    52.52145019486258,
                    60
                ],
                [
                    13.395155668258667,
                    52.521149900568716,
                    55
                ],
                [
                    13.394447565078735,
                    52.52080390677208,
                    70
                ],
                [
                    13.393653631210327,
                    52.52150241974763,
                    90
                ],
                [
                    13.392591476440428,
                    52.521881048307485,
                    60
                ],
                [
                    13.391475677490234,
                    52.522037721239755,
                    55
                ],
                [
                    13.3908212184906,
                    52.521652565946304,
                    40
                ],
                [
                    13.391668796539307,
                    52.521652565946304,
                    30
                ],
                [
                    13.391979932785034,
                    52.52016413747981,
                    35
                ],
                [
                    13.393621444702147,
                    52.520431797194824,
                    40
                ],
                [
                    13.394147157669067,
                    52.52066681413661,
                    30
                ],
                [
                    13.39508056640625,
                    52.51995523120331,
                    35
                ],
                [
                    13.395617008209229,
                    52.52010538268996,
                    40
                ]
            ]
        }
    }]
}


var feature3d = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": { color: '#99cc99' },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-2.25108, 53.475669, 20],
                [-2.250673, 53.47633, 30],
                [-2.249931, 53.477569, 100],
                [-2.249492, 53.478341, 90],
                [-2.249191, 53.479044, 17],
                [-2.248634, 53.479912, 52],
                [-2.248634, 53.479912, 60]
            ]
        }
    }]
}


var feature3d2 = {
    "type": "FeatureCollection",
    "features": [{
        "geometry": {
            "coordinates": [
                [-2.25108, 53.475669, 50],
                [-2.250673, 53.47633, 90],
                [-2.249931, 53.477569, 70],
                [-2.249492, 53.478341, 200],
                [-2.249191, 53.479044, 210],
                [-2.248634, 53.479912, 85],
                [-2.248634, 53.479912, 10]
            ],
            "type": "LineString"
        },
        "properties": { color: '#99cc99', "direction": "North", "direction_id": 1, "order": 0 },
        "type": "Feature"
    }]
}


function initMap(location, canvasId, mapCode) {
    console.log("initialising map", mapCode);
    map = L.map(canvasId, { zoomControl: false, maxZoom: 24, maxNativeZoom: 20, editable: true }).setView(location, 8);
    L.control.zoom({position: 'bottomright'}).addTo(map);

    map.getRenderer(map).options.padding = 100;
    tileLayer = L.tileLayer('https://api.mapbox.com/styles/v1/neeeel/' + mapCode + '/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibmVlZWVsIiwiYSI6ImNqaGFoN3QwZzB0eHYzNnRpdzRjbGRkMWMifQ.H5vW34S90Me6fXgm_abIJg', {
        tileSize: 512,
        zoomOffset: -1,
        maxZoom: 24,
        maxNativeZoom: 20,
        attribution: '© <a href="https://www.mapbox.com/map-feedback/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    //L.control.layers(baseMaps).addTo(map);
    //map.setZoom(19);
    map.options.maxZoom = 24;
    lineLayer = new L.featureGroup();
    markerLayer = new L.featureGroup();
    selectedMarkerLayer = new L.featureGroup();
    lineLayer.addTo(map);
    markerLayer.addTo(map);
    selectedMarkerLayer.addTo(map);
    return;
}

function initMap2(location, canvasId, mapCode) {
    console.log("initialising map", mapCode);
    map2 = L.map(canvasId, { zoomControl: false, maxZoom: 24, maxNativeZoom: 20, editable: true }).setView(location, 8);
    map2.getRenderer(map2).options.padding = 100;
    tileLayer = L.tileLayer('https://api.mapbox.com/styles/v1/neeeel/' + mapCode + '/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibmVlZWVsIiwiYSI6ImNqaGFoN3QwZzB0eHYzNnRpdzRjbGRkMWMifQ.H5vW34S90Me6fXgm_abIJg', {
        tileSize: 512,
        zoomOffset: -1,
        maxZoom: 24,
        maxNativeZoom: 20,
        attribution: '© <a href="https://www.mapbox.com/map-feedback/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map2);




    //L.control.layers(baseMaps).addTo(map);
    //map.setZoom(19);
    map2.options.maxZoom = 24;
    lineLayer2 = new L.featureGroup();
    markerLayer = new L.featureGroup();
    selectedMarkerLayer = new L.featureGroup();
    lineLayer2.addTo(map2);
    markerLayer.addTo(map2);
    selectedMarkerLayer.addTo(map2);
    return;
    if (canvasId == "map-view-map") {
        lineLayer = new L.LayerGroup();
        map.addLayer(lineLayer);

        var someFeatures = [{
                "type": "Feature",
                "properties": {
                    "name": "Busch Field",
                    "show_on_map": false,
                    "countline": false
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-2.250597, 53.476629],
                        [-2.250487, 53.476811]
                    ]
                }
            }, {
                "type": "Feature",
                "properties": {
                    "name": "Busch Field",
                    "show_on_map": false,
                    "countline": false
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-2.250514, 53.476600],
                        [-2.250621, 53.476404]
                    ]
                }
            }, {
                "type": "Feature",
                "properties": {
                    "name": "Busch Field",
                    "show_on_map": false,
                    "countline": false
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-2.252555, 53.476105],
                        [-2.251954, 53.475955]
                    ]
                }
            }, {
                "type": "Feature",
                "properties": {
                    "name": "Busch Field",
                    "show_on_map": false,
                    "countline": false
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-2.252577, 53.476019],
                        [-2.253086, 53.476147]
                    ]
                }
            },
            {
                'properties': { 'order': '0', 'direction': '1' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.251406, 53.475217],
                        [-2.251321, 53.475365]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '1', 'direction': '3' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.251365, 53.475208],
                        [-2.251431, 53.475094]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '2', 'direction': '2' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.249992, 53.477617],
                        [-2.249796, 53.477944]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '1', 'direction': '1' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.249929, 53.477603],
                        [-2.250108, 53.477289]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '2', 'direction': '3' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.250692, 53.478519],
                        [-2.250227, 53.478442]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '1', 'direction': '1' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.250704, 53.478476],
                        [-2.251211, 53.478561]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '2', 'direction': '2' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.248992, 53.478239],
                        [-2.248568, 53.478187]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '1', 'direction': '2' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.248998, 53.478211],
                        [-2.249293, 53.47825]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '2', 'direction': '3' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.24915, 53.478982],
                        [-2.249037, 53.479178]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '1', 'direction': '2' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.249198, 53.478988],
                        [-2.249282, 53.478845]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '2', 'direction': '1' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.248184, 53.480571],
                        [-2.248049, 53.480796]
                    ]
                },
                'type': 'Feature'
            },
            {
                'properties': { 'order': '1', 'direction': '1' },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-2.248114, 53.480549],
                        [-2.248305, 53.48025]
                    ]
                },
                'type': 'Feature'
            }
        ];
        lines = {
            "type": "FeatureCollection",
            "features": someFeatures
        }

        lineLayer = L.geoJson(lines, {
                style: styleLine,
                onEachFeature: function(feature, layer) {
                    if (!feature.properties.countline) {

                        var arrowHead = L.polylineDecorator(layer, {
                                patterns: [{
                                    offset: '100%',
                                    repeat: 0,
                                    symbol: L.Symbol.arrowHead({ pixelSize: 15, polygon: false, pathOptions: { stroke: true, color: "green", opacity: 0.65, weight: 8 } })
                                }]
                            }) //.addTo(map);
                    }

                }
            }) //.addTo(map);
        console.log(lineLayer);



        var icont = L.divIcon({
            className: 'test',
            html: "<div>oh hai</div>",
            //iconSize: [300, 42],
            //iconAnchor: [150, 42]
        });


        lineLayer.eachLayer(function(layer) {
            //var marker = new L.Marker.SVGMarker(layer.getLatLngs()[1], { iconOptions: {circleText:Math.floor(Math.random() * 100) * (Math.floor(Math.random() * 3) + 1),circleRatio:0.9,circleFillOpacity:0.7,fontSize:12,iconSize:[40,60]}}).addTo(map);
            //var wrapper = addBarChartToWidget();
            //marker.bindPopup(wrapper);
        })
    }


    //var feature3d = {"type":"FeatureCollection","features":[{"geometry": {"coordinates": [[-2.25108, 53.475669,20], [-2.250673, 53.47633,30], [-2.249931, 53.477569,100], [-2.249492, 53.478341,90], [-2.249191, 53.479044,17], [-2.248634, 53.479912,52], [-2.248634, 53.479912,60]], "type": "LineString"}, "properties": {"direction": "North", "direction_id": 1, "order": 0}, "type": "Feature"}]}

    var line3d = new L.Line3(feature3d)
    line3d.addTo(map);
    console.log("added 3d line!!!")
    console.log("line3d is", typeof line3d)

    setTimeout(function() {
        console.log("line3d is", typeof line3d);
        map.removeLayer(line3d);
        line3d = new L.Line3(feature3d2).addTo(map);
    }, 1000)



    return;
    //https://api.mapbox.com/styles/v1/neeeel/cjw7wu5vb04iw1cn18x9xenl4.html?fresh=true&title=true&access_token=pk.eyJ1IjoibmVlZWVsIiwiYSI6ImNqaGFoN3QwZzB0eHYzNnRpdzRjbGRkMWMifQ.H5vW34S90Me6fXgm_abIJg#13.6/37.784020/-122.403944/0
    for (var key in features) {
        //console.log("adding",key);
        layer = new L.geoJson(features[key], {
            pointToLayer: function(feature, latlng) {
                //console.log("lat lng is",latlng)
                var popup = L.popup({ maxWidth: 400, minWidth: 400 }).setLatLng(latlng);
                widget = createMetaDataPopup(feature);
                displaySiteDetails(widget, feature);
                popup.setContent(widget);
                return addPointMarker(feature, latlng).bindPopup(popup);

            },
            style: function(feature) {
                return stylePoint(feature);
            }

        })
        layers[key] = layer;
        map.addLayer(layer);

    }
    map.addLayer(tileLayer);
    showAllLayers();





    return;


    function createMetaDataPopup2(feature) {

        //console.log("showing",feature.geometry);

        var div = document.createElement("div");
        //div.style.width = "350px";
        //div.style.height = "120px";
        div.classList.add("container-fluid");
        //div.style.padding = "0";
        header = document.createElement("div");
        header.style.width = "100%";
        //header.style.height = "20px";
        header.style.fontWeight = "760";
        header.style.fontSize = "12px";
        header.classList.add("conduit-header-box");

        var title = document.createElement("div");
        title.classList.add("conduit-header-box-title");
        title.innerText = feature.properties.area + " - " + feature.properties.name;
        header.appendChild(title);
        var icons = document.createElement("div");
        icons.classList.add("d-flex");
        icons.style.marginLeft = "auto";
        header.appendChild(icons);
        var fn = document.createElement("div");
        fn.classList.add("fn");
        fn.onclick = function() {
            console.log("viewing", feature.properties.id);
            viewSite(feature.properties.id);
        };
        icons.appendChild(fn);
        var i = document.createElement("i");
        i.classList.add("icon-search-1");
        fn.appendChild(i)


        //var fn = document.createElement("div");
        //fn.classList.add("fn");
        //fn.onclick = function(){console.log("viewing", feature.properties.id)};
        //icons.appendChild(fn);
        //var i = document.createElement("i");
        //i.classList.add("icon-locked-3");
        //fn.appendChild(i)


        div.appendChild(header);



        var contentDiv = document.createElement("div");
        contentDiv.classList.add("row");
        contentDiv.style.width = "100%";
        contentDiv.style.height = "calc(100% - 20px)";
        div.appendChild(contentDiv);
        var imgDiv = document.createElement("div");
        imgDiv.classList.add("site-img-wrapper");
        imgDiv.classList.add("col-6");
        //imgDiv.classList.add("d-flex");
        //imgDiv.classList.add("justify-content-center");

        contentDiv.appendChild(imgDiv);
        var img = document.createElement("img");
        img.classList.add("site-img");
        img.classList.add("my-auto");
        //console.log("url is",feature.properties["imgURL"],feature.properties["imgURL"]=="",feature.properties["imgURL"]==null,feature.properties["imgURL"]==undefined)
        if (feature.properties["imgURL"] != null) {
            img.src = feature.properties["imgURL"];
        } else {
            img.src = "/static/crt/blank site image.jpg";
        }

        imgDiv.appendChild(img);
        img.onclick = function(e) {
            displayLargeImage(e, event.target);
        };
        var detailsDiv = document.createElement("div");
        detailsDiv.style.width = "";
        detailsDiv.classList.add("site-details-wrapper");
        detailsDiv.classList.add("col-6")
        contentDiv.appendChild(detailsDiv);

        d = document.createElement("div");
        d.innerText = "Coordinates";
        d.style.fontWeight = "760";
        detailsDiv.appendChild(d);
        d = document.createElement("div");
        d.innerText = feature.geometry.coordinates[1][1].toString().substring(0, 8) + "," + feature.geometry.coordinates[1][0].toString().substring(0, 8);
        detailsDiv.appendChild(d);

        d = document.createElement("div");
        d.innerText = "Sensor Status";
        d.style.fontWeight = "760";
        detailsDiv.appendChild(d);
        d = document.createElement("div");
        d.innerText = feature.properties.status;
        d.classList.add("status-" + feature.properties.status.toLowerCase());
        detailsDiv.appendChild(d);

        d = document.createElement("div");
        d.innerText = "Last Data Retrieved";
        d.style.fontWeight = "760";
        detailsDiv.appendChild(d);
        d = document.createElement("div");
        d.innerText = moment(feature.properties.lastDataReceived).format("MMM Do YYYY HH:mm");
        detailsDiv.appendChild(d);


        return div;
    }






    var vectorTileLayer = L.canvasTiles()
        .params({ debug: false, padding: 0.5 })
        .drawing(drawingOnCanvas);
    vectorTileLayer.setZIndex(5);
    vectorTileLayer.addTo(map);
    vectorTileLayer.on("loading", function() { console.log("canvas started loading"); });
    vectorTileLayer.on("load", function() { console.log("canvas finished loading"); });



}
// function initMap2(location, canvasId, mapCode) {
//     console.log("initialising map", mapCode);
//     map2 = L.map(canvasId, { zoomControl: false, maxZoom: 24, maxNativeZoom: 20, editable: true }).setView(location, 8);
//     map2.getRenderer(map2).options.padding = 100;
//     tileLayer = L.tileLayer('https://api.mapbox.com/styles/v1/neeeel/' + mapCode + '/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibmVlZWVsIiwiYSI6ImNqaGFoN3QwZzB0eHYzNnRpdzRjbGRkMWMifQ.H5vW34S90Me6fXgm_abIJg', {
//         tileSize: 512,
//         zoomOffset: -1,
//         maxZoom: 24,
//         maxNativeZoom: 20,
//         attribution: '© <a href="https://www.mapbox.com/map-feedback/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
//     }).addTo(map2);

//     map2.options.maxZoom = 24;
//     lineLayer2 = new L.featureGroup();
//     markerLayer = new L.featureGroup();
//     selectedMarkerLayer = new L.featureGroup();
//     lineLayer2.addTo(map2);
//     markerLayer.addTo(map2);
//     selectedMarkerLayer.addTo(map2);
//     return;

// }


var myStyle = {
    "color": "#ff7800",
    "weight": 15,
    "opacity": 0.65
};


function styleLine(feature) {
    console.log("observation type is", feature.properties.countline);
    return {
        "color": "green",
        "weight": 8,
        "opacity": 0.65
    };


}


function toRadians(angle) {
    return angle * (Math.PI / 180);
}


function createMetaDataPopup2(feature) {

    //console.log("showing",feature.geometry);

    var div = document.createElement("div");
    //div.style.width = "350px";
    //div.style.height = "120px";
    div.classList.add("container-fluid");
    //div.style.padding = "0";
    header = document.createElement("div");
    header.style.width = "100%";
    //header.style.height = "20px";
    header.style.fontWeight = "760";
    header.style.fontSize = "12px";
    header.classList.add("conduit-header-box");

    var title = document.createElement("div");
    title.classList.add("conduit-header-box-title");
    title.innerText = feature.properties.area + " - " + feature.properties.name;
    header.appendChild(title);
    var icons = document.createElement("div");
    icons.classList.add("d-flex");
    icons.style.marginLeft = "auto";
    header.appendChild(icons);
    var fn = document.createElement("div");
    fn.classList.add("fn");
    fn.onclick = function() {
        console.log("viewing", feature.properties.id);
        viewSite(feature.properties.id);
    };
    icons.appendChild(fn);
    var i = document.createElement("i");
    i.classList.add("icon-search-1");
    fn.appendChild(i)


    //var fn = document.createElement("div");
    //fn.classList.add("fn");
    //fn.onclick = function(){console.log("viewing", feature.properties.id)};
    //icons.appendChild(fn);
    //var i = document.createElement("i");
    //i.classList.add("icon-locked-3");
    //fn.appendChild(i)


    div.appendChild(header);



    var contentDiv = document.createElement("div");
    contentDiv.classList.add("row");
    contentDiv.style.width = "100%";
    contentDiv.style.height = "calc(100% - 20px)";
    div.appendChild(contentDiv);
    var imgDiv = document.createElement("div");
    imgDiv.classList.add("site-img-wrapper");
    imgDiv.classList.add("col-6");
    //imgDiv.classList.add("d-flex");
    //imgDiv.classList.add("justify-content-center");

    contentDiv.appendChild(imgDiv);
    var img = document.createElement("img");
    img.classList.add("site-img");
    img.classList.add("my-auto");
    //console.log("url is",feature.properties["imgURL"],feature.properties["imgURL"]=="",feature.properties["imgURL"]==null,feature.properties["imgURL"]==undefined)
    if (feature.properties["imgURL"] != null) {
        img.src = feature.properties["imgURL"];
    } else {
        img.src = "/static/crt/blank site image.jpg";
    }

    imgDiv.appendChild(img);
    img.onclick = function(e) {
        displayLargeImage(e, event.target);
    };
    var detailsDiv = document.createElement("div");
    detailsDiv.style.width = "";
    detailsDiv.classList.add("site-details-wrapper");
    detailsDiv.classList.add("col-6")
    contentDiv.appendChild(detailsDiv);

    d = document.createElement("div");
    d.innerText = "Coordinates";
    d.style.fontWeight = "760";
    detailsDiv.appendChild(d);
    d = document.createElement("div");
    d.innerText = feature.geometry.coordinates[1][1].toString().substring(0, 8) + "," + feature.geometry.coordinates[1][0].toString().substring(0, 8);
    detailsDiv.appendChild(d);

    d = document.createElement("div");
    d.innerText = "Sensor Status";
    d.style.fontWeight = "760";
    detailsDiv.appendChild(d);
    d = document.createElement("div");
    d.innerText = feature.properties.status;
    d.classList.add("status-" + feature.properties.status.toLowerCase());
    detailsDiv.appendChild(d);

    d = document.createElement("div");
    d.innerText = "Last Data Retrieved";
    d.style.fontWeight = "760";
    detailsDiv.appendChild(d);
    d = document.createElement("div");
    d.innerText = moment(feature.properties.lastDataReceived).format("MMM Do YYYY HH:mm");
    detailsDiv.appendChild(d);


    return div;
}


var _dblClickTimer = null;
var map;
var map2;
var lineLayer;
var marker;
var currentFunction;
var inArrow;
var outArrow;
var inMarker;
var outMarker;
var tempArrow;
var arrowCol;
var arrowHeadSize = 8;
var inBearing;
var outBearing;
var columnLines = [
    [],
    [],
    [],
    []
];
var oldLine;
colors = ["blue", "red", "orange", "green"];

//console.log("L is -", L)
var icon = L.icon({
    iconUrl: "/static/aecon/LocPin_2.svg",
    iconSize: [40, 40],
    iconAnchor: [20, 40],
});


var icon2 = L.icon({
    iconUrl: "/static/aecon/LocPin_2.svg",
    iconSize: [40, 40],
    iconAnchor: [20, 20],
});


var myNode = document.querySelector('#count-point');
if (myNode) {
    myNode.addEventListener("click", testFunc = function(e) {
        toggle_function("count-point");
    });

}





function clearMap() {
    if (marker) {
        map.removeLayer(marker);
        lineLayer.eachLayer(function(layer) {
            lineLayer.removeLayer(layer);
        });
    }
    marker = null;
    inArrow = null;
    outArrow = null;
    columnLines = [
        [],
        [],
        [],
        [],
    ];
}


/**********************************************************************************************************


Functions for displaying locations on dashboard/client map


************************************************************************************************************/

var geojsonMarkerOptions = {
    radius: 8,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.7
};


var locationStyleOptions = {
    color: "red",
    interactive: true,
    editable: true,
    weight: 5,
    order: null,
    direction: null
}

function findLayer(id) {
    //
    // find layer by properties.id
    //
    //
    //console.log("Looking for",id);
    var result;
    lineLayer.eachLayer(function(layer) {
        //console.log(layer.feature.properties.id,layer.feature.properties.id.toString() == id);
        if (layer.feature && layer.feature.properties.id.toString() == id) {
            //console.log("YES!!!");
            result = layer;
        }
    });
    return result;
}


function addCountMarker(feature, markerOptions) {
    //console.log("adding count marker to",feature);
    var coords = feature.geometry.coordinates;
    var latlng = new L.LatLng(coords[1], coords[0]);
    var icon = L.divIcon({
        html: "<div class='donut-text' id='" + feature.properties.id + "_total'>-</div>",
        iconSize: [60, 60],
        className: 'countIcon'
    });

    markerOptions.icon = icon;
    marker = L.marker(latlng, markerOptions);
    lineLayer.addLayer(marker);
    marker.feature = feature;
    return marker;
}

function addPlainMarker(feature, className) {
    var coords = feature.geometry.coordinates;
    var latlng = new L.LatLng(coords[1], coords[0]);
    if (className === "perm") {
        var icon = L.divIcon({
            html: '<i class="map-icon-red pe-3"></i>',
            iconSize: null,
            className: className
        });
    }
    else if (className === "temp"){
        var icon = L.divIcon({
            html: '<i class="map-icon-blue pe-3"></i>',
            iconSize: null,
            className: className
        });
    }
    else if (className === "hist") {
        var icon = L.divIcon({
            html: '<i class="map-icon-historic pe-3"></i>',
            iconSize: null,
            className: className
        });
    }
    else if (className === "radar") {
        var icon = L.divIcon({
            html: '<i class="map-icon-lblue pe-3"></i>',
            iconSize: null,
            className: className
        });
    }
    else if (className === "sensor") {
        var icon = L.divIcon({
            html: '<i class="map-icon-grey pe-3"></i>',
            iconSize: null,
            className: className
        });
    }
    
    //markerOptions.icon = icon;
    //marker = L.circleMarker(latlng, {radius:35,weight:2,color:color});
    marker = L.marker(latlng, { icon: icon });
    lineLayer.addLayer(marker);
    marker.feature = feature;
    return marker;

}

function addPlainMarker2(feature, className) {
    var coords = feature.geometry.coordinates;
    var latlng = new L.LatLng(coords[1], coords[0]);
    var icon = L.divIcon({

        iconSize: null,
        className: className
    });

    //markerOptions.icon = icon;
    //marker = L.circleMarker(latlng, {radius:35,weight:2,color:color});
    marker = L.marker(latlng, { icon: icon });
    lineLayer2.addLayer(marker);
    marker.feature = feature;
    return marker;

}


function addLocationPointMarker(feature, markerOptions) {
    var coords = feature.geometry.coordinates;
    var latlng = new L.LatLng(coords[1], coords[0]);
    if (feature.properties.obsType.iconURL == "") {
        for (var key in geojsonMarkerOptions) {
            //markerOptions[key] = geojsonMarkerOptions[key];
        }
        //var marker = L.circleMarker(latlng, markerOptions);

        var icon = L.divIcon({
            html: '<i class="fa wind"></i>',
            iconSize: [30, 30],
            className: 'locationIcon'
        });

        markerOptions.icon = icon;
        marker = L.marker(latlng, markerOptions);
        marker.on({ click: function(e) {} });
    } else {
        var icon = L.divIcon({
            html: '<i class="fa ' + feature.properties.obsType.iconURL + '"></i>',
            iconSize: [30, 30],
            className: 'locationIcon'
        });
        markerOptions.icon = icon;
        marker = L.marker(latlng, markerOptions);
        marker.on({ click: function(e) {} });
    }
    markerLayer.addLayer(marker);
    marker.feature = feature;
    return marker;
}


function processLocationGeojson(data) {
    //console.log("data is", data);
    new L.geoJson(data, {
        onEachFeature: dealWithLocationFeatureCollections
    });



    //map.removeLayer(lineLayer);
}

function processLocationGeojsonmap(data) {
    //console.log("data is", data);
    new L.geoJson(data, {
        onEachFeature: dealWithLocationFeatureCollection
    });



    //map.removeLayer(lineLayer);
}

function dealWithLocationFeatureCollection(feature, layer) {
    //console.log("dealing with location ", feature)
    //console.log("layer in loc", layer)
    if (feature.geometry.type == "LineString" && (feature.properties.type == "countline" || feature.properties.type == "virtual")) {
        console.log("found countline", feature);
        layer.setStyle({ color: "#2483ec" });
        layer.addTo(map);
        //layer.setStyle(locationStyleOptions);
        lineLayer.addLayer(layer);
        map.fitBounds(lineLayer.getBounds(), { "maxZoom": 19, padding: [500, 500] });
        /*
        var spans = document.getElementById("details-container").getElementsByTagName("span");
        document.getElementById("site-img").src = feature.properties.imgURL;
        spans[0].innerText = feature.properties.name;
        spans[1].innerText = feature.properties.area;
        spans[2].innerText = feature.geometry.coordinates[1].toString().substring(0, 8) + "," + feature.geometry.coordinates[0].toString().substring(0, 8);
        
        if(Boolean(feature.properties.installDate)){
            spans[3].innerText = moment(feature.properties.installDate).format("MMMM  DD, YYYY");
        }
        spans[4].innerText = moment(feature.properties.lastDataReceived).format("DD/MM/YYYY HH:mm");
        */
        // spans[5].innerText = feature.properties.status;
        // spans[5].setAttribute("class", "")
        // spans[5].classList.add("status-" + feature.properties.status.toLowerCase());
    }
    if (feature.geometry.type == "Point") {

        if (!feature.properties.temp) {
            var className = "perm";
        } else {
            var className = "temp";
        }
        var marker = addPlainMarker(feature, className);
        map.panTo(marker.getLatLng());
        /*
        var spans = document.getElementById("details-container").getElementsByTagName("span");
        document.getElementById("site-img").src = feature.properties.imgURL;
        spans[0].innerText = feature.properties.name;
        spans[1].innerText = feature.properties.area;
        spans[2].innerText = feature.geometry.coordinates[1].toString().substring(0, 8) + "," + feature.geometry.coordinates[0].toString().substring(0, 8);
        
        if(Boolean(feature.properties.installDate)){
            spans[3].innerText = moment(feature.properties.installDate).format("MMMM  DD, YYYY");
        }
        spans[4].innerText = moment(feature.properties.lastDataReceived).format("DD/MM/YYYY HH:mm");
        */
        // spans[5].innerText = feature.properties.status;
        // //console.log(1)
        // spans[5].setAttribute("class", "")
        // //console.log(1)
        // spans[5].classList.add("status-" + feature.properties.status.toLowerCase());
    }
}

function dealWithLocationFeatureCollections(feature, layer) {
    //console.log("dealing with location ", feature)
    //console.log("layer in loc", layer)
    if (feature.geometry.type == "LineString" && (feature.properties.type == "countline" || feature.properties.type == "virtual")) {
        console.log("found countline", feature);
        layer.setStyle({ color: "#2483ec" });
        layer.addTo(map);
        //layer.setStyle(locationStyleOptions);
        lineLayer.addLayer(layer);
        map.fitBounds(lineLayer.getBounds(), { "maxZoom": 19, padding: [500, 500] });
        /*
        var spans = document.getElementById("details-container").getElementsByTagName("span");
        document.getElementById("site-img").src = feature.properties.imgURL;
        spans[0].innerText = feature.properties.name;
        spans[1].innerText = feature.properties.area;
        spans[2].innerText = feature.geometry.coordinates[1].toString().substring(0, 8) + "," + feature.geometry.coordinates[0].toString().substring(0, 8);
        
        if(Boolean(feature.properties.installDate)){
            spans[3].innerText = moment(feature.properties.installDate).format("MMMM  DD, YYYY");
        }
        spans[4].innerText = moment(feature.properties.lastDataReceived).format("DD/MM/YYYY HH:mm");
        */
        // spans[5].innerText = feature.properties.status;
        // spans[5].setAttribute("class", "")
        // spans[5].classList.add("status-" + feature.properties.status.toLowerCase());
    }
    if (feature.geometry.type == "Point") {

        if (!feature.properties.temp) {
            var className = "perm";
        } else {
            var className = "temp";
        }
        var marker = addPlainMarker(feature, className);
        map.panTo(marker.getLatLng());
        /*
        var spans = document.getElementById("details-container").getElementsByTagName("span");
        document.getElementById("site-img").src = feature.properties.imgURL;
        spans[0].innerText = feature.properties.name;
        spans[1].innerText = feature.properties.area;
        spans[2].innerText = feature.geometry.coordinates[1].toString().substring(0, 8) + "," + feature.geometry.coordinates[0].toString().substring(0, 8);
        
        if(Boolean(feature.properties.installDate)){
            spans[3].innerText = moment(feature.properties.installDate).format("MMMM  DD, YYYY");
        }
        spans[4].innerText = moment(feature.properties.lastDataReceived).format("DD/MM/YYYY HH:mm");
        */
        // spans[5].innerText = feature.properties.status;
        // //console.log(1)
        // spans[5].setAttribute("class", "")
        // //console.log(1)
        // spans[5].classList.add("status-" + feature.properties.status.toLowerCase());
    }
}

/**********************************************************************************************************


Functions for drawing lines, etc on map


************************************************************************************************************/

function createPopupHtml() {
    var htmlString = "<div class='popup-container'>";
    htmlString += "<div class='greyed-out justify-content-center align-items-center'> <img src ='/static/generic/small_loading.gif' class='loading-img'></div>"
    htmlString += "<div class='popup-content'></div>"
    htmlString += "<div class=' form-group row'><label class='col-12 col-lg-4 col-form-label' for='direction'>"
    htmlString += "Direction</label><div class='col-12 col-lg-8 select-container'><select class='form-control' id='direction'>"
    htmlString += "</select></div></div>"
    htmlString += "<div class=' form-group row'><label class='col-12 col-lg-4 col-form-label' for='order'>"
    htmlString += "Order</label><div class='col-12 col-lg-8'><input type='number' class='form-control' id='order'>"
    htmlString += "</div></div>"
    htmlString += "<div class='row'><div class='col-12'><button class='btn btn-outline-dark'>Delete</button></div></div>"
    htmlString += "</div>"
    return htmlString;
}


function toRadians(angle) {
    return angle * (Math.PI / 180);
}


/***************************************************************************************************************

functions for dealing with lines for sites arms/directions etc

****************************************************************************************************************/


function resetLineDrawingEvents() {
    map.off('mousemove', lineDrawMouseMove);
    map.off('click', lineDrawClick);
    map.off('dblclick', lineDrawDoubleClick);
    //map.on("click",map_clicked);
    map.off('contextmenu', lineDrawCancel);
}


function addVertex(e, line) {
    coords = line.getLatLngs();
    coords.push(e.latlng);
    line.setLatLngs(coords);
}


function onMouseMove(event, line) {
    console.log("moving mouse")
    coords = line.getLatLngs();
    if (coords.length > 1) {
        coords.pop();
        coords.push(event.latlng);
        line.setLatLngs(coords);
    }
}


function setupLocationLineWithArrowhead(line, col) {
    var popup = L.popup();
    popup.setContent(createPopupHtml());
    line.bindPopup(popup, { minWidth: 250, minHeight: 100 });
    line.enableEdit();
    line.on("click", function(e) {
        var popup = e.target.getPopup();
        popup.setLatLng(e.latlng).openOn(map);
        getDirections().then(function(response) { return response.json(); })
            .then(function(result) {
                if (result.data) {
                    popup._wrapper.getElementsByClassName("select-container")[0].innerHTML = result.data;
                    popup._wrapper.getElementsByClassName("btn")[0].addEventListener("click", function(e) {
                        map.removeLayer(line.arrowHead);
                        lineLayer.removeLayer(line);
                    });
                    popup._wrapper.getElementsByTagName("select")[0].addEventListener("change", function(e) {
                        line.options.direction = e.target.value;
                    });
                    popup._wrapper.getElementsByTagName("select")[0].value = line.options.direction;
                    popup._wrapper.getElementsByTagName("input")[0].addEventListener("change", function(e) {
                        line.options.order = e.target.value;
                    });
                    popup._wrapper.getElementsByTagName("input")[0].value = line.options.order;
                }
            });
    });

    line.on("editable:vertex:clicked", function(e) {})
    line.on("editable:vertex:dragend", function(e) {
        line.arrowHead.setPaths(line.getLatLngs());
        map.invalidateSize()
    })
    line.on("editable:vertex:mousedown", function(e) {
        e.originalEvent.preventDefault();
        console.log("line drawing disabled");
    })
    line.arrowHead = L.polylineDecorator(line, {
            patterns: [{
                offset: '100%',
                repeat: 0,
                symbol: L.Symbol.arrowHead({ pixelSize: 15, polygon: true, pathOptions: { stroke: true, color: "green", opacity: 0.7, weight: 3 } })
            }]
        }) //.addTo(lineLayer);
}


function setupDirectionLineWithArrowhead(line, color) {
    line.arrowHead = L.polylineDecorator(line, {
        patterns: [{
            offset: '100%',
            repeat: 0,
            symbol: L.Symbol.arrowHead({ pixelSize: 3, polygon: true, pathOptions: { fill: true, stroke: true, color: color, opacity: 1, weight: 3 } })
        }]
    }).addTo(lineLayer);
}



function onDoubleClick(event, line, ele) {
    clearTimeout(_dblClickTimer);
    _dblClickTimer = null;
    event.originalEvent.stopPropagation();
    event.originalEvent.preventDefault();
    L.DomEvent.stopPropagation(event);
    resetLineDrawingEvents();
    setupLocationLineWithArrowhead(line);
    cancelActionFunction = undefined;
    ele.click();
}


function cancelDrawLine(e, line, ele) {
    //toggle_function("draw line");
    cancelActionFunction = undefined;
    lineLayer.removeLayer(line);
    resetLineDrawingEvents();

}


function startLineDraw(event, ele) {
    console.log("starting line draw")
    map.off("click", currentMapFunction);
    if (!lineLayer) {
        lineLayer = new L.LayerGroup();
        lineLayer.addTo(map);
    }
    var line = L.polyline([event.latlng, event.latlng], {
        color: "red",
        interactive: true,
        editable: true,
        weight: 5,
        order: null,
        direction: null
    });
    lineLayer.addLayer(line);
    console.log("line layer is", lineLayer)
    map.on('mousemove', lineDrawMouseMove = function(e) { onMouseMove(e, line) });
    map.on('click', lineDrawClick = function(e) {
        if (_dblClickTimer !== null) {
            return;
        }
        _dblClickTimer = setTimeout(() => {
            addVertex(e, line);
            _dblClickTimer = null;
        }, 200);
    });
    map.on("dblclick", lineDrawDoubleClick = function(e) { onDoubleClick(e, line, ele) });
    map.on('contextmenu', lineDrawCancel = function(e) {
        cancelDrawLine(e, line, ele);
        ele.click();
    });
    cancelActionFunction = function(e) { cancelDrawLine(e, line, ele) };
}


/***************************************************************************************************************

functions for setting up event listeners

****************************************************************************************************************/


function toggleActionIcon(ele) {
    console.log("toggling action icons");
    var actions = document.getElementsByClassName("map-action-icon");
    for (var i = 0; i < actions.length; i++) {
        if (actions[i] != ele) {
            actions[i].classList.remove("action-selected");
        }
    }
    ele.classList.toggle("action-selected");
    if (ele.classList.contains("action-selected")) {

    }
}


//
// set the listeners to toggle the class
//
var actions = document.getElementsByClassName("map-action-icon");
for (var i = 0; i < actions.length; i++) {
    actions[i].addEventListener("click", function() { toggleActionIcon(this) })
    actions[i].addEventListener("click", actionclick = function() { mapActionIconClicked(this) })
}


function mapActionIconClicked(ele) {
    map.off("click", currentMapFunction);
    if (cancelActionFunction) {
        cancelActionFunction();
        cancelActionFunction = undefined;
    }
    if (ele.classList.contains("action-selected")) {
        var fnName = ele.getAttribute("data-function");
        console.log("setting map click function to", fnName)
        var fn = window[fnName];
        if (typeof fn === "function") {
            map.on("click", currentMapFunction = function(e) { fn(e, ele); });
        }
    } else {
        currentMapFunction = undefined;
    }
}


function placeMarker(event, ele) {
    if (marker) {
        map.removeLayer(marker);
    }
    marker = L.marker([event.latlng.lat, event.latlng.lng], {
        icon: icon,
        draggable: true
    }).addTo(map);
    marker.on("dragend", function(event) {
        document.getElementById("lat").value = event.target.getLatLng().lat;
        document.getElementById("lon").value = event.target.getLatLng().lng;
    });
    document.getElementById("lat").value = event.latlng.lat;
    document.getElementById("lon").value = event.latlng.lng;
    ele.click();
}