
var id = document.getElementById("mb-id").value
initMap([53.476404, -2.250621],"atc-overview-map",id);
var overviewData;
var classedData;
var speedData;
var scatterData;
var dailyChart;
var scatterChart;
var classedChart;

function dealWithLocationFeatureCollection(feature,layer){
    console.log("dealing with location")
    if (feature.geometry.type == "LineString"){
        return;
        console.log(feature);
        layer.setStyle(locationStyleOptions);
        lineLayer.addLayer(layer);
        setupLocationLineWithArrowhead(layer);
        layer.options.direction = feature.properties.direction_id;
        layer.options.order = feature.properties.order;

    }
    if (feature.geometry.type == "Point"){
        var marker = addPlainMarker(feature,"perm");
        marker.on("dragend",function(event){
            document.getElementById("lat").value = event.target.getLatLng().lat;
            document.getElementById("lon").value = event.target.getLatLng().lng;
        });
    }
}


function displayOverviewTable(){
    console.log("data is",overviewData)
    data = overviewData.speedData;
    var eles = document.getElementById("overview-selector-container").getElementsByClassName("class-selector");
    var classes = [];
    for(var i=0;i<eles.length;i++){
        if (eles[i].classList.contains("selected")){
            classes.push(i);
        }
    }
    var table = document.getElementById("overview-table");
    for (var i=0;i < overviewData.directions.length;i++){
        table.rows[0].cells[i + 1].innerText = overviewData.directions[i].descriptive;
    }
    for(var row=0;row<data.length;row++){
        for (var cell=0;cell<data[row].length;cell++){
            table.rows[row + 1].cells[cell + 1].innerText = data[row][cell];
        }
    }
}


function setUpChart(){
    console.log("setting up  chart view labels are now ",classedData.graphLabels);
    var selectors = document.querySelectorAll("[data-graph-group='daily']");
    var direction = document.getElementById("directions-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-order")
    var avg = document.getElementById("averages-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-order")
    if (dailyChart){dailyChart.destroy();}
    var days = document.getElementById("countline-daily-table").getElementsByClassName("class-selector");

    var chartData = []
    for(day of days){
        chartData.push({"label":day.innerText,"data":[1,2,3],"borderColor":day.getAttribute("data-bg"),"backgroundColor":day.getAttribute("data-bg"),"fill":false,"pointRadius":0,"borderWidth":1});
    }
    console.log("length of graph labels is",classedData.graphLabels.length);


    dailyChart = createLineChart(document.getElementById("atc-daily-totals-graph"),{"labels":classedData.graphLabels,"datasets":chartData});
    //document.getElementById("directions-popup").getElementsByClassName("menu-item")[direction].click();
    dailyChart.options.scales.xAxes[0].ticks.maxTicksLimit = 12;
    Chart.defaults.line.spanGaps = true;


    classedChart = createLineChart(document.getElementById("atc-classed-totals-graph"),{"labels":classedData.graphLabels,"datasets":classedData.data.dfhhjdj.directions[direction].baseData[avg]});
}


function updateDatasets(){
    selectedClasses = getSelectedPopupIndexes("classes-popup");
    console.log("selected classes are",selectedClasses);
    for(var key in graphsDict){
        displayGraph(graphsDict[key],selectedClasses)
    }
    var dir = parseInt(document.getElementById("directions-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-order"))
    var avg = parseInt(document.getElementById("averages-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-order"))
    var day = parseInt(document.getElementById("day-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-index"));
    if(classedData){

        setUpDailyVolumesTable(classedData.data.dfhhjdj.directions[dir], classedData.graphLabels, 4);
        var dailySelectors = document.getElementById("countline-daily-table").getElementsByClassName("class-selector");
        var datasets = [];
        var tableData = [];
        console.log("classed data is", classedData);
        classedData.data.dfhhjdj.directions[dir].baseData.forEach(function(dataset,index){
            var selectedClassVolumes = [];
            selectedClasses.forEach(function(classIndex,i){
                selectedClassVolumes.push(dataset[classIndex].data);
            });
            if (selectedClasses.length != 0){
                //console.log("sleected class volumnes are",selectedClassVolumes);
                //console.log("reduced dataset is",selectedClassVolumes.reduce(sumOfDatasets));
                tableData.push(selectedClassVolumes.reduce(sumOfDatasets));
            }
            else{
                tableData.push([]);
            }
        });
        //console.log("table data is now",tableData);
        //console.log("chart is",dailyChart);
        //console.log("chart datasets are",dailyChart.data.datasets);

        dailyChart.options.scales.yAxes[0].stacked = false;
        dailyChart.data.datasets.forEach(function(dataset,index){
            //console.log("setting dataset",index,"to",tableData[index]);

     //dailySelectors[index].classList.contains("selected"))
            dataset.spanGaps = true;
            if(!dataset.limit){
                dataset.data = tableData[index];
            }
            if (!dailySelectors[index].classList.contains("selected")){
                //console.log("setting to hidden!!", dataset);
                dataset.hidden = true;
            }
            else{
                dataset.hidden = false;
            }
            //console.log("dataset is", dataset)
        });
        dailyChart.update()
        tableData = []
        console.log("direction is", dir, "avg is", avg)
        console.log(classedData.data.dfhhjdj.directions[0].baseData[avg])
        console.log("updateing classed table with", classedData.data.dfhhjdj.directions)
        classedData.data.dfhhjdj.directions[dir].baseData[avg].forEach(function(dataset,index){
                tableData.push([...dataset.data]);
                //classedChart.data.datasets[index].data = [...dataset.data];
        });
        classedChart.data.datasets = classedData.data.dfhhjdj.directions[dir].baseData[avg]
        //classedChart.update()
        fillAveragesTable("hourly-classed-table",tableData, classedData.graphLabels, 4);

        displayGraph(classedChart,selectedClasses);

    }
    if (speedData){
        console.log("there is speed data!!!");
        console.log(speedData);
        tableData = []
        console.log("daty datasets are", speedData[dir].speedCharts[day][0])
        speedData[dir].speedCharts[day].forEach(function(dataset,index){
            console.log("checking", dataset)
            var selectedClassVolumes = [];
            selectedClasses.forEach(function(classIndex,i){
                selectedClassVolumes.push(dataset.datasets[classIndex].data);
            });
            if (selectedClasses.length != 0){
                //console.log("sleected class volumnes are",selectedClassVolumes);
                //console.log("reduced dataset is",selectedClassVolumes.reduce(sumOfDatasets));
                tableData.push(selectedClassVolumes.reduce(sumOfDatasets));
            }
            else{
                tableData.push([]);
            }

        });
        fillAveragesTable("speed-table",tableData, classedData.graphLabels,4);
    }

    if (scatterData){
        console.log("displaying scatter data")
        var selectedData = []
        var colors = []
        scatterData.data.forEach(function(item,i){
            //console.log("day is", item.day,typeof item.day)
            if(item.day == day + 1 && selectedClasses.includes(item.order) && (dir == 2 || dir == item.direction)){

                selectedData.push(item);
                colors.push(item.color)
            }

            });
        scatterChart.data.datasets[0].data = selectedData;
        scatterChart.data.datasets[0].pointBackgroundColor = colors;
        scatterChart.update()
    }


}


function displayOverview(){
    //document.getElementById("atc-breadcrumbs").innerText = overviewData.breadcrumbs;
    //document.getElementById("atc-site-name").innerText = overviewData.siteName;
    //document.getElementById("overview-selector-container").innerHTML = overviewData.selectors;
    //document.getElementById("classed-speeds-selector-container").innerHTML = overviewData.selectors;
    //document.getElementById("overview-selector-container").setAttribute("data-graph-list",data.data["data-graph-list"])
    //setToggleClassSelectorsListener(document.getElementById("overview-selector-container"));
    //setToggleClassSelectorsListener(document.getElementById("classed-speeds-selector-container"));
    document.getElementById("classes-popup").getElementsByClassName("conduit-selectable-menu")[0].innerHTML = overviewData.selectors;
    setPopupListeners(document.getElementById("classes-popup"));
    var items = document.getElementById("classes-popup").getElementsByClassName("menu-item");
    for(var i=0;i<items.length;i++){
        //console.log("in inline script, setting up click listener for",items[i]);
        items[i].addEventListener("click",function(){updateDatasets();});
    }
    //console.log("data is",overviewData.donuts.dfhhjdj.directions[0].baseData[0])
    var chart = createDonutChart(document.getElementById("atc-overview-donut1"),{datasets:[{data:[]}]});
    chart.data.baseData = overviewData.donuts.dfhhjdj.directions[0].baseData[0];
    chart.data.direction = overviewData.directions[0]
    //chart.update();
    graphsDict["atc-overview-donut1"] = chart;
    var chart = createDonutChart(document.getElementById("atc-overview-donut2"),{datasets:[{data:[]}]});
    chart.data.baseData = overviewData.donuts.dfhhjdj.directions[1].baseData[0];
    graphsDict["atc-overview-donut2"] = chart;
    chart.data.direction = overviewData.directions[1]
    //chart.update();

    var chart = createDonutChart(document.getElementById("atc-overview-donut3"),{datasets:[{data:[]}]});
    chart.data.baseData = overviewData.donuts.dfhhjdj.directions[0].baseData[7];
    graphsDict["atc-overview-donut3"] = chart;
    chart.data.direction = overviewData.directions[0]

    var chart = createDonutChart(document.getElementById("atc-overview-donut4"),{datasets:[{data:[]}]});
    chart.data.baseData = overviewData.donuts.dfhhjdj.directions[1].baseData[7];
    graphsDict["atc-overview-donut4"] = chart;
    chart.data.direction = overviewData.directions[1]

    var chart = createDonutChart(document.getElementById("atc-overview-donut5"),{datasets:[{data:[]}]});
    chart.data.baseData = overviewData.donuts.dfhhjdj.directions[0].baseData[8];
    graphsDict["atc-overview-donut5"] = chart;
    chart.data.direction = overviewData.directions[0]

    var chart = createDonutChart(document.getElementById("atc-overview-donut6"),{datasets:[{data:[]}]});
    chart.data.baseData = overviewData.donuts.dfhhjdj.directions[1].baseData[8];
    graphsDict["atc-overview-donut6"] = chart;
    chart.data.direction = overviewData.directions[1]



    updateDatasets();


    document.getElementById("speed-limit").innerText = overviewData.speedLimit;
    displayOverviewTable();
}


function displaySpeedData(){
    var direction = parseInt(document.getElementById("directions-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-order"))
    var avg = parseInt(document.getElementById("averages-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-order"))
    var day = 0//parseInt(document.getElementById("day-popup").getElementsByClassName("selected")[0].parentNode.getAttribute("data-index"));
    console.log("speed data would be", speedData[direction].speedCharts[day]);
    fillAveragesTable("speed-table",speedData[direction].speedCharts[day], classedData.graphLabels,4);
    hidePopup("directions-popup");
    hidePopup("day-popup");

}


function setupSpeedData(){
    //fillAveragesTable("speed-table",speedData[0].speedCharts[0]);
    console.log(" in set up speed data")
    var formData = new FormData();
    formData.append("locId","dfhhjdj")
    fetcher(formData,"getATCScatterPlot",function(result){console.log("received results of scatter",result)
        var selectedData = []
        scatterData = result;
        scatterData.data.forEach(function(item,i){
            //console.log("day is", item.day,typeof item.day)
            if(item.day == "1"){

                selectedData.push(item);
            }

            });
        var canvas = document.getElementById("atc-speeds-graph");
        scatterChart = createScatterChart(canvas,selectedData);
        updateDatasets();
        //graphsDict["atc-speeds-graph"] = chart
    });


    displaySpeedData();
    updateDatasets();
}



var items = document.getElementById("directions-popup").getElementsByClassName("menu-item");
for(var i=0;i<items.length;i++){
    items[i].addEventListener("click",function(){updateDatasets();});
}


var items = document.getElementById("averages-popup").getElementsByClassName("menu-item");
for(var i=0;i<items.length;i++){
    items[i].addEventListener("click",function(){updateDatasets();});
}


var items = document.getElementById("day-popup").getElementsByClassName("menu-item");
for(var i=0;i<items.length;i++){
    items[i].addEventListener("click",function(){updateDatasets();});
}


function loadLocation(id){
    var formData = new FormData();
    formData.append("location_id",JSON.stringify(id));
    fetcher(formData,"getLocations",function(result){console.log("received results",result);processLocationGeojson(result.locations);});


    //showGreyedOut(document.getElementsByClassName("greyed-out")[0]);
    var formData = new FormData();
    formData.append("locId",id);
    getATCOverview(formData).then(function(response){if(response.status == 404){console.log({"message":"resource not found"});};console.log("received response",response);return response.json();})
                            .then(function(result){console.log("received results",result);overviewData = result.data;
                                displayOverview();
                                hideGreyedOut(document.getElementsByClassName("greyed-out")[0]);
                                hideGreyedOut(document.getElementsByClassName("greyed-out")[1]);
                            });

    //setClassSelectorsFunctionListener(document.getElementById("daily-volumes-selector-container"));
    //return;

    formData.append("ids",JSON.stringify([id]));
    formData.append("startDate","2019-06-01 00:00")
    formData.append("endDate","2019-07-01 00:00")
    formData.append("period","60")
    formData.append("resultType","counts")
    getATCClassedVolumes(formData).then(function(response){if(response.status == 404){console.log({"message":"resource not found"});};return response.json();})
    .then(function(result){console.log("received results",result);
        classedData = result.data;
        console.log("classed Data is", classedData)
        console.log(result.data.graphLabels)
        setUpChart();
        //var chart = createLineChart(document.getElementById("atc-daily-totals-graph"),classedData.directions[0].dailyChart);
        //dailyChart = chart;
        updateDatasets()

}).then(function(result){
    console.log("getting speed data")
    getATCSpeedData(formData).then(function(response){if(response.status == 404){console.log({"message":"resource not found"});};console.log("received response",response);return response.json();})
    .then(function(result){console.log("received speeds",result);speedData = result.data;setupSpeedData();
    })

});
    //return


}
setToggleDatasetSelectorsListener(document.getElementById("countline-daily-table"));
setDatasetSelectorsFunctionListener(document.getElementById("countline-daily-table"),function(){updateDatasets()});
loadLocation("dfhhjdj")


function hoverOnDay(ele){
    if (!dailyChart || !ele.classList.contains("selected")){
        return;
    }
    dailyChart.data.datasets.forEach(function(e) {
        if(!e.limit){
            e.hidden = true;
        }

    });
    var index = parseInt(ele.getAttribute("data-index"));
    dailyChart.data.datasets[index].hidden=false;
    dailyChart.update(0);
}


function hoverExit(event){
    if (!dailyChart){
        return;
    }
    console.log("hovered out of", event);
    updateDatasets();
}

//document.getElementById("observationType-selector").classList.remove("d-none");
//document.getElementById("project-selector").classList.remove("d-none");