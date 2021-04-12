document.onreadystatechange = function () {
  loopThroughStations();
  var state = document.readyState;
  if (state === "interactive") {
    document.getElementById("contents").style.visibility = "hidden";
  } else if (state === "complete") {
    setTimeout(function () {
      document.getElementById("interactive");
      document.getElementById("load").style.visibility = "hidden";
      document.getElementById("contents").style.visibility = "visible";
    }, 1000);
  }
};

function msToBeaufort(ms) {
  return Math.ceil(Math.cbrt(Math.pow(ms / 0.836, 2)));
}

function loopThroughStations () {
fetch('static/js/static_bikes.json')
  .then(response => response.json())
  .then(data => {
    data.sort(function (a, b) {
    return a.number > b.number;
});

  	// Do something with your data
  	    data.forEach((element) => {
      $("#station_dd_3").append("<option value='/stationstats-" + element.number + "'>" + element.number + ": " + element.address + "</option>")
    });
  });
}

window.onload = function () {

  fetch("/current_weather")
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      var weather_icon_map = {
        Clouds: "cloudy",
        Fog: "fog",
        Mist: "rain-mix",
        Clear: "sunny",
        Rain: "rain",
        Drizzle: "sprinkle",
        Thunderstorm: "thunderstorm",
        Snow: "snow",
      };
      var d = new Date();
      var hour = d.getHours();
      var date = new Date().toLocaleString();
      var hour12 = hour % 12;
      var time;
      if (hour >= 7 && hour <= 20) {
        time = "day";
      } else {
        time = "night";
        weather_icon_map["Clear"] = "clear";
      }
      var tab = "&nbsp;&nbsp;&nbsp;&nbsp;";
      beaufortSpeed = Math.round(msToBeaufort(data["weather"][0].wind_speed));
      weather_class =
        "wi-" + time + "-" + weather_icon_map[data["weather"][0].weather_main];
      weatherIconElement = document.getElementById("weatherIcon");
      timeIconElement = document.getElementById("timeIcon");
      windDegIconElement = document.getElementById("windDegIcon");
      windSpeedIconElement = document.getElementById("windSpeedIcon");
      windDegIconElement.classList.add(
        "towards-" + data["weather"][0].wind_deg + "-deg"
      );
      windSpeedIconElement.classList.add("wi-wind-beaufort-" + beaufortSpeed);

      weatherIconElement.classList.add(weather_class);
      timeIconElement.classList.add("wi-time-" + hour12);
      temp_celsius = (parseFloat(data["weather"][0].temp) - 273.15).toFixed(2);
      feelslike_celsius = (
        parseFloat(data["weather"][0].feels_like) - 273.15
      ).toFixed(2);

      document.getElementById("weatherDescText").innerHTML +=
        data["weather"][0].weather_main +
        ", " +
        data["weather"][0].weather_description +
        tab;
      document.getElementById("timeText").innerHTML += date + tab;
      document.getElementById("tempText").innerHTML +=
        "Temp: " +
        temp_celsius +
        "°C, Feels Like: " +
        feelslike_celsius +
        "°C" +
        tab;
      document.getElementById("windText").innerHTML +=
        "Wind Speed: " + data["weather"][0].wind_speed + "m/s" + tab;
      document.getElementById("windDegText").innerHTML +=
        "Wind Degrees: " + data["weather"][0].wind_deg + "°" + tab;
    });
};
