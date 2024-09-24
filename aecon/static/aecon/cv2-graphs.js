
var yAxesticks = [];

var stackedBarOptions = {
    maintainAspectRatio:false,
    responsive:true,
    animation: {
        duration: 0
    },
    tooltips: {
        intersect:false,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
              },
        callbacks: {
                label: function(tooltipItem, data) {

                    if(buildGraphLabels){
                        var result = buildGraphLabels(tooltipItem,data);
                        return result;
                    }
                text = [];

                    console.log("tooltip is",tooltipItem);
                    console.log("data is",data);
                    datasets = data.datasets;

                    for(var i=0;i<datasets.length;i++){
                        //console.log("selected classes  are",selectedClasses,selectedClasses.length,selectedClasses.indexOf(datasets[i].name),(selectedClasses.length === 0 || selectedClasses.indexOf(datasets[i].name) != -1));
                        if(datasets[i].name && datasets[i].data[tooltipItem.index] != 0 && (selectedClasses.length === 0 || selectedClasses.indexOf(parseInt(i/2)) != -1)){
                            text.push(datasets[i].name  +  " "  + datasets[i].direction[0] + ": "+ Math.abs(datasets[i].data[tooltipItem.index].toFixed(2)) +  String.fromCharCode(13));
                        }
                    }
                    return text;
                }

            }

    },
    hover :{
        animationDuration:0
    },





    scales: {
        xAxes: [{

            barPercentage: 0.8,
            categoryPercentage: 1,
            scaleLabel:{
                    display:true,
                    //fontColor:"black"]
                    labelString:"Time",
                    fontSize:11
              },

            ticks: {
                beginAtZero:true,
                fontFamily: "'Open Sans Bold', sans-serif",
                fontSize:11,
                maxTicksLimit:25

            },

            gridLines: {
                display:true,
            },
            stacked: true
        }],
        yAxes: [{

            scaleLabel:{
                    display:true,
                    //fontColor:"black"]
                    labelString:"No.of Users",
                    fontSize:11
              },
            gridLines: {

            },
            ticks: {
                beginAtZero:true,
                maxTicksLimit:1,
                fontFamily: "'Open Sans Bold', sans-serif",
                fontSize:11,
                callback : function(value,index,values){
                    yAxesticks = values;
                    return value;
                }

            },
            stacked: true
        }]
    },
    legend:{
        display:false
    },

    pointLabelFontFamily : "Quadon Extra Bold",
    scaleFontFamily : "Quadon Extra Bold",
};


var mainLineGraphOptions = {
        //layout:{padding:0},
        animation: {
            duration: 0
        },
        responsive: true,
        maintainAspectRatio: false,
        tooltips:{
            intersect:false,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
              },
            callbacks: {
                label: function(tooltipItem, data) {

                    if(buildGraphLabels){
                        var result = buildGraphLabels(tooltipItem,data);
                        return result;
                    }
                text = [];

                    console.log("tooltip is",tooltipItem);
                    console.log("data is",data);
                    datasets = data.datasets;
                    

                   

                    for(var i=0;i<datasets.length;i++){
                        //console.log("selected classes  are",selectedClasses,selectedClasses.length,selectedClasses.indexOf(datasets[i].name),(selectedClasses.length === 0 || selectedClasses.indexOf(datasets[i].name) != -1));
                        if( i== tooltipItem.datasetIndex &&  datasets[i].label && datasets[i].data[tooltipItem.index] != 0 && (selectedClasses.length === 0 || selectedClasses.indexOf(parseInt(i/2)) != -1)){
                            text.push(datasets[i].label  +  ": "+ Math.abs(datasets[i].data[tooltipItem.index].toFixed(2)) +  String.fromCharCode(13));
                        }
                    }
                    return text;
                }

            }
        },

        legend:{
            display:false
        },
        scales: {
            yAxes: [{
              //stacked:true,
              scaleLabel:{
                    display:true,
                    fontColor:"#a0a6ac",
                    labelString:"No.of Users",
                    fontSize:11
              },
              ticks: {
                beginAtZero: true,
                suggestedMax:1,
                fontColor:"#a0a6ac",
                fontSize:11,
                callback : function(value,index,values){
                    //console.log("THE CALLBACK HAS BEEN CALLED NOW!!!!!",value)
                    yAxesticks = values;
                    return Math.round(value * 100) / 100;
                }



              },


              position:"left"
            },
            {
                afterFit: function(scale) {
                    //console.log("width of scale is",scale.width);// = 80  //<-- set value as you wish
                },
                position: "right",
                "id": "axis-2",
                display: true,
                scaleLabel:{
                    display:false,
                    labelString:"Pollutant level",
                    fontColor:"black",
                    padding:1
              },
                ticks: {
                    maxTicksLimit:2,
                    beginAtZero: true,
                    //max: 100,
                    callback: (label, index, labels) => {
                       return label.toFixed(2);
                    }
                }
            }


            ],
            xAxes:[{
                scaleLabel:{
                    display:true,
                    fontColor:"#a0a6ac",
                    labelString:"Time",
                    fontSize:10
              },
              ticks:{
                //maxTicksLimit:11,
                maxTicksLimit:25,
                fontColor:"#a0a6ac",
                fontSize:11
              },

            }]
          },

    }
var LondonmainLineGraphOptions = {
        //layout:{padding:0},
        animation: {
            duration: 0
        },
        responsive: true,
        maintainAspectRatio: false,
        tooltips:{
            intersect:false,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
              },
            callbacks: {
                label: function(tooltipItem, data) {

                    if(buildGraphLabels){
                        var result = buildGraphLabels(tooltipItem,data);
                        return result;
                    }
                text = [];

                    console.log("tooltip is",tooltipItem);
                    console.log("data is",data);
                    datasets = data.datasets;

                    for(var i=0;i<datasets.length;i++){
                        //console.log("selected classes  are",selectedClasses,selectedClasses.length,selectedClasses.indexOf(datasets[i].name),(selectedClasses.length === 0 || selectedClasses.indexOf(datasets[i].name) != -1));
                        if(datasets[i].name && datasets[i].data[tooltipItem.index] != 0 && (selectedClasses.length === 0 || selectedClasses.indexOf(parseInt(i/2)) != -1)){
                            text.push(datasets[i].name  +  " "  + datasets[i].direction[0] + ": "+ Math.abs(datasets[i].data[tooltipItem.index].toFixed(2)) +  String.fromCharCode(13));
                        }
                    }
                    return text;
                }

            }
        },

        legend:{
            display:false
        },
        scales: {
            yAxes: [{
              //stacked:true,
              scaleLabel:{
                    display:true,
                    fontColor:"#a0a6ac",
                    labelString:"AQ Value",
                    fontSize:11
              },
              ticks: {
                beginAtZero: true,
                suggestedMax:1,
                fontColor:"#a0a6ac",
                fontSize:11,
                callback : function(value,index,values){
                    //console.log("THE CALLBACK HAS BEEN CALLED NOW!!!!!",value)
                    yAxesticks = values;
                    return Math.round(value * 100) / 100;
                }



              },


              position:"left"
            },
            {
                afterFit: function(scale) {
                    //console.log("width of scale is",scale.width);// = 80  //<-- set value as you wish
                },
                position: "right",
                "id": "axis-2",
                display: true,
                scaleLabel:{
                    display:false,
                    labelString:"Pollutant level",
                    fontColor:"black",
                    padding:1
              },
                ticks: {
                    maxTicksLimit:2,
                    beginAtZero: true,
                    //max: 100,
                    callback: (label, index, labels) => {
                       return label.toFixed(2);
                    }
                }
            }


            ],
            xAxes:[{
                scaleLabel:{
                    display:true,
                    fontColor:"#a0a6ac",
                    labelString:"Time",
                    fontSize:10
              },
              ticks:{
                //maxTicksLimit:11,
                maxTicksLimit:25,
                fontColor:"#a0a6ac",
                fontSize:11
              },

            }]
          },

    }

var comparisonmainLineGraphOptions = {
        //layout:{padding:0},
        animation: {
            duration: 0
        },
        responsive: true,
        maintainAspectRatio: false,
        tooltips:{
            intersect:false,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
              },
            callbacks: {
                label: function(tooltipItem, data) {

                    if(buildGraphLabels){
                        var result = buildGraphLabels(tooltipItem,data);
                        return result;
                    }
                text = [];

                    console.log("tooltip is",tooltipItem);
                    console.log("data is",data);
                    datasets = data.datasets;

                    for(var i=0;i<datasets.length;i++){
                        //console.log("selected classes  are",selectedClasses,selectedClasses.length,selectedClasses.indexOf(datasets[i].name),(selectedClasses.length === 0 || selectedClasses.indexOf(datasets[i].name) != -1));
                        if(datasets[i].name && datasets[i].data[tooltipItem.index] != 0 && (selectedClasses.length === 0 || selectedClasses.indexOf(parseInt(i/2)) != -1)){
                            text.push(datasets[i].name  +  " "  + datasets[i].direction[0] + ": "+ Math.abs(datasets[i].data[tooltipItem.index].toFixed(2)) +  String.fromCharCode(13));
                        }
                    }
                    return text;
                }

            }
        },

        legend:{
            display:true,
            position:'bottom',
            labels: {
                fontSize: 10, 
            }
        },
        scales: {
            yAxes: [{
              //stacked:true,
              "id": "axis-1",
              scaleLabel:{
                    display:true,
                    fontColor:"#a0a6ac",
                    labelString:"No.of Users",
                    fontSize:11
              },
              ticks: {
                beginAtZero: true,
                suggestedMax:1,
                fontColor:"#a0a6ac",
                fontSize:11,
                callback : function(value,index,values){
                    //console.log("THE CALLBACK HAS BEEN CALLED NOW!!!!!",value)
                    yAxesticks = values;
                    return Math.round(value * 100) / 100;
                }



              },
                gridLines : {
                    display : false
                },

              position:"left"
            },
            {
                position: "right",
                "id": "axis-2",
                display: true,
                scaleLabel:{
                    display:true,
                    labelString:"AQ Sensor Data",
                    fontColor:"#a0a6ac",
                    fontSize:11,
              },
                ticks: {
                    beginAtZero: true,
                    //max: 100,
                    fontColor:"#a0a6ac",
                    fontSize:11,
                    callback: (label, index, labels) => {
                       return label;
                    }
                },
                gridLines : {
                    display : true
                }

            }


            ],
            xAxes:[{
                scaleLabel:{
                    display:true,
                    fontColor:"#a0a6ac",
                    labelString:"Time",
                    fontSize:10
              },
              ticks:{
                //maxTicksLimit:11,
                maxTicksLimit:25,
                fontColor:"#a0a6ac",
                fontSize:11
              },

            }]
          },

    }



function createBubbleChart(context,data){
    chart = new Chart(context,{
        type: 'bubble',
        data:  {
      labels: "Africa",
      datasets: [
        {
          label: ["China"],
          backgroundColor: "rgba(255,221,50,0.2)",
          borderColor: "rgba(255,221,50,1)",
          data: [{
            x: 21269017,
            y: 5.245,
            r: 15
          }]
        }, {
          label: ["Denmark"],
          backgroundColor: "rgba(60,186,159,0.2)",
          borderColor: "rgba(60,186,159,1)",
          data: [{
            x: 258702,
            y: 7.526,
            r: 100
          }]
        }, {
          label: ["Germany"],
          backgroundColor: "rgba(0,0,0,0.2)",
          borderColor: "#000",
          data: [{
            x: 3979083,
            y: 6.994,
            r: 15
          }]
        }, {
          label: ["Japan"],
          backgroundColor: "rgba(193,46,12,0.2)",
          borderColor: "rgba(193,46,12,1)",
          data: [{
            x: 4931877,
            y: 5.921,
            r: 15
          }]
        }
      ]
    },
    options: {
      title: {
        display: true,
        text: 'Predicted world population (millions) in 2050'
      }, scales: {
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: "Happiness"
          }
        }],
        xAxes: [{
          scaleLabel: {
            display: true,
            labelString: "GDP (PPP)"
          }
        }]
      }
    },

        options: {

            maintainAspectRatio:false,
            responsive: true,
          title: {
            display: false,
            text: ''
          },
          legend:{
            display:false
        },
        }
    });
    return chart;
}


function createDonutChart(context,data){
    chart = new Chart(context,{
        type: 'doughnut',
        data: data,

        options: {
            cutoutPercentage:60,

            maintainAspectRatio:false,
            responsive: true,
          title: {
            display: false,
            text: ''
          },
          legend:{
            display:false
        },
        }
    });
    return chart;
}
//data: [{y: 40.03, x: 6}, {y: 32.63, x: 10}, {y: 31.68, x: 11}, {y: 35.26, x: 13}, {y: 31.98, x: 14}, {y: 30.11, x: 14}]

function createHorizontalBarChart(context,data){
     var myBarChart = new Chart(context, {

        type: 'horizontalBar',
        data: {

  },
        options: {
            responsive:true,
            maintainAspectRatio:false,
            legend: {
            display: false,
            },
            tooltips:{
                enabled:false
            },
            title:{

            },
            scales: {
                xAxes: [{
                    display:false,
                    stacked: true,
                    barPercentage:1.0,
                    categoryPercentage:1.0,
                    ticks:{
                        max:1
                    }
                }],
                yAxes: [{

                    stacked: true,
                    barPercentage:1.0,
                    categoryPercentage:1.0,
                    ticks: {
                        fontSize: 10
                    }
                }]
            }
        }
    });
   // myBarChart.update();
    return myBarChart;
}



function createScatterChart(context,data){

    var scatterChart = new Chart(context, {
    type: 'scatter',
    data: {
        datasets: [
        {'data': data, 'backgroundColor': '#669999', 'type': 'scatter', 'order': 1},
         {'data': [], 'backgroundColor': '#669999', 'type': 'scatter', 'order': 1},
        {'data': [], 'backgroundColor': '#999900', 'type': 'scatter', 'order': 1},
        {backgroundColor:"red",borderColor:"red",data:[{x:0,y:30},{x:86400,y:30}],type:"line",showLine:true,fill:false,borderWidth:1,order:2,alwaysVisible:true,pointRadius:0},
        ]

    },
    options: {
    tooltips:{
        callbacks:{

            label: function(tooltipItem, data){
                data = data.datasets[0].data[tooltipItem.index]
                console.log("item is", tooltipItem)
                var date = new Date(data["x"]*1000);
                console.log(date)
                return data["obsClass"] + " - " + data["y"] + " mph at " + moment(date).format("HH:mm:ss");
            }
        }
    },
    title: {
            display: false,
            text: ''
          },
          legend:{
            display:false
        },
    maintainAspectRatio:false,
            responsive: true,
        scales: {
            xAxes: [{
                type: 'linear',
                position: 'bottom',
                ticks:{
                    maxTicksLimit:6,
                    max:86400,
                    stepSize:7200,

                    callback: function(label, index, labels) {
                        return moment.utc(label*1000).format('HH:mm');
                    }
                }
            }]
        }
    }
});




return scatterChart;


    chart = new Chart(context,{
        type: 'scatter',
        data: [{x:0,y:200},{x:0,y:350},{x:1,y:12},{x:2,y:156}],

        options: {


            maintainAspectRatio:false,
            responsive: true,
          title: {
            display: false,
            text: ''
          },
          legend:{
            display:false
        },
        }
    });
    return chart;
}



function createLineChart(context,data){
    chart = new Chart(context, {
      type: 'line',
      data: data,
      options: mainLineGraphOptions
    });
    return chart;
}
function LondoncreateLineChart(context,data){
    chart = new Chart(context, {
      type: 'line',
      data: data,
      options: LondonmainLineGraphOptions
    });
    return chart;
}
function comparisoncreateLineChart(context,data){
    chart = new Chart(context, {
      type: 'line',
      data: data,
      options: comparisonmainLineGraphOptions
    });
    return chart;
}



function createStackedBarChart(context,data){
    chart = new Chart(context, {

      type: 'bar',
      data: data,
      options: stackedBarOptions
    });
    return chart;
}



function addBarChartToWidget(){

    var wrapper = document.createElement("div");
    wrapper.classList.add("canvaswrapper");

    wrapper.style.height="200px";
    wrapper.style.width="200px";
    var canvas = document.createElement("canvas");
    wrapper.appendChild(canvas);
    var ctx = canvas.getContext('2d');
    canvas.style.height="100%";
    canvas.style.width="100%";
    //ctx.canvas.setAttribute('width', '200');
    //ctx.canvas.setAttribute('height', '25');
    var chart = createBarChart(ctx);
    chart.update();
    return wrapper;
}

function getLimitLines(divisor){
    if(!divisor){
        divisor=1;
    }
    var lines = [];

    var limits = document.getElementById("graph-limit-popup").getElementsByClassName("selectable-menu-item");
    for(var i=0;i<limits.length;i++){
        if(limits[i].classList.contains("selected")){
            var y = limits[i].parentNode.getAttribute("data-limit")/divisor;
            var lowtext = limits[i].parentNode.getAttribute("data-text-low")
            var hightext = limits[i].parentNode.getAttribute("data-text-high")
            var col = limits[i].parentNode.getAttribute("data-col")
            var lowcol = limits[i].parentNode.getAttribute("data-col-low")
            var highcol = limits[i].parentNode.getAttribute("data-col-high")
            lines.push({"y": y,"lowcol": lowcol,"highcol":highcol,"lowtext":lowtext,"hightext":hightext,"style":col});
            //console.log("pushing line",lines);
        }
    }
    return lines;
}

function displayLimitLines(selectedChart,lines){
    //
    // divisor is the factor by which the limit line is divided , based on the selected time period, eg
    // if the selected time period is 30 mins, then all limits are divided by 2
    //
    selectedChart.options.scales.yAxes[0].ticks.suggestedMax = 0.1;

    var maxY = 0;
    for (var i=0;i<lines.length;i++){
        if (lines[i].y > maxY){
            maxY = lines[i].y;
        }
    }
    console.log("maxY is",maxY);
    console.log("Y axis ticks are",yAxesticks[0],selectedChart.yAxesticks[0]);
    var maxYaxisValue = selectedChart.yAxesticks[0];
    console.log("maxY is",maxY,"maxYaxisValue is",maxYaxisValue,maxY > maxYaxisValue);

    if (maxY > maxYaxisValue){
        selectedChart.options.scales.yAxes[0].ticks.suggestedMax = maxY;
    }
    console.log("at this point suggested is",selectedChart.options.scales.yAxes[0].ticks.suggestedMax)

    console.log("now suggested is",selectedChart.options.scales.yAxes[0].ticks.suggestedMax)
    console.log("lines are",lines);
    selectedChart.options.horizontalLine = lines;
    selectedChart.update();
    selectedChart.yAxesticks = yAxesticks
    console.log("y axis ticks are now",selectedChart.yAxesticks);
    if (selectedChart.yAxesticks.length > 1){
        var gap = selectedChart.yAxesticks[0] - selectedChart.yAxesticks[1];
        gap = Math.round(gap * 100) / 100
    }
    else{
        var gap = 20;
    }
    if (selectedChart.yAxesticks[0] == maxY){
        console.log("readujsting y axis values again",gap,maxY,Math.ceil((maxY + 1) / gap),Math.ceil((maxY + 1) / gap) * gap);
        if (maxY < 1){
            selectedChart.options.scales.yAxes[0].ticks.suggestedMax = maxY + gap;
        }
        else{
            selectedChart.options.scales.yAxes[0].ticks.suggestedMax =Math.ceil((maxY + 1) / gap) * gap;
        }
        //selectedChart.options.scales.yAxes[0].ticks.suggestedMax =Math.ceil((maxY + 1) / gap) * gap;
        selectedChart.update();
    }
}


var horizonalLinePlugin = {
    afterDraw : function(chartInstance) {
    var yValue;
    var yScale = chartInstance.scales["y-axis-0"];
    var canvas = chartInstance.chart;
    var ctx = canvas.ctx;
    ctx.font='bold 12px Arial';

    var lineHeight=ctx.measureText('M').width;
    var index;
    var line;
    var style;
    //console.log("chart instance",chartInstance,chartInstance.options.horizontalLine)
    if (chartInstance.options.horizontalLine) {
        //console.log("chart area is",chartInstance.chartArea);
      for (index = 0; index < chartInstance.options.horizontalLine.length; index++) {
        line = chartInstance.options.horizontalLine[index];
        //.log("drawing line",line)
        if (!line.style) {
            line.style = "rgba(169,169,169, .6)";
          line.lowcol = "rgba(169,169,169, .6)";
          line.highcol = "rgba(169,169,169, .6)";
        }
        if (line.y) {
          yValue = yScale.getPixelForValue(line.y);
        } else {
          yValue = 0;
        }

        ctx.lineWidth = 3;

        if (yValue) {
          ctx.beginPath();
          ctx.moveTo(chartInstance.chartArea.left, yValue);
          ctx.lineTo(chartInstance.chartArea.right, yValue);
          ctx.strokeStyle = line.style;
          ctx.stroke();
        }

        if (line.text) {
          ctx.fillStyle = line.lowcol;
          ctx.fillText(line.text, chartInstance.chartArea.left + 5, yValue + lineHeight);
        }
        if (line.lowtext) {
          ctx.fillStyle = line.lowcol;
          ctx.fillText(line.lowtext, chartInstance.chartArea.left + 5, yValue + lineHeight);
        }
        if (line.hightext) {
          ctx.fillStyle = line.highcol;
          ctx.fillText(line.hightext, chartInstance.chartArea.left + 5, yValue -  lineHeight - ctx.lineWidth - 10);
        }

      }
      return;
    }
  }
};

Chart.pluginService.register(horizonalLinePlugin);

var buildGraphLabels;

function displayGraph(graph,visibleDatasets){
    if(!graph){
        return;
    }
    console.log("in display graph",visibleDatasets);
    console.log(graph)
    if(graph.config.type == "doughnut"){
        var dataset = [];
        var colors  = [];
        var labels  = [];
        var total = 0;
        for (var i=0;i<visibleDatasets.length;i++){
            var index = visibleDatasets[i];
            //console.log("looking at data",graph.data)
            if (graph.data.baseData[index].data.length){
                total = total + graph.data.baseData[index].data[0];
            }

            dataset.push(graph.data.baseData[index].data[0]);
            colors.push(graph.data.baseData[index].backgroundColor);
            labels.push(graph.data.baseData[index].label);

        }
        graph.data.datasets[0].data = dataset;
        graph.data.datasets[0].backgroundColor = colors;
        graph.data.labels = labels;
        if(graph.canvas.parentNode.getElementsByClassName("donut-text")[0]){
            var spans = graph.canvas.parentNode.getElementsByClassName("donut-text")[0].getElementsByTagName("span");
            spans[1].innerText = total;
            spans[0].innerText = graph.data.direction.descriptive;
        }
    }
    else{
        //console.log("graph data is",graph.data);
        graph.data.datasets.forEach(function(dataset, i) {
            if(!dataset.alwaysVisible){
                dataset.hidden = true;
            }

        });
        for (var i=0;i<visibleDatasets.length;i++){
            var index = visibleDatasets[i];
            if(graph.data.datasets[index]){
                graph.data.datasets[index].hidden = false;
            }

        }
        //graph.canvas.parentNode.parentNode.getElementsByTagName("h6")[0].innerText = graph.data.direction.descriptive;
    }
    graph.update()
}


function resizeDailyGraphs(chart){
    return;
    console.log("chart",chart.config.type,chart.canvas.offsetWidth,chart.canvas.offsetHeight);
    parent = chart.canvas.parentNode;
    console.log("parent",parent.offsetWidth,parent.offsetHeight);
    //chart.canvas.width = parent.
    if(chart.config.type == "doughnut"){
        parent.style.height = chart.canvas.offsetWidth + "px";
    }
    if(chart.config.type == "line"){
        var col = chart.canvas.parentNode.parentNode.parentNode.parentNode;
        //parent.style.height = chart.canvas.offsetWidth + "px";
    }
}


function resizeCanvas(chart){
return;
    console.log("chart",chart.config.type,chart.canvas.offsetWidth,chart.canvas.offsetHeight);
    parent = chart.canvas.parentNode;
    console.log("parent",parent.offsetWidth,parent.offsetHeight);
    //chart.canvas.width = parent.
    if(chart.config.type == "doughnut"){
        parent.style.height = chart.canvas.offsetWidth + "px";
    }
    //parent.style.height = chart.canvas.offsetWidth + "px";
    return
    var canvas = vivacityMainChart.canvas;
    //console.log("size",canvas.width,canvas.height);
    //console.log("parent is",canvas.parentNode);
    //console.log("size is",canvas.parentNode.offsetWidth,canvas.parentNode.offsetHeight)
    var heatmap = document.getElementById("heatmap");
    if(heatmap){
        heatmap.innerHTML = "";
        if(heatmapData){
            addHeatMapToWidget(document.getElementById("heatmap"),heatmapData);
            hideGreyedOut();
        }
    }

}