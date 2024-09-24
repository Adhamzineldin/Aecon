const peakSelectBtn = document.getElementById("peak-select-btn"),
    siteSelectBtn = document.getElementById("site-select-btn")
var jtc_DataDetails;

let listData = {
    project: projectsdata,
    startTime: [{ "id": "07:00", "name": "07:00" }, { "id": "07:15", "name": "07:15" }, { "id": "07:30", "name": "07:30" }, { "id": "07:45", "name": "07:45" }, { "id": "08:00", "name": "08:00" }, { "id": "08:15", "name": "08:15" }, { "id": "08:30", "name": "08:30" }, { "id": "08:45", "name": "08:45" }, { "id": "09:00", "name": "09:00" }, { "id": "09:15", "name": "09:15" }, { "id": "09:30", "name": "09:30" }, { "id": "09:45", "name": "09:45" }, { "id": "10:00", "name": "10:00" }, { "id": "10:15", "name": "10:15" }, { "id": "10:30", "name": "10:30" }, { "id": "10:45", "name": "10:45" }, { "id": "11:00", "name": "11:00" }, { "id": "11:15", "name": "11:15" }, { "id": "11:30", "name": "11:30" }, { "id": "11:45", "name": "11:45" }, { "id": "12:00", "name": "12:00" }, { "id": "12:15", "name": "12:15" }, { "id": "12:30", "name": "12:30" }, { "id": "12:45", "name": "12:45" }, { "id": "13:00", "name": "13:00" }, { "id": "13:15", "name": "13:15" }, { "id": "13:30", "name": "13:30" }, { "id": "13:45", "name": "13:45" }, { "id": "14:00", "name": "14:00" }, { "id": "14:15", "name": "14:15" }, { "id": "14:30", "name": "14:30" }, { "id": "14:45", "name": "14:45" }, { "id": "15:00", "name": "15:00" }, { "id": "15:15", "name": "15:15" }, { "id": "15:30", "name": "15:30" }, { "id": "15:45", "name": "15:45" }, { "id": "16:00", "name": "16:00" }, { "id": "16:15", "name": "16:15" }, { "id": "16:30", "name": "16:30" }, { "id": "16:45", "name": "16:45" }, { "id": "17:00", "name": "17:00" }, { "id": "17:15", "name": "17:15" }, { "id": "17:30", "name": "17:30" }, { "id": "18:00", "name": "18:00" }, { "id": "18:15", "name": "18:15" }, { "id": "18:30", "name": "18:30" }, { "id": "18:45", "name": "18:45" },{ "id": "ALL", "name": "ALL" }],
    endTime: [{ "id": "07:15", "name": "07:15" }, { "id": "07:30", "name": "07:30" }, { "id": "07:45", "name": "07:45" }, { "id": "08:00", "name": "08:00" }, { "id": "08:15", "name": "08:15" }, { "id": "08:30", "name": "08:30" }, { "id": "08:45", "name": "08:45" }, { "id": "09:00", "name": "09:00" }, { "id": "09:15", "name": "09:15" }, { "id": "09:30", "name": "09:30" }, { "id": "09:45", "name": "09:45" }, { "id": "10:00", "name": "10:00" }, { "id": "10:15", "name": "10:15" }, { "id": "10:30", "name": "10:30" }, { "id": "10:45", "name": "10:45" }, { "id": "11:00", "name": "11:00" }, { "id": "11:15", "name": "11:15" }, { "id": "11:30", "name": "11:30" }, { "id": "11:45", "name": "11:45" }, { "id": "12:00", "name": "12:00" }, { "id": "12:15", "name": "12:15" }, { "id": "12:30", "name": "12:30" }, { "id": "12:45", "name": "12:45" }, { "id": "13:00", "name": "13:00" }, { "id": "13:15", "name": "13:15" }, { "id": "13:30", "name": "13:30" }, { "id": "13:45", "name": "13:45" }, { "id": "14:00", "name": "14:00" }, { "id": "14:15", "name": "14:15" }, { "id": "14:30", "name": "14:30" }, { "id": "14:45", "name": "14:45" }, { "id": "15:00", "name": "15:00" }, { "id": "15:15", "name": "15:15" }, { "id": "15:30", "name": "15:30" }, { "id": "15:45", "name": "15:45" }, { "id": "16:00", "name": "16:00" }, { "id": "16:15", "name": "16:15" }, { "id": "16:30", "name": "16:30" }, { "id": "16:45", "name": "16:45" }, { "id": "17:00", "name": "17:00" }, { "id": "17:15", "name": "17:15" }, { "id": "17:30", "name": "17:30" }, { "id": "18:00", "name": "18:00" }, { "id": "18:15", "name": "18:15" }, { "id": "18:30", "name": "18:30" }, { "id": "18:45", "name": "18:45" }, { "id": "19:00", "name": "19:00" },{ "id": "ALL", "name": "ALL" }],
    originArm: [],
    destArm: [],
    classification: [],
    //observation: ["Test 1", "Test 2", "Test 3", "Test 3", "Test 4"]
}


let optionList = {
    project: "project-select-option-list",
    startTime: "start-time-select-option-list",
    endTime: "end-time-select-option-list",
    originArm: "origin-arm-select-option-list",
    destArm: "dest-arm-select-option-list",
    classification: "classification-select-option-list",
    //observation: "observation-select-option-list"
}

let selectedValue = {
    project: listData.project[0].id,
    startTime: "",
    endTime: "",
    originArm: "",
    destArm: "",
    classification: "",
    peak: ""
}

let selectedSiteValue = {
    name: '',
    id: '',
    lat: '',
    lon: '',
}

let wrapperList = {
    project: "project-select-wrapper",
    site: "site-select-wrapper",
    //: "observation-select-wrapper",
    classification: "classification-select-wrapper",
    destArm: "dest-arm-select-wrapper",
    originArm: "origin-arm-select-wrapper",
    endTime: "end-time-select-wrapper",
    startTime: "start-time-select-wrapper",
}

let selectBtnList = {
    classification: { id: "classification-select-btn", name: "ALL" },
    destArm: { id: "dest-arm-select-btn", name: "ALL" },
    originArm: { id: "origin-arm-select-btn", name: "ALL" },
    endTime: { id: "end-time-select-btn", name: "All" },
    startTime: { id: "start-time-select-btn", name: "All" },
}

let inputList = {
    site: "site-select-input",
    classification: "classification-select-input",
    destArm: "dest-arm-select-input",
    originArm: "origin-arm-select-input",
    endTime: "end-time-select-input",
    startTime: "start-time-select-input",
    project: "project-select-input"
}

addListData();
document.getElementById('project-select-btn').firstElementChild.innerText = listData.project[0].name
const selectedProject = listData.project.find(project => project.id == listData.project[0].id);
displaySiteList(selectedProject.sites);

function addListData() {
    for (const item of Object.keys(optionList)) {
        document.getElementById(optionList[item]).innerHTML = "";
    }
    for (const [data, dataList] of Object.entries(listData)) {
        dataList.forEach(item => {
            let li;
            if (data === "project") {
                const isSelected = item.id == selectedValue[data];
                li = `<li onclick="updateprojectName(this, '${data}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" id="${item.id}">${item.name.replace(/\s/g,'')}${isSelected ? "<i class='fa-solid fa-check' style='color:#25d125;font-size:14px; background-color: #dddddd; height: 39px;padding-top: 12px;'></i>":""}
                </li>`;
            }else if (data === "classification") {
                const isSelected = item.id == selectedValue[data];
                li = `<li onclick="updateName(this, '${data}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" style="justify-content: start;" id="${item.id}"><div class="col-9 px-0 classification-option"><span class="red-box ${item.name}"></span>${item.name.charAt(0).toUpperCase() + item.name.slice(1).replace(/\s/g,'')}</div>${isSelected?"<i class='fa-solid fa-check' style='color:#25d125;font-size:14px; background-color: #dddddd; height: 39px;padding-top: 12px;'></i>" : ""}
                      </li>`;
            }else if (data == "originArm" || data == "destArm") {
                if(item.project == selectedValue.project){
                    const isSelected = item.id == selectedValue[data];
                    li = `<li onclick="updateName(this, '${data}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" id="${item.id}">${item.name.replace(/\s/g,'')}${isSelected ? "<i class='fa-solid fa-check' style='color:#25d125;font-size:14px; background-color: #dddddd; height: 39px;padding-top: 12px;'></i>":""}
                      </li>`;
                }
                
            } else if (data !== "observation") {
                const isSelected = item.id == selectedValue[data];
                li = `<li onclick="updateName(this, '${data}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" id="${item.id}">${item.name.replace(/\s/g,'')}${isSelected ? "<i class='fa-solid fa-check' style='color:#25d125;font-size:14px; background-color: #dddddd; height: 39px;padding-top: 12px;'></i>":""}
                      </li>`;
            // } else {
            //     li = `<li class="dd-list" onclick="observationPopup(this)" val="${item.replace(/\s/g, '')}">${item.replace(/\s/g, '')}</li>`;
            }
            if(li !== undefined){
                document.getElementById(optionList[data]).insertAdjacentHTML("beforeend", li);
            }
        });

        if (optionList[data] === 'classification-select-option-list') {
            const isSelected = '' === selectedValue.classification;
            const li = `<li onclick="updateName(this, 'classification')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" id="All" style="justify-content: start;"><div class="col-9 px-0 classification-option"><span class="red-box All"></span>ALL</div>${isSelected?"<i class='fa-solid fa-check' style='color:#25d125;font-size:14px; background-color: #dddddd; height: 39px;padding-top: 12px;'></i>":""}</li>`;
            document.getElementById(optionList[data]).insertAdjacentHTML("beforeend", li);
        }

        if (optionList[data] === 'origin-arm-select-option-list' || optionList[data] === 'dest-arm-select-option-list') {
            const isSelected = '' === selectedValue[data];
            const li = `<li onclick="updateName(this, '${data}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" id="All">ALL${isSelected ? "<i class='fa-solid fa-check' style='color:#25d125;font-size:14px; background-color: #dddddd; height: 39px;padding-top: 12px;'></i>" : ""}
                        </li>`;
            document.getElementById(optionList[data]).insertAdjacentHTML("beforeend", li);
        }
    }
}

function updateName(selectedLi, sec) {
    const updateSelectedValues = () => {
        document.getElementById(inputList[sec]).value = "";
        document.getElementById(wrapperList[sec]).classList.remove("active");
        document.getElementById(selectBtnList[sec].id).firstElementChild.innerText = selectedLi.innerText;
    };

    if (sec == 'classification') {
        const nameInnerTextArray = [];
        const idInnerTextArray = [];

        if (selectedLi.innerText == 'ALL') {
            selectedValue.classification = "";
            addListData();
            updateSelectedValues();
        } else {
            if (selectedLi.classList.contains("dd-isSelected")) {
                selectedLi.removeChild(selectedLi.lastElementChild);
                selectedLi.classList.remove("dd-isSelected");
            } else {
                selectedLi.classList.add("dd-isSelected");
                let i = document.createElement("i");
                i.classList.add("fa-solid", "fa-check");
                i.style.fontSize = "16px";
                i.style.color = "#25d125";
                selectedLi.appendChild(i);
            }

            document.querySelectorAll("#classification-select-option-list li").forEach(item => {
                if (item.classList.contains("dd-isSelected")) {
                    if (item.innerText === 'ALL') {
                        item.classList.remove("dd-isSelected");
                        item.removeChild(item.lastElementChild);
                    } else {
                        nameInnerTextArray.push(item.innerText);
                        idInnerTextArray.push(item.id);
                    }
                }
            });

            selectedValue[sec] = idInnerTextArray;
            updateSelectedValues();
            document.getElementById(selectBtnList[sec].id).firstElementChild.innerText = nameInnerTextArray;
        }
    } else {
        
        if (["startTime", "endTime"].includes(sec) && selectedLi.innerText == 'ALL') {
            selectedValue[sec] = "";
        }else if (["originArm", "destArm"].includes(sec) && selectedLi.innerText == 'ALL') {
            selectedValue[sec] = "";
        }else{
            selectedValue[sec] = selectedLi.id;
        }
        
        updateSelectedValues();
        
    }

    addListData();
    addClassificationListData(sec,selectedValue[sec]);
    loadJtcData(selectedSiteValue.id, selectedValue.project, selectedValue.originArm, selectedValue.destArm).then(function () {
        
    })
    
}

function updateSiteName(selectedLi) {
    if (selectedSiteValue.id.length > 4 && !selectedLi.classList.contains("dd-isSelected")) {
        alert('You can only select up to 5 sites');
        return;
    }
    if(document.getElementById(inputList["site"]).value != ''){
        document.querySelectorAll("#site-select-option-list li").forEach(item => {
           item.classList.remove("d-none")
        })
    }
    document.getElementById(inputList["site"]).value = "";
    var classCount = 1;

    if(selectedLi.classList.contains("dd-isSelected")){
        selectedLi.removeChild(selectedLi.lastElementChild)
        selectedLi.classList.remove("dd-isSelected")
    }else{
        selectedLi.classList.add("dd-isSelected")
        let i = document.createElement("i")
        i.classList.add("fa-solid")
        i.classList.add("fa-check")
        i.style.fontSize = "16px"
        i.style.color = "#25d125"
        selectedLi.appendChild(i)
    }
    
    const nameInnerTextArray = [];
    const idInnerTextArray = [];
    const latInnerTextArray = [];
    const lonInnerTextArray = [];
    classCount = 1;
    document.querySelectorAll("#site-select-option-list li").forEach(item => {
        if (item.lastElementChild) {
            classCount += 1            
        }
        if(item.classList.contains("dd-isSelected")){
            nameInnerTextArray.push(item.innerText);
            idInnerTextArray.push(item.id);
            latInnerTextArray.push(item.getAttribute("lat"));
            lonInnerTextArray.push(item.getAttribute("lon"));

        }
        
    })
    selectedSiteValue.name = nameInnerTextArray;
    selectedSiteValue.id = idInnerTextArray;
    selectedSiteValue.lat = latInnerTextArray;
    selectedSiteValue.lon = lonInnerTextArray;
    loadLocation(selectedSiteValue.id).then(function () {
        // listData.project = [...location_details.project]
        listData.originArm = [...location_details.arms]
        listData.destArm = [...location_details.arms]
        listData.classification = [...location_details.classes]

        selectedValue = {
            project: selectedValue.project,
            startTime: "",
            endTime: "",
            originArm: "",
            destArm: "",
            classification: "",
            site: "",
            peak: ""
        }

        addListData()
        document.getElementById("site-select-btn").firstElementChild.innerText = selectedSiteValue.name.join(', ');

        Object.keys(selectBtnList).forEach(key => document.getElementById(selectBtnList[key].id).firstElementChild.innerText = selectBtnList[key].name)

        loadJtcData(selectedSiteValue.id, selectedValue.project, selectedValue.originArm, selectedValue.destArm).then(function () {
        
        })
    
    });
    
}


function loadLocation(id){
    let formData = new FormData()
    formData.append("location_id", JSON.stringify(id))
  
    return fetcher(formData, "getLocations", function (response) {
        location_details = response;
        setSiteNameList(location_details,location_details.project[0].id)
    })
    
  }

    function loadJtcData(siteId,projectId){
        let formData = new FormData()
        formData.append("location_id",siteId)
        formData.append("project_id",projectId)

        return fetcher(formData, "get_jtc_data", function (response) {
            jtc_data = response;
            jtc_DataDetails = jtc_data.data;
            countTotalJTCdata(jtc_data.data)
            
        })
    }

function filterSiteList(e) {
    document.querySelectorAll("#site-select-option-list li").forEach(item => {
        !item.innerText.startsWith(e.value) ? item.classList.add("d-none") : item.classList.remove("d-none")
    })
}

function filterList(eve, sec) {
    let arr = [];
    let searchWord = eve != "startTime" || eve != "endTime" ? eve.value.toLowerCase() : eve.value
    arr = listData[sec].filter(data => {
        return eve != "startTime" || eve != "endTime" ? data.name.toLowerCase().startsWith(searchWord) : data.name.startsWith(searchWord)
    }).map(data => {
        let isSelected = data.name == document.getElementById(selectBtnList[sec].id).firstElementChild.innerText ? true : false;
        return `<li onclick="updateName(this,'${sec}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" id="${data.id}">${data.name}${isSelected ? "<i class='fa-solid fa-check'  style='color:#25d125;font-size:16px;'></i>" : ""}</li>`;
    }).join("");
    document.getElementById(optionList[sec]).innerHTML = arr ? arr : `<p style="margin-top: 10px;">Oops! ${sec} not found</p>`;
}

siteSelectBtn.addEventListener("click", (e) => {
    e.stopPropagation()
    Object.keys(wrapperList).forEach(item => {
        if (item == "site") {
            document.getElementById(wrapperList[item]).classList.toggle("active")
        } else {
            document.getElementById(wrapperList[item]).classList.remove("active")
        }
    })
});



document.addEventListener("click", () => {
    Object.keys(wrapperList).forEach(item => {
        document.getElementById(wrapperList[item]).classList.remove("active")
    })
})

document.getElementById("onDropdowns").addEventListener("click", (e) => {
    e.stopPropagation()
    Object.keys(wrapperList).forEach(item => {
        if (e.target.getAttribute("sectionId") && wrapperList[item] == e.target.getAttribute("sectionId")) {
            document.getElementById(e.target.getAttribute("sectionId")).classList.toggle("active")
        } else {
            document.getElementById(wrapperList[item]).classList.remove("active")
        }
    })
})


// Function to check if an element contains a certain text
function containsText(element, text) {
    return element.textContent.trim().includes(text);
}


function setSiteNameList(data, project_id) {
    mapsetup(data, project_id)
    const accordion = $('#accordion');
    let card = '';

    data.locations.features.forEach((site, index) => {
        // Collect the names of all arms for the current location
        const armNames = data.arms
            .filter(arm => arm.location === site.properties.id)
            .map(arm => arm.Fullname);

        // Create a list of arm names with each name in a separate div
        const armList = armNames.map(armName => `<div>${armName}</div>`).join('');

        card += `
            <div class="card">
                <div class="card-header">
                    <a class="card-link" data-toggle="collapse" href="#collapse${index + 1}">
                        ${site.properties.name}
                    </a>
                </div>
                <div id="collapse${index + 1}" class="collapse" data-parent="#accordion">
                    <div class="card-body">
                        <div class="side-location-loc-key">Location</div>
                        <div class="side-location-lat-value pt-3" id="sidebar-site-lat${index + 1}">
                            ${site.geometry.coordinates[0]}, ${site.geometry.coordinates[1]}
                        </div>
                        <div class="side-location-loc-key">Arm</div>
                        <div class="side-location-lat-value pt-3" id="sidebar-site-arm-${index + 1}">
                             ${armList}
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    accordion.empty().append($(card));
}




window.myApp = window.myApp || {};
window.myApp.map = window.myApp.map || null;
let count = 0; 

function mapsetup(data, project_id) {
    if (!window.myApp.map) {
        // Create a new map only if it doesn't exist
        window.myApp.map = L.map('countline-map').setView([0, 0], 25); // Set initial view

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(window.myApp.map);
    }
    if (window.myApp != undefined && window.myApp != null) {
        window.myApp.map.eachLayer(function (layer) {
            // Check if the layer is a Marker or a custom layer (e.g., L.TileLayer, L.ImageOverlay)
            if (layer instanceof L.Marker || (layer instanceof L.Layer && !layer instanceof L.TileLayer)) {
                window.myApp.map.removeLayer(layer);
            }
        });
    }
    const markersLayer = L.layerGroup().addTo(window.myApp.map);

    const bounds = L.latLngBounds();

    // Clear existing markers before adding new ones
    markersLayer.clearLayers();
    count = 0;
    data.locations.features.slice(0, 5).forEach(site => {
        if(selectedSiteValue.id.includes(site.properties.id.toString())){
            bounds.extend([site.geometry.coordinates[1], site.geometry.coordinates[0]]);

            const textContent = ++count;

            const customIcon = L.divIcon({
                className: 'custom-marker',
                html: `<div class="marker-circle">${textContent}</div>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15],
            });

            const mainMarker = L.marker([site.geometry.coordinates[1], site.geometry.coordinates[0]], { icon: customIcon }).addTo(markersLayer);
            data.arms.forEach(arm => {
                if (project_id === arm.project && site.properties.id == arm.location) {
                    const bearing = (calculateBearing([site.geometry.coordinates[1], site.geometry.coordinates[0]], [arm.lat, arm.lon]) + 360) % 360;

                    const armContainer = L.DomUtil.create('div', 'arm-container');
                    armContainer.innerHTML = `<div class="d-flex" style="position: relative; width: 100px; transform: rotate(${bearing}deg);">
                        <span class="text1" id="${site.properties.id}_${arm.id}_AllDestinations"></span>
                        <span class="image1"><img src="/static/aecon/up-arrow.png"></span>
                        <span class="image2"><img src="/static/aecon/down-arrow_1.png"></span>
                        <span class="text2" id="${site.properties.id}_AllOrigins_${arm.id}"></span>
                    </div>`;

                    const customArmIcon = L.divIcon({
                        className: 'custom-arm-icon',
                        html: armContainer.outerHTML,
                        iconSize: [30, 30],
                        iconAnchor: [15, 15],
                    });
                    const roadMarker = L.marker([arm.lat, arm.lon], { icon: customArmIcon }).addTo(markersLayer);

                    window.myApp.map.on('zoomend', function () {
                        const zoomLevel = window.myApp.map.getZoom();
                        const scaleFactor = zoomLevel / 10;
                    
                        // Select the image1 and image2 elements and adjust their size
                        const image1 = armContainer.querySelector('.image1 img');
                        const image2 = armContainer.querySelector('.image2 img');
                        var originalWidthImage1 = 24;
                        var originalWidthImage2 = 24; 
                    
                        if (image1 && image2) {
                            $('.marker-circle').height(15*scaleFactor).width(15*scaleFactor);
                            image1.style.width = `${originalWidthImage1 * scaleFactor}px`;
                            image1.style.height = `${originalWidthImage1 * scaleFactor}px`;
                    
                            image2.style.width = `${originalWidthImage2 * scaleFactor}px`; 
                            image2.style.height = `${originalWidthImage2 * scaleFactor}px`;
                    
                            // Create a new divIcon with the modified size
                            const customArmIcon = L.divIcon({
                                className: 'custom-arm-icon',
                                html: armContainer.outerHTML,
                                iconSize: [30, 30], // Use the original icon size here
                                iconAnchor: [15, 15],
                            });
                    
                            // Set the new icon to the marker
                            roadMarker.setIcon(customArmIcon);
                        }
                        if(jtc_DataDetails != undefined){
                            countTotalJTCdata(jtc_data.data)
                        }
                    });
                    
                    
                }
            });
        }
    });

    window.myApp.map.fitBounds(bounds);
    window.myApp.map.dragging.enable();
}

  

function calculateBearing(from, to) {

var lat1 = from[0] * Math.PI / 180;
var lon1 = from[1] * Math.PI / 180;
var lat2 = to[0] * Math.PI / 180;
var lon2 = to[1] * Math.PI / 180;

var y = Math.sin(lon2 - lon1) * Math.cos(lat2);
var x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);

var bearing = Math.atan2(y, x) * 180 / Math.PI;

return (bearing + 360) % 360;
}
  
function getCardinalDirection(bearing) {
    if (bearing >= 337.5 || bearing < 22.5) {
        return 'North';
    } else if (bearing >= 22.5 && bearing < 67.5) {
        return 'Northeast';
    } else if (bearing >= 67.5 && bearing < 112.5) {
        return 'East';
    } else if (bearing >= 112.5 && bearing < 157.5) {
        return 'Southeast';
    } else if (bearing >= 157.5 && bearing < 202.5) {
        return 'South';
    } else if (bearing >= 202.5 && bearing < 247.5) {
        return 'Southwest';
    } else if (bearing >= 247.5 && bearing < 292.5) {
        return 'West';
    } else {
        return 'Northwest';
    }
}


function countTotalJTCdata(JTCdata) {

    // Create a map to store total counts for each origin_arm
    const originArmCounts = new Map();
    JTCdata.forEach(({ location_id,origin_arm, value }) => {
        let totalCount = 0;
        value.forEach(({ Start_time, End_time, class: classDetails }) => {
            if (isSelectedValueValid(selectedValue, { Start_time, End_time, class: classDetails })) {
                classDetails.forEach(({ id, count }) => {
                    if (selectedValue.classification.length === 0 || selectedValue.classification.includes(id.toString())) {
                        totalCount += count;
                    }
                });
            }
        });

        const originArmKey = `${location_id}_AllOrigins_${origin_arm}`;
        originArmCounts.set(originArmKey, (originArmCounts.get(originArmKey) || 0) + totalCount);
    });

    originArmCounts.forEach((total, origin_arm) => {
        $(`#${origin_arm}`).text(total);
    });

    
    // Create a map to store total counts for each combination of location_id and destination_arm
    const locationDestinationCounts = new Map();
    JTCdata.forEach(({ location_id, destination_arm, value }) => {
        let totalCount = 0;

        value.forEach(({ Start_time, End_time, class: classDetails }) => {
            if (isSelectedValueValid(selectedValue, { Start_time, End_time, class: classDetails })) {
                classDetails.forEach(({ id, count }) => {
                    if (selectedValue.classification.length === 0 || selectedValue.classification.includes(id.toString())) {
                        totalCount += count;
                    }
                });
            }
        });
        const key = `${location_id}_${destination_arm}`;
        locationDestinationCounts.set(key, (locationDestinationCounts.get(key) || 0) + totalCount);
    });

    locationDestinationCounts.forEach((total, key) => {
        
        $(`#${key}_AllDestinations`).text(total);
    });
}



function isSelectedValueValid(selectedValue, value) {
    if (selectedValue != '') {
        if (selectedValue.startTime != '' && selectedValue.endTime != '') {
            return (
                value.Start_time >= selectedValue.startTime &&
                value.End_time <= selectedValue.endTime
            );
        } else if (selectedValue.startTime != '' && value.Start_time >= selectedValue.startTime) {
            return true;
        } else if (selectedValue.endTime != '' && value.End_time <= selectedValue.endTime) {
            return true;
        }
    }

    return selectedValue == '' || (selectedValue.endTime == '' && selectedValue.startTime == '');
}


function addClassificationListData(section,classificationData){
    if (section === 'classification' && classificationData) {
        classificationData.forEach(id => {
            let li = $('#' + id); 
            if (li.length > 0) {
                if (li.hasClass("dd-isSelected")) {
                    li.removeClass("dd-isSelected").find('.fa-check').remove();
                }
                li.addClass("dd-isSelected");
    
                let i = document.createElement("i");
                i.classList.add("fa-solid", "fa-check");
                i.style.fontSize = "16px";
                i.style.color = "#25d125";
    
                li.append(i);
            }
        });
    }
}


function updateprojectName(selectedLi, sec) {
    document.getElementById(inputList[sec]).value = "";
    selectedValue[sec] = selectedLi.id
    addListData()
    document.getElementById(wrapperList[sec]).classList.remove("active")
    document.getElementById('project-select-btn').firstElementChild.innerText = selectedLi.innerText;

    const selectedProject = listData.project.find(project => project.id == selectedLi.id);

    displaySiteList(selectedProject.sites);
    /* loadJtcData(selectedSiteValue.id, selectedValue.project).then(function () {
       
    })*/

}


function observationPopup(element) {
    fetchObservation(selectedSiteValue.id)
      .then(function () {
        $('#staticBackdrop').modal('show')
      })
      .catch(function (error) {
        console.error('Error in addupdateObservation:', error);
      });
    
}



function observationadd(){
    let Observationdata = $('#Observation-name').val();

    addupdateObservation(selectedSiteValue.id, selectedValue.project, Observationdata)
      .then(function () {
        $('#staticBackdrop').modal('hide');
      })
      .catch(function (error) {
        console.error('Error in addupdateObservation:', error);
      });
  };


function addupdateObservation(siteId,projectId,Observationdata){
    let formData = new FormData()
    formData.append("location_id",siteId)
    formData.append("project_id",projectId)
    formData.append("Observation",Observationdata)

    return fetcher(formData, "add_update_jtc_Observation", function (response) {
        // jtc_data = response;
        
    })
}
function fetchObservation(siteId){
    let formData = new FormData()
    formData.append("location_id",siteId)

    return fetcher(formData, "fetch_jtc_Observation", function (response) {
        jtc_Observation = response;
        if(jtc_Observation.length){
            $('#Observation-name').val(jtc_Observation[0].text)
        }else{
            $('#Observation-name').val('')
        }
        
    })
}


function displaySiteList(sites) {
    const liElementsWithoutDNone = $('#site-select-option-list li:not(.d-none)');
    liElementsWithoutDNone.addClass('d-none');
    selectedSiteValue.id= ''
    selectedSiteValue.name= ''
    selectedSiteValue.lat= ''
    selectedSiteValue.lon= ''

    document.getElementById(inputList["site"]).value = "";
    document.getElementById("site-select-btn").firstElementChild.innerText = 'Please select Site'
    var ulElement = document.getElementById('site-select-option-list');
    var listItems = ulElement.getElementsByTagName('li');
    for (var i = 0; i < listItems.length; i++) {
        var listItem = listItems[i];
        listItem.classList.remove('dd-isSelected');
        var iconElement = listItem.querySelector('i');
        if (iconElement) {
            listItem.removeChild(iconElement);
        }
    }

    if (sites && sites.length > 0) {
        sites.forEach(site => {
            $('#'+site.id).removeClass('d-none')
        });
    } else {
        // Display a message if no sites are available
        siteListContainer.text('No sites available for the selected project.');
    }
    
}