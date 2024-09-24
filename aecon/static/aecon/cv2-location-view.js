initMap([53.476404, -2.250621],"admin-map");
map.setZoom(18);
map.on('zoomend', function() {
    var zoomlevel = map.getZoom();
    if (zoomlevel  <18){
        if (map.hasLayer(lineLayer)) {
            map.removeLayer(lineLayer);
        } else {
        }
    }
    if (zoomlevel >= 18){
        if (map.hasLayer(lineLayer)){
        } else {
            map.addLayer(lineLayer);
        }
    }
});


function dealWithLocationFeatureCollection(feature,layer){
    //console.log("dealing with location",feature)
    if (feature.geometry.type == "LineString"){
        //console.log(feature);
        layer.setStyle(locationStyleOptions);
        lineLayer.addLayer(layer);
        setupLocationLineWithArrowhead(layer);
        layer.options.direction = feature.properties.direction_id;
        layer.options.order = feature.properties.order;

    }
    if (feature.geometry.type == "Point"){
        var marker = addLocationPointMarker(feature,{draggable:true,interactive:true});
        marker.on("dragend",function(event){
            document.getElementById("lat").value = event.target.getLatLng().lat;
            document.getElementById("lon").value = event.target.getLatLng().lng;
        });
    }
    //console.log("finished dealing with feature collection");
}


function dealWithLocationFeatureCollection(feature,layer){
        console.log("dealing with location",feature)
        if (feature.geometry.type == "LineString" && feature.properties.type == "countline"){
            //console.log("found countline",feature);
            layer.setStyle({color:"#2483ec"});
            //layer.addTo(map);
            //layer.setStyle(locationStyleOptions);
            lineLayer.addLayer(layer);

            map.fitBounds(lineLayer.getBounds(),{"maxZoom":19});
            //var spans = document.getElementById("details-container").getElementsByTagName("span");
            //spans[0].innerText = feature.properties.name;
            //spans[1].innerText = feature.properties.area;
            //spans[2].innerText = feature.geometry.coordinates[1].toString().substring(0, 8) + "," + feature.geometry.coordinates[0].toString().substring(0, 8);
            //spans[3].innerText = moment(feature.properties.installDate).format("MMMM  DD, YYYY");
            //spans[4].innerText = moment(feature.properties.lastDataReceived).format("DD/MM/YYYY HH:mm");
            //spans[5].innerText = feature.properties.status;
            //spans[5].setAttribute("class", "")
            //spans[5].classList.add("status-" + feature.properties.status.toLowerCase());
            //document.getElementById("site-img").src = feature.properties.imgURL;
        }
        if (feature.geometry.type == "Point"){
            //return;
            //marker = addLocationPointMarker(feature,{});
            //console.log("marker is",marker,marker.getLatLng());
            //var popup = L.popup({maxWidth:350,minWidth:350}).setLatLng(marker.getLatLng());
            //popup.setContent(createMetaDataPopup2(feature));
            //marker.bindPopup(popup);
            //map.panTo(marker.getLatLng());

            var spans = document.getElementById("details-container").getElementsByTagName("span");
            spans[0].innerText = feature.properties.name;
            spans[1].innerText = feature.properties.area;
            spans[2].innerText = feature.geometry.coordinates[1].toString().substring(0, 8) + "," + feature.geometry.coordinates[0].toString().substring(0, 8);
            spans[3].innerText = moment(feature.properties.installDate).format("MMMM  DD, YYYY");
            spans[4].innerText = moment(feature.properties.lastDataReceived).format("DD/MM/YYYY HH:mm");
            spans[5].innerText = feature.properties.status;
            spans[5].setAttribute("class", "")
            spans[5].classList.add("status-" + feature.properties.status.toLowerCase());
            document.getElementById("site-img").src = feature.properties.imgURL;
        }
    }


function loadLocation(id){
        console.log("in load location");
        var formData = new FormData();
        formData.append("location_id",JSON.stringify(id));
        return fetcher(formData,"getLocations",function(result){
            console.log("received results of location",result);
            lineLayer.eachLayer(function (layer) {
                    lineLayer.removeLayer(layer);
            });
            processLocationGeojson(result.locations);
            //map.fitBounds(markerLayer.getBounds());
            return;
            document.getElementById("classes-popup").getElementsByClassName("conduit-selectable-menu")[0].innerHTML = result.classes;
            console.log("directions are",result.directions);
            document.getElementById("directions-popup").getElementsByClassName("conduit-selectable-menu")[0].innerHTML = result.directions;
            setPopupListeners(document.getElementById("classes-popup"))
            setPopupListeners(document.getElementById("directions-popup"));
            var items = document.getElementById("classes-popup").getElementsByClassName("menu-item");
            document.getElementById("img-container").getElementsByTagName("div")[0].classList.remove("d-none");
            for(var i=0;i<items.length;i++){
                //console.log("in inline script, setting up click listener for",items[i]);
                items[i].addEventListener("click",function(){updateDatasets();changeGraph()});
            }
            var items = document.getElementById("directions-popup").getElementsByClassName("menu-item");
            for(var i=0;i<items.length;i++){
                //console.log("in inline script, setting up click listener for",items[i]);
                items[i].addEventListener("click",function(){changeDirection()});
            }

        });
    }


loadLocation(document.getElementById("locId").value);

var formData = new FormData();
formData.append("location_id",document.getElementById("locId").value);
//fetcher(formData,"getLocations",function(result){console.log("received results",result);processLocationGeojson(result.data);});


var datepicker = $('#upload').daterangepicker({
singleDatePicker: true,
opens:"center",
drops:"up",

locale: {
            format: 'DD/MM/YYYY'
        },

        });


datepicker.on('apply.daterangepicker', function(ev, picker) {
    datesEdited = true;
    uploadData(picker.startDate.format('YYYY-MM-DD'));
});




//fetcher(formData,"getLocationClasses",function(result){
 //                       updateClassContainers(result);
 //                   });


 addMessage("Data successfully uploaded","flaticon-success","green");
 addMessage("Sensor went offline","flaticon-warning","red");