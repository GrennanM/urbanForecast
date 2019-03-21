var ref = firebase.database().ref('weather');

var totalNumberCols = 6;

// read last entry in db
ref.limitToLast(1).on('value', function snapshotToArray(snapshot) {

  // get the reference for the table body
  var tblBody = document.getElementById('tblBody');

  // for each entry in db
  snapshot.forEach(function(childSnapshot) {
    var tempArr = []
    var orderedTempArray = []

    // for each weather property
    childSnapshot.forEach(function(attribute) {
      var weatherValue = attribute.val();
      tempArr.push(weatherValue);
    });

    // re-order elements in temp array
    var roundedTime = tempArr[5];
    var waveHeight = tempArr[9];
    var windDir = tempArr[1];
    var avgWind = tempArr[0];
    var tideHeight = tempArr[7];
    var starRating = tempArr[6];

    orderedTempArray.push(roundedTime, waveHeight, windDir, avgWind, tideHeight,
      starRating);

    // creating rows in table body
    var row = document.createElement("tr");

    // create cells in row and append weather readings
    for (var c = 0; c < totalNumberCols; c++) {
      var cell = document.createElement("td");
      var cellText = document.createTextNode(orderedTempArray[c]);
      cell.appendChild(cellText);
      row.appendChild(cell);
    }

    // append row to table body
    tblBody.appendChild(row);

  });

});
