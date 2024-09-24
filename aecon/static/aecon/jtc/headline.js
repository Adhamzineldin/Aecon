var map = L.map('countline-map').setView([40.7128, -74.0060], 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '© OpenStreetMap contributors',
maxZoom: 20
}).addTo(map);


var circleMarkers = [];
var boxMarkers = [];
var armNameLabelMarkers = [];

function initMapWithDetails(coordinates, index, armId, projectId) {
  const nextIndex = (index + 1) % armsData.length;
  let bearingforDirection = calculateBearing([armsData[nextIndex].lat, armsData[nextIndex].lon], coordinates);

  const coordinates1 = (coordinates[0] + armsData[index].lat) / 2;
  const coordinates2 = (coordinates[1] + armsData[index].lon) / 2;
  const midPoint = [coordinates1, coordinates2];

  // Create a blue circle marker with arm name
  const circleMarker = L.circleMarker(midPoint, {
    radius: 10,
    color: '#141b4d',
    fillColor: 'white',
    fillOpacity: 0.5,
  }).addTo(map);

  circleMarkers.push(circleMarker);
  let bearing = calculateBearing(midPoint, coordinates) + 85;
  bearingforDirection = (bearing + 360) % 360;

  let htmlBody = `<div class="box-container" style="transform: rotate(${bearing}deg);margin-top: -20px">`;
  
  const addBox = (armData, arrowDirection, additionalClass = '') => {
    //Uncomment to bring arrows back on map
    // htmlBody += `<div class="box01 ${arrowDirection} ${additionalClass}" id="mapBox_${armId}_${armData.id}" data-lat="${armData.lat}" data-lon="${armData.lon}">
    //                 <span id="mapdata_${armId}_${armData.id}" class="${bearing > 110 && bearing < 250 ? 'rotated-text' : ''}">0</span>
    //              </div>`;
  };
  const sortedArmsData = [...armsData];

  sortedArmsData.sort((a, b) => {
    let directionA = calculateArrowDirection([a.lat, a.lon], coordinates, bearingforDirection);
    let directionB = calculateArrowDirection([b.lat, b.lon], coordinates, bearingforDirection);
    if(a.id == armsData[index].id){
      directionA = 'U-turn'
    }
    if(b.id == armsData[index].id){
      directionB = 'U-turn'
    }

    if (directionA === 'right' && directionB !== 'right') {
        return -1;
    } else if (directionA !== 'right' && directionB === 'right') {
        return 1;
    } else if (directionA === 'left' && directionB !== 'left') {
        return 1;
    } else if (directionA !== 'left' && directionB === 'left') {
        return -1;
    } else {
        return 0;
    }
  });


  // Loop through the sorted array
  for (const armData of sortedArmsData) {
    if (projectId === armData.project) {
      const armCoordinates = [armData.lat, armData.lon];
      let arrowDirection = calculateArrowDirection(armCoordinates, coordinates, bearingforDirection);
      if (armData.id === armId) {
        arrowDirection = 'u-turn';
      }

      addBox(armData, arrowDirection);
    }
  }
  
  htmlBody += '</div>';

  const boxIcon = L.divIcon({
    className: 'location_detail',
    html: htmlBody,
  });

  // Create a marker for the box and add it to the map
  const boxMarker = L.marker([armsData[index].lat, armsData[index].lon], { icon: boxIcon }).addTo(map);

  boxMarkers.push(boxMarker);

  // Create an L.divIcon for the arm name label
  const armNameLabel = L.divIcon({
    className: 'arm-name-label',
    html: `<div id="${armsData[index].id}">${armsData[index].name}</div>`,
  });

  // Create a marker for the arm name label and add it to the map
  const armNameLabelMarker = L.marker(midPoint, { icon: armNameLabel }).addTo(map);

  armNameLabelMarkers.push(armNameLabelMarker);

  // Ensure armNameLabelMarker is displayed above boxMarker
  armNameLabelMarker.setZIndexOffset(1000);
}

// Function to calculate arrow direction (left, right, up, or u-turn)
function calculateArrowDirection(armCoordinates, midPoint, bearing) {
  var armBearing = calculateBearing(midPoint, armCoordinates);
  var relativeBearing = (armBearing - bearing + 360) % 360; // Adjusted for relative bearing

  if (relativeBearing < 45 || relativeBearing >= 315) {
    return 'right'; 
  } else if (relativeBearing >= 45 && relativeBearing < 180) {
    return 'left';
  } else if (relativeBearing >= 225 && relativeBearing < 315) {
    return 'up';
  } else {
    return 'left';
  }
}

function calculateBearing(from, to) {
	var lat1 = from[0] * Math.PI / 180;
	var lon1 = from[1] * Math.PI / 180;
	var lat2 = to[0] * Math.PI / 180;
	var lon2 = to[1] * Math.PI / 180;
  
	var y = Math.sin(lon2 - lon1) * Math.cos(lat2);
	var x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
  
	var bearing = Math.atan2(y, x) * 180 / Math.PI;
  
	return (bearing + 360) % 360;
}
  
function removeMarkersForArm() {
    circleMarkers.forEach(marker => map.removeLayer(marker));
    boxMarkers.forEach(marker => map.removeLayer(marker));
    armNameLabelMarkers.forEach(marker => map.removeLayer(marker));

    // Clear the arrays
    circleMarkers = [];
    boxMarkers = [];
    armNameLabelMarkers = [];
}


function toggleExpandMap(){
  
}