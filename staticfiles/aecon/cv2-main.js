
//initMap([],[53.483729, -2.241073])



function setupVivacityOverview() {

  chart = new Chart(document.getElementById("viv-overview-donut1"), {
    type: 'doughnut',
    data: {
      labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      baseData: [2478, 5267, 734, 784, 433],
      baseColors: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
      baseLabels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      datasets: [
        {
          label: "Population (millions)",
          backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
          data: [2478, 5267, 734, 784, 433]

        }
      ]
    },

    options: {
      cutoutPercentage: 60,

      maintainAspectRatio: false,
      responsive: true,
      title: {
        display: false,
        text: 'Predicted world population (millions) in 2050'
      },
      legend: {
        display: false
      },
    }
  });

  graphsDict["viv-overview-1"] = chart;


  chart = new Chart(document.getElementById("viv-overview-donut2"), {
    type: 'doughnut',
    data: {
      labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      baseData: [2478, 5267, 734, 784, 433],
      baseColors: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
      baseLabels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      datasets: [
        {
          label: "Population (millions)",
          backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
          data: [2478, 5267, 734, 784, 433]
        }
      ]
    },

    options: {
      cutoutPercentage: 60,

      maintainAspectRatio: false,
      responsive: true,
      title: {
        display: false,
        text: 'Predicted world population (millions) in 2050'
      },
      legend: {
        display: false
      },
    }
  });

  graphsDict["viv-overview-2"] = chart;

  var col = chart.canvas.parentNode.parentNode.parentNode.parentNode;
  console.log(col.offsetHeight);

  chart = new Chart(document.getElementById("viv-overview-line1"), {
    type: 'line',
    data: {
      labels: [1500, 1600, 1700, 1750, 1800, 1850, 1900, 1950, 1999, 2050],
      datasets: [{
        data: [86, 114, 106, 106, 107, 111, 133, 221, 783, 2478],
        label: "Africa",
        borderColor: "#3e95cd",
        fill: false,
        pointRadius: 0
      }, {
        data: [282, 350, 411, 502, 635, 809, 947, 1402, 3700, 5267],
        label: "Asia",
        borderColor: "#8e5ea2",
        fill: false,
        pointRadius: 0
      }, {
        data: [168, 170, 178, 190, 203, 276, 408, 547, 675, 734],
        label: "Europe",
        borderColor: "#3cba9f",
        fill: false,
        pointRadius: 0
      }, {
        data: [40, 20, 10, 16, 24, 38, 74, 167, 508, 784],
        label: "Latin America",
        borderColor: "#e8c3b9",
        fill: false,
        pointRadius: 0
      }, {
        data: [6, 3, 2, 2, 7, 26, 82, 172, 312, 433],
        label: "North America",
        borderColor: "#c45850",
        fill: false,
        pointRadius: 0
      }
      ]
    },
    options: mainLineGraphOptions
  });

  graphsDict["viv-overview-3"] = chart;



  initMap([53.483729, -2.241073], "viv-overview-map")

}








function displayAllGraphs(ele) {
  var eles = ele.parentNode.getElementsByClassName("class-selector");
  //console.log("eles are")
  var classes = [];
  for (var i = 0; i < eles.length; i++) {

    //console.log(eles[i]);
    if (eles[i].classList.contains("selected")) {
      classes.push(i);
    }
  }
  var graphs = JSON.parse(ele.parentNode.getAttribute("data-graph-list").replace(/'/g, '"'));
  for (var i = 0; i < graphs.length; i++) {
    console.log("trying to display", graphs[i], graphsDict[graphs[i]]);
    displayGraph(graphsDict[graphs[i]], classes);
  }
}



if (document.getElementById("atc-view")) {
  initATC();
}


function viewProject(ele) {
  // console.log("ele is",ele);
  var formData = new FormData();
  formData.append("project", ele.id);

  fetcher(formData, "viewProject", function (result) {
    document.getElementById("main-container").innerHTML = result.data;
  });

}
function set_percentage(message, status_div) {
  let text = message.filter(item => item.includes("Processing Completed"))
  if (text.length > 0) {
    let percentage = eval(text[text.length - 1].split("&")[1]) * 100
    document.querySelector(`#${status_div} .progress-bar`).style.width = `${percentage}%`
    document.querySelector(`#${status_div} .progress-bar`).innerText = `${percentage.toFixed(2)}%`
  }

  if (message.length > 0) {
    console.log(message);
    const msg = message.map(item => {
      if (item.includes("Processing")) {
        return `<p>${item.slice(0, -8)}</p>\n`;
      } else if (item.includes("Uploading Process")) {
        return `<p style="color:green;">${item}</p>\n`;
      } else {
        return `<p>${item}</p>\n`
      }
    })
    let txt_editor = document.querySelector(`#${status_div} #text-area`);
    txt_editor.innerHTML = msg.join("");
    txt_editor.scrollTop = txt_editor.scrollHeight;
  }

}

function checkFileUploadStatus(token, id, status_div) {
  $(`#${id}`).hide()
  document.getElementById(status_div).style.display = "block"
  document.querySelector(`#${status_div} .progress`).style.display = "block"
  let formData = new FormData()
  formData.append("upload_status", true);
  formData.append("file", token);
  fetcher(formData, "checkFileReady", function (result) {
    if (result.status == 'processing') {
      let msg = JSON.parse(result.message)
      set_percentage(msg, status_div)
      setTimeout(checkFileUploadStatus, 5000, token, id, status_div);
    }
    else if (result.status == 'success') {
      localStorage.removeItem("uploadToken");
      document.querySelector(`#${status_div} .progress`).style.display = "block"
      let msg = JSON.parse(result.message)
      set_percentage(msg, status_div)
      document.querySelector("#success-message h3").innerText = "File Uploading Successfully"
      document.getElementById("success-message").style.display = "block"
      document.getElementById("file-uploading-reset").style.display = "inline"
    }
    else if (result.status == 'started') {
      setTimeout(checkFileUploadStatus, 5000, token, id, status_div);
    } else if (result.status == 'failed') {
      console.log(result);
      localStorage.removeItem("uploadToken");
      document.querySelector(`#${status_div} .progress`).style.display = "none"
      let txt_editor = document.querySelector(`#${status_div} #text-area`);
      txt_editor.innerHTML = `<p style="color:red;">${result.message}</p>`
      document.getElementById("file-uploading-reset").style.display = "inline"
      document.getElementById("success-message").style.display = "block"
      document.querySelector("#success-message h3").innerText = "File Uploading Failed!"
    }
  });
}

function loadLocation(id) {

}


function updateSidebar() {
  var obsType = document.getElementById("observationType-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-type");
  var project = document.getElementById("project-popup").getElementsByClassName("selected")[0].parentNode.id;
  var sites = document.getElementsByClassName("sidebar-chevron");
  for (var i = 0; i < sites.length; i++) {
    sites[i].classList.add("d-none");
    console.log("obstype is", obsType, "sensor type is", sites[i].getAttribute("data-obstype"))
    if (sites[i].getAttribute("data-obstype") == obsType || obsType == "0") {
      sites[i].classList.remove("d-none");
    }

  }
}


//var eles = document.getElementById("observationType-popup").getElementsByTagName("li");
//for(var i=0;i< eles.length;i++){
//    eles[i].addEventListener("click",updateSidebar);
//}

var sites = document.getElementsByClassName("sidebar-chevron");
for (var i = 0; i < sites.length; i++) {
  //sites[i].addEventListener("mouseover",function(event){setTimeout(function(){showNamePopup(event)},800);})
  //sites[i].addEventListener("mouseout",function(){hidePopup('site-name-popup')});
}


function myReduce(a, b) {

  //console.log("received",a,b);
  if (typeof a === 'string' && typeof b === 'string') {
    //console.log("returning - because both blank")

    return "-"
  }
  if (typeof a === 'string') {

    //console.log("returning b - because a blank")
    return b;
  }
  if (typeof b === 'string') {

    //console.log("returning a - because b blank")
    return a;
  }
  return a + b;

}


function myMax(array) {
  //console.log("array is",array);

  arr = array.filter(e => typeof e !== 'string');
  //console.log("array is now",arr);
  if (arr.length == 0) { return -1; }
  return Math.max.apply(null, arr);
}

function saveNewEvent() {
  var dates = getDates();
  console.log("dates are", dates)
  var form = new FormData(document.getElementById("event-form"));
  form.append("startDate", dates[0].format("YYYY-MM-DD"))
  form.append("endDate", dates[1].format("YYYY-MM-DD"))
  fetcher(form, "events", function (response) {
    console.log("response", response);
    var id = "event_" + response.event_id;
    document.getElementById("events-container").innerHTML = response.events;
    //alert("saved event");
    document.getElementById(id).scrollIntoView()
    document.getElementById(id).classList.add("animate");
    var form = document.getElementById("event-form");
    form.getElementsByTagName("textarea")[0].value = "";
    form.getElementsByTagName("input")[0].value = "";
  }).catch(function (err) {

    console.log("error is", err);
    alert(err.message);
  });



}

function fillAveragesTable(table, data, graphLabels, period, comparison = false) {

  console.log("filling table", table, data)
  var count = 1
  if (comparison == true) {
    count = 2
  }
  var table = document.getElementById(table);
  if (document.getElementById("period-selector-popup")) {

    //console.log("found period selector", document.getElementById("period-selector-popup"))
    var rowOffset = parseInt(document.getElementById("period-selector-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-offset"));

  }
  else {
    var rowOffset = period;
  }
  if (!data) { return; }
  console.log("here", rowOffset)
  for (var datasetIndex = 0; datasetIndex < data.length; datasetIndex++) {
    var dataset = data[datasetIndex];
    // console.log("filling dataset",dataset);
    //console.log("graph labels are",graphLabels);
    var columnData = [];
    for (var row = 0; row < 96; row++) {

      console.log("checking row", row, rowOffset, typeof rowOffset, row % rowOffset, row % rowOffset == 0)
      if (row % rowOffset == 0) {

        if (typeof dataset[row / rowOffset] === "undefined") {
          val = "-";
        }
        else {
          var val = dataset[row / rowOffset];
          if (typeof val === 'string' || val instanceof String) {
            val = "-";
          }
          else {
            val = parseInt(val)
          }


        }
        if (table.rows[row + 1]) {
          table.rows[row + 1].classList.remove("d-none");
          if (table.rows[row + 1].cells[datasetIndex + count]) {
            table.rows[row + 1].cells[datasetIndex + count].getElementsByTagName("span")[0].innerText = val//.toFixed(0);
            columnData.push(val)
          }
        }
      }
      else {
        if (table.rows[row + 1]) {
          table.rows[row + 1].classList.add("d-none");
          columnData.push("-")
        }
      }
    }
    if (comparison == false) {
      // console.log("columndata",columnData);
      table.rows[97].cells[datasetIndex + count].innerText = columnData.slice(28, 76).reduce(function (a, b) { return myReduce(a, b) }, 0).toFixed(0);
      table.rows[98].cells[datasetIndex + count].innerText = columnData.slice(24, 88).reduce(function (a, b) { return myReduce(a, b) }, 0).toFixed(0);
      table.rows[99].cells[datasetIndex + count].innerText = columnData.slice(24).reduce(function (a, b) { return myReduce(a, b) }, 0).toFixed(0);
      table.rows[100].cells[datasetIndex + count].innerText = columnData.reduce(function (a, b) { return myReduce(a, b) }, 0).toFixed(0);
      var max = myMax(columnData.slice(0, 48));
      //console.log("looking at",dataset.slice(0,12))
      //console.log("max is",max);
      var index = columnData.slice(0, 48).indexOf(max);
      //console.log("index is",index)
      if (index == -1) {
        table.rows[101].cells[datasetIndex + count].innerText = "-";
        table.rows[102].cells[datasetIndex + count].innerText = "-";
      }
      else {
        table.rows[101].cells[datasetIndex + count].innerText = graphLabels[index / rowOffset];
        table.rows[102].cells[datasetIndex + count].innerText = max.toFixed(0);;
      }
      //console.log("looking at PM PEAK",dataset.slice(12))
      var max = myMax(columnData.slice(48));
      var index = columnData.slice(48).indexOf(max);
      //console.log("for pm peak , details are",max,index)
      if (index == -1) {

        table.rows[103].cells[datasetIndex + count].innerText = "-";
        table.rows[104].cells[datasetIndex + count].innerText = "-";
      }
      else {

        //console.log("filling",("0" + (index  + 12)).substr(-2) + ":00",max);
        table.rows[103].cells[datasetIndex + count].innerText = graphLabels[(index + 48) / rowOffset];
        table.rows[104].cells[datasetIndex + count].innerText = max.toFixed(0);;

      }
    }

  }
}


function genScreenshotgraph(elementId, title) {
  if (document.getElementById("graph-overlay")) {
    document.getElementById("graph-overlay").classList.add("d-none");
    document.getElementById("graph-overlay").classList.remove("d-flex");
  }
  html2canvas($('#' + elementId), {

    onrendered: function (canvas) {
      var downloadLink = document.createElement("a");
      console.log("width of canvas is", canvas.width);
      ctx = canvas.getContext("2d");
      ctx.textAlign = "center";
      ctx.font = "14px Arial";
      ctx.fillText(title, canvas.width / 2, 15);
      var img = canvas.toDataURL("image/jpeg");

      downloadLink.href = img;
      downloadLink.download = "chart.jpg";  //Name the file here
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      if (document.getElementById("graph-overlay")) {
        document.getElementById("graph-overlay").classList.remove("d-none");
        document.getElementById("graph-overlay").classList.add("d-flex");
      }


    },
    removeContainer: false
  });

}

function getElementAsCanvas(elementId) {

  return new Promise(function (resolve, reject) {

    if (document.getElementById("graph-overlay")) {
      document.getElementById("graph-overlay").classList.add("d-none");
      document.getElementById("graph-overlay").classList.remove("d-flex");
    }
    html2canvas($('#' + elementId), {

      onrendered: function (canvas) {
        resolve(canvas);
      },
      removeContainer: false
    });


  });

}


function isNumber(n) { return !isNaN(parseFloat(n)) && !isNaN(n - 0) }

var sumOfDatasets = function (array1, array2) {
  //console.log("in sum,",array1,array2);
  return array1.map(function (value, index) {
    if (typeof array2[index] == "string" && typeof value == "string") { return "-"; }
    if (typeof array2[index] == "string") { return value; }
    if (typeof value == "string") {
      return array2[index];
    }

    return value + array2[index];

  });
}

var sumOfArray = function (total, num) {

  //console.log(total,num);
  if (typeof num == "string" && typeof total == "string") { return "-"; }
  if (typeof num == "string") { return total; } if (typeof total == "string") { return num; }
  return total + num;
}


function getSelectedSites(obsType) {
  var ids = [];
  var selected = document.getElementById("sidebar").getElementsByClassName("selected");
  for (var i = 0; i < selected.length; i++) {
    console.log("comparing", selected[i].parentNode.getAttribute("data-obstype"), obsType.toString(), selected[i].parentNode.getAttribute("data-obstype") == obsType.toString());
    if (selected[i].parentNode.getAttribute("data-obstype") == obsType.toString()) {
      ids.push(selected[i].id);
    }

  }
  console.log("ids are", ids);
  return ids;
}
