function setSidebarLocInfo(siteName, lat, lon) {
    lon = parseFloat(lon).toFixed(6);
    lat = parseFloat(lat).toFixed(6);

    document.getElementById("sidebar-site-name").innerText = siteName
    document.getElementById("sidebar-site-lat").innerText = lat
    document.getElementById("sidebar-site-lon").innerText = lon

    var id = 'cjwgah7js2kbb1cp9aztbp6vm';
    initMap([lat, lon], "countline-map", id);
    map.setZoom(17);
    vivacity_map = map._containerId;
    initMap2([lat, lon], "london-map", id);
    map2.setZoom(17);
    london_map = map._containerId;
    function errorMsg() {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Currently Services are unavailable!',
        })
    }
}



function toggleImageSize(){
    document.getElementById("myImg").classList.toggle("expand")
    if(document.getElementById("myImg").classList.contains("expand")){
        document.getElementById("img-icon").classList.remove("fa-expand")
        document.getElementById("img-icon").classList.add("fa-compress")
    }else{
        document.getElementById("img-icon").classList.remove("fa-compress")
        document.getElementById("img-icon").classList.add("fa-expand")
    }
}