var map, activeInfoWindow;
var stations = {}
var markers = {};
var search_markers = [];
let myLatLng = {lat: 53.3531, lng: -6.2580};
const $info = document.getElementById('info');
var directionsDisplay;
var directionsService;
var routeBounds = false;
var overlayWidth = 200; // Width of the overlay DIV
var leftMargin = 30; // Grace margin to avoid too close fits on the edge of the overlay
var rightMargin = 80; // Grace margin to avoid too close fits on the right and leave space for the controls
var after_directions_latlng;

$(document).ready(function () {
    $('.js-example-basic-single').select2();
    var actualDate = new Date();
    var newDate = new Date(actualDate.getFullYear(), actualDate.getMonth(), actualDate.getDate() + 13);

    $('#demo').datetimepicker({
        inline: true,
        todayHighlight: true,
        // autoclose: true,
        // startDate: new Date(),
        minDate: actualDate,
        maxDate: newDate
    });

});

$('#datetime_picker').on('click', function () {
    var d = $('#demo').datetimepicker('getValue');
    console.log(d.getDay());
    console.log(d.getHours());
});

function GetLatlong() {
  var geocoder = new google.maps.Geocoder();
  var address = document.getElementById('searchBox').value;

  geocoder.geocode({
    'address': address
  }, function(results, status) {

    if (status == google.maps.GeocoderStatus.OK) {
      var latitude = results[0].geometry.location.lat();
      var longitude = results[0].geometry.location.lng();
          myLatLng = {lat: latitude, lng: longitude}
console.log(myLatLng);
    }
  });
}
// https://stackoverflow.com/questions/24952593/how-to-add-my-location-button-in-google-maps
function addYourLocationButton(map, marker) {
    var controlDiv = document.createElement('div');

    var firstChild = document.createElement('button');
    firstChild.style.backgroundColor = '#fff';
    firstChild.style.border = 'none';
    firstChild.style.outline = 'none';
    firstChild.style.width = '28px';
    firstChild.style.height = '28px';
    firstChild.style.borderRadius = '2px';
    firstChild.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';
    firstChild.style.cursor = 'pointer';
    firstChild.style.marginRight = '10px';
    firstChild.style.padding = '0';
    firstChild.title = 'Your Location';
    controlDiv.appendChild(firstChild);

    var secondChild = document.createElement('div');
    secondChild.style.margin = '5px';
    secondChild.style.width = '18px';
    secondChild.style.height = '18px';
    secondChild.style.backgroundImage = 'url(https://maps.gstatic.com/tactile/mylocation/mylocation-sprite-2x.png)';
    secondChild.style.backgroundSize = '180px 18px';
    secondChild.style.backgroundPosition = '0 0';
    secondChild.style.backgroundRepeat = 'no-repeat';
    firstChild.appendChild(secondChild);

    google.maps.event.addListener(map, 'center_changed', function () {
        secondChild.style['background-position'] = '0 0';
    });

    firstChild.addEventListener('click', function () {
        var imgX = 0,
            animationInterval = setInterval(function () {
                imgX = -imgX - 18;
                secondChild.style['background-position'] = imgX + 'px 0';
            }, 500);

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                var latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                map.setCenter(latlng);
                clearInterval(animationInterval);
                secondChild.style['background-position'] = '-144px 0';
            });
        } else {
            clearInterval(animationInterval);
            secondChild.style['background-position'] = '0 0';
        }
    });

    controlDiv.index = 1;
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(controlDiv);
}

function stationToStation() {
    var selectedOptionVal1 = $('#station_dd_1').find(":selected").val();
    var selectedOptionVal2 = $('#station_dd_2').find(":selected").val();
    calcRoute({
        "lat": stations[selectedOptionVal1][0],
        "lng": stations[selectedOptionVal1][1]
    }, [stations[selectedOptionVal2][0], stations[selectedOptionVal2][1]], "bike");
    // $('#overlay').css({'opacity': 100});
    return false;
}


const trackLocation = ({
                           onSuccess, onError = () => {
    }
                       }) => {
    // Omitted for brevity

    return navigator.geolocation.getCurrentPosition(onSuccess, onError, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    });
};
const getPositionErrorMessage = code => {
    switch (code) {
        case 1:
            return 'Permission denied.';
        case 2:
            return 'Position unavailable.';
        case 3:
            return 'Timeout reached.';
        default:
            return null;
    }
}

function myClick(id) {
    google.maps.event.trigger(markers[id], 'click');
}

function initMap() {
    fetch("/stations").then(response => {
        return response.json();
    }).then(data => {


            directionsService = new google.maps.DirectionsService();

            var mapOptions = {
                zoom: 15,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                center: myLatLng,
                panControlOptions: {
                    position: google.maps.ControlPosition.TOP_RIGHT
                },
                zoomControlOptions: {
                    position: google.maps.ControlPosition.TOP_RIGHT
                }
            };

            map = new google.maps.Map(document.getElementById("map"), mapOptions);
            var searchBox = new google.maps.places.SearchBox(
                (document.getElementById('searchBox')));
            var myMarker = new google.maps.Marker({
                map: map,
                animation: google.maps.Animation.DROP,
                position: myLatLng
            });
            addYourLocationButton(map, myMarker);

            $("#searchBox").on('keypress', function (e) {
                // prevent form submission on pressing Enter as there could be more inputs to fill out
                if (e.which === 13) {
                    e.preventDefault();
                }
            });

            directionsDisplay = new google.maps.DirectionsRenderer({
                draggable: true,
                map,
                panel: document.getElementById("overlayContent")
            });
            directionsDisplay.setMap(map);


            // Listen for the event fired when the user selects an item from the
            // pick list. Retrieve the matching places for that item.
            google.maps.event.addListener(searchBox, 'places_changed', function () {
                var places = searchBox.getPlaces();
                // For each place, get the icon, place name, and location.
                search_markers = [];
                var bounds = new google.maps.LatLngBounds();
                var place = null;
                var viewport = null;
                for (var i = 0; place = places[i]; i++) {
                    var image = {
                        url: place.icon,
                        size: new google.maps.Size(71, 71),
                        origin: new google.maps.Point(0, 0),
                        anchor: new google.maps.Point(17, 34),
                        scaledSize: new google.maps.Size(25, 25)
                    };

                    // Create a marker for each place.
                    var marker = new google.maps.Marker({
                        map: map,
                        icon: image,
                        title: place.name,
                        position: place.geometry.location
                    });
                    viewport = place.geometry.viewport;
                    search_markers.push(marker);

                    bounds.extend(place.geometry.location);
                }
                map.setCenter(bounds.getCenter());
            });

            // Bias the SearchBox results towards places that are within the bounds of the
            // current map's viewport.
            google.maps.event.addListener(map, 'bounds_changed', function () {
                var bounds = map.getBounds();
                searchBox.setBounds(bounds);
            });

            const current_marker = new google.maps.Marker({
                position: {lat: 53.3531, lng: -6.2580},
                icon: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
                map
            });
            trackLocation({
                onSuccess: ({coords: {latitude: lat, longitude: lng}}) => {
                    current_marker.setPosition({lat, lng});
                    map.panTo({lat, lng});
                    myLatLng = {lat: lat, lng: lng};

                    // Print out the user's location.
                    $info.textContent = `Current Location Found! Lat: ${lat} Lng: ${lng}`;
                    // Don't forget to remove any error class name.
                    $info.classList.remove('error');
                    $info.classList.add('success');
                },
                onError: err => {
                    // Print out the error message.
                    $info.textContent = `Error: ${getPositionErrorMessage(err.code) || err.message}`;
                    // Add error class name.
                    $info.classList.add('error');
                    $info.classList.remove('success');
                }
            });
            var count = 0;
            data['station'].forEach(station => {
                stations[station.number] = [station.position_lat, station.position_lng, station.available_bikes, station.available_bike_stands];
                const infoWindow = new google.maps.InfoWindow({
                    content: '<h1>' + station.address + '</h1>' + '<p>Available Bikes: ' + station.available_bikes + '</p>' + '<p>Available Bike Stands: ' + station.available_bike_stands + '</p><p>' + station.last_update + '</p>' + '<a href="stationstats-' + station.number + '">View Statistics</a>',
                });

                $("#station_dd_1").append("<option value='" + station.number + "'>" + station.number + ": " + station.address + "</option>")
                $("#station_dd_2").append("<option value='" + station.number + "'>" + station.number + ": " + station.address + "</option>")
                var availability_percentage = parseInt(station.available_bikes) / (parseInt(station.available_bikes) + parseInt(station.available_bike_stands));
                if (availability_percentage > .7) {
                    color = "green";
                } else if (availability_percentage > .3) {
                    color = "orange";
                } else {
                    color = "red";
                }
                let url = "http://maps.google.com/mapfiles/ms/icons/";
                url += color + "-dot.png";
                console.log(url);
                const marker = new google.maps.Marker({
                    position: {lat: station.position_lat, lng: station.position_lng},
                    map,
                    icon: {
                        url: url
                    },
                    title: station.address,
                });


                google.maps.event.addListener(marker, 'click', function () {
                    activeInfoWindow && activeInfoWindow.close();
                    infoWindow.open(map, marker);
                    activeInfoWindow = infoWindow;
                });
                markers[station.number] = marker;

                $("#bikes_list").append('<a href="#" onclick="myClick(' + station.number + ');" class="list-group-item list-group-item-action flex-column align-items-start"><div class="d-flex w-100 justify-content-between">\n' +
                    '                    <h5 class="mb-1">' + station.address + '</h5>\n' +
                    '                    <small>' + station.last_update +
                    '+</small>\n' +
                    '                </div>\n' +
                    '                <p class="mb-1">Available Bikes:' + station.available_bikes + '</p>\n' +
                    '            </a>'
                )
                ;
                count++;
            });

        }
    )
}

function findNow(bike_or_station) {
    num = calcDist(bike_or_station);
    myClick(num);
    calcRoute(myLatLng, [stations[num][0], stations[num][1]], bike_or_station);
    // $('#overlay').css({'opacity': 100});
}

function distance_func(lat1, lon1, lat2, lon2) {
    var p = 0.017453292519943295;    // Math.PI / 180
    var c = Math.cos;
    var a = 0.5 - c((lat2 - lat1) * p) / 2 +
        c(lat1 * p) * c(lat2 * p) *
        (1 - c((lon2 - lon1) * p)) / 2;

    return 12742 * Math.asin(Math.sqrt(a)); // 2 * R; R = 6371 km
}

function calcDist(bike_or_station) {
    dist = {};
    if (bike_or_station === "bike") {
        for (var key in stations) {
            if (stations[key][2] > 0) {
                distance = distance_func(myLatLng["lat"], myLatLng["lng"], stations[key][0], stations[key][1]);
                dist[key] = distance;
            }
        }
    } else {
        for (var key in stations) {
            if (stations[key][3] > 0) {
                distance = distance_func(myLatLng["lat"], myLatLng["lng"], stations[key][0], stations[key][1]);
                dist[key] = distance;
            }
        }
    }
    dist = sort_object(dist);
    num = dist[0][0];
    $("#success-alert").html("Bike Station Found!").fadeTo(2000, 500).slideUp(500, function () {
        $("#success-alert").slideUp(500);
    });

    return num;

}

function sort_object(dict) {
// Create items array
    var items = Object.keys(dict).map(function (key) {
        return [key, dict[key]];
    });

// Sort the array based on the second element
    items.sort(function (first, second) {
        return second[1] - first[1];
    });

    items.reverse();
// Create a new array with only the first 5 items
    return items.slice(0, 5);
}

function offsetMap() {

    if (routeBounds !== false) {

        // Clear listener defined in directions results
        google.maps.event.clearListeners(map, 'idle');

        // Top right corner
        var topRightCorner = new google.maps.LatLng(map.getBounds().getNorthEast().lat(), map.getBounds().getNorthEast().lng());

        // Top right point
        var topRightPoint = fromLatLngToPoint(topRightCorner).x;

        // Get pixel position of leftmost and rightmost points
        var leftCoords = routeBounds.getSouthWest();
        var leftMost = fromLatLngToPoint(leftCoords).x;
        var rightMost = fromLatLngToPoint(routeBounds.getNorthEast()).x;

        // Calculate left and right offsets
        var leftOffset = (overlayWidth - leftMost);
        var rightOffset = ((topRightPoint - rightMargin) - rightMost);

        // Only if left offset is needed
        if (leftOffset >= 0) {

            if (leftOffset < rightOffset) {

                var mapOffset = Math.round((rightOffset - leftOffset) / 2);

                // Pan the map by the offset calculated on the x axis
                map.panBy(-mapOffset, 0);

                // Get the new left point after pan
                var newLeftPoint = fromLatLngToPoint(leftCoords).x;

                if (newLeftPoint <= overlayWidth) {

                    // Leftmost point is still under the overlay
                    // Offset map again
                    offsetMap();
                }

            } else {

                // Cannot offset map at this zoom level otherwise both leftmost and rightmost points will not fit
                // Zoom out and offset map again
                map.setZoom(map.getZoom() - 1);
                offsetMap();
            }
        }
    }
}

function fromLatLngToPoint(latLng) {

    var scale = Math.pow(2, map.getZoom());
    var nw = new google.maps.LatLng(map.getBounds().getNorthEast().lat(), map.getBounds().getSouthWest().lng());
    var worldCoordinateNW = map.getProjection().fromLatLngToPoint(nw);
    var worldCoordinate = map.getProjection().fromLatLngToPoint(latLng);

    return new google.maps.Point(Math.floor((worldCoordinate.x - worldCoordinateNW.x) * scale), Math.floor((worldCoordinate.y - worldCoordinateNW.y) * scale));
}

function calcRoute(start, end, type) {
    start = new google.maps.LatLng(start["lat"], start["lng"]);
    end = new google.maps.LatLng(end[0], end[1]);
    after_directions_latlng = end;
    if (type == "bike") {
        travel_mode = google.maps.DirectionsTravelMode.BICYCLING;
    } else {
        travel_mode = google.maps.DirectionsTravelMode.TRANSIT;
    }
    var request = {
        origin: start,
        destination: end,
        travelMode: travel_mode
    };

    directionsService.route(request, function (response, status) {
        if (status === google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(response);
            directionsDisplay.setMap(map);
            if ($('#overlay').length) {
                // pass;
            } else {
                $('#card').append("" +
                    "            <div class='card' id=\"overlay\">\n" +
                    "                <span id='close'\n" +
                    "                      onClick='this.parentNode.parentNode.removeChild(this.parentNode);  return false;'>x</span>\n" +
                    "                <div id=\"overlayContent\"></div>\n" +
                    "            </div>\n"
                );
                $('#close').on('click', function () {
                    directionsDisplay.setMap(null);
                    directionsDisplay.setPanel(null);
                    map.setZoom(15);
                    map.setCenter(after_directions_latlng);
                });


                directionsDisplay.setPanel(document.getElementById("overlayContent"));

            }

            // Define route bounds for use in offsetMap function
            routeBounds = response.routes[0].bounds;

            // Write directions steps

            // Wait for map to be idle before calling offsetMap function
            google.maps.event.addListener(map, 'idle', function () {

                // Offset map
                offsetMap();
            });

            // Listen for directions changes to update bounds and reapply offset
            google.maps.event.addListener(directionsDisplay, 'directions_changed', function () {

                // Get the updated route directions response
                var updatedResponse = directionsDisplay.getDirections();

                // Update route bounds
                routeBounds = updatedResponse.routes[0].bounds;
                console.log(routeBounds);
                // Fit updated bounds
                map.fitBounds(routeBounds);

                // Write directions steps

                // Offset map
                offsetMap();
            });
        }
    });
}