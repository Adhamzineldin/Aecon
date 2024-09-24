


function setupATCOverview(){

    chart = new Chart(document.getElementById("atc-overview-donut1"), {
    type: 'doughnut',
    data: {
      labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      baseData:[2478,5267,734,784,433],
      baseColors:["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
      baseLabels:["Africa", "Asia", "Europe", "Latin America", "North America"],
      datasets: [
        {
          label: "Population (millions)",
          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
          data: [2478,5267,734,784,433]

        }
      ]
    },

    options: {
        cutoutPercentage:60,

        maintainAspectRatio:false,
        responsive: true,
      title: {
        display: false,
        text: 'Predicted world population (millions) in 2050'
      },
      legend:{
        display:false
    },
    }
});

graphsDict["atc-overview-1"] = chart;


chart = new Chart(document.getElementById("atc-overview-donut2"), {
    type: 'doughnut',
    data: {
      labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      baseData:[2478,5267,734,784,433],
      baseColors:["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
      baseLabels:["Africa", "Asia", "Europe", "Latin America", "North America"],
      datasets: [
        {
          label: "Population (millions)",
          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
          data: [2478,5267,734,784,433]
        }
      ]
    },

    options: {
        cutoutPercentage:60,

        maintainAspectRatio:false,
        responsive: true,
      title: {
        display: false,
        text: 'Predicted world population (millions) in 2050'
      },
      legend:{
        display:false
    },
    }
});

graphsDict["atc-overview-2"] = chart;

var col = chart.canvas.parentNode.parentNode.parentNode.parentNode;
console.log(col.offsetHeight);

chart = new Chart(document.getElementById("atc-overview-line1"), {
  type: 'line',
  data: {
    labels: [1500,1600,1700,1750,1800,1850,1900,1950,1999,2050],
    datasets: [{
        data: [86,114,106,106,107,111,133,221,783,2478],
        label: "Africa",
        borderColor: "#3e95cd",
        fill: false,
        pointRadius:0
      }, {
        data: [282,350,411,502,635,809,947,1402,3700,5267],
        label: "Asia",
        borderColor: "#8e5ea2",
        fill: false,
        pointRadius:0
      }, {
        data: [168,170,178,190,203,276,408,547,675,734],
        label: "Europe",
        borderColor: "#3cba9f",
        fill: false,
        pointRadius:0
      }, {
        data: [40,20,10,16,24,38,74,167,508,784],
        label: "Latin America",
        borderColor: "#e8c3b9",
        fill: false,
        pointRadius:0
      }, {
        data: [6,3,2,2,7,26,82,172,312,433],
        label: "North America",
        borderColor: "#c45850",
        fill: false,
        pointRadius:0
      }
    ]
  },
  options: mainLineGraphOptions
});

graphsDict["atc-overview-3"] = chart;

chart = new Chart(document.getElementById("atc-overview-line2"), {
  type: 'line',
  data: {
    labels: [1500,1600,1700,1750,1800,1850,1900,1950,1999,2050],
    datasets: [{
        data: [86,114,106,106,107,111,133,221,783,2478],
        label: "Africa",
        borderColor: "#3e95cd",
        fill: false,
        pointRadius:0
      }, {
        data: [282,350,411,502,635,809,947,1402,3700,5267],
        label: "Asia",
        borderColor: "#8e5ea2",
        fill: false,
        pointRadius:0
      }, {
        data: [168,170,178,190,203,276,408,547,675,734],
        label: "Europe",
        borderColor: "#3cba9f",
        fill: false,
        pointRadius:0
      }, {
        data: [40,20,10,16,24,38,74,167,508,784],
        label: "Latin America",
        borderColor: "#e8c3b9",
        fill: false,
        pointRadius:0
      }, {
        data: [6,3,2,2,7,26,82,172,312,433],
        label: "North America",
        borderColor: "#c45850",
        fill: false,
        pointRadius:0
      }
    ]
  },
  options: mainLineGraphOptions
});

graphsDict["atc-overview-4"] = chart;

initMap([53.483729, -2.241073],"atc-overview-map")

}








function initATC(){
    var view = document.getElementById("atc-view");
    setupATCOverview();
}




function displayATCGraphs(ele){
    var eles = ele.parentNode.getElementsByClassName("class-selector");
    var classes = [];
    for(var i=0;i<eles.length;i++){
        if (eles[i].classList.contains("selected")){
            classes.push(i);
        }

    }
    var graphs = JSON.parse(ele.parentNode.getAttribute("data-graph-list").replace(/'/g, '"'));
    for(var i=0;i<graphs.length;i++){
        displayGraph(graphsDict[graphs[i]],classes);
    }
}




//initATC();

