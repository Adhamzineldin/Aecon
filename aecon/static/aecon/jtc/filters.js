const peakSelectBtn = document.getElementById("peak-select-btn"),
    siteSelectBtn = document.getElementById("site-select-btn")
var jtc_DataDetails;

let listData = {
    project: [],
    startTime: [{ "id": "07:00", "name": "07:00" }, { "id": "07:15", "name": "07:15" }, { "id": "07:30", "name": "07:30" }, { "id": "07:45", "name": "07:45" }, { "id": "08:00", "name": "08:00" }, { "id": "08:15", "name": "08:15" }, { "id": "08:30", "name": "08:30" }, { "id": "08:45", "name": "08:45" }, { "id": "09:00", "name": "09:00" }, { "id": "09:15", "name": "09:15" }, { "id": "09:30", "name": "09:30" }, { "id": "09:45", "name": "09:45" }, { "id": "10:00", "name": "10:00" }, { "id": "10:15", "name": "10:15" }, { "id": "10:30", "name": "10:30" }, { "id": "10:45", "name": "10:45" }, { "id": "11:00", "name": "11:00" }, { "id": "11:15", "name": "11:15" }, { "id": "11:30", "name": "11:30" }, { "id": "11:45", "name": "11:45" }, { "id": "12:00", "name": "12:00" }, { "id": "12:15", "name": "12:15" }, { "id": "12:30", "name": "12:30" }, { "id": "12:45", "name": "12:45" }, { "id": "13:00", "name": "13:00" }, { "id": "13:15", "name": "13:15" }, { "id": "13:30", "name": "13:30" }, { "id": "13:45", "name": "13:45" }, { "id": "14:00", "name": "14:00" }, { "id": "14:15", "name": "14:15" }, { "id": "14:30", "name": "14:30" }, { "id": "14:45", "name": "14:45" }, { "id": "15:00", "name": "15:00" }, { "id": "15:15", "name": "15:15" }, { "id": "15:30", "name": "15:30" }, { "id": "15:45", "name": "15:45" }, { "id": "16:00", "name": "16:00" }, { "id": "16:15", "name": "16:15" }, { "id": "16:30", "name": "16:30" }, { "id": "16:45", "name": "16:45" }, { "id": "17:00", "name": "17:00" }, { "id": "17:15", "name": "17:15" }, { "id": "17:30", "name": "17:30" }, { "id": "18:00", "name": "18:00" }, { "id": "18:15", "name": "18:15" }, { "id": "18:30", "name": "18:30" }, { "id": "18:45", "name": "18:45" },{ "id": "", "name": "ALL" }],
    endTime: [{ "id": "07:15", "name": "07:15" }, { "id": "07:30", "name": "07:30" }, { "id": "07:45", "name": "07:45" }, { "id": "08:00", "name": "08:00" }, { "id": "08:15", "name": "08:15" }, { "id": "08:30", "name": "08:30" }, { "id": "08:45", "name": "08:45" }, { "id": "09:00", "name": "09:00" }, { "id": "09:15", "name": "09:15" }, { "id": "09:30", "name": "09:30" }, { "id": "09:45", "name": "09:45" }, { "id": "10:00", "name": "10:00" }, { "id": "10:15", "name": "10:15" }, { "id": "10:30", "name": "10:30" }, { "id": "10:45", "name": "10:45" }, { "id": "11:00", "name": "11:00" }, { "id": "11:15", "name": "11:15" }, { "id": "11:30", "name": "11:30" }, { "id": "11:45", "name": "11:45" }, { "id": "12:00", "name": "12:00" }, { "id": "12:15", "name": "12:15" }, { "id": "12:30", "name": "12:30" }, { "id": "12:45", "name": "12:45" }, { "id": "13:00", "name": "13:00" }, { "id": "13:15", "name": "13:15" }, { "id": "13:30", "name": "13:30" }, { "id": "13:45", "name": "13:45" }, { "id": "14:00", "name": "14:00" }, { "id": "14:15", "name": "14:15" }, { "id": "14:30", "name": "14:30" }, { "id": "14:45", "name": "14:45" }, { "id": "15:00", "name": "15:00" }, { "id": "15:15", "name": "15:15" }, { "id": "15:30", "name": "15:30" }, { "id": "15:45", "name": "15:45" }, { "id": "16:00", "name": "16:00" }, { "id": "16:15", "name": "16:15" }, { "id": "16:30", "name": "16:30" }, { "id": "16:45", "name": "16:45" }, { "id": "17:00", "name": "17:00" }, { "id": "17:15", "name": "17:15" }, { "id": "17:30", "name": "17:30" }, { "id": "18:00", "name": "18:00" }, { "id": "18:15", "name": "18:15" }, { "id": "18:30", "name": "18:30" }, { "id": "18:45", "name": "18:45" }, { "id": "19:00", "name": "19:00" },{ "id": "", "name": "ALL" }],
    originArm: [],
    destArm: [],
    classification: [],
    peak: [{ id: "AM", name: "<label>AM     <p>07:00-10:00</p></label>" }, { id: "IP", name: "<label>IP   <p>10:00-15:00</p></label>" }, { id: "PM", name: "<label>PM   <p>15:00-19:00</p></label>" }, { id: "ALL", name: "<label>ALL</label>" }]
    // observation: ["Test 1", "Test 2", "Test 3", "Test 3", "Test 4"]
}


let optionList = {
    project: "project-select-option-list",
    startTime: "start-time-select-option-list",
    endTime: "end-time-select-option-list",
    originArm: "origin-arm-select-option-list",
    destArm: "dest-arm-select-option-list",
    classification: "classification-select-option-list",
    peak: "peak-select-option-list",
    // observation: "observation-select-option-list"
}

let selectedValue = {
    project: "",
    startTime: "",
    endTime: "",
    originArm: "",
    destArm: "",
    classification: "",
    peak: ""
}
var selectedSiteValue = {
    name: '',
    id: '',
    lat: '',
    lon: '',
}

var selectedTurningCountSiteValue = {
    name: '',
    id: '',
    lat: '',
    lon: '',
    img:''
}


var jtc_toggler = false

if (jtc_toggler){
    toggle_jtc_menu(false);
    $('#jtc_toggler').prop('checked', false);
}
else{
    toggle_jtc_menu(false);
    $('#jtc_toggler').prop('checked', false);
}

if((localStorage.getItem("selectedSiteValue") && !jtc_toggler) || 
    (localStorage.getItem("selectedTurningCountSiteValue") && jtc_toggler)){  

    var SitejsonData = localStorage.getItem("selectedSiteValue");

    var SiteValue = JSON.parse(SitejsonData);
     selectedSiteValue = {
        name: SiteValue.name,
        id: SiteValue.id,
        lat: SiteValue.lat,
        lon: SiteValue.lon,
    }
}else{
    let jtc_site = document.querySelectorAll("#site-select-option-list li[data-obs='11']")[0];
    // let temp_site = document.querySelectorAll("#site-select-option-list li[data-obs='13']")[0];

    selectedSiteValue = {
        name: jtc_site.innerText,
        id: jtc_site.id,
        lat: jtc_site.getAttribute("lat"),
        lon: jtc_site.getAttribute("lon"),
    }
    // selectedTurningCountSiteValue = {
    //     name: temp_site.innerText,
    //     id: temp_site.id,
    //     lat: temp_site.getAttribute("lat"),
    //     lon: temp_site.getAttribute("lon"),
    //     img: temp_site.getAttribute("img")
    // }
    localStorage.setItem("selectedSiteValue", JSON.stringify(selectedSiteValue))
    // localStorage.setItem("selectedTurningCountSiteValue", JSON.stringify(selectedTurningCountSiteValue))
}

let wrapperList = {
    project: "project-select-wrapper",
    site: "site-select-wrapper",
    // observation: "observation-select-wrapper",
    classification: "classification-select-wrapper",
    destArm: "dest-arm-select-wrapper",
    originArm: "origin-arm-select-wrapper",
    endTime: "end-time-select-wrapper",
    startTime: "start-time-select-wrapper",
    peak: "peak-select-wrapper"
}

let selectBtnList = {
    peak: { id: "peak-select-btn", name: "Network Peak" },
    classification: { id: "classification-select-btn", name: "ALL" },
    destArm: { id: "dest-arm-select-btn", name: "ALL" },
    originArm: { id: "origin-arm-select-btn", name: "ALL" },
    endTime: { id: "end-time-select-btn", name: "All" },
    startTime: { id: "start-time-select-btn", name: "All" },
    project: { id: "project-select-btn", name: "Project Name" }
}

let inputList = {
    peak: "peak-select-input",
    site: "site-select-input",
    classification: "classification-select-input",
    destArm: "dest-arm-select-input",
    originArm: "origin-arm-select-input",
    endTime: "end-time-select-input",
    startTime: "start-time-select-input",
    project: "project-select-input"
}

$("#jtc_toggler").click( function(){
    // var flg = $('#jtc_toggler').is(":checked");
    // var site = null
    // if (flg && localStorage.getItem("selectedTurningCountSiteValue")){
    //     site = JSON.parse(localStorage.getItem("selectedTurningCountSiteValue"))
    // }
    // else if (localStorage.getItem("selectedSiteValue")){
    //     site = JSON.parse(localStorage.getItem("selectedSiteValue"))
    // }
    

    // if (site){
    //     $(`#${site.id}`).click()
    // }
    // toggle_jtc_menu(flg)
});

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
        if (sec == "peak") {
            peakHoursCount(jtc_DataDetails,selectedLi.id)
        }else{
            if (["startTime", "endTime"].includes(sec) && selectedLi.innerText == 'ALL') {
                selectedValue[sec] = "";
            }else if (["originArm", "destArm"].includes(sec) && selectedLi.innerText == 'ALL') {
                selectedValue[sec] = "";
                $('.lg-table-top-text').text('Destination : Arm')
            }else{
                selectedValue[sec] = selectedLi.id;
                if(sec == 'destArm'){
                    var armsname = getArmNameById(location_details.arms,selectedLi.id)
                    $('.lg-table-top-text').text('Destination : Arm ' +armsname)
                }
            }
            
            updateSelectedValues();
        }
        
    }

    addListData();
    addClassificationListData(sec,selectedValue[sec]);

    $("#lg-table").css("display", "none");
    $('#calender-content').addClass("calender-content");
    $('.box01').removeClass("td-active");

    AppendJtcCountdata(jtc_DataDetails, selectedValue, sec);

    if (url.includes('jtc-volume')) {
        VehicleChartData(jtc_data, selectedValue);
        numberOfVehicleChart(jtc_data, selectedValue);
    }

    if (["originArm", "destArm"].includes(sec)) {
        xyandmapdatahighlight(selectedValue);
    }
}

function updateSiteName(selectedLi) {
    if(document.getElementById(inputList["site"]).value != ''){
        document.querySelectorAll("#site-select-option-list li").forEach(item => {
           item.classList.remove("d-none")
        })
    }
    document.getElementById(inputList["site"]).value = "";

    document.querySelectorAll("#site-select-option-list li").forEach(item => {
        if (item.lastElementChild) {
            item.removeChild(item.lastElementChild)
            item.classList.remove("dd-isSelected")
        }
    })
    selectedSiteValue.name = selectedLi.innerText
    selectedSiteValue.id = selectedLi.id
    selectedSiteValue.lat = selectedLi.getAttribute("lat")
    selectedSiteValue.lon = selectedLi.getAttribute("lon")
    // if ($('#jtc_toggler').is(":checked")){
    //     localStorage.removeItem("selectedTurningCountSiteValue");
    //     localStorage.setItem("selectedTurningCountSiteValue",JSON.stringify(selectedSiteValue))
    // }
    // else{
        localStorage.removeItem("selectedSiteValue");
        localStorage.setItem("selectedSiteValue",JSON.stringify(selectedSiteValue))
    // }
    selectedLi.classList.add("dd-isSelected")
    let i = document.createElement("i")
    i.classList.add("fa-solid")
    i.classList.add("fa-check")
    i.style.fontSize = "16px"
    i.style.color = "#25d125"
    selectedLi.appendChild(i)

    loadLocation(selectedSiteValue.id).then(function () {
        // if ($('#jtc_toggler').is(":checked")){
        //     $('#myImg').attr('src',location_details.imgURL)
        // }
        listData.project = [...location_details.project]
        listData.originArm = [...location_details.arms]
        listData.destArm = [...location_details.arms]
        listData.classification = [...location_details.classes]

        selectedValue = {
            project: listData.project[0].id,
            startTime: "",
            endTime: "",
            originArm: "",
            destArm: "",
            classification: "",
            site: "",
            peak: ""
        }

        addListData()

        document.getElementById("site-select-btn").firstElementChild.innerText = selectedSiteValue.name;

        document.getElementById("project-select-btn").firstElementChild.innerText =  listData.project[0].name
        
        Object.keys(selectBtnList).forEach(key => document.getElementById(selectBtnList[key].id).firstElementChild.innerText = selectBtnList[key].name)

        loadJtcData(selectedSiteValue.id, selectedValue.project, selectedValue.originArm, selectedValue.destArm).then(function () {
            AppendJtcCountdata(jtc_data.data,selectedValue,'');
            if (url.indexOf('jtc-volume') !== -1) {
                VehicleChartData(jtc_data,selectedValue);
                numberOfVehicleChart(jtc_data,selectedValue);
            }
        })
        try{
            setSidebarLocInfo(selectedSiteValue.name, selectedSiteValue.lat, selectedSiteValue.lon);
        }
        catch(e){
            console.log(e)
        }
    }).then( function(){
        $.when(addListData()).then(function(){
            let project_text = $('#project-select-option-list .dd-isSelected').text() ;
            $('#project-select-btn span').text(project_text);
        });
    })
}

loadLocation(selectedSiteValue.id).then(function () {
    // if ($('#jtc_toggler').is(":checked")){
    //     $('#myImg').attr('src',location_details.imgURL)
    // }
    listData.project = [...location_details.project]
    listData.originArm = [...location_details.arms].sort((a, b) => a.id - b.id);
    listData.destArm = [...location_details.arms]
    listData.classification = [...location_details.classes]
    selectedValue.project = listData.project[0].id
    selectedValue.originArm = '';
    selectedValue.destArm = '';
    document.getElementById(selectedSiteValue.id).classList.add("dd-isSelected");
    // document.querySelectorAll("#site-select-option-list li")[0]
    let i = document.createElement("i")
    i.classList.add("fa-solid")
    i.classList.add("fa-check")
    i.style.fontSize = "16px"
    i.style.color = "#25d125"
    document.getElementById(selectedSiteValue.id).appendChild(i)
    addListData()
    document.getElementById(selectBtnList.project.id).firstElementChild.innerText = listData.project[0].name
    // document.getElementById(selectBtnList.originArm.id).firstElementChild.innerText = listData.originArm[0].name
    // document.getElementById(selectBtnList.destArm.id).firstElementChild.innerText = listData.destArm[0].name
    document.getElementById("site-select-btn").firstElementChild.innerText = selectedSiteValue.name
    console.log('here2')

    loadJtcData(selectedSiteValue.id, selectedValue.project).then(function () {
        AppendJtcCountdata(jtc_data.data,selectedValue,'');
        if (url.indexOf('jtc-volume') !== -1) {
            VehicleChartData(jtc_data,selectedValue);
            numberOfVehicleChart(jtc_data,selectedValue);
        }
    })
    setSidebarLocInfo(selectedSiteValue.name, selectedSiteValue.lat, selectedSiteValue.lon)
})


function loadLocation(id){
    let formData = new FormData()
    formData.append("location_id", id)
  
    return fetcher(formData, "getLocations", function (response) {
        location_details = response;
        createArmHeader(location_details.arms,location_details.project[0].id);
        createModalpoputable(location_details.classes);

        armsData = response.arms;
        var pathname = new URL(url).pathname;
       
        if (pathname !== '/aecon/jtc-data/jtc-volume') {
            map.setView([location_details.locations.features[0].geometry.coordinates[1], location_details.locations.features[0].geometry.coordinates[0]], 18);
    
            map.eachLayer(function (layer) {
              if (layer instanceof L.Marker) {
                map.removeLayer(layer);
              }
            });

            removeMarkersForArm();
            armsData.forEach((arm, index) => {
                if (location_details.project[0].id == arm.project) {

                    initMapWithDetails([location_details.locations.features[0].geometry.coordinates[1], location_details.locations.features[0].geometry.coordinates[0]], index, arm.id, location_details.project[0].id);
                }
            });
            
        }
       
    })
    
  }

  function loadJtcData(siteId,projectId){
        let formData = new FormData()
        formData.append("location_id",siteId)
        formData.append("project_id",projectId)

        return fetcher(formData, "get_jtc_data", function (response) {
            jtc_data = response;
            jtc_DataDetails = jtc_data.data;
            
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
        if(sec == 'classification'){
            return `<li onclick="updateName(this,'${sec}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" style="justify-content: start;" id="${data.id}"><div class="col-9 px-0 classification-option"><span class="red-box ${data.name}"></span>${data.name}</div>${isSelected ? "<i class='fa-solid fa-check'  style='color:#25d125;font-size:16px;'></i>" : ""}</li>`;
        }else if (sec == "originArm" || sec == "destArm") {
            if(data.project == selectedValue.project){
                return `<li onclick="updateName(this,'${sec}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" id="${data.id}">${data.name}${isSelected ? "<i class='fa-solid fa-check'  style='color:#25d125;font-size:16px;'></i>" : ""}</li>`;
            }
        }else{
            return `<li onclick="updateName(this,'${sec}')" class="${isSelected ? 'dd-isSelected' : ''} dd-list" id="${data.id}">${data.name}${isSelected ? "<i class='fa-solid fa-check'  style='color:#25d125;font-size:16px;'></i>" : ""}</li>`;
        }
    }).join("");
    if(searchWord == '' && sec == 'classification'){
        arr += `<li onclick="updateName(this,'${sec}')" class="dd-list" style="justify-content: start;" id="All"><div class="col-9"><span class="red-box All"></span>ALL</div></li>`;
    }else if(searchWord == '' && (sec == 'originArm' || sec == 'endTime')){
        arr += `<li onclick="updateName(this,'${sec}')" class="dd-list"  id="All">ALL</li>`;

    }
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

peakSelectBtn.addEventListener("click", (e) => {
    e.stopPropagation()
    Object.keys(wrapperList).forEach(item => {
        if (item == "peak") {
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


function updateprojectName(selectedLi, sec) {
    document.getElementById(inputList[sec]).value = "";
    selectedValue[sec] = selectedLi.id
    addListData()
    document.getElementById(wrapperList[sec]).classList.remove("active")
    document.getElementById(selectBtnList[sec].id).firstElementChild.innerText = selectedLi.innerText;
    
    $("#lg-table").css("display", "none");
    $('#calender-content').addClass("calender-content");
    $('.box01').removeClass("td-active");

    createArmHeader(location_details.arms,selectedValue.project);
    createModalpoputable(location_details.classes);
    if (!url.includes('jtc-volume')) {
        removeMarkersForArm();
    }
    
    location_details.arms.forEach((arm, index) => {
        if (selectedValue.project == arm.project) {
            if (url.includes('jtc-headline') || url.indexOf('jtc-data') ) {
                initMapWithDetails([location_details.locations.features[0].geometry.coordinates[1], location_details.locations.features[0].geometry.coordinates[0]], index, arm.id, selectedValue.project);
            }
        }
    });

    loadJtcData(selectedSiteValue.id, selectedValue.project).then(function () {
        AppendJtcCountdata(jtc_data.data,selectedValue,'');
        if (url.indexOf('jtc-volume') !== -1) {
            VehicleChartData(jtc_data,selectedValue);
            numberOfVehicleChart(jtc_data,selectedValue);
        }
    })

}
// Function to check if an element contains a certain text
function containsText(element, text) {
    return element.textContent.trim().includes(text);
}


function peakHoursCount(jtc_DataDetails, id) {
    selectedValue.peak = id;
    document.getElementById('peak-select-btn').firstElementChild.innerText = id;
    if(id != 'ALL'){
        const timeSlotCounts = {}; // Create an object to store total counts for each time slot

        // Iterate through the data to accumulate counts for each time slot
        jtc_DataDetails.forEach(({ value }) => {
            value.forEach(({ Start_time, End_time, class: classDetails }) => {
                if (isSelectedPeakValue(id, { Start_time, End_time, class: classDetails })) {
                    classDetails.forEach(({ count }) => {
                        // Calculate the start time of the time slot (round down to 15 minutes)
                        const startTime = roundDownTo15Minutes(Start_time);

                        // Initialize the total count for the time slot if not already initialized
                        timeSlotCounts[startTime] = timeSlotCounts[startTime] || 0;

                        // Accumulate the count for the time slot
                        timeSlotCounts[startTime] += count;
                    });
                }
            });
        });

        // Find the time slot with the highest total count within the specified range
        let peakTimeSlot;
        let peakTotalCount = -1;
        Object.entries(timeSlotCounts).forEach(([timeSlot, totalCount]) => {
            
            if (totalCount > peakTotalCount) {
                peakTimeSlot = timeSlot;
                peakTotalCount = totalCount;
            }
        });

        if (peakTimeSlot !== undefined) {
            const endTime = calculateEndTime(peakTimeSlot);
            selectedValue.startTime = peakTimeSlot;
            selectedValue.endTime = endTime;
            addListData();
            
            document.getElementById(selectBtnList.startTime.id).firstElementChild.innerText = peakTimeSlot;
            document.getElementById(selectBtnList.endTime.id).firstElementChild.innerText = endTime;
        } else {
            console.log("Unable to determine peak hour. No valid time slot found within the specified peak time.");
        }
    }else{
        selectedValue.startTime = '07:00';
        selectedValue.endTime = '19:00';
        addListData();
        
        document.getElementById(selectBtnList.startTime.id).firstElementChild.innerText = '07:00';
        document.getElementById(selectBtnList.endTime.id).firstElementChild.innerText = '19:00';
    }
}

function roundDownTo15Minutes(time) {
    const date = new Date(`2000-01-01T${time}`);
    const hours = String(date.getHours()).padStart(2, '0'); // Ensure two-digit hours
    const minutes = date.getMinutes();
    const roundedMinutes = Math.floor(minutes / 15) * 15;
    return `${hours}:${String(roundedMinutes).padStart(2, '0')}`;
}


function calculateEndTime(startTime) {
    const [hours, minutes] = startTime.split(':').map(Number);
    const endTime = new Date(2000, 0, 1, hours, minutes + 60); // Add 60 minutes for 1 hour

    const formattedHours = String(endTime.getHours()).padStart(2, '0');
    const formattedMinutes = String(endTime.getMinutes()).padStart(2, '0');

    return `${formattedHours}:${formattedMinutes}`;
}

function isSelectedPeakValue(id, value) {
    if (id != '') {
        if (id == 'AM' && value.Start_time >= '07:00' && value.End_time <= '10:00') {
            return true;
        } else if (id == 'IP' && value.Start_time >= '10:00' && value.End_time <= '15:00') {
            return true;
        } else if (id == 'PM' && value.Start_time >= '15:00' && value.End_time <= '19:00') {
            return true;
        }else if(id == 'ALL'){
            return true;
        }
    }
    return false;
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


function getArmNameById(arms, armId) {
    const selectedArm = arms.find(arm => arm.id == armId);

    if (selectedArm) {
        armname = selectedArm.name +' '+ selectedArm.Fullname
        return armname;
    } else {
        return null; 
    }
}

function toggle_jtc_menu(flg){
    // if (flg){
    //     $('#overview').hide();
    //     $('#jtc-upload').attr('onclick', "location.href = '/aecon/jtc-turning-count-upload';");
    //     $('#jtc_img').show();
    //     $('#site-select-option-list [data-obs="11"]').hide();
    //     $('#site-select-option-list [data-obs="13"]').show();

    // }
    // else{
        $('#overview').hide();
        $('#jtc-upload').attr('onclick', "location.href = '/aecon/jtc-upload';");
        $('#jtc_img').hide();
        $('#site-select-option-list [data-obs="11"]').show();
        $('#site-select-option-list [data-obs="13"]').hide();
    // }
    localStorage.setItem("jtc_toggler", false);
}