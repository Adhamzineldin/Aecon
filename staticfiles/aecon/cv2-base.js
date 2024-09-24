

graphsDict = {};
var cntrlIsPressed = false;


$(document).keydown(function(event) {
    if (event.which == "17")
        cntrlIsPressed = true;
});

$(document).keyup(function() {
    cntrlIsPressed = false;
});

/*********************************************************************************************************


   Red to Green color gradient


*********************************************************************************************************/


function getGreenToRed(percent) {
    r = percent < 50 ? 255 : Math.floor(255 - (percent * 2 - 100) * 255 / 100);
    g = percent > 50 ? 255 : Math.floor((percent * 2) * 255 / 100);
    return 'rgb(' + r + ',' + g + ',0)';
}


function hsl_col_perc(percent, start, end) {
    var a = percent / 100,
        b = (end - start) * a,
        c = b + start;

    // Return a CSS HSL string
    return 'hsl(' + c + ', 100%, 50%)';
}



function perc2color(perc) {
    var r, g, b = 0;
    if (perc < 50) {
        r = 255;
        g = Math.round(5.1 * perc);
	}
	else {
        g = 255;
        r = Math.round(510 - 5.10 * perc);
    }
    var h = r * 0x10000 + g * 0x100 + b * 0x1;
    return '#' + ('000000' + h.toString(16)).slice(-6);
}

/*********************************************************************************************************


popups and menus


*********************************************************************************************************/


function showPopup(id, ele) {
    var popup = document.getElementById(id);
    //console.log("ele is",ele);
    hideAllPopups(id);
    if (popup) {
        if ((popup.style.top == "-1000px") || (popup.style.top == "") || (popup.currentItem && (popup.currentItem != ele))) {
            var br = ele.getBoundingClientRect();
            if (ele.classList.contains("opens-left")) {
                var x = br.right - popup.offsetWidth;
            }
            else{
                var x = br.left;
            }

            var y = br.bottom;
            scrolledY = window.scrollY
                // console.log("opening at", x, y)
                // console.log("scrolled Y is", window.scrollY)
            popup.style.top = (y + scrolledY) + 'px';
            popup.style.left = (x) + 'px';
            popup.currentItem = ele;
        }
        else{

            popup.style.top = '-1000px';
            popup.style.left = '-1000px';
            popup.currentItem = undefined;
        }
    }
}


function hidePopup(id) {
    var popup = document.getElementById(id);
    popup.style.top = '-1000px';
    popup.style.left = '-1000px';
}


function hideAllPopups(except) {
    var popups = document.getElementsByClassName("conduit-popup");
    for (var i = 0; i < popups.length; i++) {
        if (except != popups[i].id) {
            hidePopup(popups[i].id);
        }
    }
}



function classSelectorToggleDelegate(elem) {
    return function() {
        classSelectorToggle(elem);
    }
}


function classSelectorToggle(elem) {
    console.log(elem, "clicked")
    if (elem.classList.contains("no-select")) { return; }
    var grp = elem.getAttribute("data-graph-group");
    var siblings = document.querySelectorAll("[data-graph-group='" + grp + "']");
    var selectionType = elem.getAttribute("data-selection-type");
    var selected = getSelectedDatasets(grp);
    if (elem.classList.contains("selected") && (selected.length > 1)) {
        elem.classList.remove("selected");
        elem.style.backgroundColor = "#b6b6b8";
        elem.style.borderColor = "grey";
    }
    else{
        elem.classList.add("selected");
        elem.style.borderColor = elem.getAttribute("data-bg");
        elem.style.backgroundColor = "white";
    }
    if (selectionType != "multi") {
        console.log("not mutli!!!");
        for (var i = 0; i < siblings.length; i++) {
            //console.log("comparing",siblings[i] , elem,siblings[i] != elem)
            if (siblings[i] != elem) {
                siblings[i].classList.remove("selected");
                siblings[i].style.backgroundColor = "#b6b6b8";
                siblings[i].style.borderColor = "grey";
            }
        }
    }

}

function classSelectorSelectAll(grp) {
    var siblings = document.querySelectorAll("[data-graph-group='" + grp + "']");
    for (var i = 0; i < siblings.length; i++) {
        siblings[i].classList.remove("selected");
        classSelectorToggle(siblings[i]);
    }
}



function IconToggleDelegate(elem) {
    return function() {
        IconToggle(elem);
    }
}


function IconToggle(elem) {
    var icon = elem.getElementsByTagName("i")[0];
    //console.log("icon is",icon);
    if (icon) {
        if (icon.hasAttribute("data-alt")) {
            var altClassList = icon.getAttribute("data-alt").split(" ");
            var currentClassList = Array.from(icon.classList);
            //console.log("current is",Array.from(currentClassList),"alt is",altClassList);
            icon.setAttribute("class", "")
            for (var i = 0; i < altClassList.length; i++) {
                icon.classList.add(altClassList[i]);
            }

            icon.setAttribute("data-alt", currentClassList.join(" "));

            //console.log("current is now ",Array.from(icon.classList),"alt is",icon.getAttribute("data-alt"));

        }

        if (icon.hasAttribute("data-alt-col")) {
            //console.log("yers it has alt col");
            var altCol = icon.getAttribute("data-alt-col");
            var col = icon.style.color;
            icon.setAttribute("data-alt-col", col)


            icon.style.color = altCol;

            //console.log("current is now ",Array.from(icon.classList),"alt is",icon.getAttribute("data-alt"));

        }
    }

}



function navItemToggleDelegate(elem) {
    return function() {
        navItemToggle(elem);
    }
}


function navItemToggle(elem) {
    console.log("clicked on", elem);
    var ul = elem.parentNode.parentNode;
    var items = ul.getElementsByTagName("a");
    for (var i = 0; i < items.length; i++) {
        items[i].classList.remove("selected");
    }
    elem.classList.add("selected");
}


function MenuItemToggleDelegate(elem) {
    //console.log("setting up toggle listener for",elem);
    return function() {
        MenuItemToggle(elem);
    }
}


function MenuItemToggle(elem) {
    // console.log("executing click listener in base");
    var menu = elem.parentNode.parentNode;
    var selected = menu.getElementsByClassName("selected");
    if (!($(menu.parentNode).hasClass('vivacity-1'))) {
        for (var i = 0; i < selected.length; i++) {
            if ($(selected[i])[0] != $(elem).children()[0]) {
                selected[i].classList.remove("selected");
            }
        }
    }
    console.log("menu is",menu)
    var items = menu.querySelectorAll('a:not(.select-all)');
    var allSelector = menu.getElementsByClassName("select-all");
    var currentItem = elem.getElementsByTagName("a")[0];
    if (currentItem.classList.contains("disabled")) {
        //console.log("ITS DISABLED!!!!")
        return;
    }
    if (currentItem.classList.contains("select-all")) {

        for (var i = 0; i < items.length; i++) {
            if (currentItem.classList.contains("selected")) {
                items[i].classList.remove("selected");
            }
            else{
                items[i].classList.add("selected");
            }
        }

        currentItem.classList.toggle("selected");


    }
    else{
        var selected = menu.getElementsByClassName("selected");
        if (menu.classList.contains("min-1") && currentItem.classList.contains("selected") && (selected.length == 1)) {
            return;
        }

        if (menu.classList.contains("multi") && !currentItem.classList.contains("selected")) {
            for (let item of items) {
                if (item != currentItem) {
                    if (item.classList.contains("selected")) {
                        item.classList.replace("selected", "selected");
                    }
                }
            }
        }
        currentItem.classList.toggle("selected");

        selectableHeaderId = menu.getAttribute("data-header");

        if (selectableHeaderId) {
            var header = document.getElementById(selectableHeaderId);
            if (header) {

                header.getElementsByTagName("span")[0].innerText = currentItem.innerText;
                var popup = elem.parentNode.parentNode.parentNode.id;
                hidePopup(popup);
            }
        }
    }
    var selected = menu.getElementsByClassName("selected");
    if (selected.length == 0) {
        $('#measurement').text('Measurements')
    }

}


function setPopupValues(name, values) {
    var popup = document.getElementById(name);
    var items = popup.getElementsByTagName("a");
    for (var i = 0; i < values.length; i++) {
        if (values[i]) {
            items[i].classList.add("selected");
        }
        else{
            items[i].classList.remove("selected");
        }
    }
}


function getPopupValues(name) {
    var values = [];
    var popup = document.getElementById(name);
    var items = popup.getElementsByTagName("a");
    for (var i = 0; i < items.length; i++) {
        if (items[i].classList.contains("selected")) {
            values.push(true);
        }
        else{
            values.push(false);
        }
    }
    return values;
}


function getSelectedPopupIndexes(name) {
    var values = [];
    var popup = document.getElementById(name);
    var items = popup.querySelectorAll('a:not(.select-all)');
    for (var i = 0; i < items.length; i++) {
        if (items[i].classList.contains("selected")) {
            values.push(i);
        }
    }
    return values;
}

function getSelectedPopupValues(name) {
    var values = [];
    var popup = document.getElementById(name);
    var items = popup.querySelectorAll('a:not(.select-all)');
    for (var i = 0; i < items.length; i++) {
        if (items[i].classList.contains("selected")) {
            values.push(items[i].parentNode.id);
        }
    }
    return values;
}


function toggleBetween(group) {
    console.log("group is", group);
    var eles = document.querySelectorAll("[data-group='" + group + "']");
    console.log("else are", eles);
    for (var i = 0; i < eles.length; i++) {
        console.log("displaying", eles[i])
        if (eles[i].classList.contains("d-none")) {
            eles[i].classList.remove("d-none");
        }
        else{
            eles[i].classList.add("d-none");
        }

    }
}

/*********************************************************************************************************


Graph Selectors


*********************************************************************************************************/


function addGraphSelectorListeners(ele) {
    var eles = ele.querySelectorAll("[data-graph]")
}




/*********************************************************************************************************


sliding toggle button


*********************************************************************************************************/




/*********************************************************************************************************


side bar


*********************************************************************************************************/
var sidebarWidth = 300;

function showNamePopup(event) {
    //console.log("event is",event.target);
    var br = event.target.getBoundingClientRect();
    popup = document.getElementById("site-name-popup");
    popup.innerText = event.target.innerText;
    //console.log("set value of widget to",popup.getElementsByTagName("div")[0].innerText );
    //console.log("display is",popup.style.display);
    var x = event.clientX + 100;
    var y = br.bottom;
    //console.log("x,y,",x,y);
    popup.style.top = (y - 50) + 'px';
    //console.log("width is",popup.offsetWidth,"-", popup.clientWidth,"-",popup.style.width);
    popup.style.left = (x + 10) + 'px';
    event.target.classList.add("expanded");
    $('#site-name-popup').show();

}



function toggleSideBar(event) {

    var sidebar = document.getElementById("sidebar");
    if (sidebar.classList.contains("normal")) {
        pinSideBar();
    }
    else{
        unpinSideBar();
    }
}


// function pinSideBar(event){
//     var sidebar = document.getElementById("sidebar");
//     sidebar.classList.replace("normal","maximized");
//     var button = sidebar.getElementsByClassName("sidebar-brand-button")[0]
//     button.getElementsByTagName("i")[0].classList.remove("icon-menu");
//     button.getElementsByTagName("i")[0].classList.add("icon-pin");
//     document.getElementById("main-container").style.paddingLeft = "315px";
//     document.getElementById("topbar-selection-container").style.marginLeft = "300px";
//     //document.getElementById("main-container").style.width = "calc(100% - 300px)";
// }


function unpinSideBar(event) {
    var sidebar = document.getElementById("sidebar");
    sidebar.classList.replace("maximized", "normal");
    var button = sidebar.getElementsByClassName("sidebar-brand-button")[0]
    button.getElementsByTagName("i")[0].classList.add("icon-menu");
    button.getElementsByTagName("i")[0].classList.remove("icon-pin");
    document.getElementById("main-container").style.paddingLeft = "28px";
    document.getElementById("topbar-selection-container").style.marginLeft = "55px";
    //document.getElementById("main-container").style.width = "calc(100% - 55px)";
}



function checkResize(event) {
    if (document.getElementById("sidebar")) {
        var sidebar = document.getElementById("sidebar");
        var w = sidebar.offsetWidth;
        //console.log("width is",w);
        if (w > 100 && w > sidebarWidth && !sidebar.classList.contains("expanded")) {
            console.log("expanding");

            sidebar.classList.add("expanded");
            //sidebar.getElementsByClassName("sidebar-icons")[0].classList.add("d-none");
            //sidebar.getElementsByClassName("sidebar-list")[0].classList.remove("d-none");
            sidebar.getElementsByClassName("sidebar-brand-logo")[0].classList.remove("d-none");
        }

        if (w < sidebarWidth && sidebar.classList.contains("expanded")) {
            console.log("collapsing");
            sidebar.classList.remove("expanded");
            //sidebar.getElementsByClassName("sidebar-icons")[0].classList.remove("d-none");
            //sidebar.getElementsByClassName("sidebar-list")[0].classList.add("d-none");
            sidebar.getElementsByClassName("sidebar-brand-logo")[0].classList.add("d-none");
        }

        sidebarWidth = w;

    }

}



/*********************************************************************************************************


    Navs and view selectors


*********************************************************************************************************/





/*********************************************************************************************************


    Greyed out functionality


*********************************************************************************************************/


function showGreyedOut(greyedOut) {
    greyedOut.classList.add("show");
    return;
    console.log("func is", func);
    var greyed = document.getElementsByClassName("greyed-out");
    for (var i = 0; i < greyed.length; i++) {
        if (index) {
            if (index == i) {
                greyed[i].style.display = "flex";
            }

        }
        else{
            greyed[i].style.display = "flex";
        }

    }
    setTimeout(func, 10);
}


function hideGreyedOut(greyedOut) {
    greyedOut.classList.remove("show");
    return
    console.log("hiding greyed out");
    var greyed = document.getElementsByClassName("greyed-out");
    for (var i = 0; i < greyed.length; i++) {
        greyed[i].classList.add("d-none");
    }
}


function hideAllGreyedOut() {
    var eles = document.getElementsByClassName("greyed-out");
    for (var i = 0; i < eles.length; i++) {
        hideGreyedOut(eles[i]);
    }
}

function showAllGreyedOut() {
    var eles = document.getElementsByClassName("greyed-out");
    for (var i = 0; i < eles.length; i++) {
        showGreyedOut(eles[i]);
    }
}

/*********************************************************************************************************


    Switching between various views and subviews


*********************************************************************************************************/


function switchSubView(ele) {
    console.log("in switch sub view", ele);

    var views = document.getElementsByClassName("sub-view");
    for (var i = 0; i < views.length; i++) {
        views[i].classList.add("d-none");
    }
    var id = ele.getAttribute("data-sub-view");
    var view = document.getElementById(id);
    if (view) {
        view.classList.remove("d-none");
    }

    hideAllPopups();
}


function switchView(ele) {
    console.log("clicked", ele.id)
    getView(ele.id).then(function(response) {
            if (response.status == 404) {
                console.log({ "message": "resource not found" });
            };
            //console.log("received response",response);
        return response.json();})
        .then(function(result) {
            console.log(result);
            window.location.href = result.redirect;
        });

}



/*********************************************************************************************************


    Set up all the listeners for the various widgets


*********************************************************************************************************/

function setToggleDatasetSelectorsListener(ele) {
    var items = ele.getElementsByClassName("class-selector");
    for (var i = 0; i < items.length; i++) {
        items[i].style.borderColor = items[i].getAttribute("data-bg");
        items[i].classList.add("selected");
        //items[i].style.color = items[i].getAttribute("data-col");
        items[i].addEventListener("click", classSelectorToggleDelegate(items[i]));
    }
}

function setDatasetSelectorsFunctionListener(ele, func) {
    var items = ele.getElementsByClassName("class-selector");
    for (var i = 0; i < items.length; i++) {
        items[i].addEventListener("click", function(ele) { return function() { func(ele) } }(items[i]));
    }

}


function getSelectedDatasets(grp) {
    datasets = [];
    var selectors = document.querySelectorAll("[data-graph-group='" + grp + "']");
    //console.log("selecteors are",selectors);
    for (var i = 0; i < selectors.length; i++) {
        if (selectors[i].classList.contains("selected")) {
            //console.log("pushing dataset",i);
            datasets.push(i);
        }
    }
    //console.log("selected datasets are",datasets);
    return datasets;

}





function setClassSelectorsFunctionListener(ele, func) {

    var items = ele.getElementsByClassName("class-selector");
    for (var i = 0; i < items.length; i++) {
        items[i].addEventListener("click", function(ele) { return function() { func(ele) } }(items[i]));
    }

}


function setPopupListeners(popup) {
    var items = popup.getElementsByClassName("menu-item");
    for (var i = 0; i < items.length; i++) {
        items[i].addEventListener("click", MenuItemToggleDelegate(items[i]));
    }
}


function init() {

    var popups = document.getElementsByClassName("conduit-popup");
    for (var i = 0; i < popups.length; i++) {
        setPopupListeners(popups[i]);
        var trigger = document.getElementsByClassName(popups[i].id + "-trigger");
        if (trigger.length > 0) {
            for (var t = 0; t < trigger.length; t++) {
                trigger[t].addEventListener("click", function(id, ele) {
                    return function() { showPopup(id, ele) }
                }(popups[i].id, trigger[t]));
            }

        }
    }

    var items = document.getElementsByClassName("nav-button");
    for (var i = 0; i < items.length; i++) {
        items[i].addEventListener("click", navItemToggleDelegate(items[i]));
    }


    var items = document.getElementsByClassName("icon-toggle");
    for (var i = 0; i < items.length; i++) {
        items[i].addEventListener("click", IconToggleDelegate(items[i]));
    }


    var items = document.getElementsByClassName("toggle-between");
    for (var i = 0; i < items.length; i++) {

        items[i].addEventListener("click", function(ele) {
            return function() {

                                                       toggleBetween(ele.getAttribute("data-target"))}
        }(items[i]));
    }

    var items = document.getElementsByClassName("sub-view-nav");
    for (var i = 0; i < items.length; i++) {
        items[i].addEventListener("click", function(ele) {
            return function() { switchSubView(ele) }
        }(items[i]));
    }


    var items = document.getElementsByClassName("toggle-other-elem");
    for (var i = 0; i < items.length; i++) {
        items[i].addEventListener("click", function(ele) {
            return function() {
                console.log("clicked", ele)
                var id = ele.getAttribute("data-target");
                console.log("id is", id);
                document.getElementById(id).classList.toggle("d-none");
            }
        }(items[i]));
    }




    var items = document.getElementsByClassName("view-nav");
    for (var i = 0; i < items.length; i++) {
        items[i].addEventListener("click", function(ele) {
            return function() { switchView(ele) }
        }(items[i]));
    }

    if (document.getElementById("sidebar")) {
        var leaves = document.getElementById("sidebar").getElementsByClassName("leaf");
        for (var i = 0; i < leaves.length; i++) {

            leaves[i].addEventListener("click",function(elem){return function(){
                if (!document.getElementById("sidebar").classList.contains("multi"))
                {
                        var eles = document.getElementById("sidebar").getElementsByClassName("leaf");
                        for (var e = 0; e < eles.length; e++) {
                            eles[e].getElementsByTagName("a")[0].classList.remove("selected");
                        }
                    }
                elem.getElementsByTagName("a")[0].classList.toggle("selected");}}(leaves[i]));
                }
        }


}



function searchString(obj) {
    var value = obj.value.toLowerCase();
    var len = value.length;
    console.log("looking for", value);
    var sites = document.getElementsByClassName("leaf");
    for (var i = 0; i < sites.length; i++) {
        sites[i].classList.remove("d-none");
    }


    var submenus = document.getElementById("sidebar").getElementsByClassName("submenu-item");
    for (var i = 0; i < submenus.length; i++) {
        submenus[i].classList.remove("d-none");
        var city = submenus[i].getElementsByTagName("a")[0].innerText.trim().toLowerCase();
        var s = submenus[i].getElementsByClassName("leaf");
        console.log("sites for city are", s);
        //console.log("comparing",value,city,value != "" && city.includes(value));
        if (value != "" && city.includes(value)) {
            //console.log("showing whole of",city);
        }
        else{

            for (var site = 0; site < s.length; site++) {
                var itemVal = s[site].getElementsByTagName("a")[0].innerText.trim().toLowerCase();
                console.log("comparing", itemVal, "to", value);
                if (value != "" && !itemVal.includes(value)) {
                    s[site].classList.add("d-none");
                    // console.log("hiding",sites[site],"because city didnt match and site didnt match");
                }
            }
        }

    }

    for (var i = 0; i < submenus.length; i++) {
        var id = submenus[i].getElementsByTagName("a")[0].getAttribute("href").replace("#", "")
            //console.log("checking submenu",submenus[i].getElementsByTagName("a")[0].innerText.trim(),submenus[i].getElementsByTagName("a")[0].getAttribute("href"));
        var leaves = document.getElementById(id).getElementsByClassName("leaf");
        breakPoint: {
            for (var j = 0; j < leaves.length; j++) {
                if (!leaves[j].classList.contains("d-none")) {
                    break breakPoint;
                }
            }
            submenus[i].classList.add("d-none");
        }

    }


}


function pickHex(color1, color2, weight) {
    var p = weight;
    var w = p * 2 - 1;
    var w1 = (w / 1 + 1) / 2;
    var w2 = 1 - w1;
    var rgb = [Math.round(color1[0] * w1 + color2[0] * w2),
        Math.round(color1[1] * w1 + color2[1] * w2),
        Math.round(color1[2] * w1 + color2[2] * w2)];
    return 'rgb(' + rgb.join() + ')';
}

/*********************************************************************************************************


    CRT style table sorting


*********************************************************************************************************/
function tableHeaderClicked(event) {
    var table = event.target.parentNode.parentNode.parentNode;
    var headers = table.getElementsByTagName("th");
    for (var i = 0; i < headers.length; i++) {
        console.log("checking", headers[i], headers[i].innerHTML);
        headers[i].innerHTML = headers[i].innerHTML.replace("\u25be", "").replace("\u25b4", "");
        if (headers[i] != event.target) {
            headers[i].classList.remove("sort-desc");
            headers[i].classList.remove("sort-asc");
        }
    }
    console.log("clicked table is", table.id);
    var col = event.target.cellIndex;
    console.log("target was", event.target, "index was", event.target.cellIndex);
    if (event.target.classList.contains("sort-asc")) {
        var dir = "desc";
        event.target.classList.remove("sort-asc");
        event.target.classList.add("sort-desc");
        event.target.innerHTML = event.target.innerHTML + "&#9662";
    }
    else if (event.target.classList.contains("sort-desc")){
        var dir = "asc";
        event.target.classList.remove("sort-desc");
        event.target.classList.add("sort-asc");
        event.target.innerHTML = event.target.innerHTML + "&#9652";
    }
    else{
        var dir = "desc";
        event.target.classList.add("sort-desc");
        event.target.innerHTML = event.target.innerHTML + "&#9662";
    }
    if (col == 3 && table.id == "countline-table-header") { col = 5; }
    console.log("dir is", dir, "col is", col);

    table = document.getElementById("countline-table").getElementsByTagName("tbody")[0];
    sortTable(table, col, dir);


}


function sortTable(table, column, dir) {
    var rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    console.log(table, column, dir);
    switching = true;
    // Set the sorting direction to ascending:
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        console.log("rows are", rows);
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 0; i < (rows.length - 1); i += 1) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            //console.log("looking at row",rows[i]);
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("td")[column];
            y = rows[i + 1].getElementsByTagName("td")[column];
            //console.log("x is",x);
            //console.log("y is",y);
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            //console.log("looking at",x);
            if (!isNaN(x.innerHTML)) {
                if (dir == "asc") {
                    if (parseFloat(x.innerHTML) > parseFloat(y.innerHTML)) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        //console.log("we should switch!");
                        break;
                    }
          }
          else if (dir == "desc") {
                    if (parseFloat(x.innerHTML) < parseFloat(y.innerHTML)) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        //console.log("we should switch!");
                        break;
                    }
                }
      }
      else{
                if (dir == "asc") {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        //console.log("we should switch!");
                        break;
                    }
          }
          else if (dir == "desc") {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        //console.log("we should switch!");
                        break;
                    }
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            //rows[i+1].parentNode.insertBefore(rows[i + 2], rows[i+1]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
                //dir = "desc";
                //switching = true;
            }
        }
    }
}


init();
setInterval(checkResize, 100);