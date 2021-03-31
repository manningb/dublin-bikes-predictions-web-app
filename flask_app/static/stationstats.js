//(number);


google.charts.load("current", { packages: ["corechart", "gauge","calendar"] });
var Myarr;

function fetch48(number) {
  fetch("/hour48-" + number)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      //("data: ", data);
      var arr = [];

      for (var date in data) {
        arr.push([date, data[date]]);
      }
      console.log(arr);
      var graphdata = new google.visualization.DataTable();
      graphdata.addColumn("string", "time_queried");
      graphdata.addColumn("number", "available_bike_stands");
      graphdata.addRows(arr);
      google.charts.setOnLoadCallback(drawChart48hr(graphdata));
    });
}


function fetchAverage(number) {
  fetch("/averagestation-" + number)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      //("data: ", data);
      google.charts.setOnLoadCallback(drawCalAvailBikeStation(data));
      google.charts.setOnLoadCallback(drawCalAvailBikes(data));
    });
}

function fetchStation(number) {
  fetch("/statstation-" + number)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      //("data: ", data);
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
      //(Myarr["station"][0]["available_bike_stands"]);
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
      google.charts.setOnLoadCallback(drawPieChart(pieData));
      google.charts.setOnLoadCallback(drawChart(graphdata));
    });
}
fetchStation(number);

fetch48(number);

fetchAverage(number);


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

function drawChart48hr(data) {
  var options = {
    title: "Predicted Available Bike Stands",
    legend: { position: "bottom" },
  };

  var chart = new google.visualization.LineChart(
    document.getElementById("48hour")
  );

  chart.draw(data, options);
}

function drawPieChart(pieData) {
  //(pieData);
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
  //(finaldata);
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
  //(finaldata);
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
