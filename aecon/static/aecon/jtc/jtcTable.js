
$("#sm-t-body").on("click", "td:not(:first-child, :last-child):not(:last-child):not(:last-child of tr:last-child)", function (e) {
	var clickedTd = $(e.target);
	if (!clickedTd.closest('tr').is(':last-child') || clickedTd.closest('tr').attr('id') !== 'jtc-counttr-data_Total') {
		if (clickedTd.hasClass("td-active") && clickedTd.hasClass("Filter") !== true) {
			$("#lg-table").css("display", "none");
			clickedTd.removeClass("td-active");
			$('#calender-content').addClass("calender-content");
			$('.box01').removeClass("td-active");
		} else {
			AppendPopumodaldata(clickedTd)
			totalcountofPopmodaltabl();
			calculateColumnTotals();
		}
	}
});


function AppendJtcCountdata(countdata, selectedValue, sec) {
	if (selectedValue !== '' && selectedValue.startTime !== '' && selectedValue.endTime !== '' && selectedValue.startTime > selectedValue.endTime) {
		alert('You cant set finish time to before the Start time');
		return;
	}
	countdata.forEach(({ origin_arm, destination_arm, value }) => {
		let TDtotalcount = 0;
		value.forEach(({ Start_time, End_time, class: classDetails }) => {
			if (isSelectedValueValid(selectedValue, { Start_time, End_time, class: classDetails })) {
				classDetails.forEach(({ count, id }) => {
					if (selectedValue.classification.length === 0 || selectedValue.classification.includes(id.toString())) {
						TDtotalcount += count;
					}
				});
			}
		});
		updateHTML(origin_arm, destination_arm, TDtotalcount);
	});

	$("#sm-t-body tr").each(function () {
		const rownumber = $(this).attr('id').split('_');
		$('#jtc-counttd-total_' + rownumber[1]).text('0');
		let rowSum = 0;

		$(this).find('td').each(function () {
			const cellValue = parseInt($(this).text());
			if (!isNaN(cellValue)) {
				rowSum += cellValue;
			}
		});

		$('#jtc-counttd-total_' + rownumber[1]).text(0);
		$('#jtc-counttd-total_' + rownumber[1]).text(rowSum);
	});

	const numCols = $('.small-table-tr thead tr th').length;
	let tdhtml = '<td>Total</td>';
	$('#jtc-counttr-data_Total').empty();

	for (let i = 1; i < numCols; i++) {
		let total = 0;

		$('.small-table-tr tbody tr').each(function () {
			const value = parseInt($(this).find(`td:eq(${i})`).text()) || 0;
			total += value;
		});

		tdhtml += `<td>${total}</td>`;
	}

	$('#jtc-counttr-data_Total').append(tdhtml);

	if (!$('#calender-content').hasClass("calender-content")) {
		$('#sm-t-body .td-active').each(function () {
			if ($(this).length === 1) {
				AppendPopumodaldata($(this));
				totalcountofPopmodaltabl();
				calculateColumnTotals();
			}
		});
	}
}

function updateHTML(originArm, destinationArm, totalCount) {
	$('#jtc-counttd-data_' + originArm + '_' + destinationArm).text(totalCount);
	$('#mapdata_' + originArm + '_' + destinationArm).html(totalCount);
}

function isSelectedValueValid(selectedValue, value) {
	if (selectedValue != '') {
		if (selectedValue.startTime != '' && selectedValue.endTime != '') {
			return (
				value.Start_time >= selectedValue.startTime &&
				value.End_time <= selectedValue.endTime
			);
		} else if (selectedValue.startTime != '' && value.Start_time >= selectedValue.startTime) {
			return true;
		} else if (selectedValue.endTime != '' && value.End_time <= selectedValue.endTime) {
			return true;
		}
	}

	return selectedValue == '' || (selectedValue.endTime == '' && selectedValue.startTime == '');
}

function calculateCountForValue(value, selectedValue) {
	if (value.class && value.class.length > 0) {
		if (selectedValue.classification != '') {
			for (var k = 0; k < value.class.length; k++) {
				if (value.class[k].id == selectedValue.classification) {
					return value.class[k].count || 0;
				}
			}
		} else {
			// If no classification is specified, return the count of the first class (if available)
			return value.class[0].count || 0;
		}
	}

	// Return 0 if there are no classes or no count information
	return 0;
}


function xyandmapdatahighlight(data,armData){
	if(data.destArm != '' && data.originArm != '' && data.destArm != 'All' && data.originArm != 'All'){
		$('.box01').removeClass("td-active");
		$('#sm-t-body td.td-active').removeClass('td-active');
		$('#jtc-counttd-data_'+data.originArm+'_'+data.destArm).addClass("td-active").addClass('Filter');
		$('#mapdata_'+data.originArm+'_'+data.destArm).closest('.box01').addClass("td-active").addClass('Filter');
	}else if(data.destArm != '' && data.originArm == ''){
		$('.box01').removeClass("td-active");
		$('#sm-t-body td.td-active').removeClass('td-active');
		for(i=0;i<location_details.arms.length;i++){
			$('#jtc-counttd-data_'+location_details.arms[i].id+'_'+data.destArm).addClass("td-active").addClass('Filter');
			$('#mapdata_'+location_details.arms[i].id+'_'+data.destArm).closest('.box01').addClass("td-active").addClass('Filter');
		}
	}else if(data.destArm == '' && data.originArm != ''){
		$('.box01').removeClass("td-active");
		$('#sm-t-body td.td-active').removeClass('td-active');
		for(i=0;i<location_details.arms.length;i++){
			$('#jtc-counttd-data_'+data.originArm+'_'+location_details.arms[i].id).addClass("td-active").addClass('Filter');
			$('#mapdata_'+data.originArm+'_'+location_details.arms[i].id).closest('.box01').addClass("td-active").addClass('Filter');
		}
	}else{
		$('.box01').removeClass("td-active");
		$('#sm-t-body td.td-active').removeClass('td-active');
	}
}



function createTableCell(id, content) {
	return `<td id="${id}">${content}</td>`;
}

function createTableRow(startTime, classId, count) {
	let htmlRow = `<tr>`;
	
	// Create cells for each column
	$("#countline-daily-table-avg-head tr.table-header th").each(function () {
		const cellId = $(this).attr('id');
		if (cellId === 'StartTime') {
			htmlRow += createTableCell('', startTime,'-');
		} else  {
			const cellClassId = `class_${classId}_${cellId}`;
			htmlRow += createTableCell(cellClassId, '-');
		}
	});

	htmlRow += `</tr>`;
	$('#countline-daily-table-avg-data').append(htmlRow);
}

function createTotalRow(hr, classId) {
	let htmlRow = `<tr class="total${hr}hr">`;

	// Create cells for each column
	$("#countline-daily-table-avg-head tr.table-header th").each(function () {
		const cellId = $(this).attr('id');
		if (cellId === 'StartTime') {
			htmlRow += createTableCell('', `${hr} HR`,'-');
		} else{
			const totalClassId = `totalhr_${classId}_${cellId}`;
			htmlRow += createTableCell(totalClassId, '-');
		}
	});

	htmlRow += `</tr>`;
	$('#countline-daily-table-avg-data').append(htmlRow);
}

function generateRows() {
	const startHour = 7;
	const endHour = 18;
	const intervalMinutes = 15;

	for (let hour = startHour; hour <= endHour; hour++) {
		for (let minute = 0; minute < 60; minute += intervalMinutes) {
			const formattedHour = hour.toString().padStart(2, '0');
			const formattedMinute = minute.toString().padStart(2, '0');
			const startTime = `${formattedHour}:${formattedMinute}`;
			if(startTime == '10:00'){
				createTotalRow(3, 'AM', '');
			}else if(startTime == '15:00'){
				createTotalRow(4, 'IP', '');
			}else{
				createTableRow(startTime, formattedMinute + '_' + formattedHour, '');
			}
			if (minute === 45) {
				createTotalRow(1, formattedMinute + '_' + formattedHour, '');
			}
			if(startTime == '18:45'){
				createTotalRow(5, 'PM', '');
			}
		}
	}

	 // Create the footer row
	 createTableFooter();

}

function AppendPopumodaldata(clickedTd) {
	clickedTd.removeClass("Filter");
	$('#countline-daily-table-avg-data').empty();
	$("#lg-table").css("display", "block");
	$("#sm-t-body td").removeClass("td-active");
	clickedTd.addClass("td-active");
	$('#calender-content').removeClass("calender-content");

	var  arms = clickedTd.attr('id').split('_');
	var originarm =arms[1]
	var destinationarm = arms[2]

	generateRows();
	let prevHourlyRow = '';
	let prevHourlyCount = 0;
	let hourlyCounts = {};
	// Initialize an object to store the total count for each class across all time intervals

	const columnTotalCounts = {};
	const amcolumnTotalCounts = {};
	const IPcolumnTotalCounts = {};
	const pmcolumnTotalCounts = {};

	jtc_DataDetails.forEach(({ origin_arm, destination_arm, value }) => {
		if (origin_arm == originarm && destination_arm == destinationarm) {
			// Create a map to store total counts for each class during the time interval
			const classTotalCounts = new Map();

			value.forEach(({ Start_time, End_time, class: classDetails }) => {
				if (isSelectedValueValid(selectedValue, { Start_time, End_time, class: classDetails })) {
					const splittime = Start_time.split(':');

					const isAMTimeInRange = splittime[0] >= '07' && splittime[0] < '10';
					const isIPTimeInRange = splittime[0] >= '10' && splittime[0] < '15';
					const isPMTimeInRange = splittime[0] >= '15' && splittime[0] < '19';
					classDetails.forEach(({ id, count }) => {
						if (selectedValue.classification.length === 0 || selectedValue.classification.includes(id.toString())) {							// Create a unique identifier for each class based on time and class id
							const classId = `class_${splittime[1]}_${splittime[0]}_${id}`;

							// Accumulate the count for each class
							classTotalCounts.set(classId, (classTotalCounts.get(classId) || 0) + count);

							// Accumulate the total count for each class column-wise
							columnTotalCounts[id] = (columnTotalCounts[id] || 0) + count;

							if(isAMTimeInRange){
								amcolumnTotalCounts[id] = (amcolumnTotalCounts[id] || 0) + count;
							}
							if(isIPTimeInRange){
								IPcolumnTotalCounts[id] = (IPcolumnTotalCounts[id] || 0) + count;
							}
							if(isPMTimeInRange){
								pmcolumnTotalCounts[id] = (pmcolumnTotalCounts[id] || 0) + count;
							}
						}
					});
				}
			});
	
			// Update the table cells with the accumulated counts
			classTotalCounts.forEach((total, classId) => {
				$('#' + classId).text(total);
	
				// Update hourlyCounts if needed
				const splittime = classId.split('_');
				const hourlyRow = classId.replace('class_', 'totalhr_').replace(`_${splittime[1]}_`, '_00_');
				hourlyCounts[hourlyRow] = (hourlyCounts[hourlyRow] || 0) + total;
			});
		}
	});

	// Update the last row of each column with the total count column-wise
	Object.entries(columnTotalCounts).forEach(([classId, totalCount]) => {
		const totalCellId = `class_total_${classId}`;
		$('#' + totalCellId).text(totalCount);
	});

	// Update the AM row of each column with the total count column-wise
	Object.entries(amcolumnTotalCounts).forEach(([classId, totalCount]) => {
		const totalCellId = `totalhr_AM_${classId}`;
		$('#' + totalCellId).text(totalCount);
	});

	// Update the IP row of each column with the total count column-wise
	Object.entries(IPcolumnTotalCounts).forEach(([classId, totalCount]) => {
		const totalCellId = `totalhr_IP_${classId}`;
		$('#' + totalCellId).text(totalCount);
	});

	// Update the PM row of each column with the total count column-wise
	Object.entries(pmcolumnTotalCounts).forEach(([classId, totalCount]) => {
		const totalCellId = `totalhr_PM_${classId}`;
		$('#' + totalCellId).text(totalCount);
	});



	// Update next 1-hour row with accumulated counts
	for (const [hourlyRow, count] of Object.entries(hourlyCounts)) {
		const nextHourlyRow = hourlyRow.replace('_00_', '_45_');
		const nextHourlyCell = $('#' + nextHourlyRow);
		const nextHourlyCount = parseInt(nextHourlyCell.text()) || 0;
		nextHourlyCell.text(nextHourlyCount + count);
	}

	if (url.includes('jtc-volume')) {
		selectedValue.originArm = originarm
		selectedValue.destArm = destinationarm
        VehicleChartData(jtc_data, selectedValue);
        numberOfVehicleChart(jtc_data, selectedValue);
    // }else if((url.includes('jtc-headline') || url.indexOf('jtc-data') ) ){
	// 	xyandmapdatahighlight(selectedValue);
	}
	
}

function totalcountofPopmodaltabl(){
	$('#countline-daily-table-avg tbody tr').each(function() {
		var total = 0;
		// Iterate through each cell in the row, excluding the last one
		$(this).find('td:not(:first,:last)').each(function() {
		  var value = parseInt($(this).text()) || 0;
		  total += value;
		});
	
		// Update the last column with the total
		$(this).find('td:last').text(total);
	});
	
	var numberOfClasses = $('[class^="totalhr_"]').length;
	// Iterate over each class
	for (var i = 1; i <= numberOfClasses; i++) {
		var className = 'totalhr_' + i;
		// Initialize the total for each column
		var totals = Array.from({ length: $('#countline-daily-table-avg tr.' + className + ' td').length }, () => 0);
		// Iterate through each row with the corresponding class
		$('#countline-daily-table-avg tr[class^="' + i + '_hr"]').each(function() {
		// Iterate through each cell in the row
			$(this).find('td:not(:first)').each(function(index) {
				var value = parseInt($(this).text()) || 0;
				totals[index] += value;
			});
		});

		// Update the total row with the calculated sums
		$('#countline-daily-table-avg tr.' + className + ' td:not(:first)').each(function(index) {
		$(this).text(totals[index]);
		});
	}

	$('#countline-daily-table-avg tfoot tr').each(function() {
		var total = 0;
		// Iterate through each cell in the row, excluding the last one
		$(this).find('td:not(:first,:last)').each(function() {
		  var value = parseInt($(this).text()) || 0;
		  total += value;
		});
	
		// Update the last column with the total
		$(this).find('td:last').text(total);
	});

}

function calculateColumnTotals() {
	var $table = $('#countline-daily-table-avg');
	var $rows = $table.find('tbody tr[class^="totalhr_"]');
  
	var numCols = $rows.first().find('td').length;
	var columnTotals = new Array(numCols).fill(0);
  
	$rows.each(function() {
	  var $cells = $(this).find('td');
  
	  $cells.each(function(index) {
		if(index != 0){
			var cellValue = parseInt($(this).text());
			if (!isNaN(cellValue)) {
				columnTotals[index] += cellValue;
			}
		}
	  });
	});
	var $footerRow = $table.find('tfoot tr');
  
	$footerRow.find('td').each(function(index) {
		if(index == 0){
			$(this).text('Totals');
		}else{
			$(this).text(columnTotals[index]);
		}
	  
	});
  }
  


function createArmHeader(arm, project_id) {
    let html2 = '<th>A</th>';
    let htmltableBody = '';
    let htmltableBodyTD = '';

    for (const armItem of arm) {
        if (project_id == armItem.project) {
            html2 += `<th>${armItem.name}</th>`;
            htmltableBody += `<tr class="small-table-tr" id="jtc-counttr-data_${armItem.id}">`;
            htmltableBody += `<td>${armItem.name}</td>`;

            const cnt = arm.findIndex(item => project_id == item.project);
            for (const armJ of arm) {
                if (project_id == armJ.project) {
                    htmltableBody += `<td id="jtc-counttd-data_${armItem.id}_${armJ.id}">0</td>`;
                }
            }
            htmltableBody += `<td id="jtc-counttd-total_${armItem.id}">0</td>`;
            htmltableBody += '</tr>';
        }
    }

    const peakhtmltablBody = arm.filter(item => project_id == item.project).map(item => `<tr><th>${item.name}</th><th>${item.Fullname}</th></tr>`).join('');

    $('.peak-tbody').empty().append(peakhtmltablBody);
    html2 += '<th>Total</th>';
    htmltableBody += '<tr class="small-table-tr" id="jtc-counttr-data_Total"><td>Total</td></tr>';

    $('#jtc-table-header').empty().append(html2);
    $('#sm-t-body').empty().append(htmltableBody);
}



function createModalpoputable(data){
	var htmltableBody = '<tr><th colspan="8" class="lg-table-top-text">Destination : Arm </th><th class="lg-table-top-border-text" style="border: 0;position: absolute;top: 16px;">Total</th></tr><tr class="table-header"><th id="StartTime" class="table-firstchild">time</th>';
	for(i=0;i<data.length;i++){
		htmltableBody += '<th id='+data[i].id+'>'+data[i].name+'</th>';
	}
	htmltableBody +=  '<th id="End"></th>'
	$('#countline-daily-table-avg-head').empty().append(htmltableBody)
}


function createTableFooter() {
	let htmlRow = '<tr>';

	// Create cells for each column
	$("#countline-daily-table-avg-head tr.table-header th").each(function () {
		const cellId = $(this).attr('id');
		if (cellId === 'StartTime') {
			htmlRow += '<td>Total</td>';
		} else{
			const totalClassId = `class_total_${cellId}`;
			htmlRow += `<td id="${totalClassId}">0</td>`;
		}
	});

	htmlRow += '</tr>';
	$('#countline-daily-table-avg-foot').empty().append(htmlRow);
}



