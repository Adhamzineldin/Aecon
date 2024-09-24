function fetcher(formData, url, func, redirect) {
    if (!redirect) { redirect = "error"; }
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/aecon/" + url, { body: formData, method: "POST", credentials: 'same-origin', redirect: "follow" });

    return f.then(handleErrors).catch(function(err) { throw err })
        .then(function(response) { return response.json(); })
        .then(function(result) { func(result) })

}


function fetcherGet(url, func, redirect) {
    if (!redirect) { redirect = "error"; }
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/aecon/" + url, { method: "GET", credentials: 'same-origin', redirect: "follow" });
    return f.then(handleErrors).catch(function(err) { throw err })
        .then(function(response) { return response.json(); })
        .then(function(result) { func(result) })

}



function handleErrors(response) {

    if (!response.ok) {
       
        throw Error(response.statusText);
    } else {

        if (response.headers.get("Content-Type") == "application/json") {
            return response;
        }
        if (response.redirected) {
            //console.log("redirecting");
            window.location.href = response.url;
            //console.log("finised setting href");
            throw new Error("Break");
        }
        if (response.status == 500) {
            window.location.href = "/";
            //console.log("finised setting href");
            throw new Error("Break");
        }
    }
}


function catchConnectionErrors(exception) {
    if (exception.status) {
        return exception;
    } else {
        throw Error("Server not responding")
    }
}



function getDirections() {
    var formData = new FormData();
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/getDirections", { body: formData, method: "POST", credentials: 'same-origin', "redirect": "follow" });
    return f;
}


function getAPIClasses() {
    var formData = new FormData();
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/getAPIClasses", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}


function getLocationClasses(id) {
    var formData = new FormData();
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    formData.append("location_id", id);
    var f = fetch("/schoolstreets/getLocationClasses", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}


function saveLocationClasses(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/saveLocationClasses", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}


function saveGroup(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/applyGroup", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}


function getLocationsAsGeojson() {
    var formData = new FormData();
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/getLocations", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}


function getView(id) {
    var formData = new FormData();
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value);
    formData.append("view", id);
    var f = fetch("/schoolstreets/getView", { body: formData, method: "POST", redirect: "follow", credentials: 'same-origin', });
    return f;
}


function uploadLocationData(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/uploadLocationData", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}

function getATCOverview(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/getATCOverview", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}

function getATCClassedVolumes(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/getATCClassedVolumes", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}


function getATCSpeedData(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/getATCSpeedData", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}


function getLocationDataCounts(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/getLocationDataCounts", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}


function getLocationDataCountsHourly(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/getLocationDataCountsHourly", { body: formData, method: "POST", credentials: 'same-origin', });
    return f.catch(catchConnectionErrors).then(handleErrors).then(function(response) { return response.json(); })







}


function toggleBadData(formData) {
    formData.append("csrfmiddlewaretoken", document.getElementsByName("csrfmiddlewaretoken")[0].value)
    var f = fetch("/schoolstreets/toggleBadData", { body: formData, method: "POST", credentials: 'same-origin', });
    return f;
}