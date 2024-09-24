function tabContent(type,flg=""){
        var id_list = {"Headline":"sensor-headata",
                        "Volumes":"sensor-trafficvol",
                        "Classification":"sensor-classify",
                        "Comparsion":"sensor-download",
                        "Analysis":"sensor-analysis",
                      }
        var class_lst = ['compIcon','singleNumber']
        var keys = Object.keys(id_list);
        for (let i=0;i<keys.length;i++)
        {
          if (type == keys[i] && type !="" ){
          // $("#"+keys[i]).show();
            window.location.href ="/worcester/sensor-data/"+id_list[keys[i]]
          }
          else if (flg !="", flg == id_list[keys[i]])
          {
            document.getElementById(keys[i]).classList.add("active");
          }
        }
      }
tabContent("",'{{flg}}')
    function addSite(content,id){
    var tbody = document.getElementById("selected-table").getElementsByTagName("tbody")[0];
    var tr = document.createElement("tr");
    tr.id = "selected_" + id
    var td = document.createElement("td");
    td.innerText = content;
    tr.appendChild(td);
    tr.onclick  = function(e) {
            removeSite(tr);
            document.getElementById(id).classList.remove("selected");
        };
    tbody.appendChild(tr);

    document.getElementById("myField").value = getIds();
}

function getIds() {
    var ids = [];
    var selected = document.getElementById("selected-table").getElementsByTagName("tbody")[0].querySelectorAll('tr');
    var length = selected.length;
    for (var i=0;i< selected.length;i++){
            var myarray = selected[i].id.split("_");
            ids.push(myarray[1]);
    }
    return JSON.stringify(ids);
}

function getClasses() {
    var classes = [
    '1','2','3', '4', '5', '6','7', '8', '9', '10', '11', '12',
    '13', '14', '15', '16', '167', '168', '169', '170', '171', '172',
    '173', '174', '3034', '3035','3036','3037','3038', '43071', '43072',
    '43073', '43074', '43075', '43097', '43098', '43099', '43100', '43101',
    '43102', '43103', '43104', '43105', '43106', '43107', '43108', '43109',
    '43110', '43111', '43112', '43113' ,'43114' ,'43115' ,'43116', '43117', '43118'
    ];
    return JSON.stringify(classes);
}

    document.getElementById("myCField").value = getClasses();


function clearAllSites(){
    console.log("clearing all sites");
    var tbody = document.getElementById("selected-table").getElementsByTagName("tbody")[0];
    tbody.innerHTML = "";
}

function selectAllSites(){
    console.log("selecting all");

    location_items = document.querySelectorAll('#atcList');
    console.log(location_items);
    location_items.forEach(function(ele) {
        var inputs = ele.querySelectorAll('input');
        var value;
        for (value of inputs.values()) {
            console.log(value.id);
            addSite(value.value, value.id);
        }
    });

//    for(var i=0;i<sites.length;i++){
//        if(sites){
//            addSite(sites[i].getAttribute("data-content"),sites[i].getElementsByTagName("a")[0].id);
//            sites[i].getElementsByTagName("a")[0].classList.add("selected");
//        }
//    }
}


function toggleSidebarFunctionality(){
        if(userGuideActive){toggleUserGuide();}
        if (downloadActive){
            if(!sidebarMulti){
                document.getElementById("sidebar").classList.remove("multi");
            }
            downloadActive = false;
            $('#exampleModalCenter').modal('hide');
            //document.getElementById("main-container-greyed-out").classList.add("d-none");
            unpinSideBar();
            var leaves = document.getElementById("sidebar").getElementsByClassName("leaf");
            for (var i=0;i<leaves.length;i++){
                leaves[i].getElementsByTagName("a")[0].classList.remove("selected");
            }
            for (var i=0;i<selectedSites.length;i++){
                selectedSites[i].classList.add("selected");
            }
            document.getElementById("sidebar").getElementsByClassName("sidebar-brand-button")[0].onclick = toggleSideBar;
            return;}
        else{
            //document.getElementById("main-container-greyed-out").classList.remove("d-none");
            $('#exampleModalCenter').modal('show');
            pinSideBar();
            sidebarMulti = document.getElementById("sidebar").classList.contains("multi");
            document.getElementById("sidebar").classList.add("multi");
            selectedSites = [];
            var sites = document.getElementById("sidebar").getElementsByClassName("selected");
            for (var i=0;i< sites.length;i++){
                selectedSites.push(sites[i]);
            }
            var leaves = document.getElementById("sidebar").getElementsByClassName("leaf");
            downloadActive = true;
            document.getElementById("sidebar").getElementsByClassName("sidebar-brand-button")[0].onclick = function(){};
        }
}

function addSelected(id) {
   document.getElementById(id+"_radio").classList.add("selected");
}