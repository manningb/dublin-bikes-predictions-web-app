console.log(number);
google.charts.load("current", { packages: ["corechart"] });
google.charts.load("current", { packages: ["calendar"] });
var Myarr;
fetchAverage(number);
function fetchAverage(number) {
  fetch("/averagestation-" + number)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log("data: ", data);
      google.charts.setOnLoadCallback(drawCalAvailBikes(data));
      google.charts.setOnLoadCallback(drawCalAvailBikeStation(data));
    });
}

function fetchStation(number) {
  fetch("/statstation-" + number)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log("data: ", data);
      Myarr = data;
      document.getElementById("status").innerText =
        Myarr["station"][0]["station_status"];
      if (Myarr["station"][0]["station_status"] == "OPEN") {
        document.getElementById("status").style.color = "green";
      } else {
        document.getElementById("status").style.color = "red";
      }
      var graphdata = new google.visualization.DataTable();
      var availbleRows = [];
      var pieData = new google.visualization.DataTable();
      pieData.addColumn("string", "Type");
      pieData.addColumn("number", "Number");
      console.log(Myarr["station"][0]["available_bike_stands"]);
      pieData.addRows([
        ["Available bike stands", Myarr["station"][0]["available_bike_stands"]],
        ["Available Bikes", Myarr["station"][0]["available_bikes"]],
      ]);
      graphdata.addColumn("string", "time_queried");
      graphdata.addColumn("number", "available_bike_stands");

      Myarr["station"].forEach((element) => {
        availbleRows.push([
          element["time_queried"],
          element["available_bikes"],
        ]);
      });
      graphdata.addRows(availbleRows);
      google.charts.setOnLoadCallback(drawChart(graphdata));
      google.charts.setOnLoadCallback(drawPieChart(pieData));
    });
}
fetchStation(number);

function drawChart(data) {
  var options = {
    title: "Available Bike Stands",
    legend: { position: "bottom" },
  };

  var chart = new google.visualization.LineChart(
    document.getElementById("curve_chart")
  );

  chart.draw(data, options);
}

function drawPieChart(pieData) {
  console.log(pieData);
  var data = pieData;

  var options = {
    title: "Current availability",
    pieHole: 0.4,
  };

  var chart = new google.visualization.PieChart(
    document.getElementById("donutchart")
  );
  chart.draw(data, options);
}

function drawCalAvailBikes(data) {
  var dataTable = new google.visualization.DataTable();
  dataTable.addColumn({ type: "date", id: "Date" });
  dataTable.addColumn({ type: "number", id: "Availability" });

  var finaldata = [];
  data.forEach((element) => {
    finaldata.push([
      new Date(element["yearq"], element["monthq"], element["dateq"]),
      parseFloat(element["avgavailbikes"]),
    ]);
  });
  console.log(finaldata);
  dataTable.addRows(finaldata);

  var chart = new google.visualization.Calendar(
    document.getElementById("calendar_basic")
  );

  var options = {
    title: "Average available bikes",
    height: 350,
  };

  chart.draw(dataTable, options);
}

function drawCalAvailBikeStation(data) {
  var dataTable = new google.visualization.DataTable();
  dataTable.addColumn({ type: "date", id: "Date" });
  dataTable.addColumn({ type: "number", id: "Availability" });

  var finaldata = [];
  data.forEach((element) => {
    finaldata.push([
      new Date(element["yearq"], element["monthq"], element["dateq"]),
      parseFloat(element["avgavailbikestation"]),
    ]);
  });
  console.log(finaldata);
  dataTable.addRows(finaldata);

  var chart = new google.visualization.Calendar(
    document.getElementById("calendar_basic_stations")
  );

  var options = {
    title: "Average available bike Stations",
    height: 350,
  };

  chart.draw(dataTable, options);
}
