

var selectedDate;
var comparisonChart;

function toggleHiddenFields(ele){
    var id = ele.id;
    var value = ele.value;
    var hiddenFields = document.querySelectorAll("[data-dependency='" + id  + "']");
    for(var i=0;i<hiddenFields.length;i++){
        hiddenFields[i].getAttribute("data-value")
        hiddenFields[i].classList.add("d-none");
        if (hiddenFields[i].getAttribute("data-value") == value){
            hiddenFields[i].classList.remove("d-none");
        }
    }
}


var items = document.getElementsByClassName("toggle-fields");
for(var i=0;i<items.length;i++){
    items[i].addEventListener("click",function(ele){
                                                   return function(){
                                                   toggleHiddenFields(ele)}
                                                }(items[i]));
}


function testAPI(){
    var form = document.getElementById("api-form");
    if (!form){
        return;
    }
    var formData = new FormData(form);
    fetcher(formData,"testAPI",function(result){
        if(result.data){
            document.getElementById("json-container").innerText = result.data;
        }
        if(result.message){
             alert(result.message);
        }
    });
}


function saveLocationClasses(){
    var formData = new FormData(document.getElementById("location-form"));
    var classes = [];
    var selected = document.getElementById("selected-obsclass-container").getElementsByTagName("div");
    for (var i=0;i<selected.length;i++){
        classes.push(selected[i].id.replace("selected-class-",""))
    }
    formData.append("classes",JSON.stringify(classes));
    formData.append("csrfmiddlewaretoken",document.getElementsByName("csrfmiddlewaretoken")[0].value)
    fetcher(formData,"",function(result){
        if(result.message){
            alert(result.message);
        }
        updateClassContainers(result);
    });
}


function saveLocation(action){
    var formData = new FormData(document.getElementById("location-form"));
    //formData.append("location_id",document.getElementById("locId").value);
    formData.append("csrfmiddlewaretoken",document.getElementsByName("csrfmiddlewaretoken")[0].value)
    if(document.getElementById("locId").readOnly){
        var action="update";
    }
    else{
        var action= "create";
    }
    formData.append("action",action);
    directionLines = [];
    flag = false;
    if(lineLayer){
        lineLayer.eachLayer(function(layer){
            console.log("looking at ",layer);

            //console.log("line coords are",layer.getLatLngs());
            if(layer.arrowHead){
                if(layer.options.order >=0 && layer.options.direction){
                    feature = layer.toGeoJSON();
                    feature.properties.direction = layer.options.direction;
                    feature.properties.order = layer.options.order;
                    directionLines.push(feature);
                    console.log("adding direction",feature);
                }
                else{
                    flag=true;
                }
            }
        });
    }
    if(flag){
        alert("You have added a line, but havent assigned a direction or index");
        return;
    }
    if (!marker){
        alert("You need to select a lat/lon for this site");
        return;
    }
    formData.append("marker",JSON.stringify(marker.toGeoJSON()));
    formData.append("directions",JSON.stringify(directionLines));
    fetcher(formData,"admin/saveLocation",function(result){alert(result.message);});


}


function saveVivacityAPI(action){
    var formData = new FormData(document.getElementById("api-form"));
    formData.append("csrfmiddlewaretoken",document.getElementsByName("csrfmiddlewaretoken")[0].value)
    formData.append("action",action);
    fetcher(formData,"saveVivacityAPI",function(result){alert(result.message);});
}


function updateLabel(event){
    console.log(event);
    label = document.querySelector("label[for=" + event.target.id + "]");
    if (label){
        label.innerText = event.target.files[0].name;
    }
}


function updateClassContainers(result){
    console.log("filling with",result.data);
    document.getElementById("obsclass-container").innerHTML = result.data;
    console.log("updating class containers")
    var items = document.getElementById("obsclass-container").getElementsByClassName("menu-item");
    console.log("here");
    for(var i=0;i<items.length;i++){
        items[i].addEventListener("click",MenuItemToggleDelegate(items[i]));
        items[i].addEventListener("click",toggleSelectedClass);
        items[i].addEventListener("click",saveLocationClasses);
    }
    console.log("now here");
    displayOrderedClasses(result.orderedClasses);
    document.getElementById("obsclass-group-container").innerHTML = result.groups;

}


function displayOrderedClasses(orderedClasses){
    var selectedContainer = document.getElementById("selected-obsclass-container");
    selectedContainer.innerHTML = "";
    for(var i=0;i<orderedClasses.length;i++){
        var row = addClassRow(orderedClasses[i].id,orderedClasses[i].displayName)
        selectedContainer.appendChild(row)
    }

}


function toggleSelectedClass(event){
    var selectedContainer = document.getElementById("selected-obsclass-container");
    var id = this.id;
    var row = document.getElementById("selected-class-" + id);
    if(row){
        row.parentNode.removeChild(row);
    }
    else{
        var row = addClassRow(id,this.getElementsByTagName("a")[0].innerText);
        selectedContainer.appendChild(row);
    }
}


function applyGroup(ele){
    var formData = new FormData()
    formData.append("group",ele.id.replace("group-",""));
    formData.append("location_id",document.getElementById("locId").value);
    fetcher(formData,"applyGroup",function(result){
                        updateClassContainers(result);
                    });
}


function clearClasses(){
    document.getElementById("selected-obsclass-container").innerHTML = "";
    saveLocationClasses();
}


function addClassRow(id,name){
    var row = document.createElement("div");
    row.id = "selected-class-" + id;
    row.classList.add("selected-class");
    var a = document.createElement("a");
    row.appendChild(a);
    a.innerText = name;
    row.setAttribute('draggable', true);
    row.style.cursor="pointer";
    row.addEventListener('dragstart', function(e) {
      e.dataTransfer.setData("text", e.target.id);
      }, false);
    row.addEventListener('ondrop',function(e) {

      }, false);

     row.ondragover = function(e) {

      e.preventDefault();

      };
      row.ondrop = function(e){ dropClass(this);};
      return row;
}


function dropClass(targetZone){
    var selectedItem = event.dataTransfer.getData("text");
    selectedItem = document.getElementById(selectedItem);
    //console.log("selected Item was",selectedItem);
    //console.log("dropping onto",targetZone);
    event.preventDefault();
    var orderedClasses = [];
    var cl = document.getElementById("selected-obsclass-container").getElementsByTagName("div");
    for(var i=0;i<cl.length;i++){
        //console.log(cl[i].id,targetZone.id,selectedItem.id);
        if (cl[i].id == targetZone.id){
            orderedClasses.push({"id":selectedItem.id.replace("selected-class-",""),"displayName":selectedItem.getElementsByTagName("a")[0].innerText});
        }
        if (cl[i].id != selectedItem.id){
            orderedClasses.push({"id":cl[i].id.replace("selected-class-",""),"displayName":cl[i].getElementsByTagName("a")[0].innerText});
        }
    }
    //console.log("ordered classes is",orderedClasses);
    displayOrderedClasses(orderedClasses);
    saveLocationClasses();
    return;
}


function uploadData(d){
    var input = document.createElement('input');
    input.type = 'file';
    input.setAttribute("multiple",true);
    input.onchange = e => {
        console.log(e.target.files);
       var files = e.target.files;
       for (var i = 0; i < files.length; i++) {
              var formData = new FormData();
               formData.append("data-file",files[i]);
               formData.append("startDate",d);
               formData.append("location_id",document.getElementById("locId").value);
               fetcher(formData,"uploadLocationData",function(result){
                                console.log(result.status);
                                addMessage(result.message,result.status);

                            });
               }

    }
    input.click();

}


function addMessage(msg,icon,col){
    var div = document.createElement("div");
    div.classList.add("conduit-notification");
    var icondiv = document.createElement("div");
    icondiv.classList.add("conduit-notification-icon")
    div.appendChild(icondiv);
    var i = document.createElement("i");
    i.style.color = col;
    //i.classList.add("far");
    i.classList.add(icon);
    icondiv.appendChild(i);
    var dets = document.createElement("div");
    dets.classList.add("conduit-notification-details");
    div.appendChild(dets);
    var title = document.createElement("div");
    title.classList.add("conduit-notification-details-title")
    dets.appendChild(title);
    title.innerText = msg;
    var d = document.createElement("div");
    dets.appendChild(d);
    d.innerText = "01/05/2019";
    d.classList.add("conduit-notification-details-date")
    document.getElementById("messages-popup").appendChild(div);
}

var calendarData;


function getCalendarData(year, toggle){

     var formData = new FormData();
    formData.append("location_id",document.getElementById("locId").value);
    formData.append("year",year);
    fetcher(formData,"getLocationDataCounts",function(result){
        console.log("result is", result.result.data);
        calendarData = result.result;
        fillCalendar(toggle);
    });

}


function fillCalendar(toggle){


    var months = document.getElementById("calendar-wrapper").getElementsByClassName("month-container");
    for(var i=0;i<calendarData.data.length;i++){
        var d = moment(calendarData.data[i][0])
        //console.log("processing", calendarData.data[i], d, d.month() - 1)
        var selectedMonth = document.querySelectorAll("[data-month-id='" + d.month()   + "']")[0];
        //console.log("selected month is", selectedMonth)
        //console.log("selected day is", d.date())

        var cell = selectedMonth.querySelectorAll('.day:not(.old):not(.new)')[d.date() -1];
        //console.log("cell is", cell)
        var val = calendarData.data[i][1];

        //var status = calendarData.data[i+1][d+1]["status"];
        //var removed = calendarData.data[i+1][d+1]["removed"];
        var text = "Total count: " + val + "\n"
        if (!val){
            col = "white";
        }
        else{
            if(toggle=="off"){
                var col = getGreenToRed(val*100/calendarData.max);
            }
            else{
                var col = getGreenToRed((calendarData.data[i][2] ) * 100);
                text = text + parseInt((1 - calendarData.data[i][2]) * 100) + "% of days are more normal than this day"
            }

            console.log("col is now", col)
        }
        //console.log("val is", val," color is", col)
        cell.style.backgroundColor = col;
        //if(status == 1){
        //   cells[d].classList.add("bad-data");
        //}
        //else{
        //    cells[d].classList.remove("bad-data");
        //}
        //if(removed == 1){
        //    cells[d].classList.add("removed-data");
        //}
        //else{
        //    cells[d].classList.remove("removed-data");
        //}

        cell.setAttribute("data-toggle","tooltip")
        cell.setAttribute("data-placement", "top")
        cell.setAttribute("title", text)
        cell.classList.add("calendar-popup-trigger");
        cell.addEventListener("click",function(id,ele){
                               return function(){showPopup(id,ele)}
                            }("calendar-popup",cell));


    }
    $('.popover').remove();
    $(function () {
      $('[data-toggle="popover"]').popover({ trigger: "hover",container:"body",placement:"top" })
    })






}


function viewFullDay(selectedDate){
    console.log ( "IN BIEW FULL DAYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
    if (comparisonChart){
        comparisonChart.destroy();
    }
    var formData = new FormData();
    formData.append("location_id",document.getElementById("locId").value);
    formData.append("date",moment(selectedDate).format("YYYY-MM-DD"));
    //console.log("selected date is",selectedDate);
    fetcher(formData,"getLocationDataCountsHourly",function(result){
                        //console.log("received back result",result);
                        var rows = document.getElementById("daily-table").getElementsByTagName("tr");

                        comparisonChart = createLineChart(document.getElementById("daily-comparison-graph"),result.chart);
                        for(var i=1;i<rows.length;i++){
                            rows[i].cells[1].innerText = result.chart.datasets[0]["data"][i-1];
                            rows[i].cells[2].innerText = result.chart.datasets[1]["data"][i-1];
                            if(result.data[i-1].status == 1){
                                rows[i].classList.add("bad-data");
                            }
                            else{
                                rows[i].classList.remove("bad-data");
                            }
                            if(result.data[i-1].removed == 1){
                                rows[i].classList.add("removed-data");
                            }
                            else{
                                rows[i].classList.remove("removed-data");
                            }
                        }

    })
    hidePopup("calendar-popup");

}


function closeFullDay(){
    document.getElementById("day-wrapper").classList.add("d-none");
    document.getElementById("calendar-wrapper").classList.remove("d-none");
}


function dailyPopupBadDataClicked(){
    var item = document.getElementById("daily-popup").currentItem;
    var hour = item.getAttribute("data-hour");
    userToggleBadData(selectedDate,hour);
}


function calendarPopupBadDataClicked(){
    userToggleBadData(selectedDate,null);
}



function userToggleBadData(date,hour){
    var formData = new FormData();
    formData.append("location_id",document.getElementById("locId").value);
    formData.append("date",moment(date).format("YYYY-MM-DD"));
    formData.append("hour",hour);
    fetcher(formData,"toggleBadData",function(result){console.log("received results",result);if(result.status == "ok"){
                                viewFullDay();
                                if(calendar){
                                    console.log("found calendar",calendar);
                                    calendar.render();
                                }
                                hideAllPopups();}


    });
}


function viewSite(id){


}


function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function cookieToDict(cookie){

        if(!cookie || cookie == ""){return {}}
        var items = cookie.split("&");
        //console.log("items are",items);
        var dict = {};
        for (var i=0;i<items.length;i++){
            if (items[i] != ""){
                var s = items[i].split("=");
                var key = s[0];
                var val = s[1].split(",");
                if (val == ""){val = [];}
                //console.log("key",key,"val",val,val=="");
                dict[key] = val;
            }
        }
        return dict;
}


function saveSettings(){

        var filters = {}
        filters["acceptable"] = document.getElementById("acceptable").value;
        filters["unacceptable"] = document.getElementById("unacceptable").value;
        filters["medium"] = document.getElementById("medium").value;
        text = "";
        for (var key in filters){
            data = filters[key];
            text = text + key + "=" + data.toString() + "&"
        }
        console.log("text is",text)
        document.cookie="userSettings=" + text
    }

function editSettings(){
    console.log("saving!!!")
    saveSettings();
    loadSettings();
    applySettings();
}

function getThresholdClass(val){
    filters = getCookie("userSettings")
    filters = cookieToDict(filters);
    //console.log("fiolters are", filters)
    //console.log("looking at value", val)
    var thresholds = []
    if (filters["acceptable"] == "" || filters["acceptable"] == 0){
        return null
    }
    else{

        if ((val >= 100 - parseInt(filters["acceptable"])) && (val < 100 + parseInt(filters["acceptable"]))){
                return "acceptable"
        }


        if (filters["medium"] != "" && filters["medium"] != 0){
            if (((val >= 100 - parseInt(filters["medium"])) && (val < 100 - parseInt(filters["acceptable"])))  ||
                ((val >= 100 + parseInt(filters["acceptable"])) && (val < 100 + parseInt(filters["medium"])))){
                    return "medium"
            }
        }
        return "unacceptable"
    }

}

function loadSettings(){
    filters = getCookie("userSettings")
    filters = cookieToDict(filters);
    console.log("fiolters are", filters)

    var eles = document.getElementById("settings-popup").getElementsByClassName("col-11")
    var labels = document.getElementById("settings-popup").getElementsByTagName("label")
    for (var i=0;i<eles.length;i++){
        eles[i].classList.remove("d-none")
        eles[i].classList.add("d-flex")
    }
    if(document.getElementById("acceptable")){
        document.getElementById("acceptable").value = filters["acceptable"]
    }
    if(document.getElementById("medium")){
        document.getElementById("medium").value = filters["medium"]
        if (filters["acceptable"] == "" || filters["acceptable"] == 0){
            eles[2].classList.remove("d-flex")
            eles[2].classList.add("d-none")
            eles[3].classList.remove("d-flex")
            eles[3].classList.add("d-none")
        }
    }
    if(document.getElementById("unacceptable")){
        document.getElementById("unacceptable").value = filters["unacceptable"]
        if (filters["acceptable"] == "" || filters["acceptable"] == 0){
            eles[4].classList.remove("d-flex")
            eles[4].classList.add("d-none")
            eles[5].classList.remove("d-flex")
            eles[5].classList.add("d-none")
        }
    }
    if (filters["acceptable"] != "" && filters["acceptable"] != 0){
        var txt = 100 - parseInt(filters["acceptable"]) + "% - " + (100 + parseInt(filters["acceptable"])) + "%"
        labels[0].innerText = txt
        var val = parseInt(filters["acceptable"])
    }
    else{
        labels[0].innerText = "N/A"
        return;
    }
    if (filters["medium"] != "" && filters["medium"] != 0){
        var txt = 100 - parseInt(filters["medium"])  + "% - " + (100 - parseInt(filters["acceptable"])) + "% ,"
        txt = txt + (100 + parseInt(filters["acceptable"])) + "% - " + (100 + parseInt(filters["medium"])) + "% "
        labels[1].innerText = txt
        var val = parseInt(filters["medium"])
    }
    else{
        labels[1].innerText = "N/A"

    }

    var txt = "0% - " + (100 - val) + "%, "
    var txt = txt +(100 + val) + "%+ "
    labels[2].innerText = txt


}

function applySettings(){
    var table = document.getElementById("sensor-table")
    if(!table){return}
    var eles = document.querySelectorAll(".variance");
    for(var i=0;i<eles.length;i++){
        eles[i].classList.remove("acceptable", "medium", "unacceptable")
        eles[i].classList.add(getThresholdClass(eles[i].innerText))
    }


}

loadSettings();
//setToggleDatasetSelectorsListener(document.getElementsByClassName("class-selector-container")[0]);