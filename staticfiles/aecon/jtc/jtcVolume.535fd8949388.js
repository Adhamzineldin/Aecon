function VehicleChartData(jtc_data, selectedValue) {
    const ctx = document.getElementById("classedVehicleChart");
    // Get the associated Chart object
    const existingChart = Chart.getChart(ctx);

    // Destroy the existing chart if it exists
    if (existingChart) {
        existingChart.destroy();
    }
    const allData = jtc_data.data;

    var selectedStartTime = "07:00";
    var selectedEndTime = "19:00";
    var selectedClassId = '';
    var selectedOrigin = '';
    var selectedDestination = '';
    
    if (selectedValue !== '') {
        selectedStartTime = selectedValue.startTime != undefined && selectedValue.startTime != null ? selectedValue.startTime : '07:00';
        selectedEndTime = selectedValue.endTime != undefined && selectedValue.endTime != null ? selectedValue.endTime : '19:00';
        selectedClassId = selectedValue.classification !== undefined && selectedValue.classification !== null ? selectedValue.classification : '';
        selectedOrigin = selectedValue.originArm !== undefined && selectedValue.originArm !== null ? selectedValue.originArm : '';
        selectedDestination = selectedValue.destArm !== undefined && selectedValue.destArm !== null ? selectedValue.destArm : '';
    }
   
    // Combine counts for each class across selected records
    const classDetails = location_details.classes;

    // Initialize combinedData with all class names
    const combinedData = {};
    classDetails.forEach(classItem => {
        const classId = classItem.id;
        combinedData[classId] = {
            id: classId,
            name: classItem.name,
            order: classItem.order,
            count: 0
        };
    });

    allData.forEach(record => {
        // Filter records based on selected criteria if filter data is not null
        const filteredTimeSlots = record.value.filter(timeSlot => {
            const timeInRange = (
                (!selectedStartTime || timeSlot.Start_time >= selectedStartTime) &&
                (!selectedEndTime || timeSlot.End_time <= selectedEndTime)
            );
            const originMatch = (!selectedOrigin || record.origin_arm == selectedOrigin);
            const destinationMatch = (!selectedDestination || record.destination_arm == selectedDestination);
            return timeInRange && originMatch && destinationMatch;
        });
        // If filter data is null or any time slots match the criteria, proceed with combining counts
        if (!filteredTimeSlots || filteredTimeSlots.length > 0) {
            filteredTimeSlots.forEach(timeSlot => {
                timeSlot.class.forEach(classItem => {
                    const classId = classItem.id;
                   
                    if (selectedClassId.length === 0 || selectedClassId.includes(classId.toString())) {
                        combinedData[classId].count += classItem.count;
                    }else{
                        combinedData[classId].count = 0
                    }
                });
            });
        }
    });

    // Calculate total count
    const totalCount = Object.values(combinedData).reduce((sum, item) => sum + item.count, 0);

    // Extract the labels and data for the chart, with rounded percentages
    const labels = Object.keys(combinedData).map(classId => {
        const classInfo = location_details.classes.find(c => c.id == classId);
        return classInfo ? classInfo.name : "";
    });

    const chartData = Object.values(combinedData).map(item => ((item.count / totalCount) * 100).toFixed(2));

    // Your existing chart creation code
    const myChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    data: chartData,
                    backgroundColor: [
                        '#5b9bd6',
                        '#209022',
                        '#fe5104',
                        '#63666a',
                        '#141b4d',
                        '#ff0000',
                        '#12d231'
                    ],
                    borderWidth: 1,
                    borderRadius: 10,
                    datalabels: {
                        anchor: "end",
                        align: "end",
                        color: "black",
                        font: {
                            weight: "bold",
                        },
                        formatter: function (value, context) {
                            return value + '%';
                        }
                    },
                },
            ],
        },
        plugins: [ChartDataLabels],
        options: {
            scales: {
                y: {
                    ticks: {
                        display: false,
                    },
                    grid: {
                        display: false,
                        color: "rgba(0, 0, 0, 0)",
                    },
                    gridLines: {
                        color: "rgba(0, 0, 0, 0)",
                    },
                },
                x: {
                    grid: {
                        display: false,
                    },
                },
            },
            legend: {
                display: false,
            },
            plugins: {
                legend: {
                    display: false,
                },
            },
            layout: {
                padding: {
                    top: 22
                }
            },
        },
    });
}


function numberOfVehicleChart(jtc_data, selectedValue) {
    const cty = document.getElementById("numberOfVehicleChart");
    // Get the associated Chart object
    const existingChart = Chart.getChart(cty);

    // Destroy the existing chart if it exists
    if (existingChart) {
        existingChart.destroy();
    }

    const allData = jtc_data.data;

    var selectedStartTime = "07:00";
    var selectedEndTime = "19:00";
    var selectedClassId = '';
    var selectedOrigin = '';
    var selectedDestination = '';

    if (selectedValue !== '') {
        selectedStartTime = selectedValue.startTime !== undefined && selectedValue.startTime !== null ? selectedValue.startTime : '07:00';
        selectedEndTime = selectedValue.endTime !== undefined && selectedValue.endTime !== null ? selectedValue.endTime : '19:00';
        selectedClassId = selectedValue.classification !== undefined && selectedValue.classification !== null ? selectedValue.classification : '';
        selectedOrigin = selectedValue.originArm !== undefined && selectedValue.originArm !== null ? selectedValue.originArm : '';
        selectedDestination = selectedValue.destArm !== undefined && selectedValue.destArm !== null ? selectedValue.destArm : '';
    }

    // Define all the 15-minute intervals between 07:00 and 19:00
    const allIntervals = [];
    let currentTime = "07:00";
    while (currentTime <= "19:00") {
        allIntervals.push(currentTime);
        const [hours, minutes] = currentTime.split(":").map(Number);
        const totalMinutes = hours * 60 + minutes + 15;
        currentTime = `${Math.floor(totalMinutes / 60)
            .toString()
            .padStart(2, "0")}:${(totalMinutes % 60).toString().padStart(2, "0")}`;
    }

    const groupedTimeSlots = {};
    allData.forEach(record => {
        const filteredTimeSlots = record.value.filter(timeSlot => {
            const timeInRange =
                (!selectedStartTime || timeSlot.Start_time >= selectedStartTime) &&
                (!selectedEndTime || timeSlot.End_time <= selectedEndTime);
            const originMatch = (!selectedOrigin || record.origin_arm == selectedOrigin);
            const destinationMatch = (!selectedDestination || record.destination_arm == selectedDestination);

            return timeInRange && originMatch && destinationMatch;
        });
        filteredTimeSlots.forEach(timeSlot => {
            const startTime = timeSlot.Start_time;
            const roundedStartTime = roundDownTo15Minutes(startTime);
        
            if (!groupedTimeSlots[roundedStartTime]) {
                groupedTimeSlots[roundedStartTime] = 0; // Initialize count to 0
            }
        
            timeSlot.class.forEach(classItem => {
                const classId = classItem.id;
                // Add the condition you've shared
                if (selectedClassId.length === 0 || selectedClassId.includes(classId.toString())) {
                    groupedTimeSlots[roundedStartTime] += classItem.count || 0;
                } else {
                    groupedTimeSlots[roundedStartTime] += 0;
                }
            });
        });
    });

    const intervalChartData = allIntervals.map(interval => {
        const roundedStartTime = roundDownTo15Minutes(interval);
        return groupedTimeSlots[roundedStartTime] || '';
    });

    new Chart(cty, {
        type: "line",
        data: {
            labels: allIntervals,
            datasets: [
                {
                    label: "",  // You can still leave the label empty if needed
                    data: intervalChartData,
                    borderColor: "#141b4d", // Line color
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4, // Smooth the line
                },
            ],
        },
        options: {
            animation: {
                duration: 0
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false  // This disables the legend (key with the colored box)
                },
                tooltip: {
                    intersect: false,
                    displayColors: false,
                    callbacks: {
                        label: function(tooltipItem, data) {
                            var text = [];
                            var datasets = data.datasets;
                            for (var i = 0; i < datasets.length; i++) {
                                if (i == tooltipItem.datasetIndex && datasets[i].data[tooltipItem.dataIndex] != 0) {
                                    text.push("Count: " + Math.abs(datasets[i].data[tooltipItem.dataIndex].toFixed(2)));
                                }
                            }
                            return text;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxTicksLimit: 25,
                        color: "#a0a6ac",
                        font: {
                            size: 11
                        }
                    },
                },
                y: {
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: 1,
                        color: "#a0a6ac",
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return Math.round(value * 100) / 100;
                        }
                    },
                    position: "left"
                }
            },
            layout: {
                padding: {
                    top: 30,
                },
            },
        },
    });
}



// Function to round down time to the nearest 15 minutes
function roundDownTo15Minutes(time) {
    const [hours, minutes] = time.split(":").map(Number);
    const roundedMinutes = Math.floor(minutes / 15) * 15;
    return `${hours.toString().padStart(2, "0")}:${roundedMinutes.toString().padStart(2, "0")}`;
}
