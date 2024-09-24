// ash-task 2:(2) problem: make "Download" tab have green line beneath it upon clicking it in "Sensor Data" section.
// added logic for "Download" tab, and specific condition since download page url doesn't have "/sensor-data/" in its url
function tabContent(type,flg=""){
        var id_list = {"Headline":"sensor-headata",
                        "Volumes":"sensor-trafficvol",
                        "Classification":"sensor-classify",
                        "Comparsion":"sensor-download",
                        "Analysis":"sensor-analysis",
                        "Download":"download-view",
                      };
        var class_lst = ['compIcon','singleNumber'];
        var keys = Object.keys(id_list);
        for (let i=0;i<keys.length;i++)
        {
          if (type == keys[i] && type !="" ){
          // $("#"+keys[i]).show();
            if (keys[i] != "Download"){
                var base_url = "/aecon/sensor-data/";
            } else{
                var base_url = "/";
            }
            window.location.href = base_url+id_list[keys[i]];
          }
          else if (keys[i] == "Download" || flg !="" && flg == id_list[keys[i]]) {
            document.getElementById(keys[i]).classList.add("active");
          }
        }
}

// apparently, calling onclick="tabContent('Download'); is not enough.
// tabContent has to be also called here
// i do not know why this is the case...
tabContent("",'{{flg}}')

// ash-task 3:(2) problem: checkboxes are not working properly: when de-selecting a location, checkbox is kept, and it is added again to table on the right section of the page
// changed addSite() and addSelected() logics and they are now called only by toggleSite()
// also changed logic of clearAllSites() and selectAllSites() to reflect the changes done to functions above
function toggleSite(content,id){

    if (id.includes("_radio")){
        var id_with_radio = id;
        id = id.split("_")[0];
    } else {
        var id_with_radio = id + "_radio";
    }
    var is_checkbox_selected = (document.getElementById(id_with_radio).classList.contains('selected'));
    if (!is_checkbox_selected) {
        addSite(content,id);
    } else {
        removeSite(id);
    }
}

function removeSite(id){
    // removing element from selected table
    ele = document.getElementById("selected_"+id);
    ele.parentNode.removeChild(ele);
    // removing "selected" class from classList of the de-selected location
    document.getElementById(id+"_radio").classList.remove("selected");
}

function addSite(content,id){
    var tbody = document.getElementById("selected-table").getElementsByTagName("tbody")[0];
    var tr = document.createElement("tr");
    tr.id = "selected_" + id
    var td = document.createElement("td");
    td.innerText = content;
    tr.appendChild(td);
    tbody.appendChild(tr);

    document.getElementById("myField").value = getIds();

    document.getElementById(id+"_radio").classList.add("selected");
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
    if (tbody.innerHTML == ""){
        return;
    }
    var trs = tbody.querySelectorAll('tr');
    trs.forEach((tr) => {
        var location_id = tr.id.split("_")[1];
        var location_name = tr.querySelector('td').innerText;
        toggleSite(location_name, location_id)
    })
}

function selectAllSites(){
  console.log("selecting all");

  location_items = document.querySelectorAll('#atcList');
  console.log(location_items);
  location_items.forEach(function(ele) {
      var inputs = ele.querySelectorAll('option');
      var value;
      for (value of inputs.values()) {
          console.log(value.id);
          toggleSite(value.value, value.id);
      }
  });

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